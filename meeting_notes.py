"""CLI to turn meeting audio recordings into structured minutes.

Requires an `OPENAI_API_KEY` environment variable.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import Iterable, List, Optional

from openai import OpenAI
from pydub import AudioSegment
from dotenv import load_dotenv


@dataclass
class ActionItem:
    description: str
    owner: Optional[str] = None
    due_date: Optional[str] = None


@dataclass
class MeetingMinutes:
    date: str
    summary: List[str]
    decisions: List[str]
    action_items: List[ActionItem]
    timeline: List[str]
    transcript: str

    def to_markdown(self, title: str) -> str:
        lines: List[str] = [f"# {title} - {self.date}", ""]
        if self.summary:
            lines.append("## Summary")
            lines.extend([f"- {item}" for item in self.summary])
            lines.append("")
        if self.decisions:
            lines.append("## Decisions")
            lines.extend([f"- {item}" for item in self.decisions])
            lines.append("")
        if self.action_items:
            lines.append("## Action Items")
            for action in self.action_items:
                owner_text = f"{action.owner} — " if action.owner else ""
                due_text = f" (due {action.due_date})" if action.due_date else ""
                lines.append(f"- [ ] {owner_text}{action.description}{due_text}")
            lines.append("")
        if self.timeline:
            lines.append("## Timeline")
            lines.extend([f"- {item}" for item in self.timeline])
            lines.append("")
        lines.append("## Full Transcript")
        lines.append(self.transcript)
        return "\n".join(lines).strip() + "\n"


SYSTEM_PROMPT = """You are a meticulous meeting scribe. Generate concise, structured minutes from a transcript.
Return only JSON using the following schema:
{
  "summary": ["bullet", ...],
  "decisions": ["decision", ...],
  "action_items": [
     {"description": "", "owner": "", "due_date": ""}
  ],
  "timeline": ["HH:MM:SS topic" , ...]
}
Keep bullets crisp and actionable. If data is missing, use empty arrays.
"""


def require_api_key() -> str:
    """Load and return the OpenAI API key, exiting early if missing."""

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY environment variable.")
    return api_key


def validate_audio_path(audio_path: pathlib.Path) -> pathlib.Path:
    if not audio_path.exists():
        raise SystemExit(f"Audio file not found: {audio_path}")
    if not audio_path.is_file():
        raise SystemExit(f"Audio path is not a file: {audio_path}")
    return audio_path


def chunk_audio(audio_path: pathlib.Path, chunk_seconds: int) -> Iterable[AudioSegment]:
    audio = AudioSegment.from_file(audio_path)
    stride = chunk_seconds * 1000
    for start_ms in range(0, len(audio), stride):
        yield audio[start_ms : start_ms + stride]


def transcribe_audio(client: OpenAI, audio_path: pathlib.Path, prompt: Optional[str], chunk_seconds: Optional[int], language: Optional[str]) -> str:
    audio_path = validate_audio_path(audio_path)

    if chunk_seconds and chunk_seconds > 0:
        segments = []
        for segment in chunk_audio(audio_path, chunk_seconds):
            with NamedTemporaryFile(suffix=".mp3") as temp:
                segment.export(temp.name, format="mp3")
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=open(temp.name, "rb"),
                    prompt=prompt,
                    language=language,
                )
            segments.append(response.text)
        return "\n".join(segments)

    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            prompt=prompt,
            language=language,
        )
    return response.text


def summarize_transcript(client: OpenAI, transcript: str, model: str, meeting_title: str, meeting_date: str) -> MeetingMinutes:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Meeting: {meeting_title}\n"
                f"Date: {meeting_date}\n"
                "Transcript:\n" + transcript
            ),
        },
    ]
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
    )
    content = completion.choices[0].message.content or "{}"

    data = {}
    for candidate in (content, content.strip().strip("`")):
        try:
            data = json.loads(candidate)
            break
        except json.JSONDecodeError:
            continue

    summary = data.get("summary", []) if isinstance(data.get("summary"), list) else []
    decisions = data.get("decisions", []) if isinstance(data.get("decisions"), list) else []
    raw_actions = data.get("action_items", []) if isinstance(data.get("action_items"), list) else []
    action_items = [
        ActionItem(
            description=item.get("description", "").strip(),
            owner=item.get("owner") or None,
            due_date=item.get("due_date") or None,
        )
        for item in raw_actions
        if isinstance(item, dict) and item.get("description")
    ]
    timeline = data.get("timeline", []) if isinstance(data.get("timeline"), list) else []

    return MeetingMinutes(
        date=meeting_date,
        summary=summary,
        decisions=decisions,
        action_items=action_items,
        timeline=timeline,
        transcript=transcript,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert meeting audio into structured minutes.")
    parser.add_argument("audio", type=pathlib.Path, help="Path to the audio file (mp3, m4a, wav, etc.)")
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("minutes.md"), help="Where to write the minutes (Markdown).")
    parser.add_argument("--title", type=str, default="Meeting Minutes", help="Title used in the Markdown output.")
    parser.add_argument("--date", type=str, default=dt.date.today().isoformat(), help="Date string to stamp the minutes.")
    parser.add_argument("--chunk-seconds", type=int, default=None, help="Chunk size for long audio (in seconds).")
    parser.add_argument("--language", type=str, default=None, help="Language hint for Whisper (e.g., en, ko).")
    parser.add_argument("--whisper-prompt", type=str, default=None, help="Optional prompt to bias Whisper transcription.")
    parser.add_argument(
        "--summary-model",
        type=str,
        default="gpt-4o-mini",
        help="Model used for summarization (e.g., gpt-4o-mini, gpt-4o).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = OpenAI(api_key=require_api_key())

    transcript = transcribe_audio(
        client=client,
        audio_path=args.audio,
        prompt=args.whisper_prompt,
        chunk_seconds=args.chunk_seconds,
        language=args.language,
    )

    minutes = summarize_transcript(
        client=client,
        transcript=transcript,
        model=args.summary_model,
        meeting_title=args.title,
        meeting_date=args.date,
    )

    args.output.write_text(minutes.to_markdown(args.title), encoding="utf-8")
    print(f"Minutes saved to {args.output.resolve()}")


if __name__ == "__main__":
    main()
