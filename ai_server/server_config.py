"""
서버 설정 모듈
서버 실행 모드 및 설정 관리
"""
import os
import logging
from typing import Dict, Any, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ai_server.log")
    ]
)
logger = logging.getLogger("ai_server")

# 서버 모드 설정
SERVER_MODE = os.environ.get("SERVER_MODE", "test").lower()
if SERVER_MODE not in ["main", "test"]:
    logger.warning(f"유효하지 않은 서버 모드: {SERVER_MODE}, 기본값(test)으로 설정합니다.")
    SERVER_MODE = "test"

# 서버 포트 설정
SERVER_PORT = int(os.environ.get("SERVER_PORT", 5000 if SERVER_MODE == "test" else 5001))

# 서버 모드별 설정
SERVER_CONFIG = {
    "main": {
        "name": "Main Server",
        "description": "LLM, OpenFace, Whisper, TTS, Librosa 등 실제 AI 모듈 사용",
        "port": 5001,
        "use_llm": True,
        "use_tts": True
    },
    "test": {
        "name": "Test Server",
        "description": "LLM 제외, 고정 응답 반환 (OpenFace, Whisper, TTS, Librosa 모듈 사용 가능)",
        "port": 5000,
        "use_llm": False,
        "use_tts": True
    }
}

# 현재 서버 설정
CURRENT_CONFIG = SERVER_CONFIG.get(SERVER_MODE, SERVER_CONFIG["test"])

# 서버 정보 로깅
logger.info(f"서버 모드: {SERVER_MODE}")
logger.info(f"서버 이름: {CURRENT_CONFIG['name']}")
logger.info(f"서버 설명: {CURRENT_CONFIG['description']}")
logger.info(f"포트 번호: {SERVER_PORT}")
logger.info(f"LLM 사용: {CURRENT_CONFIG['use_llm']}")
logger.info(f"TTS 사용: {CURRENT_CONFIG['use_tts']}")

def get_server_info() -> Dict[str, Any]:
    """
    현재 서버 정보 반환
    
    Returns:
        Dict[str, Any]: 서버 정보
    """
    return {
        "mode": SERVER_MODE,
        "name": CURRENT_CONFIG["name"],
        "description": CURRENT_CONFIG["description"],
        "port": SERVER_PORT,
        "use_llm": CURRENT_CONFIG["use_llm"],
        "use_tts": CURRENT_CONFIG["use_tts"]
    }
