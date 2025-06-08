#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStudios 통합 예시 파일
기존 main_server.py에 AIStudios 모듈을 통합하는 방법을 보여주는 예시

사용법:
1. 이 파일을 참고하여 기존 main_server.py 수정
2. 또는 이 파일을 main_server_aistudios.py로 복사하여 실행

필요한 환경 변수:
- AISTUDIOS_API_KEY: AIStudios API 키
"""

# AIStudios 모듈 임포트 추가 (기존 import 구문 뒤에 추가)
try:
    from modules.aistudios.client import AIStudiosClient
    from modules.aistudios.video_manager import VideoManager
    from modules.aistudios.routes import setup_aistudios_routes
    from modules.aistudios.interview_routes import setup_interview_routes
    AISTUDIOS_AVAILABLE = True
    print("✅ AIStudios 모듈 로드 성공")
except ImportError as e:
    print(f"❌ AIStudios 모듈 로드 실패: {e}")
    AISTUDIOS_AVAILABLE = False

# 전역 변수에 AIStudios 관련 변수 추가
aistudios_client = None
video_manager = None

def initialize_ai_systems_with_aistudios():
    """기존 initialize_ai_systems() 함수에 AIStudios 초기화 추가"""
    global aistudios_client, video_manager
    
    # ... 기존 초기화 코드 ...
    
    # AIStudios 모듈 초기화 추가
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

def setup_aistudios_integration():
    """AIStudios 라우트를 Flask 앱에 통합"""
    if AISTUDIOS_AVAILABLE and aistudios_client and video_manager:
        try:
            # 기존에 import된 app, openface_integration, whisper_model 사용
            # AIStudios 일반 라우트 설정
            setup_aistudios_routes(app)
            
            # AIStudios 면접 라우트 설정 
            setup_interview_routes(
                app, 
                openface_integration,  # 기존에 초기화된 변수 사용
                whisper_model,         # 기존에 초기화된 변수 사용
                aistudios_client, 
                video_manager
            )
            
            logger.info("✅ AIStudios 라우트 통합 완료")
        except Exception as e:
            logger.error(f"❌ AIStudios 라우트 설정 실패: {str(e)}")
    else:
        logger.warning("⚠️ AIStudios 모듈이 사용 불가능하여 라우트 설정을 건너뜁니다.")

# 기존 test_connection 엔드포인트에 AIStudios 정보 추가
def update_test_endpoint():
    """기존 /ai/test 엔드포인트에 AIStudios 정보 추가하는 방법"""
    
    # 기존 응답에 AIStudios 정보 추가
    aistudios_info = {
        "aistudios": "사용 가능" if AISTUDIOS_AVAILABLE else "사용 불가",
        "aistudios_details": {
            "client_initialized": aistudios_client is not None,
            "video_manager_initialized": video_manager is not None,
            "api_key_configured": bool(os.environ.get('AISTUDIOS_API_KEY')),
            "cache_dir": str(aistudios_client.cache_dir) if aistudios_client else None,
            "videos_dir": str(video_manager.base_dir) if video_manager else None
        }
    }
    
    # 새로운 엔드포인트 추가
    additional_endpoints = {
        "aistudios_video_generation": {
            "ai_opening_video": "/ai/debate/ai-opening-video",
            "ai_rebuttal_video": "/ai/debate/ai-rebuttal-video",
            "ai_counter_rebuttal_video": "/ai/debate/ai-counter-rebuttal-video",
            "ai_closing_video": "/ai/debate/ai-closing-video",
            "ai_question_video": "/ai/interview/next-question-video",
            "ai_feedback_video": "/ai/interview/feedback-video"
        }
    }
    
    return aistudios_info, additional_endpoints

# 메인 함수 수정 예시
def main_with_aistudios():
    """기존 main 함수에 AIStudios 통합"""
    
    # 시작 시 AI 시스템 초기화 (AIStudios 포함)
    initialize_ai_systems_with_aistudios()
    
    # AIStudios 라우트 통합
    setup_aistudios_integration()
    
    print("🚀 VeriView AI 메인 서버 (AIStudios 통합) 시작...")
    print("📍 서버 주소: http://localhost:5000")
    print("🔍 테스트 엔드포인트: http://localhost:5000/ai/test")
    print("=" * 80)
    
    if AISTUDIOS_AVAILABLE:
        print("🎬 AIStudios 기능:")
        print("  📹 토론 AI 영상 생성:")
        print("    - POST /ai/debate/ai-opening-video")
        print("    - POST /ai/debate/ai-rebuttal-video") 
        print("    - POST /ai/debate/ai-counter-rebuttal-video")
        print("    - POST /ai/debate/ai-closing-video")
        print("  🎤 면접 AI 영상 생성:")
        print("    - POST /ai/interview/next-question-video")
        print("    - POST /ai/interview/feedback-video")
        print("  🔧 영상 관리:")
        print("    - GET /api/aistudios/status")
        print("    - POST /api/admin/cache/clear")
        
        api_key_status = "✅ 설정됨" if os.environ.get('AISTUDIOS_API_KEY') else "❌ 미설정"
        print(f"  - API 키 상태: {api_key_status}")
        
        if not os.environ.get('AISTUDIOS_API_KEY'):
            print("")
            print("⚠️  환경 변수 'AISTUDIOS_API_KEY'를 설정해주세요!")
            print("   Windows: set AISTUDIOS_API_KEY=your_api_key")
            print("   Linux/Mac: export AISTUDIOS_API_KEY=your_api_key")
        
        print("=" * 80)
    
    # Flask 앱 실행
    # app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    print("📋 이 파일은 AIStudios 통합 예시입니다.")
    print("실제 사용을 위해서는 기존 main_server.py를 수정하거나")
    print("이 코드를 참고하여 새로운 파일을 만들어주세요.")
    
    # 예시 실행
    main_with_aistudios()
