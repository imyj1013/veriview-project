# VeriView AI Server

VeriView 프로젝트의 AI 서버 모듈입니다. 토론면접, 개인면접, 공고추천 기능을 제공하는 Flask 기반 서버입니다.

## 주요 기능

### 1. 토론면접 (Debate Interview)
- AI와의 실시간 토론 진행
- 입론, 반론, 재반론, 최종변론 단계별 처리
- 음성인식 및 얼굴분석을 통한 종합적 평가
- 실시간 피드백 제공

### 2. 개인면접 (Personal Interview)  
- 개인별 맞춤 면접 질문 생성
- 답변 영상 분석 및 평가
- 다양한 질문 유형 지원 (일반, 기술, 행동)

### 3. 공고추천 (Job Recommendation)
- 면접 결과 기반 맞춤 공고 추천
- 카테고리별 공고 검색
- 백엔드와의 완전한 연동 지원

## 서버 모드

### Main Server (`main_server.py`)
**모든 AI 모듈을 포함한 완전한 AI 서버**

**포함된 기능:**
- **LLM (대화형 AI)**: GPT-4, Claude 등 실제 언어모델 사용
- **OpenFace 2.0**: 실시간 얼굴 분석 및 감정 인식
- **Whisper**: 고품질 음성 인식
- **TTS**: 자연스러운 음성 합성
- **Librosa**: 음성 특성 분석
- **공고추천**: ML 기반 개인화 추천

**실행 방법:**
```bash
python main_server.py
```

### Test Server (`test_server.py`)
**LLM을 제외한 AI 모듈 + 고정 응답**

**포함된 기능:**
- **LLM**: 대신 고정된 응답 사용 (비용 절약)
- **OpenFace 2.0**: 실시간 얼굴 분석 및 감정 인식
- **Whisper**: 고품질 음성 인식
- **TTS**: 자연스러운 음성 합성
- **Librosa**: 음성 특성 분석
- **공고추천**: ML 기반 개인화 추천

**실행 방법:**
```bash
python test_server.py
```

## 프로젝트 구조

```
ai_server/
├── main_server.py               # 메인 서버 (모든 AI 모듈 포함)
├── test_server.py               # 테스트 서버 (LLM 제외)
├── backend_integration_test.py  # 백엔드 연동 테스트
├── job_recommendation_module.py # 공고추천 모듈
├── server_runner.py             # (기존 서버, 사용 안함)
├── interview_features/          # 실제 AI 모듈들
│   ├── debate/                  # 토론면접 (LLM 포함)
│   └── personal_interview/      # 개인면접
├── test_features/               # 테스트 모듈들 (LLM 미사용)
│   ├── debate/                  # 토론면접 테스트
│   └── personal_interview/      # 개인면접 테스트
├── models/                      # 학습된 모델 파일
├── tools/                       # 외부 도구 (OpenFace 등)
└── resources/                   # 리소스 파일
```

## 설치 및 실행

### 1. 환경 설정
```bash
# Python 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. 서버 선택 및 실행

#### 완전한 AI 기능이 필요한 경우
```bash
# 모든 AI 모듈 사용 (LLM 포함)
python main_server.py
```

#### 테스트 또는 비용 절약이 필요한 경우
```bash
# LLM 제외, 나머지 AI 모듈 사용
python test_server.py
```

### 3. 서버 실행 확인
서버가 정상 실행되면 `http://localhost:5000`에서 접근 가능합니다.

```bash
# 서버 상태 확인
curl http://localhost:5000/ai/test

# 또는 브라우저에서
http://localhost:5000/ai/test
```

## 🔌 API 엔드포인트

### 기본 상태 확인
- `GET /ai/health` - 헬스 체크 및 서버 타입 확인
- `GET /ai/test` - 연결 테스트 및 모듈 상태 확인
- `GET /ai/debate/modules-status` - 상세 모듈 상태

