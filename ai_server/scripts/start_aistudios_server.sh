#!/bin/bash

echo "========================================"
echo "VeriView AIStudios 통합 서버 시작"
echo "========================================"
echo

# 환경 변수 체크
if [ -z "$AISTUDIOS_API_KEY" ]; then
    echo "⚠️  경고: AISTUDIOS_API_KEY 환경 변수가 설정되지 않았습니다."
    echo
    echo "API 키를 설정하세요:"
    echo "export AISTUDIOS_API_KEY=your_actual_api_key_here"
    echo
    read -p "API 키를 입력하세요 (또는 Enter를 눌러 건너뛰기): " api_key
    if [ ! -z "$api_key" ]; then
        export AISTUDIOS_API_KEY=$api_key
        echo "✅ API 키가 설정되었습니다."
    fi
    echo
fi

# Python 가상환경 활성화 (있는 경우)
if [ -f "venv/bin/activate" ]; then
    echo "🔄 Python 가상환경 활성화 중..."
    source venv/bin/activate
fi

# AIStudios 통합 확인
echo "🔍 AIStudios 모듈 확인 중..."
python3 -c "from modules.aistudios.client import AIStudiosClient; print('✅ AIStudios 모듈 정상')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ AIStudios 모듈을 찾을 수 없습니다."
    echo "   modules/aistudios/ 디렉토리가 있는지 확인해주세요."
    exit 1
fi

# 디렉토리 생성
echo "📁 필요한 디렉토리 생성 중..."
mkdir -p aistudios_cache
mkdir -p videos/{interview,opening,rebuttal,counter_rebuttal,closing}

# 권한 설정
chmod 755 aistudios_cache
chmod 755 videos
chmod 755 videos/*

# 서버 시작
echo
echo "🚀 서버 시작 중..."
echo "📍 주소: http://localhost:5000"
echo "🔍 테스트: http://localhost:5000/ai/test"
echo
echo "중단하려면 Ctrl+C를 누르세요."
echo "========================================"

python3 main_server.py
