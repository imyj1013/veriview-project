from flask import Flask, jsonify, request, Response, send_file, stream_with_context
import os
import tempfile
import logging
import time
import json
from pathlib import Path

# AIStudios 모듈 임포트
from modules.aistudios.client import AIStudiosClient
from modules.aistudios.video_manager import VideoManager

# 로깅 설정
logger = logging.getLogger(__name__)

# AIStudios 클라이언트 및 영상 관리자 인스턴스
aistudios_client = None
video_manager = None

def initialize_aistudios():
    """AIStudios 관련 모듈 초기화"""
    global aistudios_client, video_manager
    try:
        # 환경 변수에서 API 키 가져오기
        api_key = os.environ.get('AISTUDIOS_API_KEY', 'YOUR_API_KEY')
        
        # AIStudios 클라이언트 초기화
        aistudios_client = AIStudiosClient(api_key=api_key)
        
        # 영상 관리자 초기화
        videos_dir = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / 'videos'
        video_manager = VideoManager(base_dir=videos_dir)
        
        logger.info("AIStudios 모듈 초기화 완료")
        return True
    except Exception as e:
        logger.error(f"AIStudios 모듈 초기화 실패: {str(e)}")
        return False

def setup_aistudios_routes(app):
    """AIStudios 관련 라우트 설정"""
    
    # AIStudios 모듈 초기화
    if not initialize_aistudios():
        logger.warning("AIStudios 라우트 설정 중단 - 초기화 실패")
        return
    
    # AI 토론자 관련 엔드포인트
    
    @app.route('/ai/debate/ai-opening-video', methods=['POST'])
    def ai_debate_opening_video():
        """AI 토론자 입론 영상 생성 엔드포인트"""
        try:
            data = request.json
            if not data or 'ai_opening_text' not in data:
                return jsonify({"error": "ai_opening_text가 필요합니다."}), 400
            
            text = data['ai_opening_text']
            debate_id = data.get('debate_id', int(time.time()))
            
            # 캐시 확인
            cached_video = video_manager.get_video_if_exists(debate_id=debate_id, phase='opening', is_ai=True)
            if cached_video:
                logger.info(f"캐시된 AI 입론 영상 반환: {cached_video}")
                return send_file(cached_video, mimetype='video/mp4')
            
            # 영상 생성
            logger.info(f"AI 입론 영상 생성 시작: debate_id={debate_id}")
            video_path = aistudios_client.generate_avatar_video(text)
            
            # 영상 저장
            final_path = video_manager.save_video(
                source_path=video_path, 
                debate_id=debate_id, 
                phase='opening', 
                is_ai=True
            )
            
            return send_file(final_path, mimetype='video/mp4')
        except Exception as e:
            logger.error(f"AI 입론 영상 생성 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/debate/<int:debate_id>/ai-opening-video', methods=['GET'])
    def get_ai_debate_opening_video(debate_id):
        """AI 토론자 입론 영상 조회 엔드포인트"""
        try:
            # 캐시 확인
            cached_video = video_manager.get_video_if_exists(debate_id=debate_id, phase='opening', is_ai=True)
            if cached_video:
                logger.info(f"캐시된 AI 입론 영상 반환: {cached_video}")
                return send_file(cached_video, mimetype='video/mp4')
            
            return jsonify({"error": "영상을 찾을 수 없습니다."}), 404
        except Exception as e:
            logger.error(f"AI 입론 영상 조회 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/ai/debate/ai-rebuttal-video', methods=['POST'])
    def ai_debate_rebuttal_video():
        """AI 토론자 반론 영상 생성 엔드포인트"""
        try:
            data = request.json
            if not data or 'ai_rebuttal_text' not in data:
                return jsonify({"error": "ai_rebuttal_text가 필요합니다."}), 400
            
            text = data['ai_rebuttal_text']
            debate_id = data.get('debate_id', int(time.time()))
            
            # 캐시 확인
            cached_video = video_manager.get_video_if_exists(debate_id=debate_id, phase='rebuttal', is_ai=True)
            if cached_video:
                logger.info(f"캐시된 AI 반론 영상 반환: {cached_video}")
                return send_file(cached_video, mimetype='video/mp4')
            
            # 영상 생성
            logger.info(f"AI 반론 영상 생성 시작: debate_id={debate_id}")
            video_path = aistudios_client.generate_avatar_video(text)
            
            # 영상 저장
            final_path = video_manager.save_video(
                source_path=video_path, 
                debate_id=debate_id, 
                phase='rebuttal', 
                is_ai=True
            )
            
            return send_file(final_path, mimetype='video/mp4')
        except Exception as e:
            logger.error(f"AI 반론 영상 생성 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/debate/<int:debate_id>/ai-rebuttal-video', methods=['GET'])
    def get_ai_debate_rebuttal_video(debate_id):
        """AI 토론자 반론 영상 조회 엔드포인트"""
        try:
            # 캐시 확인
            cached_video = video_manager.get_video_if_exists(debate_id=debate_id, phase='rebuttal', is_ai=True)
            if cached_video:
                logger.info(f"캐시된 AI 반론 영상 반환: {cached_video}")
                return send_file(cached_video, mimetype='video/mp4')
            
            return jsonify({"error": "영상을 찾을 수 없습니다."}), 404
        except Exception as e:
            logger.error(f"AI 반론 영상 조회 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/ai/debate/ai-counter-rebuttal-video', methods=['POST'])
    def ai_debate_counter_rebuttal_video():
        """AI 토론자 재반론 영상 생성 엔드포인트"""
        try:
            data = request.json
            if not data or 'ai_counter_rebuttal_text' not in data:
                return jsonify({"error": "ai_counter_rebuttal_text가 필요합니다."}), 400
            
            text = data['ai_counter_rebuttal_text']
            debate_id = data.get('debate_id', int(time.time()))
            
            # 캐시 확인
            cached_video = video_manager.get_video_if_exists(debate_id=debate_id, phase='counter_rebuttal', is_ai=True)
            if cached_video:
                logger.info(f"캐시된 AI 재반론 영상 반환: {cached_video}")
                return send_file(cached_video, mimetype='video/mp4')
            
            # 영상 생성
            logger.info(f"AI 재반론 영상 생성 시작: debate_id={debate_id}")
            video_path = aistudios_client.generate_avatar_video(text)
            
            # 영상 저장
            final_path = video_manager.save_video(
                source_path=video_path, 
                debate_id=debate_id, 
                phase='counter_rebuttal', 
                is_ai=True
            )
            
            return send_file(final_path, mimetype='video/mp4')
        except Exception as e:
            logger.error(f"AI 재반론 영상 생성 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/debate/<int:debate_id>/ai-counter-rebuttal-video', methods=['GET'])
    def get_ai_debate_counter_rebuttal_video(debate_id):
        """AI 토론자 재반론 영상 조회 엔드포인트"""
        try:
            # 캐시 확인
            cached_video = video_manager.get_video_if_exists(debate_id=debate_id, phase='counter_rebuttal', is_ai=True)
            if cached_video:
                logger.info(f"캐시된 AI 재반론 영상 반환: {cached_video}")
                return send_file(cached_video, mimetype='video/mp4')
            
            return jsonify({"error": "영상을 찾을 수 없습니다."}), 404
        except Exception as e:
            logger.error(f"AI 재반론 영상 조회 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/ai/debate/ai-closing-video', methods=['POST'])
    def ai_debate_closing_video():
        """AI 토론자 최종변론 영상 생성 엔드포인트"""
        try:
            data = request.json
            if not data or 'ai_closing_text' not in data:
                return jsonify({"error": "ai_closing_text가 필요합니다."}), 400
            
            text = data['ai_closing_text']
            debate_id = data.get('debate_id', int(time.time()))
            
            # 캐시 확인
            cached_video = video_manager.get_video_if_exists(debate_id=debate_id, phase='closing', is_ai=True)
            if cached_video:
                logger.info(f"캐시된 AI 최종변론 영상 반환: {cached_video}")
                return send_file(cached_video, mimetype='video/mp4')
            
            # 영상 생성
            logger.info(f"AI 최종변론 영상 생성 시작: debate_id={debate_id}")
            video_path = aistudios_client.generate_avatar_video(text)
            
            # 영상 저장
            final_path = video_manager.save_video(
                source_path=video_path, 
                debate_id=debate_id, 
                phase='closing', 
                is_ai=True
            )
            
            return send_file(final_path, mimetype='video/mp4')
        except Exception as e:
            logger.error(f"AI 최종변론 영상 생성 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/debate/<int:debate_id>/ai-closing-video', methods=['GET'])
    def get_ai_debate_closing_video(debate_id):
        """AI 토론자 최종변론 영상 조회 엔드포인트"""
        try:
            # 캐시 확인
            cached_video = video_manager.get_video_if_exists(debate_id=debate_id, phase='closing', is_ai=True)
            if cached_video:
                logger.info(f"캐시된 AI 최종변론 영상 반환: {cached_video}")
                return send_file(cached_video, mimetype='video/mp4')
            
            return jsonify({"error": "영상을 찾을 수 없습니다."}), 404
        except Exception as e:
            logger.error(f"AI 최종변론 영상 조회 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # AI 면접관 관련 엔드포인트
    
    @app.route('/ai/interview/ai-video', methods=['POST'])
    def ai_interview_video():
        """AI 면접관 영상 생성 엔드포인트"""
        try:
            data = request.json
            if not data or 'question_text' not in data:
                return jsonify({"error": "question_text가 필요합니다."}), 400
            
            text = data['question_text']
            interview_id = data.get('interview_id', int(time.time()))
            question_type = data.get('question_type', 'general')
            
            # 캐시 확인
            cached_video = video_manager.get_video_if_exists(
                interview_id=interview_id, 
                question_type=question_type, 
                is_ai=True
            )
            if cached_video:
                logger.info(f"캐시된 AI 면접 영상 반환: {cached_video}")
                return send_file(cached_video, mimetype='video/mp4')
            
            # 영상 생성
            logger.info(f"AI 면접 영상 생성 시작: interview_id={interview_id}, question_type={question_type}")
            video_path = aistudios_client.generate_avatar_video(text)
            
            # 영상 저장
            final_path = video_manager.save_video(
                source_path=video_path, 
                interview_id=interview_id, 
                question_type=question_type, 
                is_ai=True
            )
            
            return send_file(final_path, mimetype='video/mp4')
        except Exception as e:
            logger.error(f"AI 면접 영상 생성 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # 캐시 관리 엔드포인트
    
    @app.route('/api/admin/cache/clear', methods=['POST'])
    def clear_cache():
        """캐시 정리 엔드포인트 (관리자용)"""
        try:
            hours = request.json.get('hours', 24)
            seconds = hours * 3600
            
            # AIStudios 캐시 정리
            if aistudios_client:
                aistudios_client.clear_cache(older_than=seconds)
            
            # 영상 캐시 정리
            if video_manager:
                count = video_manager.clean_expired_videos()
                return jsonify({"success": True, "cleared_files": count})
            
            return jsonify({"success": True, "message": "캐시 정리 완료"})
        except Exception as e:
            logger.error(f"캐시 정리 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # 상태 확인 엔드포인트
    
    @app.route('/api/aistudios/status', methods=['GET'])
    def aistudios_status():
        """AIStudios 모듈 상태 확인 엔드포인트"""
        try:
            status = {
                "aistudios_client": aistudios_client is not None,
                "video_manager": video_manager is not None,
                "cache_dir": str(aistudios_client.cache_dir) if aistudios_client else None,
                "videos_dir": str(video_manager.base_dir) if video_manager else None,
                "available_avatars": len(aistudios_client.get_available_avatars()) if aistudios_client else 0
            }
            
            return jsonify(status)
        except Exception as e:
            logger.error(f"상태 확인 중 오류 발생: {str(e)}")
            return jsonify({"error": str(e)}), 500
