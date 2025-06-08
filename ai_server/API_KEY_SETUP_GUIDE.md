# 🔐 다양한 환경별 API 키 설정 가이드

## 🚀 지원되는 환경들

VeriView AIStudios는 다음 환경에서 자동으로 API 키를 검색합니다:

1. **런타임 설정** (최우선)
2. **환경 변수**
3. **AWS Secrets Manager**
4. **설정 파일**
5. **`.env` 파일**
6. **기본 설정**

---

## 🏠 1. 로컬 개발 환경

### 방법 1: `.env` 파일 사용 (권장)
```bash
# ai_server/.env
AISTUDIOS_API_KEY=sk-proj-your-actual-api-key-here

# 선택적 설정
AISTUDIOS_DEFAULT_AVATAR_ID=avatar_123
```

### 방법 2: 환경 변수 직접 설정
```bash
# Windows
set AISTUDIOS_API_KEY=sk-proj-your-actual-api-key-here

# PowerShell
$env:AISTUDIOS_API_KEY = "sk-proj-your-actual-api-key-here"

# Linux/Mac
export AISTUDIOS_API_KEY=sk-proj-your-actual-api-key-here
```

### 방법 3: 런타임 설정
```python
from modules.aistudios.client import AIStudiosClient

# API 키 없이 클라이언트 생성
client = AIStudiosClient()

# 런타임에서 API 키 설정
client.set_api_key("sk-proj-your-actual-api-key-here")
```

---

## ☁️ 2. AWS 환경

### AWS Secrets Manager 사용 (권장)
```bash
# AWS CLI로 시크릿 생성
aws secretsmanager create-secret \
  --name "veriview/aistudios" \
  --description "VeriView AIStudios API Keys" \
  --secret-string '{"AISTUDIOS_API_KEY":"sk-proj-your-actual-api-key-here"}'

# 또는 다른 시크릿 이름들 (자동 검색됨)
aws secretsmanager create-secret \
  --name "ai-server/api-keys" \
  --secret-string '{"aistudios_api_key":"sk-proj-your-actual-api-key-here"}'
```

### AWS EC2 환경 변수
```bash
# EC2 인스턴스에서
echo 'export AISTUDIOS_API_KEY=sk-proj-your-actual-api-key-here' >> ~/.bashrc
source ~/.bashrc
```

### AWS Lambda 환경 변수
```python
# serverless.yml 또는 CloudFormation
Environment:
  Variables:
    AISTUDIOS_API_KEY: sk-proj-your-actual-api-key-here
```

---

## 🐳 3. Docker 환경

### Dockerfile
```dockerfile
FROM python:3.11

# 환경 변수 설정 (빌드 시점 - 권장하지 않음)
# ENV AISTUDIOS_API_KEY=sk-proj-your-api-key

# 앱 복사
COPY . /app
WORKDIR /app

# 의존성 설치
RUN pip install -r requirements.txt

# 런타임 시점에 환경 변수로 전달받을 준비
CMD ["python", "run.py", "--mode", "main"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  veriview-ai:
    build: .
    ports:
      - "5000:5000"
    environment:
      - AISTUDIOS_API_KEY=${AISTUDIOS_API_KEY}
    # 또는 .env 파일 사용
    env_file:
      - .env
```

### Docker 실행
```bash
# 환경 변수로 전달
docker run -e AISTUDIOS_API_KEY=sk-proj-your-api-key veriview-ai

# .env 파일 사용
docker run --env-file .env veriview-ai
```

---

## 🔄 4. CI/CD 환경

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy VeriView AI
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to AWS
        env:
          AISTUDIOS_API_KEY: ${{ secrets.AISTUDIOS_API_KEY }}
        run: |
          # 배포 스크립트 실행
          ./deploy.sh
```

### GitLab CI
```yaml
# .gitlab-ci.yml
deploy:
  stage: deploy
  variables:
    AISTUDIOS_API_KEY: $AISTUDIOS_API_KEY
  script:
    - python run.py --mode main
