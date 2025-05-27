# VeriView AI 서버 모듈화 가이드

## 1. 프로젝트 구조

```
ai_server/
├── modules/                  # 모듈화된 기능 폴더
│   ├── text_to_speech/       # TTS 모듈
│   │   ├── __init__.py
│   │   └── tts_module.py
│   └── common/               # 공통 유틸리티 
│       ├── audio_utils.py    # 오디오 관련 유틸리티
│       └── file_utils.py     # 파일 관련 유틸리티
├── run.py                    # 서버 실행 스크립트
├── main_server.py            # 메인 서버 (LLM 포함)
└── test_server.py            # 테스트 서버 (LLM 제외)
```

## 2. 모듈 설명

### 2.1 TTS 모듈 (modules/text_to_speech)

- **tts_module.py**: 텍스트를 음성으로 변환하는 기능 제공
  - gTTS(Google Text-to-Speech): 경량 한국어 TTS 지원
  - pyttsx3: 오프라인 TTS 엔진 (선택적)

### 2.2 공통 유틸리티 (modules/common)

- **audio_utils.py**: 오디오 처리 관련 유틸리티
  - 비디오에서 오디오 추출, 오디오 분석 등 기능
- **file_utils.py**: 파일 관리 유틸리티
  - 임시 파일 정리 등 기능

## 3. 서버 설정

### 3.1 서버 모드 설정

- **main**: LLM, OpenFace, Whisper, TTS, Librosa 등 실제 AI 모듈 사용 (포트: 5001)
- **test**: LLM 제외, 고정 응답 반환 (OpenFace, Whisper, TTS, Librosa 모듈 사용) (포트: 5000)

### 3.2 설정 방법

- 환경 변수: `SERVER_MODE=main` 또는 `SERVER_MODE=test`
- 명령줄 인자: `python run.py --mode main` 또는 `python run.py --mode test`

## 4. API 엔드포인트

### 4.1 공통 엔드포인트

- `/ai/health`: 헬스 체크
- `/ai/test`: 연결 테스트 및 상태 확인
- `/ai/tts-test`: TTS 테스트

### 4.2 토론면접 엔드포인트

- `/ai/debate/<debate_id>/ai-opening`: AI 입론 생성
- `/ai/debate/<debate_id>/opening-video`: 사용자 입론 영상 처리
- `/ai/debate/<debate_id>/rebuttal-video`: 사용자 반론 영상 처리
- `/ai/debate/<debate_id>/counter-rebuttal-video`: 사용자 재반론 영상 처리
- `/ai/debate/<debate_id>/closing-video`: 사용자 최종 변론 영상 처리

### 4.3 개인면접 엔드포인트

- `/ai/interview/start`: 개인면접 시작
- `/ai/interview/generate-question`: 면접 질문 생성
- `/ai/interview/<interview_id>/question`: 면접 질문 조회
- `/ai/interview/<interview_id>/<question_type>/answer-video`: 개인면접 답변 영상 처리

### 4.4 공고추천 엔드포인트

- `/ai/recruitment/posting`: 백엔드 연동용 공고추천
- `/ai/jobs/recommend`: 공고 추천
- `/ai/jobs/categories`: 공고 카테고리 목록 조회
- `/ai/jobs/stats`: 공고 통계 정보 조회

## 5. TTS 스트리밍 사용 방법

TTS 스트리밍을 사용하려면 다음과 같이 `stream=true` 쿼리 파라미터를 추가합니다:

```
http://localhost:5000/ai/debate/1/ai-opening?stream=true
http://localhost:5000/ai/interview/1/question?stream=true
http://localhost:5000/ai/tts-test?text=안녕하세요
```

## 6. 의존성 설치

```bash
# 기본 의존성
pip install flask flask_cors

# TTS 모듈
pip install gtts
# 또는
pip install pyttsx3

# 음성 인식 및 분석
pip install openai-whisper
pip install librosa

# 공고추천
pip install numpy pandas scikit-learn

# 모든 의존성
pip install -r requirements.txt
```

## 7. 테스트 방법

```bash
# 서버 실행
python run.py --mode test

# curl을 사용한 테스트
curl -X GET "http://localhost:5000/ai/tts-test?text=안녕하세요"

# 토론면접 테스트
curl -X POST -F "video=@test_video.mp4" http://localhost:5000/ai/debate/1/opening-video

# 스트리밍 테스트
curl http://localhost:5000/ai/tts-test?text=안녕하세요 | ffmpeg -i - -acodec mp3 response.mp3
```
