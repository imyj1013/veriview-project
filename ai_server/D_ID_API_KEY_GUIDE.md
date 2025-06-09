# D-ID API 키 설정 가이드

## 문제 상황
현재 API 키로 401 Unauthorized 에러가 발생하고 있습니다.

## D-ID API 키 올바르게 가져오기

### 1. D-ID Studio 접속
1. https://studio.d-id.com 에 로그인
2. 우측 상단의 프로필 아이콘 클릭
3. "API Keys" 메뉴 선택

### 2. 새 API 키 생성
1. "Create New API Key" 버튼 클릭
2. API 키 이름 입력 (예: "VeriView Project")
3. "Create" 클릭

### 3. API 키 복사
1. 생성된 API 키가 화면에 표시됨
2. **전체 키를 복사** (매우 긴 문자열)
3. D-ID API 키는 일반적으로 100자 이상의 긴 문자열입니다

### 4. .env 파일 업데이트
```bash
# 올바른 형식 (따옴표 없음)
D_ID_API_KEY=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkQ4aFNhR1hndDhBN1ZCQnRheVo2dCJ9...

# 잘못된 형식
D_ID_API_KEY="키값"  # 따옴표 사용 X
D_ID_API_KEY='키값'  # 따옴표 사용 X
```

## 일반적인 D-ID API 키 형식

D-ID API 키는 다음 중 하나의 형식입니다:

1. **JWT 토큰** (가장 일반적)
   - 매우 긴 문자열 (200-500자)
   - 점(.)으로 구분된 3부분
   - 예: `eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

2. **UUID 형식**
   - `did_` 접두사 + UUID
   - 예: `did_a1b2c3d4-e5f6-7890-abcd-ef1234567890`

## 테스트 방법

```bash
# 1. Bearer 토큰 테스트
python test_d_id_bearer.py

# 2. 모든 인증 방식 테스트
python test_d_id_all_auth.py
```

## 주의사항

- Trial Plan은 제한된 크레딧을 제공합니다 (12 크레딧)
- API 키는 한 번만 표시되므로 안전하게 보관하세요
- 키가 노출되면 즉시 재생성하세요

## 대안: 샘플 비디오 사용

API 키 문제가 지속되면 임시로 샘플 비디오만 사용하도록 설정:

```bash
# .env 파일에서
PREFERRED_AVATAR_SERVICE=SAMPLE
```
