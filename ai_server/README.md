# AI 서버

VeriView 프로젝트의 AI 분석 서버입니다. OpenFace, Whisper, Librosa를 활용한 실시간 토론 분석 기능을 제공합니다.

## 폴더 구조

```
ai_server/
├── src/
│   ├── app/              # 프로덕션용 Flask 서버
│   │   ├── debate_server.py     # 메인 Flask 서버
│   │   ├── debate_client.py     # 클라이언트 코드
│   │   ├── realtime_facial_analysis.py  # 얼굴 분석
│   │   └── realtime_speech_to_text.py   # 음성 인식
│   └── tests/            # 테스트용 구현
│       ├── test_debate.py       # 통합 테스트 클래스
│       ├── realtime_facial_analysis.py  # 테스트용 얼굴 분석
│       └── realtime_speech_to_text.py   # 테스트용 음성 인식
├── tools/
│   └── FeatureExtraction.exe    # OpenFace 실행 파일
├── resources/
│   └── debate_topic.txt         # 토론 주제 목록 (424개)
├── models/                      # 모델 파일
├── run.py                       # 메인 실행 파일 (환경에 따라 분기)
├── test_runner.py               # 테스트 실행 스크립트
├── server_runner.py             # Flask 서버 실행 스크립트
└── requirements.txt             # 의존성 패키지
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 테스트 모드 실행 (기능 테스트)

```bash
# 테스트 모드로 실행
python test_runner.py [영상파일경로]

# 예시
python test_runner.py sample_video.mp4
```

### 3. Flask 서버 실행 (백엔드 연동)

```bash
# Flask 서버 실행
python server_runner.py
```

또는 환경변수를 설정하여 run.py 사용:

```bash
# 프로덕션 모드
set USE_TEST_MODE=false
python run.py

# 테스트 모드 (기본값)
set USE_TEST_MODE=true
python run.py
```

## 주요 기능

### OpenFace 얼굴 분석
- 실시간 얼굴 표정 분석
- 시선 추적
- 감정 상태 평가

### Whisper 음성 인식
- 한국어 음성을 텍스트로 변환
- 영상에서 오디오 추출 및 변환

### Librosa 음성 분석
- 피치 안정성 측정
- 에너지 레벨 분석
- 템포 분석

### 토론 점수 계산
- 적극성, 협력적태도, 의사소통능력
- 논리력, 문제해결능력
- 목소리, 행동 점수

## API 엔드포인트

### 테스트 연결
- `GET /ai/test` - 서버 상태 확인

### 토론 관련
- `POST /ai/debate/{debate_id}/ai-opening` - AI 입론 생성
- `POST /ai/debate/{debate_id}/opening-video` - 입론 영상 분석
- `POST /ai/debate/{debate_id}/rebuttal-video` - 반론 영상 분석
- `POST /ai/debate/{debate_id}/counter-rebuttal-video` - 재반론 영상 분석
- `POST /ai/debate/{debate_id}/closing-video` - 최종변론 영상 분석

## 환경 설정

### 환경 변수
- `USE_TEST_MODE`: 테스트 모드 여부 (기본값: true)
- `OPENFACE_PATH`: OpenFace 실행파일 경로
- `ZONOS_API_KEY`: TTS API 키 (선택사항)

### 필수 파일
- `tools/FeatureExtraction.exe`: OpenFace 실행파일
- `resources/debate_topic.txt`: 토론 주제 목록

## 참고사항

1. **OpenFace**: 얼굴 분석을 위해 반드시 필요
2. **FFmpeg**: 영상 변환을 위해 시스템에 설치 필요
3. **GPU**: Whisper 모델 실행 시 GPU 사용 권장
4. **메모리**: 대용량 영상 분석 시 충분한 메모리 필요

## 문제 해결

### OpenFace 오류
- `tools/FeatureExtraction.exe` 파일 존재 여부 확인
- OPENFACE_PATH 환경변수 설정

### Whisper 오류
- 충분한 GPU 메모리 확보
- 영상 파일 형식 확인 (mp4, webm 지원)

### 종합 연동 테스트
1. 테스트 모드로 먼저 각 기능 확인
2. Flask 서버 실행하여 백엔드 연동 테스트
3. 프론트엔드에서 영상 업로드 테스트
