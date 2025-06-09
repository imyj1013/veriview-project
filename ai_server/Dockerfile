FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 필요한 디렉토리 생성
RUN mkdir -p aistudios_cache videos logs

# 환경 변수 설정 (기본값)
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# 비특권 사용자 생성
RUN useradd -m -u 1000 veriview && \
    chown -R veriview:veriview /app
USER veriview

# 포트 노출
EXPOSE 5000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 기본 실행 명령
CMD ["python", "run.py", "--mode", "main"]