### 토론면접 API
- `POST /ai/debate/<debate_id>/ai-opening` - AI 입론 생성
- `POST /ai/debate/<debate_id>/opening-video` - 사용자 입론 영상 처리
- `POST /ai/debate/<debate_id>/rebuttal-video` - 사용자 반론 영상 처리
- `POST /ai/debate/<debate_id>/counter-rebuttal-video` - 사용자 재반론 영상 처리
- `POST /ai/debate/<debate_id>/closing-video` - 사용자 최종변론 영상 처리
- `GET /ai/debate/<debate_id>/ai-rebuttal` - AI 반론 생성
- `GET /ai/debate/<debate_id>/ai-counter-rebuttal` - AI 재반론 생성
- `GET /ai/debate/<debate_id>/ai-closing` - AI 최종변론 생성

### 개인면접 API
- `POST /ai/interview/start` - 개인면접 시작
- `GET /ai/interview/<interview_id>/question` - 면접 질문 생성
- `POST /ai/interview/<interview_id>/answer-video` - 답변 영상 처리

### 공고추천 API
- `POST /ai/jobs/recommend` - 공고 추천 (면접 점수 또는 카테고리 기반)
- `GET /ai/jobs/categories` - 공고 카테고리 목록
- `GET /ai/jobs/stats` - 공고 통계 정보
- `POST /ai/recruitment/posting` - 백엔드 연동용 공고추천

## 🔗 백엔드 연동

### 연동 아키텍처
```
Frontend (React) → Backend (Spring Boot) → AI Server (Flask)
    :3000               :4000                  :5000
```

### 백엔드에서 AI 서버 호출
백엔드의 각 서비스에서 다음과 같이 AI 서버를 호출합니다:

#### RecruitmentService 연동
```java
// 백엔드 코드 (주석 해제 시)
String flaskUrl = "http://localhost:5000/ai/recruitment/posting";
ResponseEntity<RecruitmentResponse> response = restTemplate.exchange(
    flaskUrl, HttpMethod.POST, entity, RecruitmentResponse.class);
```

#### DebateService 연동
```java
// 백엔드 코드 (주석 해제 시)
String flaskUrl = "http://localhost:5000/ai/debate/" + debateId + "/ai-opening";
ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
    flaskUrl, HttpMethod.POST, requestEntity, ...);
```

### 연동 테스트
```bash
# 통합 연동 테스트 실행
python backend_integration_test.py

# 특정 서버만 테스트
python backend_integration_test.py ai        # AI 서버만
python backend_integration_test.py backend   # 백엔드만
python backend_integration_test.py both      # 둘 다 (기본값)
```

## 테스트 및 검증

### 1. 기본 기능 테스트
```bash
# 토론 AI 입론 테스트
curl -X POST http://localhost:5000/ai/debate/1/ai-opening \
  -H "Content-Type: application/json" \
  -d '{"topic": "인공지능", "position": "CON"}'

# 공고추천 테스트
curl -X POST http://localhost:5000/ai/jobs/recommend \
  -H "Content-Type: application/json" \
  -d '{"category": "ICT", "limit": 5}'

# 개인면접 시작 테스트
curl -X POST http://localhost:5000/ai/interview/start \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 2. 백엔드 연동 테스트
```bash
# 자동화된 통합 테스트
python backend_integration_test.py

# 결과 예시:
# AI 서버 상태: available
# 백엔드 서버 상태: available  
# 공고추천 연동: 정상
# 토론면접 연동: 정상
# 개인면접 연동: 정상
```

## 📊 서버 타입 비교

| 기능 | Main Server | Test Server |
|------|-------------|-------------|
| **LLM (GPT, Claude)** | 실제 사용 | 고정 응답 |
| **OpenFace 2.0** | 사용 | 사용 |
| **Whisper** | 사용 | 사용 |
| **TTS** | 사용 | 사용 |
| **Librosa** | 사용 | 사용 |
| **공고추천** | 사용 | 사용 |
| **비용** | 높음 (LLM API) | 낮음 |
| **응답 품질** | 최고 | 높음 |
| **개발/테스트** | 프로덕션용 | 개발/테스트용 |

## 🔧 환경 설정

### 필수 요구사항
- **Python**: 3.8 이상
- **FFmpeg**: 오디오/비디오 처리용
- **CUDA** (선택적): GPU 가속용

### 환경 변수 (선택적)
```bash
# LLM API 키 설정 (main_server.py 사용시)
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# 서버 설정
export AI_SERVER_PORT=5000
export BACKEND_URL="http://localhost:4000"
```

### OpenFace 설치 (선택적)
```bash
# Windows - OpenFace 2.0 설치
# tools/FeatureExtraction.exe 실행 가능 여부 확인

