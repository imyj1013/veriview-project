#!/usr/bin/env python3
"""
API 키 설정 테스트 및 진단 스크립트
다양한 환경에서 API 키가 올바르게 설정되었는지 확인합니다.
"""

import os
import sys
import json
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

def test_api_key_sources():
    """모든 API 키 소스를 테스트합니다."""
    print("🔍 VeriView AIStudios API 키 설정 진단")
    print("=" * 50)
    
    try:
        from modules.aistudios.api_key_manager import api_key_manager
        from modules.aistudios.client import AIStudiosClient
        
        print("✅ 모듈 import 성공")
        
        # 1. 모든 소스 상태 확인
        print("\n📋 API 키 소스별 상태:")
        status = api_key_manager.get_all_sources_status()
        
        sources_found = []
        for source, info in status.items():
            available = "✅" if info.get('available') else "❌"
            print(f"  {available} {source.replace('_', ' ').title()}")
            
            if info.get('available'):
                sources_found.append(source)
                if info.get('key_preview'):
                    print(f"     키 미리보기: {info['key_preview']}")
            elif info.get('error'):
                print(f"     오류: {info['error']}")
        
        # 2. 최종 API 키 확인
        print(f"\n🔑 최종 로드된 API 키:")
        api_key = api_key_manager.get_aistudios_api_key()
        
        if api_key:
            print(f"  ✅ 성공: {api_key[:10]}***")
            print(f"  📍 로드 소스: {sources_found[0] if sources_found else '알 수 없음'}")
        else:
            print("  ❌ API 키를 찾을 수 없습니다.")
        
        # 3. AIStudios 클라이언트 테스트
        print(f"\n🤖 AIStudios 클라이언트 테스트:")
        try:
            client = AIStudiosClient()
            if client.test_connection():
                print("  ✅ 클라이언트 초기화 성공")
                
                # API 키 상태 확인
                client_status = client.get_api_key_status()
                print(f"  📊 클라이언트 상태: {json.dumps(client_status, indent=2, ensure_ascii=False)}")
            else:
                print("  ❌ 클라이언트 연결 테스트 실패")
        except Exception as e:
            print(f"  ❌ 클라이언트 오류: {e}")
        
        # 4. 설정 권장사항
        print(f"\n💡 권장사항:")
        if not api_key:
            print("  🔑 API 키를 설정해주세요:")
            print("     1. .env 파일: AISTUDIOS_API_KEY=your_api_key")
            print("     2. 환경 변수: set AISTUDIOS_API_KEY=your_api_key")
            print("     3. AWS Secrets Manager (운영환경)")
            print("     4. 런타임 설정: client.set_api_key('your_api_key')")
        else:
            print("  ✅ API 키가 올바르게 설정되었습니다.")
            print("  🚀 이제 서버를 시작할 수 있습니다:")
            print("     python run.py --mode test")
        
        # 5. 환경별 설정 가이드
        print(f"\n📚 환경별 설정 가이드:")
        print("  📁 로컬 개발: .env 파일 사용")
        print("  ☁️  AWS 운영: scripts/aws/setup_secrets.bat 실행")
        print("  🐳 Docker: docker-compose.yml 환경 변수 설정")
        print("  🔄 CI/CD: 플랫폼별 시크릿 관리 시스템 사용")
        
        return bool(api_key)
        
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        print("📝 modules/aistudios/ 디렉토리가 존재하는지 확인하세요.")
        return False
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False

def check_environment_files():
    """환경 설정 파일들을 확인합니다."""
    print(f"\n📂 환경 설정 파일 확인:")
    
    files_to_check = [
        ('.env', '로컬 환경 설정'),
        ('config/production.json', '운영 환경 설정'),
        ('config/development.json', '개발 환경 설정'),
        ('config/aws.json', 'AWS 환경 설정'),
        ('docker-compose.yml', 'Docker 설정')
    ]
    
    for file_path, description in files_to_check:
        if Path(file_path).exists():
            print(f"  ✅ {description}: {file_path}")
        else:
            print(f"  ❌ {description}: {file_path} (없음)")

def provide_quick_setup():
    """빠른 설정 옵션을 제공합니다."""
    print(f"\n⚡ 빠른 설정:")
    print("  1. start_env_server.bat - 환경별 서버 시작")
    print("  2. scripts/aws/setup_secrets.bat - AWS 설정")
    print("  3. 직접 설정:")
    
    api_key = input("     AIStudios API 키를 입력하세요 (Enter로 건너뛰기): ").strip()
    
    if api_key:
        # .env 파일에 저장
        env_content = f"AISTUDIOS_API_KEY={api_key}\nENVIRONMENT=development\nDEBUG=True\n"
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("  ✅ .env 파일에 API 키가 저장되었습니다.")
        print("  🚀 이제 'python run.py --mode test'로 서버를 시작하세요.")
        
        return True
    
    return False

if __name__ == "__main__":
    try:
        # API 키 소스 테스트
        success = test_api_key_sources()
        
        # 환경 파일 확인
        check_environment_files()
        
        # 빠른 설정 제공
        if not success:
            provide_quick_setup()
        
        print(f"\n🏁 진단 완료")
        
        if success:
            print("✅ 모든 설정이 올바릅니다. 서버를 시작할 준비가 되었습니다!")
            exit(0)
        else:
            print("⚠️  일부 설정이 필요합니다. 위의 권장사항을 따라 설정해주세요.")
            exit(1)
            
    except KeyboardInterrupt:
        print(f"\n🛑 진단이 중단되었습니다.")
        exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
        exit(1)
