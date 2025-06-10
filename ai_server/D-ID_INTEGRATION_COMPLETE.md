# VeriView AI 서버 D-ID API 통합 완료 가이드

## 통합 완료 상태

VeriView AI 면접 플랫폼에 D-ID API가 성공적으로 통합되었습니다!

### 완료된 작업들

1. **D-ID API 키 설정 완료**: `.env` 파일에 실제 API 키 적용
2. **기존 실행 방식 유지**: `python run.py main/test` 명령어 그대로 사용
3. **실사 아바타 영상 생성**: D-ID를 통한 고품질 AI 아바타
4. **한국어 TTS 최적화**: Microsoft Azure 한국어 음성 사용
5. **폴백 시스템 구축**: D-ID 실패시 AIStudios 자동 전환
6. **기존 API 호환성**: Backend 수정 없이 기존 엔드포인트 사용 가능

---

## 실행 방법

### 1. 서버 시작

```bash
# 테스트 모드로 실행 (권장)
python run.py test

# 또는 메인 모드로 실행
python run.py main
```

### 2. 서버 시작 후 확인 사항

서버 시작시 다음과 같은 메시지가 표시되어야 합니다:

```
VeriView AI 서버 시작 (모드: TEST, D-ID API 통합)
================================================================================
서버 주소: http://localhost:5000
테스트 엔드포인트: http://localhost:5000/ai/test

D-ID (우선 사용) 상태:
  - 모듈 상태: D-ID 모듈 로드 성공
  - API 키: D-ID API 키 설정됨
  - API 연결: D-ID API 연결 성공

영상 생성 기능:
  - 주요 서비스: D-ID API (실사 아바타)
  - 한국어 TTS: Microsoft Azure 음성
  - 캐싱 시스템: 활성화
```

---

## 테스트 방법

### 1. 기본 연결 테스트

```bash
# 터미널에서 실행
python test_d_id_connection.py
```

또는 브라우저에서:
```
http://localhost:5000/ai/test
```

### 2. Backend 통합 테스트

```bash
# 서버를 먼저 실행한 후
python test_backend_integration.py
```

### 3. 주요 엔드포인트 테스트

#### 채용 공고 추천
```bash
curl -X POST http://localhost:5000/ai/recruitment/posting \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "category": "ICT",
    "workexperience": "1-3년",
    "tech_stack": "Java, Spring, React"
  }'
```

#### AI 면접관 영상 생성 (D-ID)
```bash
curl -X POST http://localhost:5000/ai/interview/ai-video \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "자기소개를 해주세요.",
    "interviewer_gender": "male"
  }' \
  --output interview_video.mp4
```

#### AI 토론 영상 생성 (D-ID)
```bash
curl -X POST http://localhost:5000/ai/debate/ai-opening-video \
  -H "Content-Type: application/json" \
  -d '{
    "ai_opening_text": "AI 기술은 인류 발전에 필수적입니다.",
    "debater_gender": "female"
  }' \
  --output debate_video.mp4
```

---

## 주요 기능

### 1. D-ID 실사 아바타 영상

- **면접관 영상**: 실사 느낌의 면접관이 질문을 진행
- **토론자 영상**: 자연스러운 토론 참여자 아바타
- **한국어 TTS**: 자연스러운 한국어 음성 합성
- **성별 선택**: 남성/여성 아바타 선택 가능

### 2. 캐싱 시스템

- **자동 캐싱**: 동일한 질문은 캐시된 영상 사용
- **7일 만료**: 캐시 파일 자동 만료 및 정리
- **용량 최적화**: 중복 생성 방지로 저장공간 절약

### 3. 폴백 시스템

1. **1순위**: D-ID API (실사 아바타)
2. **2순위**: AIStudios API (폴백)
3. **3순위**: 샘플 영상 (최종 폴백)

---

## 🔧 Backend 연동

### 기존 엔드포인트 그대로 사용 가능

