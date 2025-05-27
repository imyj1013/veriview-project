"""
공통 API 라우트
서버 상태, 헬스 체크 등 공통 엔드포인트
"""
import time
import logging
from flask import jsonify, request
import server_config
from modules.text_to_speech import TTSModule

logger = logging.getLogger(__name__)

def register_common_routes(app):
    """
    공통 라우트 등록
    
    Args:
        app: Flask 앱 인스턴스
    """
    
    @app.route('/ai/health', methods=['GET'])
    def health_check():
        """헬스 체크 엔드포인트"""
        # 전역 변수로 선언된 모듈 사용 가능 여부 확인
        from server import (
            LLM_MODULE_AVAILABLE, 
            OPENFACE_INTEGRATION_AVAILABLE, 
            WHISPER_AVAILABLE, 
            TTS_MODULE_AVAILABLE, 
            LIBROSA_AVAILABLE,
            JOB_RECOMMENDATION_AVAILABLE
        )
        
        return jsonify({
            "status": "healthy",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "server_type": server_config.CURRENT_CONFIG["name"],
            "server_mode": server_config.SERVER_MODE,
            "services": {
                "llm": LLM_MODULE_AVAILABLE and server_config.CURRENT_CONFIG["use_llm"],
                "openface": OPENFACE_INTEGRATION_AVAILABLE,
                "whisper": WHISPER_AVAILABLE,
                "tts": TTS_MODULE_AVAILABLE and server_config.CURRENT_CONFIG["use_tts"],
                "librosa": LIBROSA_AVAILABLE,
                "job_recommendation": JOB_RECOMMENDATION_AVAILABLE
            }
        })

    @app.route('/ai/test', methods=['GET'])
    def test_connection():
        """연결 테스트 및 상태 확인 엔드포인트"""
        logger.info("연결 테스트 요청 받음: /ai/test")
        
        # 전역 변수로 선언된 모듈 사용 가능 여부 확인
        from server import (
            LLM_MODULE_AVAILABLE, 
            OPENFACE_INTEGRATION_AVAILABLE, 
            WHISPER_AVAILABLE, 
            TTS_MODULE_AVAILABLE, 
            LIBROSA_AVAILABLE,
            JOB_RECOMMENDATION_AVAILABLE
        )
        
        # 백엔드 연결 테스트
        backend_status = "연결 확인 필요"
        try:
            import requests
            response = requests.get("http://localhost:4000/api/test", timeout=2)
            if response.status_code == 200:
                backend_status = "연결됨 (정상 작동)"
            else:
                backend_status = f"연결됨 (상태 코드: {response.status_code})"
        except Exception as e:
            backend_status = f"연결 실패: {str(e)}"
        
        test_response = {
            "status": f"AI {server_config.CURRENT_CONFIG['name']}가 정상 작동 중입니다.",
            "server_type": server_config.CURRENT_CONFIG["name"],
            "server_mode": server_config.SERVER_MODE,
            "server_description": server_config.CURRENT_CONFIG["description"],
            "backend_connection": backend_status,
            "modules": {
                "llm": "사용 가능" if LLM_MODULE_AVAILABLE and server_config.CURRENT_CONFIG["use_llm"] else "사용 불가",
                "openface": "사용 가능" if OPENFACE_INTEGRATION_AVAILABLE else "사용 불가",
                "whisper": "사용 가능" if WHISPER_AVAILABLE else "사용 불가",
                "tts": "사용 가능" if TTS_MODULE_AVAILABLE and server_config.CURRENT_CONFIG["use_tts"] else "사용 불가",
                "librosa": "사용 가능" if LIBROSA_AVAILABLE else "사용 불가",
                "job_recommendation": "사용 가능" if JOB_RECOMMENDATION_AVAILABLE else "사용 불가"
            },
            "endpoints": {
                "debate": {
                    "start": "/ai/debate/start",
                    "ai_opening": "/ai/debate/<debate_id>/ai-opening",
                    "opening_video": "/ai/debate/<debate_id>/opening-video"
                },
                "personal_interview": {
                    "start": "/ai/interview/start",  
                    "question": "/ai/interview/<interview_id>/question",
                    "answer_video": "/ai/interview/<interview_id>/answer-video"
                },
                "job_recommendation": {
                    "recommend": "/ai/jobs/recommend",
                    "categories": "/ai/jobs/categories",
                    "recruitment_posting": "/ai/recruitment/posting"
                }
            }
        }
        
        logger.info(f"테스트 응답: {test_response}")
        return jsonify(test_response)
    
    @app.route('/ai/tts-test', methods=['GET'])
    def tts_test():
        """TTS 테스트 엔드포인트"""
        # 테스트 텍스트 (쿼리 파라미터에서 가져오거나 기본값 사용)
        text = request.args.get('text', '안녕하세요, 베리뷰입니다. TTS 테스트 중입니다.')
        
        # TTS 모듈 참조
        from server import tts_module
        
        if tts_module is None:
            return jsonify({"error": "TTS 모듈을 사용할 수 없습니다."}), 500
        
        try:
            from modules.common.flask_utils import create_tts_streaming_response
            
            # TTS 스트리밍 응답 생성
            return create_tts_streaming_response(tts_module, text)
            
        except Exception as e:
            logger.error(f"TTS 테스트 오류: {str(e)}")
            return jsonify({"error": f"TTS 테스트 오류: {str(e)}"}), 500
