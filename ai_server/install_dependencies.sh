#!/bin/bash
# AI 서버 의존성 설치 스크립트

echo "========================================="
echo "AI 서버 의존성 패키지 설치 시작"
echo "========================================="

# pip 업그레이드
echo "1. pip 업그레이드..."
python -m pip install --upgrade pip

# requirements.txt 기반 설치
echo "2. requirements.txt 기반 패키지 설치..."
pip install -r requirements.txt

# TTS 모델 캐시 미리 다운로드 (선택사항)
echo "3. TTS 기본 모델 사전 다운로드..."
python -c "
try:
    from TTS.api import TTS
    print('TTS 패키지 설치 확인 완료')
    
    # 기본 모델들 미리 로드 (첫 실행 시 자동 다운로드됨)
    print('기본 TTS 모델 초기화 중...')
    tts = TTS()
    print('✓ 기본 TTS 모델 로드 완료')
    
    # 영어 모델 로드
    try:
        tts_en = TTS('tts_models/en/ljspeech/tacotron2-DDC')
        print('✓ 영어 TTS 모델 로드 완료')
    except:
        print('⚠ 영어 TTS 모델 로드 실패 (선택사항)')
        
except Exception as e:
    print(f'TTS 설치 확인 실패: {e}')
    print('수동으로 다음 명령어를 실행해보세요:')
    print('pip install TTS --upgrade')
"

echo "========================================="
echo "설치 완료!"
echo "========================================="
echo ""
echo "다음 단계:"
echo "1. TTS 테스트: python test_tts.py"
echo "2. 서버 실행: python server_runner.py"
echo ""