Backend에서는 기존 API 호출 방식을 그대로 사용하면 됩니다:

```java
// 예시: Spring Boot에서 AI 면접관 영상 요청
RestTemplate restTemplate = new RestTemplate();
String aiServerUrl = "http://localhost:5000/ai/interview/ai-video";

Map<String, Object> request = new HashMap<>();
request.put("question_text", "자기소개를 해주세요.");
request.put("interviewer_gender", "male");

ResponseEntity<byte[]> response = restTemplate.postForEntity(
    aiServerUrl, 
    request, 
    byte[].class
);

// 응답은 MP4 비디오 파일
byte[] videoData = response.getBody();
```

### 새로운 D-ID 전용 엔드포인트

- **AI 면접관 영상**: `POST /ai/interview/ai-video`
- **AI 토론 입론**: `POST /ai/debate/ai-opening-video`
- **AI 토론 반론**: `POST /ai/debate/ai-rebuttal-video`
- **AI 토론 재반론**: `POST /ai/debate/ai-counter-rebuttal-video`
- **AI 토론 최종변론**: `POST /ai/debate/ai-closing-video`

---

## 🎬 영상 생성 예시

### 면접 시나리오

1. **기술 질문**: "Java와 Python의 차이점을 설명해주세요."
2. **인성 질문**: "팀워크에서 중요한 요소는 무엇인가요?"
3. **경험 질문**: "가장 도전적이었던 프로젝트는 무엇인가요?"

### 토론 시나리오

1. **입론**: "AI 기술 발전은 인류에게 도움이 됩니다."
2. **반론**: "AI 기술의 부작용을 고려해야 합니다."
3. **재반론**: "적절한 규제로 부작용을 최소화할 수 있습니다."
4. **최종변론**: "결론적으로 AI 기술 발전이 필요합니다."

---

## 🔍 모니터링 및 디버깅

### 로그 파일

- **서버 로그**: `ai_server.log`
- **D-ID 요청/응답**: 콘솔 출력으로 확인
- **캐시 상태**: 비디오 관리자에서 조회

### 상태 확인

```bash
# 서버 상태 확인
curl http://localhost:5000/ai/test

# 저장소 정보 확인 (Python 코드에서)
from modules.d_id.video_manager import VideoManager
vm = VideoManager()
print(vm.get_storage_info())
```

### 문제 해결

1. **D-ID API 연결 실패**:
   - API 키 확인: `.env` 파일의 `D_ID_API_KEY`
   - 네트워크 연결 확인
   - D-ID 서비스 상태 확인

2. **영상 생성 시간 초과**:
   - D-ID 서버 응답 지연 (정상적인 현상)
   - 타임아웃 설정 늘리기 (300초 기본값)

3. **캐시 문제**:
   - `videos/` 디렉토리 권한 확인
   - 디스크 용량 확인
   - 캐시 정리: `cleanup_old_videos()` 실행

---

## 📊 성능 최적화

### 캐싱 활용

- 동일 질문 재사용시 즉시 응답
- 캐시 적중률 95% 이상 목표
- 저장공간 효율적 사용

### 비동기 처리

- D-ID API 호출 비동기 처리
- 다중 영상 생성 대기열 관리
- 타임아웃 및 재시도 로직

### 자원 관리

- 임시 파일 자동 정리
- 메모리 사용량 최적화
- 디스크 공간 모니터링

---

### 다음 단계

1. **서버 실행**: `python run.py test`
2. **테스트 실행**: `python test_backend_integration.py`
3. **Backend 연동**: 기존 API 호출 방식 그대로 사용
4. **운영 배포**: 필요시 환경 설정 조정

### 지원되는 기능

- 실사 AI 아바타 (D-ID)
- 한국어 TTS 최적화
- 자동 폴백 시스템
- 영상 캐싱 및 관리
- 기존 API 호환성
- 면접/토론 시나리오 지원

모든 설정이 완료
