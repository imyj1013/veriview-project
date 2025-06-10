#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID 통합 라우트 모듈
백엔드와 연동하여 AI 아바타 영상 생성
"""

from flask import Blueprint, jsonify, request, send_file
import os
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
d_id_routes = Blueprint('d_id_routes', __name__)

# 전역 변수
d_id_client = None
video_manager = None

def init_d_id_routes(client, manager):
    """D-ID 라우트 초기화"""
    global d_id_client, video_manager
    d_id_client = client
    video_manager = manager
    logger.info("D-ID 라우트 초기화 완료")

# ==================== 개인면접 AI 아바타 영상 ====================

@d_id_routes.route('/ai/interview/next-question-video', methods=['POST'])
def generate_interview_question_video():
    """
    면접 질문 AI 아바타 영상 생성
    백엔드 API 명세: POST /ai/interview/next-question-video
    """
    try:
        data = request.json or {}
        logger.info(f"면접 질문 영상 생성 요청: {data}")
        
        # 필수 파라미터 추출
        question_text = data.get('question_text', '')
        interview_id = data.get('interview_id', int(time.time()))
        question_type = data.get('question_type', 'GENERAL')
        
        if not question_text:
            return jsonify({"error": "question_text는 필수입니다."}), 400
        
        # 면접관 성별 (기본: 여성)
        interviewer_gender = data.get('interviewer_gender', 'female')
        
        # 캐시 확인
        cache_key = f"interview_{question_type}_{hash(question_text)}"
        cached_video = video_manager.get_cached_video(cache_key) if video_manager else None
        
        if cached_video and os.path.exists(cached_video):
            logger.info(f"캐시된 영상 사용: {cached_video}")
            return send_file(
                cached_video,
                mimetype='video/mp4',
                as_attachment=True,
                download_name=f'interview_question_{interview_id}.mp4'
            )
        
        # D-ID 클라이언트로 영상 생성
        if d_id_client:
            try:
                # 면접관 톤으로 스크립트 조정
                script = format_interview_script(question_text, question_type)
                
                # 영상 생성
                video_path = d_id_client.generate_interview_video(
                    question_text=script,
                    interviewer_gender=interviewer_gender
                )
                
                if video_path and os.path.exists(video_path):
                    # 캐시 저장
                    if video_manager:
                        video_manager.cache_video(cache_key, video_path)
                    
                    logger.info(f"면접 질문 영상 생성 성공: {video_path}")
                    
                    return send_file(
                        video_path,
                        mimetype='video/mp4',
                        as_attachment=True,
                        download_name=f'interview_question_{interview_id}.mp4'
                    )
                else:
                    logger.error("D-ID 영상 생성 실패")
                    
            except Exception as e:
                logger.error(f"D-ID 영상 생성 중 오류: {str(e)}")
        
        # 폴백: 샘플 영상 반환
        logger.warning("D-ID 사용 불가, 샘플 영상 반환")
        sample_path = create_sample_interview_video(question_text, interview_id)
        
        return send_file(
            sample_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'interview_question_{interview_id}.mp4'
        )
        
    except Exception as e:
        logger.error(f"면접 질문 영상 생성 중 오류: {str(e)}")
        return jsonify({"error": f"영상 생성 실패: {str(e)}"}), 500

@d_id_routes.route('/ai/interview/feedback-video', methods=['POST'])
def generate_interview_feedback_video():
    """
    면접 피드백 AI 아바타 영상 생성
    백엔드 API 명세: POST /ai/interview/feedback-video
    """
    try:
        data = request.json or {}
        logger.info(f"면접 피드백 영상 생성 요청: {data}")
        
        # 피드백 내용 추출
        feedback_text = data.get('feedback_text', '')
        interview_id = data.get('interview_id', int(time.time()))
        overall_score = data.get('overall_score', 0)
        
        if not feedback_text:
            # 점수 기반 기본 피드백 생성
            feedback_text = generate_default_feedback(overall_score)
        
        # 피드백 스크립트 생성
        script = format_feedback_script(feedback_text, overall_score)
        
        # D-ID 클라이언트로 영상 생성
        if d_id_client:
            try:
                video_path = d_id_client.generate_interview_video(
                    question_text=script,
                    interviewer_gender='female'
                )
                
                if video_path and os.path.exists(video_path):
                    logger.info(f"피드백 영상 생성 성공: {video_path}")
                    
                    return send_file(
                        video_path,
                        mimetype='video/mp4',
                        as_attachment=True,
                        download_name=f'interview_feedback_{interview_id}.mp4'
                    )
                    
            except Exception as e:
                logger.error(f"D-ID 피드백 영상 생성 중 오류: {str(e)}")
        
        # 폴백: 샘플 피드백 영상
        sample_path = create_sample_feedback_video(feedback_text, interview_id)
        
        return send_file(
            sample_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'interview_feedback_{interview_id}.mp4'
        )
        
    except Exception as e:
        logger.error(f"피드백 영상 생성 중 오류: {str(e)}")
        return jsonify({"error": f"피드백 영상 생성 실패: {str(e)}"}), 500

# ==================== 토론면접 AI 아바타 영상 ====================

@d_id_routes.route('/ai/debate/ai-opening-video', methods=['POST'])
def generate_debate_opening_video():
    """
    AI 입론 영상 생성
    백엔드 API 명세: POST /ai/debate/ai-opening-video
    """
    try:
        data = request.json or {}
        logger.info(f"AI 입론 영상 생성 요청: {data}")
        
        # 필수 파라미터 추출
        opening_text = data.get('ai_opening_text', '')
        debate_id = data.get('debate_id', int(time.time()))
        topic = data.get('topic', '인공지능')
        position = data.get('position', 'CON')
        
        if not opening_text:
            # 기본 입론 생성
            opening_text = generate_default_opening(topic, position)
        
        # 캐시 확인
        cache_key = f"debate_opening_{position}_{hash(opening_text)}"
        cached_video = video_manager.get_cached_video(cache_key) if video_manager else None
        
        if cached_video and os.path.exists(cached_video):
            logger.info(f"캐시된 영상 사용: {cached_video}")
            return send_file(
                cached_video,
                mimetype='video/mp4',
                as_attachment=True,
                download_name=f'debate_opening_{debate_id}.mp4'
            )
        
        # D-ID 클라이언트로 영상 생성
        if d_id_client:
            try:
                # 토론자 성별 (찬성: 남성, 반대: 여성)
                debater_gender = 'male' if position == 'PRO' else 'female'
                
                video_path = d_id_client.generate_debate_video(
                    debate_text=opening_text,
                    debater_gender=debater_gender,
                    debate_phase='opening'
                )
                
                if video_path and os.path.exists(video_path):
                    # 캐시 저장
                    if video_manager:
                        video_manager.cache_video(cache_key, video_path)
                    
                    logger.info(f"AI 입론 영상 생성 성공: {video_path}")
                    
                    return send_file(
                        video_path,
                        mimetype='video/mp4',
                        as_attachment=True,
                        download_name=f'debate_opening_{debate_id}.mp4'
                    )
                    
            except Exception as e:
                logger.error(f"D-ID 입론 영상 생성 중 오류: {str(e)}")
        
        # 폴백: 샘플 영상
        sample_path = create_sample_debate_video(opening_text, 'opening', debate_id)
        
        return send_file(
            sample_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'debate_opening_{debate_id}.mp4'
        )
        
    except Exception as e:
        logger.error(f"AI 입론 영상 생성 중 오류: {str(e)}")
        return jsonify({"error": f"입론 영상 생성 실패: {str(e)}"}), 500

@d_id_routes.route('/ai/debate/ai-rebuttal-video', methods=['POST'])
def generate_debate_rebuttal_video():
    """AI 반론 영상 생성"""
    return generate_debate_video_generic('rebuttal')

@d_id_routes.route('/ai/debate/ai-counter-rebuttal-video', methods=['POST'])
def generate_debate_counter_rebuttal_video():
    """AI 재반론 영상 생성"""
    return generate_debate_video_generic('counter_rebuttal')

@d_id_routes.route('/ai/debate/ai-closing-video', methods=['POST'])
def generate_debate_closing_video():
    """AI 최종 변론 영상 생성"""
    return generate_debate_video_generic('closing')

def generate_debate_video_generic(phase: str):
    """토론 영상 생성 공통 함수"""
    try:
        data = request.json or {}
        logger.info(f"AI {phase} 영상 생성 요청: {data}")
        
        # 텍스트 키 매핑
        text_keys = {
            'rebuttal': 'ai_rebuttal_text',
            'counter_rebuttal': 'ai_counter_rebuttal_text',
            'closing': 'ai_closing_text'
        }
        
        text_key = text_keys.get(phase, f'ai_{phase}_text')
        debate_text = data.get(text_key, '')
        debate_id = data.get('debate_id', int(time.time()))
        position = data.get('position', 'CON')
        
        if not debate_text:
            # 기본 텍스트 생성
            topic = data.get('topic', '인공지능')
            debate_text = generate_default_debate_text(phase, topic, position)
        
        # D-ID 클라이언트로 영상 생성
        if d_id_client:
            try:
                debater_gender = 'male' if position == 'PRO' else 'female'
                
                video_path = d_id_client.generate_debate_video(
                    debate_text=debate_text,
                    debater_gender=debater_gender,
                    debate_phase=phase
                )
                
                if video_path and os.path.exists(video_path):
                    logger.info(f"AI {phase} 영상 생성 성공: {video_path}")
                    
                    return send_file(
                        video_path,
                        mimetype='video/mp4',
                        as_attachment=True,
                        download_name=f'debate_{phase}_{debate_id}.mp4'
                    )
                    
            except Exception as e:
                logger.error(f"D-ID {phase} 영상 생성 중 오류: {str(e)}")
        
        # 폴백: 샘플 영상
        sample_path = create_sample_debate_video(debate_text, phase, debate_id)
        
        return send_file(
            sample_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'debate_{phase}_{debate_id}.mp4'
        )
        
    except Exception as e:
        logger.error(f"{phase} 영상 생성 중 오류: {str(e)}")
        return jsonify({"error": f"{phase} 영상 생성 실패: {str(e)}"}), 500

# ==================== 헬퍼 함수들 ====================

def format_interview_script(question_text: str, question_type: str) -> str:
    """면접 질문 스크립트 포맷팅"""
    greetings = {
        'GENERAL': '안녕하세요. 일반 질문을 드리겠습니다.',
        'TECH': '기술 관련 질문을 드리겠습니다.',
        'FIT': '인성 관련 질문을 드리겠습니다.',
        'SITUATION': '상황 대처 능력을 확인하는 질문입니다.'
    }
    
    greeting = greetings.get(question_type, '질문드리겠습니다.')
    
    # 질문이 이미 인사말을 포함하는 경우
    if question_text.startswith(('안녕', '질문')):
        return question_text
    
    return f"{greeting} {question_text}"

def format_feedback_script(feedback_text: str, score: float) -> str:
    """피드백 스크립트 포맷팅"""
    if score >= 4.5:
        opening = "수고하셨습니다. 매우 우수한 면접이었습니다."
    elif score >= 4.0:
        opening = "수고하셨습니다. 좋은 면접이었습니다."
    elif score >= 3.5:
        opening = "수고하셨습니다. 양호한 면접이었습니다."
    else:
        opening = "수고하셨습니다. 개선할 부분이 있었습니다."
    
    return f"{opening} {feedback_text}"

def generate_default_feedback(score: float) -> str:
    """기본 피드백 생성"""
    if score >= 4.5:
        return "전반적으로 매우 훌륭한 답변이었습니다. 자신감 있고 논리적인 답변이 인상적이었습니다."
    elif score >= 4.0:
        return "좋은 답변이었습니다. 조금 더 구체적인 예시를 들어주시면 더 좋을 것 같습니다."
    elif score >= 3.5:
        return "적절한 답변이었습니다. 답변의 구조를 더 체계적으로 정리하시면 좋겠습니다."
    else:
        return "답변에 개선이 필요합니다. 질문의 요점을 파악하고 간결하게 답변하는 연습이 필요합니다."

def generate_default_opening(topic: str, position: str) -> str:
    """기본 입론 생성"""
    if position == 'PRO':
        return f"안녕하세요. 저는 {topic}에 대해 찬성하는 입장입니다. {topic}은 우리 사회에 긍정적인 변화를 가져올 것입니다."
    else:
        return f"안녕하세요. 저는 {topic}에 대해 신중한 접근이 필요하다고 생각합니다. 여러 부작용을 고려해야 합니다."

def generate_default_debate_text(phase: str, topic: str, position: str) -> str:
    """기본 토론 텍스트 생성"""
    templates = {
        'rebuttal': {
            'PRO': f"상대측 주장을 들었지만, {topic}의 긍정적 측면이 더 크다고 생각합니다.",
            'CON': f"상대측 의견에도 일리가 있지만, {topic}의 위험성을 간과해서는 안됩니다."
        },
        'counter_rebuttal': {
            'PRO': f"추가로 말씀드리면, {topic}은 장기적으로 더 큰 이익을 가져올 것입니다.",
            'CON': f"또한 {topic}이 가져올 수 있는 사회적 문제도 고려해야 합니다."
        },
        'closing': {
            'PRO': f"결론적으로 {topic}은 우리가 받아들여야 할 변화입니다.",
            'CON': f"정리하면, {topic}에 대해서는 더 신중한 검토가 필요합니다."
        }
    }
    
    return templates.get(phase, {}).get(position, f"{topic}에 대한 제 입장을 말씀드렸습니다.")

def create_sample_interview_video(question_text: str, interview_id: int) -> str:
    """샘플 면접 영상 생성 (폴백)"""
    sample_dir = Path('videos/samples')
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    # 기존 샘플 파일 확인
    sample_file = sample_dir / 'interview_sample.mp4'
    
    if not sample_file.exists():
        # 간단한 테스트 영상 생성 (실제로는 미리 준비된 파일 사용)
        logger.warning("샘플 영상 파일이 없습니다. 빈 파일 생성")
        sample_file.write_bytes(b'')  # 실제로는 유효한 MP4 파일이어야 함
    
    return str(sample_file)

def create_sample_feedback_video(feedback_text: str, interview_id: int) -> str:
    """샘플 피드백 영상 생성 (폴백)"""
    return create_sample_interview_video(feedback_text, interview_id)

def create_sample_debate_video(debate_text: str, phase: str, debate_id: int) -> str:
    """샘플 토론 영상 생성 (폴백)"""
    sample_dir = Path('videos/samples')
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    sample_file = sample_dir / f'debate_{phase}_sample.mp4'
    
    if not sample_file.exists():
        logger.warning(f"샘플 {phase} 영상 파일이 없습니다.")
        sample_file.write_bytes(b'')
    
    return str(sample_file)

# ==================== 상태 확인 엔드포인트 ====================

@d_id_routes.route('/ai/d-id/status', methods=['GET'])
def check_d_id_status():
    """D-ID 서비스 상태 확인"""
    try:
        status = {
            "service": "D-ID",
            "client_initialized": d_id_client is not None,
            "video_manager_initialized": video_manager is not None,
            "api_key_configured": bool(os.getenv('D_ID_API_KEY')),
            "connection_test": False
        }
        
        # D-ID 연결 테스트
        if d_id_client:
            try:
                status["connection_test"] = d_id_client.test_connection()
            except:
                status["connection_test"] = False
        
        # 캐시 상태
        if video_manager:
            status["cache_info"] = {
                "cache_dir": str(video_manager.cache_dir),
                "cached_videos": len(list(Path(video_manager.cache_dir).glob('*.mp4')))
            }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"D-ID 상태 확인 중 오류: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 라우트 설정 함수
def setup_d_id_routes(app, client, manager):
    """Flask 앱에 D-ID 라우트 추가"""
    init_d_id_routes(client, manager)
    app.register_blueprint(d_id_routes)
    logger.info("D-ID 라우트가 Flask 앱에 등록되었습니다.")
