"""
Flask 스트리밍 유틸리티 모듈
Flask 스트리밍 응답 처리 기능 제공
"""
import logging
from flask import Response, stream_with_context
from typing import Dict, Any, Optional, Generator, Union

logger = logging.getLogger(__name__)

def create_streaming_response(generator_func, mimetype="audio/mpeg", status=200, headers=None):
    """
    Flask 스트리밍 응답 생성
    
    Args:
        generator_func: 스트리밍 데이터 생성 함수
        mimetype: 미디어 타입 (기본값: "audio/mpeg")
        status: 상태 코드 (기본값: 200)
        headers: 추가 헤더 (기본값: None)
        
    Returns:
        Flask Response: 스트리밍 응답
    """
    if headers is None:
        headers = {}
    
    # CORS 헤더 추가
    headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Cache-Control': 'no-cache'
    })
    
    return Response(
        stream_with_context(generator_func()),
        mimetype=mimetype,
        status=status,
        headers=headers
    )

def create_json_streaming_response(json_data, status=200, headers=None):
    """
    JSON 스트리밍 응답 생성
    
    Args:
        json_data: JSON 데이터
        status: 상태 코드 (기본값: 200)
        headers: 추가 헤더 (기본값: None)
        
    Returns:
        Flask Response: JSON 스트리밍 응답
    """
    import json
    
    if headers is None:
        headers = {}
    
    # CORS 헤더 추가
    headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache'
    })
    
    return Response(
        json.dumps(json_data),
        status=status,
        headers=headers,
        mimetype='application/json'
    )

def create_tts_streaming_response(tts_module, text, status=200, headers=None):
    """
    TTS 스트리밍 응답 생성
    
    Args:
        tts_module: TTS 모듈 인스턴스
        text: 변환할 텍스트
        status: 상태 코드 (기본값: 200)
        headers: 추가 헤더 (기본값: None)
        
    Returns:
        Flask Response: TTS 스트리밍 응답
    """
    if headers is None:
        headers = {}
    
    # 스트리밍 생성기 함수
    def generate():
        try:
            # 텍스트를 음성으로 변환
            audio_data = tts_module.synthesize_text(text)
            
            if not audio_data:
                logger.warning("TTS 변환 실패")
                yield b''
                return
                
            # 오디오 데이터 스트리밍
            for chunk in tts_module.stream_audio(audio_data):
                yield chunk
                
        except Exception as e:
            logger.error(f"TTS 스트리밍 응답 생성 오류: {e}")
            yield b''
    
    # CORS 헤더 추가
    headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Cache-Control': 'no-cache'
    })
    
    return Response(
        stream_with_context(generate()),
        mimetype=tts_module.get_content_type(),
        status=status,
        headers=headers
    )
