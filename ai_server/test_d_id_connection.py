#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 연결 테스트 스크립트
"""

import os
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 현재 디렉터리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# D-ID 모듈 임포트
try:
    from modules.d_id.client import DIDClient
    from modules.d_id.video_manager import DIDVideoManager
    from modules.d_id.tts_manager import TTSManager
    print("✅ D-ID 모듈 로드 성공")
except ImportError as e:
    print(f"❌ D-ID 모듈 로드 실패: {e}")
    sys.exit(1)

def test_d_id_integration():
    """D-ID 통합 테스트"""
    print("=" * 60)
    print("🧪 D-ID API 통합 테스트 시작")
    print("=" * 60)
    
    # 1. API 키 확인
    api_key = os.environ.get('D_ID_API_KEY')
    if not api_key or api_key == 'your_actual_d_id_api_key_here':
        print("❌ D_ID_API_KEY가 올바르게 설정되지 않음")
        return False
    
    print(f"✅ API 키 설정됨: {api_key[:20]}...")
    
    # 2. D-ID 클라이언트 초기화
    try:
        client = DIDClient(api_key=api_key)
        print("✅ D-ID 클라이언트 초기화 성공")
    except Exception as e:
        print(f"❌ D-ID 클라이언트 초기화 실패: {e}")
        return False
    
    # 3. API 연결 테스트
    print("🔄 API 연결 테스트 중...")
    try:
        connection_ok = client.test_connection()
        if connection_ok:
            print("✅ D-ID API 연결 성공")
        else:
            print("❌ D-ID API 연결 실패")
            return False
    except Exception as e:
        print(f"❌ API 연결 테스트 중 오류: {e}")
        return False
    
    # 4. TTS 관리자 테스트
    try:
        tts_manager = TTSManager()
        
        # 면접관 음성 테스트
        male_voice = tts_manager.get_voice_for_interviewer('male')
        female_voice = tts_manager.get_voice_for_interviewer('female')
        print(f"✅ TTS 설정 - 남성 면접관: {male_voice}")
        print(f"✅ TTS 설정 - 여성 면접관: {female_voice}")
        
        # 토론자 음성 테스트
        debater_male = tts_manager.get_voice_for_debater('male')
        debater_female = tts_manager.get_voice_for_debater('female')
        print(f"✅ TTS 설정 - 남성 토론자: {debater_male}")
        print(f"✅ TTS 설정 - 여성 토론자: {debater_female}")
        
    except Exception as e:
        print(f"❌ TTS 관리자 테스트 실패: {e}")
        return False
    
    # 5. 비디오 관리자 테스트
    try:
        video_manager = DIDVideoManager()
        storage_info = video_manager.get_storage_info()
        print(f"✅ 비디오 관리자 초기화 완료")
        print(f"   저장소 경로: {storage_info.get('base_dir', 'videos')}")
        print(f"   캐시된 파일: {storage_info.get('total_files', 0)}개")
        
    except Exception as e:
        print(f"❌ 비디오 관리자 테스트 실패: {e}")
        return False
    
    # 6. 스크립트 포맷팅 테스트
    try:
        test_question = "자기소개를 해주세요."
        formatted_script = tts_manager.format_script_for_interview(test_question)
        print(f"✅ 면접 스크립트 포맷팅: {formatted_script[:50]}...")
        
        test_debate = "AI 기술의 발전은 인류에게 도움이 됩니다."
        debate_script = tts_manager.format_script_for_debate(test_debate, 'opening')
        print(f"✅ 토론 스크립트 포맷팅: {debate_script[:50]}...")
        
    except Exception as e:
        print(f"❌ 스크립트 포맷팅 테스트 실패: {e}")
        return False
    
    print("=" * 60)
    print("🎉 D-ID API 통합 테스트 완료!")
    print("=" * 60)
    print()
    print("📋 다음 명령어로 서버를 실행하세요:")
    print("   python run.py test    # 테스트 모드")
    print("   python run.py main    # 메인 모드")
    print()
    print("🌐 서버 시작 후 테스트 엔드포인트:")
    print("   http://localhost:5000/ai/test")
    print()
    return True

if __name__ == "__main__":
    success = test_d_id_integration()
    if success:
        print("✅ 모든 테스트 통과 - D-ID 통합 완료!")
    else:
        print("❌ 일부 테스트 실패 - 설정을 확인하세요.")
        sys.exit(1)
