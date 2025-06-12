# VeriView AI Server - Windows Edition

Windows 환경에서 VeriView AI 서버를 실행하기 위한 가이드입니다.

## 🪟 Windows 전용 기능

- **한글 인코딩 자동 처리**: Windows의 한글 인코딩 문제 자동 해결
- **경로 자동 처리**: Windows 경로 구분자 자동 변환
- **브라우저 자동 실행**: 서버 시작 시 테스트 페이지 자동 열기
- **안전한 호스트 설정**: 기본적으로 localhost(127.0.0.1) 사용
- **포트 충돌 방지**: 포트 사용 가능 여부 자동 확인
- **의존성 자동 체크**: 필요한 패키지 설치 여부 확인

## 🚀 빠른 시작

### 방법 1: 배치 파일 사용 (권장)

1. **메인 모드 실행**
   ```cmd
   start_windows.bat
   ```

2. **테스트 모드 실행**
   ```cmd
   start_test_windows.bat
   ```

3. **디버그 모드 실행**
   ```cmd
   start_debug_windows.bat
   ```

### 방법 2: 명령줄 직접 실행

1. **메인 모드 (완전 기능)**
   ```cmd
   python run_windows.py --mode main
   ```

2. **테스트 모드 (D-ID API 테스트)**
   ```cmd
   python run_windows.py --mode test
   ```

3. **디버그 모드 (상세 로깅)**
   ```cmd
   python run_windows.py --mode debug
   ```

4. **프로덕션 모드**
   ```cmd
   python run_windows.py --mode production
   ```

## ⚙️ 추가 옵션

### 포트 변경
```cmd
python run_windows.py --mode main --port 8080
```

### 호스트 변경 (외부 접근 허용)
```cmd
python run_windows.py --mode main --host 0.0.0.0
```

### 브라우저 자동 실행 비활성화
```cmd
python run_windows.py --mode main --no-browser
```

### 모든 옵션 조합
```cmd
python run_windows.py --mode main --port 8080 --host 0.0.0.0 --no-browser
```

## 📋 사전 요구사항

