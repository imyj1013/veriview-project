#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 실행 파일 (D-ID API 통합)
사용법: python run.py [--mode test|main] [--d-id] [--aistudios]
"""
import sys
import os
import argparse
import time

# 현재 디렉터리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'src'))

def check_d_id_availability():
    """D-ID 모듈 사용 가능 여부 확인"""
    try:
        from modules.d_id.client import DIDClient
        from modules.d_id.video_manager import DIDVideoManager
        from modules.d_id.tts_manager import TTSManager
        return True, "D-ID 모듈 로드 성공"
    except ImportError as e:
        return False, f"D-ID 모듈 로드 실패: {str(e)}"

def check_aistudios_availability():
    """AIStudios 모듈 사용 가능 여부 확인 (폴백용)"""
    try:
        from modules.aistudios.client import AIStudiosClient
        from modules.aistudios.video_manager import VideoManager
        return True, "AIStudios 모듈 로드 성공 (폴백용)"
    except ImportError as e:
        return False, f"AIStudios 모듈 로드 실패: {str(e)}"

def check_d_id_api_key():
    """D-ID API 키 설정 확인"""
    api_key = os.environ.get('D_ID_API_KEY')
    if not api_key:
        return False, "D_ID_API_KEY 환경 변수 미설정"
    elif api_key in ['your_api_key', 'YOUR_API_KEY', 'your_actual_d_id_api_key_here']:
        return False, "기본값 사용 중 (실제 D-ID API 키 필요)"
    else:
        return True, "D-ID API 키 설정됨"

def check_aistudios_api_key():
    """AIStudios API 키 설정 확인 (폴백용)"""
    api_key = os.environ.get('AISTUDIOS_API_KEY')
    if not api_key:
        return False, "AISTUDIOS_API_KEY 환경 변수 미설정"
    elif api_key in ['your_api_key', 'YOUR_API_KEY', 'your_actual_aistudios_api_key_here']:
        return False, "기본값 사용 중 (실제 AIStudios API 키 필요)"
    else:
        return True, "AIStudios API 키 설정됨 (폴백용)"

def test_d_id_connection():
    """D-ID API 연결 테스트"""
    try:
        from modules.d_id.client import DIDClient
        api_key = os.environ.get('D_ID_API_KEY')
        
        if not api_key or api_key == 'your_actual_d_id_api_key_here':
            return False, "API 키 미설정"
        
        client = DIDClient(api_key=api_key)
        if client.test_connection():
            return True, "D-ID API 연결 성공"
        else:
            return False, "D-ID API 연결 실패"
    except Exception as e:
        return False, f"연결 테스트 실패: {str(e)}"

def setup_directories():
    """필요한 디렉토리 생성"""
    directories = [
        'videos',
        'videos/cache',  # D-ID 캐시용
        'videos/interviews',  # 면접 영상
        'videos/debates',  # 토론 영상
        'aistudios_cache',  # AIStudios 캐시 (폴백용)
        'temp'  # 임시 파일
    ]
    
    created_dirs = []
    for dir_path in directories:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                created_dirs.append(dir_path)
            except Exception as e:
                print(f"디렉토리 생성 실패: {dir_path} - {str(e)}")
    
    if created_dirs:
        print(f"생성된 디렉토리: {', '.join(created_dirs)}")

def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(description='VeriView AI 서버 실행 (D-ID API 통합)')
    parser.add_argument('--mode', choices=['test', 'main'], 
                       default='main', help='실행 모드 선택 (test: 테스트 서버, main: 메인 서버)')
    parser.add_argument('--d-id', action='store_true',
                       help='D-ID 기능 강제 활성화')
    parser.add_argument('--aistudios', action='store_true',
                       help='AIStudios 폴백 활성화')
    parser.add_argument('--no-avatar', action='store_true',
                       help='아바타 기능 비활성화 (샘플 영상만 사용)')
    return parser.parse_args()

def display_startup_info(mode, d_id_status, aistudios_status, d_id_api_status, aistudios_api_status, d_id_connection_status):
    """시작 정보 표시"""
    print("=" * 80)
    print(f"VeriView AI 서버 시작 (모드: {mode.upper()}, D-ID API 통합)")
    print("=" * 80)
    print(f"서버 주소: http://localhost:5000")
    print(f"테스트 엔드포인트: http://localhost:5000/ai/test")
    print()
    
    # D-ID 상태 표시
    d_id_available, d_id_msg = d_id_status
    d_id_api_configured, d_id_api_msg = d_id_api_status
    d_id_connected, d_id_connection_msg = d_id_connection_status
    
    print("D-ID (우선 사용) 상태:")
    print(f"  - 모듈 상태: {'module O' if d_id_available else 'module X'} {d_id_msg}")
    print(f"  - API 키: {'api O' if d_id_api_configured else 'module X'} {d_id_api_msg}")
    print(f"  - API 연결: {'api O' if d_id_connected else 'module X'} {d_id_connection_msg}")
    
    # AIStudios 폴백 상태 표시
    aistudios_available, aistudios_msg = aistudios_status
    aistudios_api_configured, aistudios_api_msg = aistudios_api_status
    
    print()
    print("AIStudios (폴백) 상태:")
    print(f"  - 모듈 상태: {'module O' if aistudios_available else 'module X'} {aistudios_msg}")
    print(f"  - API 키: {'api O' if aistudios_api_configured else 'api X'} {aistudios_api_msg}")
    
    # 영상 생성 상태 요약
    print()
    print("영상 생성 기능:")
    if d_id_available and d_id_api_configured and d_id_connected:
        print("  - 주요 서비스:  D-ID API (실사 아바타)")
        print("  - 한국어 TTS:  Microsoft Azure 음성")
        print("  - 캐싱 시스템:  활성화")
    elif aistudios_available and aistudios_api_configured:
        print("  - 주요 서비스:   AIStudios 폴백 사용")
        print("  - 캐싱 시스템:  활성화")
    else:
        print("  - 주요 서비스:  샘플 영상만 사용")
        print("  - 캐싱 시스템:  비활성화")
    
    print()
    print("주요 엔드포인트:")
    
    if mode == 'test':
        print("  테스트 모드 엔드포인트:")
        print("    - 연결 테스트: /ai/test")
        print("    - 공고 추천: /ai/recruitment/posting")
        print("    - 면접 질문 생성: /ai/interview/generate-question")
        print("    - AI 면접관 영상: /ai/interview/ai-video (D-ID)")
        print("    - 면접 답변 분석: /ai/interview/{interview_id}/{question_type}/answer-video")
        print("    - 꼬리질문 생성: /ai/interview/{interview_id}/genergate-followup-question")
        print("    - 토론 입론: /ai/debate/{debate_id}/opening-video")
        print("    - 토론 반론: /ai/debate/{debate_id}/rebuttal-video")
        print("    - 토론 재반론: /ai/debate/{debate_id}/counter-rebuttal-video")
        print("    - 토론 최종변론: /ai/debate/{debate_id}/closing-video")
    else:
        print("  메인 모드 엔드포인트:")
        print("    - 모듈 상태: /ai/debate/modules-status")
        print("    - 공고 추천: /ai/recruitment/posting")
        print("    - 면접 시작: /ai/interview/start")
        print("    - 토론 시작: /ai/debate/start")
    
    if d_id_available or aistudios_available:
        print()
        print("AI 아바타 영상 생성 엔드포인트:")
        print("  토론 AI 영상 (D-ID 우선):")
        print("    - AI 입론: /ai/debate/ai-opening-video")
        print("    - AI 반론: /ai/debate/ai-rebuttal-video")
        print("    - AI 재반론: /ai/debate/ai-counter-rebuttal-video")
        print("    - AI 최종변론: /ai/debate/ai-closing-video")
        print("  면접 AI 영상 (D-ID 우선):")
        print("    - AI 질문: /ai/interview/ai-video")
    
    print("=" * 80)
    
    # 설정 가이드
    if not d_id_api_configured and d_id_available:
        print()
        print(" D-ID API 키가 설정되지 않았습니다!")
        print("   다음 중 하나의 방법으로 설정하세요:")
        print("   1. 환경 변수: export D_ID_API_KEY='your_d_id_api_key'")
        print("   2. Windows: set D_ID_API_KEY=your_d_id_api_key")
        print("   3. .env 파일에 D_ID_API_KEY=your_d_id_api_key 추가")
        print("   4. D-ID 무료 계정: https://www.d-id.com")
        print()
    
    if not aistudios_api_configured and aistudios_available and not (d_id_available and d_id_api_configured):
        print("폴백을 위한 AIStudios API 키 설정:")
        print("   1. 환경 변수: export AISTUDIOS_API_KEY='your_aistudios_api_key'")
        print("   2. .env 파일에 AISTUDIOS_API_KEY=your_aistudios_api_key 추가")
        print()

def setup_avatar_integration(mode, args):
    """아바타 API 통합 설정"""
    # D-ID 상태 확인
    d_id_status = check_d_id_availability()
    d_id_api_status = check_d_id_api_key()
    
    # D-ID 연결 테스트
    d_id_connection_status = (False, "연결 테스트 안함")
    if d_id_status[0] and d_id_api_status[0]:
        d_id_connection_status = test_d_id_connection()
    
    # AIStudios 폴백 상태 확인
    aistudios_status = check_aistudios_availability()
    aistudios_api_status = check_aistudios_api_key()
    
    # 환경 변수 설정
    preferred_service = 'D_ID'
    use_fallback = 'True'
    
    if args.no_avatar:
        preferred_service = 'NONE'
        use_fallback = 'False'
    elif args.aistudios and not args.d_id:
        preferred_service = 'AISTUDIOS'
    
    os.environ['PREFERRED_AVATAR_SERVICE'] = preferred_service
    os.environ['USE_FALLBACK_SERVICE'] = use_fallback
    
    # 각 서비스 활성화 상태 설정
    if d_id_status[0] and d_id_api_status[0]:
        os.environ['D_ID_ENABLED'] = 'true'
    
    if aistudios_status[0] and aistudios_api_status[0]:
        os.environ['AISTUDIOS_ENABLED'] = 'true'
    
    return d_id_status, aistudios_status, d_id_api_status, aistudios_api_status, d_id_connection_status

def load_environment_variables():
    """환경 변수 로드"""
    try:
        from dotenv import load_dotenv
        # .env 파일 경로 명시적 지정
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        load_dotenv(dotenv_path=env_path, override=True)
        
        # 로드 후 주요 환경 변수 확인
        d_id_key = os.environ.get('D_ID_API_KEY', '')
        aistudios_key = os.environ.get('AISTUDIOS_API_KEY', '')
        
        print(f".env 파일에서 환경 변수 로드 완료")
        print(f"   D-ID API 키: {'*' * 20 + d_id_key[-10:] if d_id_key and len(d_id_key) > 20 else '미설정'}")
        print(f"   AIStudios API 키: {'*' * 10 + aistudios_key[-5:] if aistudios_key and len(aistudios_key) > 10 else '미설정'}")
        return True
    except ImportError:
        print(" python-dotenv가 설치되지 않음")
        print("   설치: pip install python-dotenv")
        print("   또는 환경 변수 수동 설정 필요")
        return False
    except Exception as e:
        print(f" 환경 변수 로드 중 오류: {e}")
        return False

if __name__ == "__main__":
    args = parse_arguments()
    
    # 환경 변수 로드
    load_environment_variables()
    
    # 필요한 디렉토리 생성
    setup_directories()
    
    # 아바타 API 통합 설정
    d_id_status, aistudios_status, d_id_api_status, aistudios_api_status, d_id_connection_status = setup_avatar_integration(args.mode, args)
    
    # 시작 정보 표시
    display_startup_info(args.mode, d_id_status, aistudios_status, d_id_api_status, aistudios_api_status, d_id_connection_status)
    
    if args.mode == "test":
        # 테스트 모드: server_runner.py 사용 (D-ID 통합)
        try:
            print("테스트 서버 모듈 로드 중...")
            from server_runner import app, initialize_analyzers, initialize_d_id, initialize_aistudios
            
            print("분석기 초기화 중...")
            initialize_analyzers()
            
            print("D-ID 초기화 중...")
            d_id_initialized = initialize_d_id()
            
            if d_id_initialized:
                print("D-ID 초기화 완료 - 실사 아바타 영상 생성 기능 사용 가능")
            else:
                print("D-ID 초기화 실패 - AIStudios 폴백 시도")
                
                print("AIStudios 폴백 초기화 중...")
                aistudios_initialized = initialize_aistudios()
                
                if aistudios_initialized:
                    print("AIStudios 폴백 초기화 완료")
                else:
                    print("AIStudios 폴백도 실패 - 샘플 영상 모드로 동작")
            
            print()
            print("테스트 서버 시작...")
            print("중단하려면 Ctrl+C를 누르세요.")
            print("=" * 80)
            
            # Flask 서버 실행
            app.run(host="0.0.0.0", port=5000, debug=True)
            
        except ImportError as e:
            print(f"테스트 서버 모듈 로드 실패: {e}")
            print("server_runner.py 파일이 존재하는지 확인하세요.")
            print()
            print("해결 방법:")
            print("   1. D-ID 모듈 설치 확인")
            print("   2. requirements.txt 재설치: pip install -r requirements.txt")
            sys.exit(1)
        except Exception as e:
            print(f"테스트 서버 실행 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    else:
        # 메인 모드: main_server.py 사용 (D-ID 통합)
        try:
            print("메인 서버 모듈 로드 중...")
            
            # main_server.py가 있는지 확인
            if not os.path.exists('main_server.py'):
                print("main_server.py가 없습니다. 테스트 모드로 대체 실행합니다.")
                print()
                print("테스트 서버로 대체 실행...")
                from server_runner import app, initialize_analyzers, initialize_d_id, initialize_aistudios
                
                print("분석기 초기화 중...")
                initialize_analyzers()
                
                print("D-ID 초기화 중...")
                d_id_initialized = initialize_d_id()
                
                if d_id_initialized:
                    print("D-ID 초기화 완료")
                else:
                    print("D-ID 초기화 실패 - AIStudios 폴백 시도")
                    aistudios_initialized = initialize_aistudios()
                    if aistudios_initialized:
                        print("AIStudios 폴백 초기화 완료")
                    else:
                        print("AIStudios 폴백도 실패 - 샘플 영상 모드로 동작")
            else:
                from main_server import app, initialize_ai_systems
                
                print("🔧 AI 시스템 초기화 중...")
                initialize_ai_systems()
            
            print()
            print("🚀 메인 서버 시작...")
            print("중단하려면 Ctrl+C를 누르세요.")
            print("=" * 80)
            
            # Flask 서버 실행
            app.run(host="0.0.0.0", port=5000, debug=True)
            
        except ImportError as e:
            print(f"메인 서버 모듈 로드 실패: {e}")
            print()
            print("대안: 테스트 모드로 실행...")
            try:
                from server_runner import app, initialize_analyzers, initialize_d_id, initialize_aistudios
                
                print("분석기 초기화 중...")
                initialize_analyzers()
                
                print("D-ID 초기화 중...")
                d_id_initialized = initialize_d_id()
                
                if d_id_initialized:
                    print("D-ID 초기화 완료")
                else:
                    print("D-ID 초기화 실패 - 샘플 영상 모드로 동작")
                
                print("대체 서버 시작...")
                app.run(host="0.0.0.0", port=5000, debug=True)
                
            except Exception as fallback_error:
                print(f"대체 서버도 실행 실패: {fallback_error}")
                print("권장 실행 방법: python run.py test")
                sys.exit(1)
        except Exception as e:
            print(f"메인 서버 실행 중 오류 발생: {e}")
            print()
            print("디버그 정보:")
            import traceback
            traceback.print_exc()
            sys.exit(1)
