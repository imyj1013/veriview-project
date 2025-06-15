"""
파일 관련 유틸리티 함수
파일 관리, 임시 파일 처리 등의 기능 제공
"""
import os
import logging

logger = logging.getLogger(__name__)

def cleanup_temp_files(file_paths: list):
    """
    임시 파일 정리
    
    Args:
        file_paths: 삭제할 파일 경로 목록
    """
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"임시 파일 삭제: {file_path}")
            except Exception as e:
                logger.warning(f"임시 파일 삭제 실패: {file_path} - {str(e)}")