```

### Jenkins
```groovy
pipeline {
    agent any
    environment {
        AISTUDIOS_API_KEY = credentials('aistudios-api-key')
    }
    stages {
        stage('Deploy') {
            steps {
                sh 'python run.py --mode main'
            }
        }
    }
}
```

---

## 🏢 5. 운영 환경

### 시스템 서비스 (systemd)
```ini
# /etc/systemd/system/veriview-ai.service
[Unit]
Description=VeriView AI Server
After=network.target

[Service]
Type=simple
User=veriview
WorkingDirectory=/opt/veriview-ai
Environment=AISTUDIOS_API_KEY=sk-proj-your-api-key
ExecStart=/usr/bin/python3 run.py --mode main
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx + uWSGI
```ini
# uwsgi.ini
[uwsgi]
module = main_server:app
master = true
processes = 5
socket = veriview-ai.sock
chmod-socket = 666
vacuum = true
die-on-term = true

# 환경 변수 설정
env = AISTUDIOS_API_KEY=sk-proj-your-api-key
```

---

## 📋 6. 설정 파일 사용

### config/api_keys.json
```json
{
  "api_keys": {
    "AISTUDIOS_API_KEY": "sk-proj-your-actual-api-key-here"
  },
  "aistudios": {
    "api_key": "sk-proj-your-actual-api-key-here",
    "default_avatar_id": "avatar_123"
  }
}
```

### config/production.json
```json
{
  "environment": "production",
  "AISTUDIOS_API_KEY": "sk-proj-your-actual-api-key-here",
  "logging": {
    "level": "INFO"
  }
}
```

---

## 🔍 7. 설정 확인 방법

### API 키 상태 확인
```python
from modules.aistudios.client import AIStudiosClient

client = AIStudiosClient()
status = client.get_api_key_status()
print(status)
```

### 웹 API로 확인
```bash
curl http://localhost:5000/ai/test
```

---

## ⚡ 8. 우선순위 시스템

API 키는 다음 순서로 검색됩니다:

1. **런타임 설정** (`client.set_api_key()`)
2. **환경 변수** (`AISTUDIOS_API_KEY`, `VERIVIEW_AISTUDIOS_API_KEY`)
3. **AWS Secrets Manager** (`veriview/aistudios`, `ai-server/api-keys`)
4. **설정 파일** (`config/api_keys.json`, `config/production.json`)
5. **`.env` 파일** (`.env`, `.env.local`, `.env.production`)
6. **기본 설정** (개발용만)

---

## 🔒 보안 모범 사례

### ✅ 권장사항
- **운영환경**: AWS Secrets Manager 사용
- **개발환경**: `.env` 파일 사용 (`.gitignore`에 포함)
- **CI/CD**: 플랫폼별 시크릿 관리 시스템 사용
- **Docker**: 환경 변수나 시크릿 볼륨 사용

### ❌ 하지 말 것
- 코드에 API 키 하드코딩
- API 키를 Git에 커밋
- 로그에 API 키 출력
- 공개 저장소에 설정 파일 업로드

---

## 🚀 빠른 시작

### 로컬 개발
```bash
# 1. API 키 설정
echo "AISTUDIOS_API_KEY=sk-proj-your-api-key" > .env

# 2. 서버 시작
python run.py --mode test
```

### AWS 배포
```bash
# 1. Secrets Manager에 키 저장
aws secretsmanager create-secret \
  --name "veriview/aistudios" \
  --secret-string '{"AISTUDIOS_API_KEY":"sk-proj-your-api-key"}'

# 2. EC2에서 서버 시작
python run.py --mode main
```

### Docker 실행
```bash
# 1. 환경 변수 파일 생성
echo "AISTUDIOS_API_KEY=sk-proj-your-api-key" > .env

# 2. Docker 실행
docker-compose up
```