### 1. Python 설치
- **Python 3.8 이상** 필요
- [Python 공식 홈페이지](https://python.org)에서 다운로드
- 설치 시 "Add Python to PATH" 체크 필수

### 2. 필수 패키지 설치
```cmd
pip install flask flask-cors python-dotenv requests numpy opencv-python librosa openai-whisper
```

### 3. 선택적 패키지 (AI 기능 향상)
```cmd
pip install torch torchvision torchaudio
pip install transformers
pip install TTS
```

## 🔧 환경 설정

### 1. .env 파일 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# D-ID API 설정
D_ID_API_KEY=your_actual_d_id_api_key_here
D_ID_API_URL=https://api.d-id.com

# 서버 설정
FLASK_ENV=development
FLASK_DEBUG=1

# 디렉토리 설정
D_ID_CACHE_DIR=./videos
TEMP_DIR=./temp
LOG_DIR=./logs

# 기타 설정
PREFERRED_AVATAR_SERVICE=D_ID
USE_FALLBACK_SERVICE=True
WHISPER_MODEL_SIZE=base
```

### 2. 환경 변수 확인
```cmd
# Windows 명령 프롬프트에서
set D_ID_API_KEY=your_api_key_here

# PowerShell에서
$env:D_ID_API_KEY="your_api_key_here"
```

## 📁 폴더 구조

실행 후 다음과 같은 폴더들이 자동으로 생성됩니다:

```
ai_server/
├── run_windows.py          # Windows용 실행 스크립트
├── start_windows.bat        # 메인 모드 배치 파일
├── start_test_windows.bat   # 테스트 모드 배치 파일
├── start_debug_windows.bat  # 디버그 모드 배치 파일
├── logs/                    # 로그 파일 저장
│   ├── ai_server_prod.log
│   ├── ai_server_test.log
│   └── ai_server_debug.log
├── temp/                    # 임시 파일 저장
├── videos/                  # 생성된 영상 저장
│   └── samples/            # 샘플 영상
└── .env                    # 환경 변수 설정
```

## 🌐 접속 주소

서버 실행 후 다음 주소들로 접속할 수 있습니다:

- **메인 페이지**: http://localhost:5000
- **테스트 페이지**: http://localhost:5000/ai/test
- **API 문서**: http://localhost:5000/api/docs (예정)

## 🔍 주요 엔드포인트

### 채용 공고 추천
```
POST /ai/recruitment/posting
```

### 면접 관련
```
POST /ai/interview/generate-question
POST /ai/interview/ai-video
POST /ai/interview/<interview_id>/<question_type>/answer-video
POST /ai/interview/<interview_id>/genergate-followup-question
```

### 토론 관련
```
POST /ai/debate/<debate_id>/ai-opening
POST /ai/debate/ai-opening-video
POST /ai/debate/ai-rebuttal-video
POST /ai/debate/ai-counter-rebuttal-video
POST /ai/debate/ai-closing-video
POST /ai/debate/<debate_id>/opening-video
POST /ai/debate/<debate_id>/rebuttal-video
POST /ai/debate/<debate_id>/counter-rebuttal-video
POST /ai/debate/<debate_id>/closing-video
```

## 🐛 문제 해결

### 1. Python을 찾을 수 없음
```
❌ 'python'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```
**해결방법**: Python을 PATH에 추가하거나 `python3` 명령어 사용

### 2. 포트가 이미 사용 중
```
❌ 포트 5000가 이미 사용 중입니다.
```
**해결방법**: 다른 포트 사용
```cmd
python run_windows.py --mode main --port 8080
```

### 3. 모듈을 찾을 수 없음
```
❌ ModuleNotFoundError: No module named 'flask'
```
**해결방법**: 필요한 패키지 설치
```cmd
pip install flask flask-cors python-dotenv
```

### 4. 한글 인코딩 문제
Windows에서 한글이 깨지는 경우, `run_windows.py`가 자동으로 UTF-8 인코딩을 설정합니다.

### 5. D-ID API 키 문제
```
❌ D_ID_API_KEY가 설정되지 않음
```
**해결방법**: `.env` 파일에 올바른 API 키 설정

## 📊 로그 확인

### 로그 파일 위치
- **프로덕션**: `logs/ai_server_prod.log`
- **테스트**: `logs/ai_server_test.log`
- **디버그**: `logs/ai_server_debug.log`

### 실시간 로그 확인 (PowerShell)
```powershell
Get-Content -Path "logs/ai_server_debug.log" -Wait -Tail 10
```

## 🔒 보안 주의사항

1. **API 키 보호**: `.env` 파일을 Git에 커밋하지 마세요
2. **방화벽 설정**: 외부 접근이 필요한 경우만 `--host 0.0.0.0` 사용
3. **포트 관리**: 기본 포트 5000 외의 포트 사용 권장

## 🆕 업데이트 및 유지보수

### 패키지 업데이트
```cmd
pip install --upgrade flask flask-cors python-dotenv
```

### 로그 정리
```cmd
# logs 폴더의 오래된 로그 파일 정리
del logs\*.log
```

### 임시 파일 정리
```cmd
# temp 폴더의 임시 파일 정리 (자동으로 정리되지만 수동으로도 가능)
del temp\temp_*
```

## 💡 팁과 요령

1. **첫 실행시**: `start_test_windows.bat`로 테스트 후 메인 모드 실행
2. **개발시**: `start_debug_windows.bat`로 상세 로그 확인
3. **배포시**: `start_windows.bat`로 안정적인 실행
4. **문제 발생시**: `logs` 폴더의 로그 파일 확인

## 📞 지원

문제가 발생하거나 질문이 있으시면:
1. 로그 파일 확인
2. 이 가이드의 문제 해결 섹션 참조
3. 필요시 개발팀에 문의

---

**Made for Windows 💙 VeriView AI Team**