# Linux/Mac - OpenFace 빌드 필요
# 자세한 설치 방법은 OpenFace 공식 문서 참조
```

## 문제 해결

### 1. 서버 실행 오류
```bash
# 포트 충돌 해결
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# 다른 포트 사용
export PORT=5001
python main_server.py
```

### 2. 모듈 로드 실패
```bash
# 의존성 재설치
pip install -r requirements.txt --force-reinstall

# 가상환경 재생성
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. 백엔드 연동 오류
```bash
# 백엔드 서버 실행 확인
curl http://localhost:4000/api/test

# AI 서버 연결 확인
curl http://localhost:5000/ai/test

# 연동 테스트
python backend_integration_test.py
```

### 4. GPU 관련 오류
```bash
# CUDA 사용 가능 여부 확인
python -c "import torch; print(torch.cuda.is_available())"

# GPU 메모리 사용량 확인
nvidia-smi
```

## 성능 최적화

### 메모리 사용량 최적화
- Whisper: 작은 모델 사용 (`tiny`, `base`)
- 영상 처리: 해상도 제한 (720p 이하 권장)
- 배치 처리: 동시 요청 수 제한

### GPU 가속 사용
```python
# main_server.py에서 GPU 사용 확인
import torch
if torch.cuda.is_available():
    print(f"GPU 사용 가능: {torch.cuda.get_device_name()}")
```

## 개발 가이드

### 새로운 AI 모듈 추가
1. `interview_features/` 또는 `test_features/`에 모듈 생성
2. `main_server.py` 또는 `test_server.py`에 임포트 추가
3. API 엔드포인트 구현
4. 테스트 스크립트 업데이트

### 백엔드 연동 API 추가
1. AI 서버에 새 엔드포인트 구현
2. 백엔드 서비스에서 AI 서버 호출 코드 추가
3. `backend_integration_test.py`에 테스트 추가

## 지원 및 문의

문제 발생 시 확인 사항:
1. **서버 로그 확인**: 터미널 출력 메시지
2. **연결 테스트**: `curl http://localhost:5000/ai/test`
3. **통합 테스트**: `python backend_integration_test.py`
4. **시스템 요구사항**: Python 버전, 필수 패키지
5. **포트 충돌**: 5000번 포트 사용 여부
6. **백엔드 연결**: 4000번 포트 백엔드 서버 확인

---

## 빠른 체크리스트

### 처음 실행할 때
- [ ] Python 3.8+ 설치 확인
- [ ] 가상환경 생성 및 활성화
- [ ] `pip install -r requirements.txt` 실행
- [ ] FFmpeg 설치 (오디오/비디오 처리용)
- [ ] 서버 선택 (`main_server.py` vs `test_server.py`)
- [ ] 서버 실행 및 `http://localhost:5000/ai/test` 접속

### 백엔드 연동할 때
- [ ] 백엔드 서버(`localhost:4000`) 실행 확인
- [ ] AI 서버(`localhost:5000`) 실행 확인
- [ ] `python backend_integration_test.py` 실행
- [ ] 백엔드 서비스에서 AI 서버 호출 코드 주석 해제

### 개발/테스트할 때
- [ ] `test_server.py` 사용 (비용 절약)
- [ ] 로그 레벨을 DEBUG로 설정
- [ ] 포트 충돌 확인
- [ ] API 테스트 스크립트 활용

---

**VeriView AI Server v2.0**  
*완전한 AI 기능을 위한 Main Server와 효율적인 개발을 위한 Test Server*
