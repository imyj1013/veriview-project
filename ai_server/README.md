# VeriView AI 서버 실행 방법

## 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

### 1. 테스트 모드 (권장)
D-ID API 없이 샘플 비디오로 테스트할 수 있습니다.

**Windows:**
```bash
run_test.bat
```

**Linux/Mac:**
```bash
chmod +x run_test.sh
./run_test.sh
```

**Python 직접 실행:**
```bash
python run.py --mode test
```

### 2. 프로덕션 모드
실제 D-ID API를 사용합니다. (API 키 필요)

```bash
python run.py
```

### 3. 디버그 모드
상세 로깅을 활성화합니다.

```bash
python run.py --mode debug
```

### 4. 포트 변경
기본 포트(5000) 대신 다른 포트 사용:

```bash
python run.py --port 5001
```

## 환경 변수 설정

`.env` 파일에서 다음 변수들을 설정할 수 있습니다:

- `D_ID_API_KEY`: D-ID API 키
- `PREFERRED_AVATAR_SERVICE`: 사용할 서비스 (D_ID, AISTUDIOS, SAMPLE)
- `USE_FALLBACK_SERVICE`: 폴백 서비스 사용 여부 (True/False)

## 테스트

서버가 실행되면 브라우저에서 다음 URL로 접속하여 테스트:

```
http://localhost:5000/ai/test
```
