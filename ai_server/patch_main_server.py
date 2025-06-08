#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 main_server.py에 AIStudios 통합을 추가하는 간단한 패치

사용법:
1. python patch_main_server.py 실행
2. 또는 수동으로 main_server.py 수정

이 스크립트는 기존 main_server.py를 백업하고 AIStudios 통합을 추가합니다.
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

def apply_aistudios_to_main_server():
    """main_server.py에 AIStudios 통합 추가"""
    
    if not os.path.exists('main_server.py'):
        print("❌ main_server.py 파일을 찾을 수 없습니다.")
        return False
    
    # 백업
    backup_main_server()
    
    # 파일 읽기
    with open('main_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # AIStudios import 추가 (기존 import 섹션 뒤에)
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
    
    # 전역 변수 추가
    globals_patch = '''
# AIStudios 전역 변수 (새로 추가)
aistudios_client = None
video_manager = None
'''
    
    # 초기화 함수에 AIStudios 초기화 추가
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
    
    # 라우트 설정 함수 추가
    routes_setup_patch = '''
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
    
    # 패치 적용
    patched_content = content
    
    # 1. Import 추가
    llm_import_pos = content.find('LLM_MODULE_AVAILABLE = True')
    if llm_import_pos != -1:
        # 해당 줄 뒤에 추가
        end_pos = content.find('\n', llm_import_pos) + 1
        patched_content = patched_content[:end_pos] + import_patch + patched_content[end_pos:]
    
    # 2. 전역 변수 추가
    tts_model_pos = patched_content.find('tts_model = None')
    if tts_model_pos != -1:
        end_pos = patched_content.find('\n', tts_model_pos) + 1
        patched_content = patched_content[:end_pos] + globals_patch + patched_content[end_pos:]
    
    # 3. 초기화 함수에 AIStudios 추가
    tts_init_pos = patched_content.find('logger.info("TTS 모델 초기화 완료")')
    if tts_init_pos != -1:
        end_pos = patched_content.find('\n', tts_init_pos) + 1
        patched_content = patched_content[:end_pos] + init_patch + patched_content[end_pos:]
    
    # 4. 라우트 설정 함수 추가 (함수 정의 부분에)
    func_start = patched_content.find('def process_audio_with_librosa')
    if func_start != -1:
        patched_content = patched_content[:func_start] + routes_setup_patch + '\n\n' + patched_content[func_start:]
    
    # 5. test_connection 엔드포인트에 AIStudios 정보 추가
    modules_section = '"tfidf_recommendation": "사용 가능" if TFIDF_RECOMMENDATION_AVAILABLE else "사용 불가"'
    if modules_section in patched_content:
        aistudios_line = ',\n            "aistudios": "사용 가능" if AISTUDIOS_AVAILABLE else "사용 불가"'
        patched_content = patched_content.replace(modules_section, modules_section + aistudios_line)
    
    # 6. 메인 실행 부분에 AIStudios 라우트 설정 추가
    init_call = 'initialize_ai_systems()'
    if init_call in patched_content:
        aistudios_setup = '''
    # AIStudios 라우트 통합 (새로 추가)
    setup_aistudios_integration()
    '''
        patched_content = patched_content.replace(init_call, init_call + aistudios_setup)
    
    # 7. 모듈 상태 출력에 AIStudios 추가
    tfidf_print = 'print(f"  - TF-IDF 공고추천: {\'✅\' if TFIDF_RECOMMENDATION_AVAILABLE else \'❌\'}")'
    if tfidf_print in patched_content:
        aistudios_print = '\n    print(f"  - AIStudios: {\'✅\' if AISTUDIOS_AVAILABLE else \'❌\'}")'
        patched_content = patched_content.replace(tfidf_print, tfidf_print + aistudios_print)
    
    # 8. AIStudios 기능 정보 추가
    final_equal_pos = patched_content.rfind('print("="*80)')
    if final_equal_pos != -1:
        aistudios_info = '''
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
        
        print("=" * 80)
    '''
        end_pos = patched_content.find('\n', final_equal_pos) + 1
        patched_content = patched_content[:end_pos] + aistudios_info + patched_content[end_pos:]
    
    # 파일 저장
    with open('main_server.py', 'w', encoding='utf-8') as f:
        f.write(patched_content)
    
    print("✅ main_server.py에 AIStudios 통합 완료!")
    return True

if __name__ == "__main__":
    print("🔧 main_server.py AIStudios 통합 패치 시작...")
    
    if apply_aistudios_to_main_server():
        print()
        print("✅ AIStudios 통합 완료!")
        print("📋 사용법:")
        print("1. 환경 변수 설정: export AISTUDIOS_API_KEY=your_api_key")
        print("2. 메인 모드 실행: python run.py --mode main")
        print("3. 테스트 모드 실행: python run.py --mode test")
        print("4. 테스트: http://localhost:5000/ai/test")
    else:
        print("❌ 패치 적용 실패")
