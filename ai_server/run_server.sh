#!/bin/bash
# AI Server 실행 스크립트 (Linux/Mac)

echo "AI Server 시작 준비 중..."

# 환경 변수 설정 (필요시)
# export OPENFACE_PATH="/usr/local/bin/FeatureExtraction"
# export OPENFACE_OUTPUT_DIR="/tmp/openface_output"

# Python 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
fi

# 의존성 확인
echo "의존성 확인 중..."
pip install -r requirements.txt --quiet

# 서버 시작
echo "AI Server 시작..."
python server_runner.py
