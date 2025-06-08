"""
기존 main_server.py에 AIStudios 통합을 추가하는 패치

사용법:
1. 이 파일을 ai_server 디렉토리에 저장
2. python apply_aistudios_patch.py 실행
3. 또는 수동으로 main_server.py에 아래 코드들을 추가

주의: 기존 main_server.py를 백업한 후 적용하세요
"""

import os
import shutil
from datetime import datetime

def backup_main_server():
    """기존 main_server.py 백업"""
    if os.path.exists('main_server.py'):
        backup_name = f'main_server_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy('main_server.py', backup_name)
        print(f"✅ 기존 파일 백업 완료: {backup_name}")
        return True
    return False

def read_main_server():
    """기존 main_server.py 읽기"""
    if os.path.exists('main_server.py'):
        with open('main_server.py', 'r', encoding='utf-8') as f:
            return f.read()
    return None

def apply_aistudios_patch(content):
    """AIStudios 통합 패치 적용"""
    
    # 1. Import 구문 추가
    import_patch = '''
# AIStudios 모듈 임포트 (새로 추가)
try:
    from modules.aistudios.client import AIStudiosClient
    from modules.aistudios.video_manager import VideoManager
    from modules.aistudios.routes import setup_aistudios_routes
    from modules.aistudios.interview_routes import setup_interview_routes
    AISTUDIOS_AVAILABLE = True
    print("✅ AIStudios 모듈 로드 성공: 영상 생성 기능 사용 가능")
except ImportError as e:
    print(f"❌ AIStudios 모듈 로드 실패: {e}")
    AISTUDIOS_AVAILABLE = False
'''
    
    # 2. 전역 변수 추가
    globals_patch = '''
# AIStudios 전역 변수 (새로 추가)
aistudios_client = None
video_manager = None
'''
    
    # 3. 초기화 함수 패치
    init_patch = '''
        # AIStudios 모듈 초기화 (새로 추가)
        if AISTUDIOS_AVAILABLE:
            try:
                # 환경 변수에서 API 키 가져오기
                api_key = os.environ.get('AISTUDIOS_API_KEY')
                if not api_key:
                    logger.warning("⚠️ AISTUDIOS_API_KEY 환경 변수가 설정되지 않았습니다.")
                    logger.warning("   .env 파일이나 시스템 환경 변수에 API 키를 설정해주세요.")
                
                # AIStudios 클라이언트 초기화
                aistudios_client = AIStudiosClient(api_key=api_key)
                logger.info("✅ AIStudios 클라이언트 초기화 완료")
                
                # 영상 관리자 초기화
                from pathlib import Path
                videos_dir = Path(__file__).parent / 'videos'
                video_manager = VideoManager(base_dir=videos_dir)
                logger.info("✅ AIStudios 영상 관리자 초기화 완료")
                
                logger.info(f"📁 영상 저장 디렉토리: {video_manager.base_dir}")
                logger.info(f"💾 캐시 디렉토리: {aistudios_client.cache_dir}")
                
            except Exception as e:
                logger.error(f"❌ AIStudios 초기화 실패: {str(e)}")
'''
    
    # 4. 라우트 설정 함수 추가
    route_setup_patch = '''
def setup_aistudios_integration():
    """AIStudios 라우트를 Flask 앱에 통합"""
    global aistudios_client, video_manager
    
    if AISTUDIOS_AVAILABLE and aistudios_client and video_manager:
        try:
            # AIStudios 일반 라우트 설정
            setup_aistudios_routes(app)
            
            # AIStudios 면접 라우트 설정 
            setup_interview_routes(
                app, 
                openface_integration,
                whisper_model,
                aistudios_client, 
                video_manager
            )
            
            logger.info("✅ AIStudios 라우트 통합 완료")
        except Exception as e:
            logger.error(f"❌ AIStudios 라우트 설정 실패: {str(e)}")
    else:
        logger.warning("⚠️ AIStudios 모듈이 사용 불가능하여 라우트 설정을 건너뜁니다.")
'''
    
    # 5. test_connection 엔드포인트 수정
    test_patch_add = '''
            "aistudios": "사용 가능" if AISTUDIOS_AVAILABLE else "사용 불가"  # 새로 추가'''
    
    test_patch_info = '''
        "aistudios_info": {  # 새로 추가
            "client_initialized": aistudios_client is not None,
            "video_manager_initialized": video_manager is not None,
            "api_key_configured": bool(os.environ.get('AISTUDIOS_API_KEY')),
            "cache_dir": str(aistudios_client.cache_dir) if aistudios_client else None,
            "videos_dir": str(video_manager.base_dir) if video_manager else None
        },'''
    
    # 6. 메인 실행 부분 수정
    main_patch = '''
    # AIStudios 라우트 통합 (새로 추가)
    setup_aistudios_integration()
    
    print("🚀 VeriView AI 메인 서버 (AIStudios 통합) 시작...")'''
    
    aistudios_info_patch = '''
    print(f"  - AIStudios: {'✅' if AISTUDIOS_AVAILABLE else '❌'}")'''
    
    final_info_patch = '''
    if AISTUDIOS_AVAILABLE:
        print("🎬 AIStudios 기능:")
        print("  - AI 아바타 영상 생성")
        print("  - 영상 캐싱 및 관리")
        print("  - 면접관 질문 영상")
        print("  - 토론자 발언 영상")
        print("  - 비동기 영상 처리")
        
        api_key_status = "✅ 설정됨" if os.environ.get('AISTUDIOS_API_KEY') else "❌ 미설정"
        print(f"  - API 키 상태: {api_key_status}")
        
        if not os.environ.get('AISTUDIOS_API_KEY'):
            print("⚠️  환경 변수 'AISTUDIOS_API_KEY'를 설정해주세요!")
        
        print("=" * 80)'''
    
    # 패치 적용
    patched_content = content
    
    # Import 추가
    llm_import_pos = content.find('from interview_features.debate.llm_module')
    if llm_import_pos != -1:
        patched_content = patched_content[:llm_import_pos] + import_patch + '\n' + patched_content[llm_import_pos:]
    
    # 전역 변수 추가
    global_vars_pos = patched_content.find('whisper_model = None')
    if global_vars_pos != -1:
        end_pos = patched_content.find('\n', global_vars_pos) + 1
        patched_content = patched_content[:end_pos] + '\n' + globals_patch + patched_content[end_pos:]
    
    # 초기화 함수에 AIStudios 초기화 추가
    tts_init_pos = patched_content.find('logger.info("TTS 모델 초기화 완료")')
    if tts_init_pos != -1:
        end_pos = patched_content.find('\n', tts_init_pos) + 1
        patched_content = patched_content[:end_pos] + '\n' + init_patch + patched_content[end_pos:]
    
    # 라우트 설정 함수 추가
    func_def_pos = patched_content.find('def process_audio_with_librosa')
    if func_def_pos != -1:
        patched_content = patched_content[:func_def_pos] + route_setup_patch + '\n\n' + patched_content[func_def_pos:]
    
    # test_connection 엔드포인트 수정
    tfidf_line = '"tfidf_recommendation": "사용 가능" if TFIDF_RECOMMENDATION_AVAILABLE else "사용 불가"'
    if tfidf_line in patched_content:
        patched_content = patched_content.replace(
            tfidf_line,
            tfidf_line.rstrip() + ',\n            ' + test_patch_add.strip()
        )
    
    # aistudios_info 추가
    endpoints_pos = patched_content.find('"endpoints": {')
    if endpoints_pos != -1:
        patched_content = patched_content[:endpoints_pos] + test_patch_info + '\n        ' + patched_content[endpoints_pos:]
    
    # 메인 실행 부분 수정
    init_systems_call = 'initialize_ai_systems()'
    if init_systems_call in patched_content:
        patched_content = patched_content.replace(
            init_systems_call,
            init_systems_call + '\n    \n    ' + main_patch.strip()
        )
    
    # 모듈 상태 출력에 AIStudios 추가
    librosa_status = 'print(f"  - Librosa: {\'✅\' if LIBROSA_AVAILABLE else \'❌\'}")'
    if librosa_status in patched_content:
        patched_content = patched_content.replace(
            librosa_status,
            librosa_status + '\n    ' + aistudios_info_patch.strip()
        )
    
    # 최종 정보 출력 추가
    final_print_pos = patched_content.find('print("="*80)')
    if final_print_pos != -1:
        end_pos = patched_content.find('\n', final_print_pos) + 1
        patched_content = patched_content[:end_pos] + '    ' + final_info_patch.strip() + '\n    \n' + patched_content[end_pos:]
    
    return patched_content

def write_patched_file(content, filename='main_server_aistudios.py'):
    """패치된 내용을 새 파일로 저장"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ AIStudios 통합 서버 생성 완료: {filename}")

def main():
    """메인 실행 함수"""
    print("🔧 AIStudios 통합 패치 적용 시작...")
    
    # 백업
    if backup_main_server():
        print("💾 백업 완료")
    
    # 기존 파일 읽기
    content = read_main_server()
    if not content:
        print("❌ main_server.py 파일을 찾을 수 없습니다.")
        return
    
    # 패치 적용
    patched_content = apply_aistudios_patch(content)
    
    # 새 파일 저장
    write_patched_file(patched_content)
    
    print("\n✅ AIStudios 통합 완료!")
    print("📋 사용법:")
    print("1. 환경 변수 설정: set AISTUDIOS_API_KEY=your_api_key")
    print("2. 서버 실행: python main_server_aistudios.py")
    print("3. 테스트: http://localhost:5000/ai/test")

if __name__ == "__main__":
    main()
