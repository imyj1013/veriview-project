#!/bin/bash

echo ""
echo "=== VeriView AI 서버 테스트 모드 실행 ==="
echo ""

# Python 실행 파일 확인
if ! command -v python3 &> /dev/null; then
    echo "오류: Python3가 설치되어 있지 않습니다."
    echo "Python3를 설치해주세요."
    exit 1
fi

# 가상환경 활성화 (있는 경우)
if [ -f "venv/bin/activate" ]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    echo "가상환경 활성화 중..."
    source .venv/bin/activate
fi

# 테스트 모드로 서버 실행
echo "테스트 모드로 서버를 시작합니다..."
echo "(D-ID API 대신 샘플 비디오 사용)"
echo ""
python3 run.py --mode test
