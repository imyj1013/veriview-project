"""
AIStudios 연동 테스트 스크립트

Veriview 프로젝트에서 AIStudios의 생성형 AI 아바타를 활용한 
토론자 및 면접관 기능 통합 테스트를 위한 스크립트
"""

import os
import sys
import requests
import json
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 서버 URL 설정
BASE_URL = "http://localhost:5000"

def test_connection():
    """서버 연결 테스트"""
    try:
        response = requests.get(f"{BASE_URL}/ai/test")
        if response.status_code == 200:
            logger.info("서버 연결 성공!")
            logger.info(f"응답 데이터: {response.json()}")
            return True
        else:
            logger.error(f"서버 연결 실패: 상태 코드 {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"서버 연결 테스트 중 오류 발생: {str(e)}")
        return False

def test_aistudios_status():
    """AIStudios 모듈 상태 테스트"""
    try:
        response = requests.get(f"{BASE_URL}/api/aistudios/status")
        if response.status_code == 200:
            logger.info("AIStudios 모듈 상태 확인 성공!")
            logger.info(f"응답 데이터: {response.json()}")
            return True
        else:
            logger.error(f"AIStudios 모듈 상태 확인 실패: 상태 코드 {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"AIStudios 모듈 상태 확인 중 오류 발생: {str(e)}")
        return False

def test_debate_features():
    """토론 기능 테스트"""
    debate_id = int(time.time())
    
    # 1. AI 입론 생성
    try:
        data = {
            "topic": "인공지능의 발전이 인류에게 도움이 될 것인가?",
            "position": "PRO"
        }
        response = requests.post(f"{BASE_URL}/ai/debate/{debate_id}/ai-opening", json=data)
        if response.status_code == 200:
            logger.info("AI 입론 생성 성공!")
            ai_opening_text = response.json().get("ai_opening_text", "")
            logger.info(f"AI 입론: {ai_opening_text[:50]}...")
            
            # 2. AI 입론 영상 생성
            data = {
                "ai_opening_text": ai_opening_text,
                "debate_id": debate_id
            }
            response = requests.post(f"{BASE_URL}/ai/debate/ai-opening-video", json=data)
            if response.status_code == 200:
                logger.info("AI 입론 영상 생성 성공!")
                # 영상 파일이 바이너리로 반환됨
                logger.info(f"응답 크기: {len(response.content)} 바이트")
            else:
                logger.error(f"AI 입론 영상 생성 실패: 상태 코드 {response.status_code}")
        else:
            logger.error(f"AI 입론 생성 실패: 상태 코드 {response.status_code}")
    except Exception as e:
        logger.error(f"토론 기능 테스트 중 오류 발생: {str(e)}")

def test_interview_features():
    """면접 기능 테스트"""
    interview_id = int(time.time())
    
    # 1. 면접 질문 생성
    try:
        data = {
            "job_position": "백엔드 개발자",
            "question_type": "technical"
        }
        response = requests.post(f"{BASE_URL}/ai/interview/generate-question", json=data)
        if response.status_code == 200:
            logger.info("면접 질문 생성 성공!")
            question = response.json().get("question", "")
            question_type = response.json().get("question_type", "")
            logger.info(f"질문 타입: {question_type}, 질문: {question}")
            
            # 2. 면접관 질문 영상 생성
            data = {
                "question": question,
                "interview_id": interview_id,
                "question_type": question_type
            }
            response = requests.post(f"{BASE_URL}/ai/interview/next-question-video", json=data)
            if response.status_code == 200:
                logger.info("면접관 질문 영상 생성 성공!")
                video_path = response.json().get("video_path", "")
                logger.info(f"영상 경로: {video_path}")
            else:
                logger.error(f"면접관 질문 영상 생성 실패: 상태 코드 {response.status_code}")
        else:
            logger.error(f"면접 질문 생성 실패: 상태 코드 {response.status_code}")
    except Exception as e:
        logger.error(f"면접 기능 테스트 중 오류 발생: {str(e)}")

def run_all_tests():
    """모든 테스트 실행"""
    logger.info("=== AIStudios 연동 테스트 시작 ===")
    
    # 서버 연결 테스트
    if not test_connection():
        logger.error("서버 연결 테스트 실패. 다른 테스트를 건너뜁니다.")
        return
    
    # AIStudios 모듈 상태 테스트
    test_aistudios_status()
    
    # 토론 기능 테스트
    logger.info("=== 토론 기능 테스트 시작 ===")
    test_debate_features()
    
    # 면접 기능 테스트
    logger.info("=== 면접 기능 테스트 시작 ===")
    test_interview_features()
    
    logger.info("=== 모든 테스트 완료 ===")

if __name__ == "__main__":
    run_all_tests()
