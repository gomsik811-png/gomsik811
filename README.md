# Automatic Meeting Minutes from Audio

This repo contains a small Python CLI that converts a recorded meeting audio file into a clean set of meeting minutes using OpenAI Whisper for transcription and GPT-based models for summarization.

## Quick start (한 줄 요약)
1. **필수 설치**: `pip install -r requirements.txt`
2. **키 위치**: 프로젝트 루트에 `.env` 만들고 `OPENAI_API_KEY=...` 한 줄 저장
3. **실행**: `python meeting_notes.py input_audio.m4a --output minutes.md --title "팀 미팅"`
4. **길이 긴 파일**: `--chunk-seconds 300` 같이 초 단위로 잘라 Whisper 부담 줄이기

## 무엇을 어디에 두면 되는지 (폴더/파일 위치)
- **프로젝트 루트**: `meeting_notes.py`, `requirements.txt`, `README.md`와 같은 위치.
- **.env**: 루트에 `.env` 파일을 만들고 아래처럼 API 키를 한 줄로 적어둡니다.
  ```env
  OPENAI_API_KEY=sk-...
  ```
- **오디오 파일**: 아무 위치나 가능하지만, 경로가 길면 `audio/input.m4a` 같이 프로젝트 내부 폴더를 만들어 넣어두면 편합니다.
- **출력 파일**: 기본은 루트에 `minutes.md`로 저장되며 `--output logs/2024-06-미팅.md`처럼 원하는 위치를 지정할 수 있습니다.

## 단계별 자세한 사용법
### 0) 사전 준비 (필수 설치)
- Python 3.11+ (Anaconda 환경 권장)
- `pip install -r requirements.txt`

### 1) Anaconda Prompt에서 환경 만들기/켜기
```bash
conda create -n meeting-minutes python=3.11 -y
conda activate meeting-minutes
```
- `argument -n/--name expected one argument` 에러가 나면 `meeting-minutes` 이름 부분이 빠지지 않았는지 확인하고 위 두 줄을 한 줄씩 그대로 복사해 실행하세요.

### 2) API 키 저장 위치 정하기
- **가장 쉬운 방법**: 루트에 `.env` 파일 생성 → `OPENAI_API_KEY=...` 입력 → 저장.
- **터미널에서만 쓰기**: Anaconda Prompt에서 `setx OPENAI_API_KEY "sk-..."` 실행 후 새 창을 엽니다.

### 3) 오디오 파일 두기
- 파일 위치는 자유입니다. 예시로 프로젝트 루트에 `audio/weekly.m4a`를 넣었다고 가정합니다.

### 4) VS Code에서 실행 (GUI 선호 시)
1. VS Code 실행 → 명령 팔레트(⇧⌘P / Ctrl+Shift+P) → **Python: Select Interpreter** → `meeting-minutes` 선택
2. 좌측 **Run & Debug** → **Run meeting_notes** 구성 선택
3. `.vscode/launch.json`의 `programArgs` 값을 오디오 경로로 수정 (예: `audio/weekly.m4a`)
4. 디버그 실행 ▶️ → 완료 후 루트에 `minutes.md` 생성

### 5) 터미널에서 바로 실행 (빠른 방법)
```bash
python meeting_notes.py audio/weekly.m4a --output minutes.md --title "주간 회의"
```

### 6) 길이가 긴 녹음 처리
- 5분 단위로 자르려면 `--chunk-seconds 300` 옵션을 추가합니다.
  ```bash
  python meeting_notes.py audio/weekly.m4a --chunk-seconds 300 --output minutes.md
  ```
- 더 짧게 자르고 싶으면 숫자(초 단위)만 줄이면 됩니다.

### 7) 결과물을 GitHub/유튜브에 쓰기
- 생성된 `minutes.md`에는 요약/결정/액션아이템/타임라인/전체 녹취가 포함됩니다.
- README나 이슈 설명, 유튜브 영상 설명란에 그대로 붙여넣으면 됩니다.

## 가장 빠르게 쓰는 순서 (요약)
1. **가상환경 열기**: Anaconda Prompt에서 `conda activate meeting-minutes`(없다면 README 아래 가이드를 따라 생성).
2. **키 확인**: 프로젝트 루트에 `.env`를 두고 `OPENAI_API_KEY=...`가 들어있는지 확인.
3. **파일만 넣어 실행**: VS Code 디버그 구성(**Run meeting_notes**)에서 `programArgs`를 녹음 파일 경로로 바꾸고 실행하거나, 터미널에서 아래처럼 실행합니다.
   ```bash
   python meeting_notes.py path/to/audio.m4a --output minutes.md --title "팀 미팅"
   ```
4. **길이 긴 파일**: 필요하면 `--chunk-seconds 300` 옵션을 추가해 5분 단위로 자릅니다.

