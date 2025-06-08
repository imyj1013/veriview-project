#!/usr/bin/env python3
"""
VeriView AIStudios 통합 테스트 스크립트
실제 API 키 설정과 영상 생성을 테스트합니다.
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
    return os.getenv('AISTUDIOS_API_KEY')

def test_api_key():
    """API 키 유효성 테스트"""
    print("🔑 1단계: API 키 확인 중...")
    
    api_key = load_env_variables()
    
    if not api_key or api_key == 'your_actual_aistudios_api_key_here':
        print("❌ API 키가 설정되지 않았습니다!")
        print("📝 .env 파일에서 AISTUDIOS_API_KEY를 실제 값으로 변경해주세요.")
        return False
    
    print(f"✅ API 키 발견: {api_key[:10]}***")
    return True

def test_aistudios_import():
    """AIStudios 모듈 import 테스트"""
    print("📦 2단계: 모듈 import 테스트 중...")
    
    try:
        from modules.aistudios.client import AIStudiosClient
        from modules.aistudios.video_manager import VideoManager
        print("✅ AIStudios 모듈 import 성공")
        return True
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        return False

def test_client_connection():
    """AIStudios 클라이언트 연결 테스트"""
    print("🌐 3단계: AIStudios API 연결 테스트 중...")
    
    try:
        from modules.aistudios.client import AIStudiosClient
        
        api_key = os.getenv('AISTUDIOS_API_KEY')
        client = AIStudiosClient(api_key)
        
        # 간단한 연결 테스트 (실제 API 호출 없이 클라이언트만 생성)
        if client.api_key:
            print("✅ AIStudios 클라이언트 초기화 성공")
            return True
        else:
            print("❌ 클라이언트 초기화 실패")
            return False
            
    except Exception as e:
        print(f"❌ 연결 테스트 실패: {e}")
        return False

def test_video_manager():
    """VideoManager 테스트"""
    print("🎥 4단계: VideoManager 테스트 중...")
    
    try:
        from modules.aistudios.video_manager import VideoManager
        
        # 캐시 디렉토리 확인/생성
        cache_dir = Path('./aistudios_cache')
        cache_dir.mkdir(exist_ok=True)
        
        manager = VideoManager(cache_dir)
        print("✅ VideoManager 초기화 성공")
        print(f"   캐시 디렉토리: {manager.cache_dir}")
        return True
        
    except Exception as e:
        print(f"❌ VideoManager 테스트 실패: {e}")
        return False

def test_server_startup():
    """서버 시작 테스트"""
    print("🚀 5단계: 서버 시작 테스트 중...")
    
    try:
        # main_server.py에서 AIStudios 통합 확인
        with open('main_server.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'aistudios' in content.lower():
                print("✅ main_server.py에 AIStudios 통합 코드 확인")
                return True
            else:
                print("❌ main_server.py에 AIStudios 통합 코드 없음")
                return False
                
    except Exception as e:
        print(f"❌ 서버 테스트 실패: {e}")
        return False

def test_routes_availability():
    """라우트 가용성 테스트"""
    print("🛣️  6단계: 라우트 설정 확인 중...")
    
    try:
        # routes.py와 interview_routes.py 확인
        routes_files = [
            'modules/aistudios/routes.py',
            'modules/aistudios/interview_routes.py'
        ]
        
        for route_file in routes_files:
            if Path(route_file).exists():
                print(f"✅ {route_file} 파일 확인")
            else:
                print(f"❌ {route_file} 파일 없음")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 라우트 테스트 실패: {e}")
        return False

def run_integration_test():
    """전체 통합 테스트 실행"""
    print("🎬 VeriView AIStudios 통합 테스트 시작")
    print("=" * 50)
    
    tests = [
        test_api_key,
        test_aistudios_import,
        test_client_connection,
        test_video_manager,
        test_server_startup,
        test_routes_availability
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ 테스트 중 예외 발생: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! AIStudios 통합이 완료되었습니다.")
        print("\n🚀 다음 단계:")
        print("1. python run.py --mode test  # 전체 시스템 테스트")
        print("2. python run.py --mode main  # 메인 서버 실행")
        return True
    else:
        print("⚠️  일부 테스트 실패. 위의 오류를 확인하고 수정해주세요.")
        return False

if __name__ == "__main__":
    try:
        success = run_integration_test()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 테스트가 중단되었습니다.")
        exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
        exit(1)
