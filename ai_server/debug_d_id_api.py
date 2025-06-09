#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 디버깅 테스트 스크립트
500 에러의 원인을 파악하기 위한 상세 테스트
"""

import os
import sys
import requests
import json
import base64
import logging
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

def test_d_id_api():
    """D-ID API 연결 및 영상 생성 테스트"""
    
    # API 키 확인
    api_key = os.environ.get('D_ID_API_KEY')
    if not api_key:
        logger.error("D_ID_API_KEY가 설정되지 않았습니다.")
        return
    
    logger.info(f"API 키 형식: {'email:password' if ':' in api_key else 'api_key'}")
    
    # 인증 헤더 설정
    if ':' in api_key:
        encoded_key = base64.b64encode(api_key.encode()).decode('ascii')
        auth_header = f'Basic {encoded_key}'
    else:
        auth_header = f'Bearer {api_key}'
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    base_url = "https://api.d-id.com"
    
    # 1. API 연결 테스트 - 여러 엔드포인트 시도
    logger.info("=== D-ID API 연결 테스트 시작 ===")
    
    # /clips 엔드포인트 테스트
    logger.info("1. /clips 엔드포인트 테스트")
    try:
        response = requests.get(f"{base_url}/clips", headers=headers, timeout=10)
        logger.info(f"응답 코드: {response.status_code}")
        logger.info(f"응답 헤더: {dict(response.headers)}")
        if response.status_code != 200:
            logger.error(f"응답 내용: {response.text}")
    except Exception as e:
        logger.error(f"요청 실패: {str(e)}")
    
    # /actors 엔드포인트 테스트  
    logger.info("\n2. /actors 엔드포인트 테스트")
    try:
        response = requests.get(f"{base_url}/actors", headers=headers, timeout=10)
        logger.info(f"응답 코드: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"응답 내용: {response.text}")
    except Exception as e:
        logger.error(f"요청 실패: {str(e)}")
    
    # 2. 간단한 영상 생성 테스트
    logger.info("\n=== 영상 생성 테스트 ===")
    
    # 최소한의 요청 데이터로 테스트
    test_data_minimal = {
        "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Noam_front_thumbnail.jpg",
        "script": {
            "type": "text",
            "input": "Hello, this is a test."
        }
    }
    
    logger.info("3. 최소 요청 데이터로 /talks 생성 테스트")
    logger.info(f"요청 데이터: {json.dumps(test_data_minimal, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/talks", 
            headers=headers, 
            json=test_data_minimal,
            timeout=30
        )
        logger.info(f"응답 코드: {response.status_code}")
        logger.info(f"응답 헤더: {dict(response.headers)}")
        logger.info(f"응답 내용: {response.text}")
        
        if response.status_code == 201:
            logger.info("✅ 영상 생성 요청 성공!")
            result = response.json()
            talk_id = result.get('id')
            logger.info(f"Talk ID: {talk_id}")
    except Exception as e:
        logger.error(f"요청 실패: {str(e)}")
    
    # 한국어 음성 포함 테스트
    test_data_korean = {
        "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Noam_front_thumbnail.jpg",
        "script": {
            "type": "text",
            "provider": {
                "type": "microsoft",
                "voice_id": "ko-KR-InJoonNeural"
            },
            "input": "안녕하세요, 테스트입니다."
        }
    }
    
    logger.info("\n4. 한국어 음성 포함 /talks 생성 테스트")
    logger.info(f"요청 데이터: {json.dumps(test_data_korean, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/talks", 
            headers=headers, 
            json=test_data_korean,
            timeout=30
        )
        logger.info(f"응답 코드: {response.status_code}")
        logger.info(f"응답 내용: {response.text}")
    except Exception as e:
        logger.error(f"요청 실패: {str(e)}")
    
    # 3. 지원되는 음성 목록 확인
    logger.info("\n=== 지원되는 음성 목록 확인 ===")
    logger.info("5. /voices 엔드포인트 테스트")
    
    try:
        response = requests.get(f"{base_url}/voices", headers=headers, timeout=10)
        logger.info(f"응답 코드: {response.status_code}")
        if response.status_code == 200:
            voices = response.json()
            # 한국어 음성만 필터링
            korean_voices = [v for v in voices.get('voices', []) if 'ko' in v.get('locale', '').lower()]
            logger.info(f"한국어 음성 수: {len(korean_voices)}")
            for voice in korean_voices[:5]:  # 처음 5개만 출력
                logger.info(f"  - {voice.get('name', 'N/A')} ({voice.get('provider', 'N/A')})")
        else:
            logger.error(f"응답 내용: {response.text}")
    except Exception as e:
        logger.error(f"요청 실패: {str(e)}")

if __name__ == "__main__":
    test_d_id_api()
