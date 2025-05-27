# VeriView AI 서버 실행 가이드

## 준비 사항

1. Python 3.8 이상 설치
2. 필요한 패키지 설치

```bash
# 기본 패키지 설치
pip install flask flask_cors gtts

# 추가 패키지 설치 (선택적)
pip install openai-whisper librosa numpy pandas scikit-learn

# 모든 패키지 설치
pip install -r requirements.txt
```

## 실행 방법

### 1. 테스트 서버 실행 (LLM 제외, 고정 응답)

```bash
# 환경 변수 설정
export SERVER_MODE=test
# 또는 Windows
set SERVER_MODE=test

# 실행
python run.py
# 또는 명시적 모드 지정
python run.py --mode test
```

### 2. 메인 서버 실행 (LLM 포함)

```bash
# 환경 변수 설정
export SERVER_MODE=main
# 또는 Windows
set SERVER_MODE=main

# 실행
python run.py
# 또는 명시적 모드 지정
python run.py --mode main
```

## 테스트 방법

### 1. 서버 상태 확인

```bash
# 헬스 체크
curl -X GET http://localhost:5000/ai/health

# 테스트 엔드포인트
curl -X GET http://localhost:5000/ai/test
```

### 2. TTS 테스트

```bash
# TTS 테스트
curl -X GET "http://localhost:5000/ai/tts-test?text=안녕하세요"

# 오디오 파일로 저장
curl -X GET "http://localhost:5000/ai/tts-test?text=안녕하세요" > test.mp3
```

### 3. 토론면접 테스트

```bash
# AI 입론 생성
curl -X POST -H "Content-Type: application/json" -d '{"topic":"인공지능","position":"CON","debate_id":1}' http://localhost:5000/ai/debate/1/ai-opening

# AI 입론 생성 (TTS 스트리밍)
curl -X POST -H "Content-Type: application/json" -d '{"topic":"인공지능","position":"CON","debate_id":1}' "http://localhost:5000/ai/debate/1/ai-opening?stream=true" > ai_opening.mp3

# 사용자 입론 영상 처리
curl -X POST -F "video=@test_video.mp4" http://localhost:5000/ai/debate/1/opening-video
```

### 4. 개인면접 테스트

```bash
# 개인면접 시작
curl -X POST -H "Content-Type: application/json" -d '{}' http://localhost:5000/ai/interview/start

# 면접 질문 생성
curl -X POST -H "Content-Type: application/json" -d '{"interview_id":1,"job_category":"ICT"}' http://localhost:5000/ai/interview/generate-question

# 면접 질문 조회
curl -X GET http://localhost:5000/ai/interview/1/question

# 면접 질문 조회 (TTS 스트리밍)
curl -X GET "http://localhost:5000/ai/interview/1/question?stream=true" > question.mp3

# 답변 영상 처리
curl -X POST -F "video=@test_video.mp4" http://localhost:5000/ai/interview/1/INTRO/answer-video
```

### 5. 공고추천 테스트

```bash
# 공고추천
curl -X POST -H "Content-Type: application/json" -d '{"category":"ICT"}' http://localhost:5000/ai/recruitment/posting

# 카테고리 조회
curl -X GET http://localhost:5000/ai/jobs/categories
```

## 포트 정보

- 테스트 서버: `http://localhost:5000`
- 메인 서버: `http://localhost:5001`

## 문제 해결

### 1. 모듈 임포트 오류

```
ImportError: No module named 'gtts'
```

해결 방법: 필요한 패키지 설치

```bash
pip install gtts
```

### 2. 포트 충돌

```
OSError: [Errno 98] Address already in use
```

해결 방법: 포트 변경

```bash
python run.py --port 5002
```

### 3. FFmpeg 오류

```
Error: FFmpeg not found
```

해결 방법: FFmpeg 설치

```bash
# Ubuntu/Debian
apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# FFmpeg 웹사이트에서 다운로드 후 설치
```

## 참고 문서

- [Flask 문서](https://flask.palletsprojects.com/)
- [gTTS 문서](https://gtts.readthedocs.io/)
- [Whisper 문서](https://github.com/openai/whisper)
- [Librosa 문서](https://librosa.org/)