## Features
- Loads `OPENAI_API_KEY` automatically from the environment or `.env`.
- Validates audio input and supports chunking long files for stable Whisper runs.
- Produces structured minutes including summary, decisions, action items, and timestamps.
- Exports minutes as Markdown for easy sharing to GitHub and video descriptions on YouTube.

## Example output
```markdown
# Meeting Minutes - 2024-06-11

## Summary
- Team aligned on launch timeline for Q3.
- Backend migration blocked by missing staging data.

## Decisions
- Proceed with feature freeze on June 20.

## Action Items
- [ ] Alice — deliver staging dump by Jun 13
- [ ] Bob — finalize QA checklist by Jun 18

## Timeline
- 00:00:00 Kickoff & agenda
- 00:05:12 Backend migration discussion
- 00:22:41 QA readiness review
```

## CLI options
- `--title` / `--date`: customize the Markdown heading and date stamp.
- `--chunk-seconds`: split long audio into N-second segments before transcription.
- `--language`: language hint for Whisper (e.g., `en`, `ko`).
- `--whisper-prompt`: context phrase that can improve transcription accuracy for names/jargon.
- `--summary-model`: GPT model for summarization (`gpt-4o-mini` by default).

## Notes
- Whisper works best with clear audio; consider recording directly from your meeting tool.
- For very long recordings, adjust `--chunk-seconds` to balance speed and quality.
- If you plan to publish a walkthrough on YouTube, use the generated Markdown minutes as your video description.

## GitHub Code 탭에 올리는 방법 (처음부터 끝까지)
아직 GitHub 원격 저장소가 없다는 가정으로, 로컬(또는 Codespace)에서 작업한 내용을 본인 GitHub 계정의 **Code** 탭으로 푸시하는 절차입니다.

1. **GitHub에서 새 저장소 생성**: 브라우저에서 GitHub → New repository → 저장소 이름 입력 → **Create repository**.
2. **원격 주소 복사**: 생성 직후 페이지에 표시되는 `https://github.com/USERNAME/REPO.git` HTTPS 주소를 복사합니다.
3. **프로젝트 루트에서 원격 등록**:
   ```bash
   git remote add origin https://github.com/USERNAME/REPO.git
   ```
   이미 원격이 설정돼 있다면 `git remote set-url origin ...`으로 교체합니다.
4. **현재 브랜치 확인**: 이 템플릿은 기본으로 `work` 브랜치를 사용합니다. `git branch --show-current`로 확인하세요.
5. **커밋 만들기** (필요 시): 수정이 있다면
   ```bash
   git add .
   git commit -m "Add meeting minutes CLI"
   ```
6. **푸시**: 현재 브랜치를 원격에 올립니다.
   ```bash
   git push -u origin work
   ```
   - 기본 브랜치 이름을 `main`으로 쓰고 싶다면 `git push -u origin main`처럼 브랜치명을 바꾸고, 필요하면 `git branch -M main`으로 로컬 이름도 변경 후 푸시합니다.
7. **Code 탭에서 확인**: GitHub 저장소 페이지의 **Code** 탭에서 파일이 올라간 것을 확인합니다.

## 아나콘다 프롬프트 + VS Code 환경 세팅
Windows에서 Anaconda Prompt와 VS Code를 함께 쓰는 경우 아래 순서를 따르면 바로 실행할 수 있습니다.

1. **가상환경 생성 및 활성화** (Python 3.11 이상 권장)
   ```bash
   conda create -n meeting-minutes python=3.11 -y
   conda activate meeting-minutes
   ```
   - `argument -n/--name expected one argument` 에러가 뜨면, 위 명령어에서 `meeting-minutes` 부분이 빠지지 않았는지 확인하고 한 줄씩 그대로 복사해 실행하세요.

2. **필수 라이브러리 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **API 키 설정 (.env 권장)**
   - 프로젝트 루트에 `.env` 파일을 만들고 아래처럼 키를 넣습니다.
     ```env
     OPENAI_API_KEY=sk-...
     ```
   - Anaconda Prompt에서만 쓸 거라면 환경 변수로도 설정할 수 있습니다.

4. **VS Code에서 인터프리터 선택**
   - VS Code 명령 팔레트(⇧⌘P / Ctrl+Shift+P) → "Python: Select Interpreter" → `meeting-minutes` 선택.

5. **디버그 실행**
   - `.vscode/launch.json` 기본 설정이 포함되어 있습니다.
   - VS Code 좌측 Run & Debug에서 **"Run meeting_notes"** 선택 후 녹음 파일 경로(`programArgs`)만 바꿔 실행하면 `minutes.md`가 생성됩니다.

6. **터미널 수동 실행 (선호 시)**
   ```bash
   python meeting_notes.py path/to/audio.m4a --output minutes.md --title "팀 미팅"
   ```

> 팁: 길이가 긴 녹음은 `--chunk-seconds 300`처럼 5분 단위로 자르면 Whisper 메모리 사용량이 줄고 VS Code 터미널에서도 안정적으로 돌아갑니다.

