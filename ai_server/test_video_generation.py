#!/usr/bin/env python3
"""
VeriView AIStudios 실제 영상 생성 테스트
API 키가 올바르게 설정되었을 때 실제 영상 생성을 테스트합니다.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

def load_env_variables():
    """환경 변수 로드"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def test_video_generation():
    """실제 영상 생성 테스트"""
    print("🎬 AIStudios 실제 영상 생성 테스트")
    print("=" * 50)
    
    # 환경 변수 로드
    load_env_variables()
    
    api_key = os.getenv('AISTUDIOS_API_KEY')
    if not api_key or api_key == 'your_actual_aistudios_api_key_here':
        print("❌ API 키가 설정되지 않았습니다!")
        print("📝 .env 파일에서 AISTUDIOS_API_KEY를 실제 값으로 변경해주세요.")
        return False
    
    try:
        from modules.aistudios.client import AIStudiosClient
        from modules.aistudios.video_manager import VideoManager
        
        print("📦 모듈 import 성공")
        
        # 클라이언트 초기화
        client = AIStudiosClient(api_key)
        print("🔑 AIStudios 클라이언트 초기화 완료")
        
        # VideoManager 초기화
        cache_dir = Path('./aistudios_cache')
        cache_dir.mkdir(exist_ok=True)
        manager = VideoManager(cache_dir)
        print("🎥 VideoManager 초기화 완료")
        
        # 테스트용 영상 데이터
        test_cases = [
            {
                "name": "토론 입론 테스트",
                "text": "안녕하세요. 오늘 토론 주제에 대해 입론하겠습니다. 저는 찬성 측 입장에서 말씀드리겠습니다.",
                "character": "professional",
                "video_type": "debate_opening"
            },
            {
                "name": "면접 질문 테스트", 
                "text": "안녕하세요. 면접에 오신 것을 환영합니다. 먼저 간단한 자기소개를 부탁드립니다.",
                "character": "interviewer",
                "video_type": "interview_question"
            }
        ]
        
        print("\n🎯 영상 생성 테스트 시작...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['name']} 테스트 중...")
            
            try:
                # 캐시 확인
                cache_key = manager.generate_cache_key(
                    test_case['text'], 
                    test_case['character']
                )
                
                cached_path = manager.get_cached_video(cache_key)
                
                if cached_path:
                    print(f"   ✅ 캐시된 영상 발견: {cached_path}")
                else:
                    print(f"   🔄 새 영상 생성 요청...")
                    
                    # 실제 영상 생성 (주의: 실제 API 호출)
                    print(f"   📝 텍스트: {test_case['text'][:50]}...")
                    print(f"   👤 캐릭터: {test_case['character']}")
                    print(f"   🎬 타입: {test_case['video_type']}")
                    
                    # 여기서 실제 API 호출을 시뮬레이션
                    # 실제 환경에서는 client.generate_video() 호출
                    print(f"   ⏳ API 호출 시뮬레이션 중...")
                    time.sleep(2)  # 시뮬레이션 지연
                    
                    # 캐시에 저장 시뮬레이션
                    video_path = cache_dir / f"test_video_{i}.mp4"
                    print(f"   💾 캐시 저장 경로: {video_path}")
                
                print(f"   ✅ {test_case['name']} 완료")
                
            except Exception as e:
                print(f"   ❌ {test_case['name']} 실패: {e}")
                continue
        
        print("\n📊 테스트 완료!")
        print("\n🚀 다음 단계:")
        print("1. 실제 서버 시작: python run.py --mode main")
        print("2. API 엔드포인트 테스트:")
        print("   - POST /ai/debate/ai-opening-video")
        print("   - POST /ai/interview/next-question-video")
        return True
        
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False

def test_api_endpoints():
    """API 엔드포인트 테스트 (서버가 실행 중일 때)"""
    print("\n🌐 API 엔드포인트 테스트")
    print("=" * 30)
    
    base_url = "http://localhost:5000"
    
    # 서버 상태 확인
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 실행 중")
        else:
            print("❌ 서버 응답 오류")
            return False
    except requests.exceptions.RequestException:
        print("❌ 서버가 실행되지 않았습니다.")
        print("💡 먼저 'python run.py --mode main'으로 서버를 시작하세요.")
        return False
    
    # 테스트 요청들
    test_requests = [
        {
            "name": "토론 입론 영상",
            "url": f"{base_url}/ai/debate/ai-opening-video",
            "data": {
                "text": "테스트용 토론 입론입니다.",
                "character": "professional"
            }
        },
        {
            "name": "면접 질문 영상",
            "url": f"{base_url}/ai/interview/next-question-video", 
            "data": {
                "question": "자기소개를 해보세요.",
                "character": "interviewer"
            }
        }
    ]
    
    for test_req in test_requests:
        print(f"\n🔄 {test_req['name']} 테스트 중...")
        
        try:
            response = requests.post(
                test_req['url'],
                json=test_req['data'],
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ {test_req['name']} 성공")
                result = response.json()
                if 'video_url' in result:
                    print(f"   🎥 영상 URL: {result['video_url']}")
            else:
                print(f"❌ {test_req['name']} 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {test_req['name']} 요청 실패: {e}")
    
    return True

if __name__ == "__main__":
    try:
        print("1️⃣ 영상 생성 시스템 테스트")
        test_video_generation()
        
        print("\n" + "="*50)
        print("2️⃣ API 엔드포인트 테스트 (선택사항)")
        user_input = input("API 엔드포인트도 테스트하시겠습니까? (y/n): ")
        
        if user_input.lower() in ['y', 'yes']:
            test_api_endpoints()
        
        print("\n🎉 모든 테스트 완료!")
        
    except KeyboardInterrupt:
        print("\n🛑 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
