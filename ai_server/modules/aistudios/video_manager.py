import os
import logging
import tempfile
import time
from pathlib import Path
from datetime import datetime

# 로깅 설정
logger = logging.getLogger(__name__)

class VideoManager:
    """
    영상 파일 관리 및 캐싱 시스템
    """
    
    def __init__(self, base_dir=None, cache_expiry=86400):
        """
        영상 관리자 초기화
        
        Args:
            base_dir (str, optional): 영상 저장 기본 디렉토리. 기본값은 프로젝트 루트의 'videos' 폴더입니다.
            cache_expiry (int, optional): 캐시 만료 시간(초). 기본값은 1일(86400초)입니다.
        """
        if base_dir is None:
            self.base_dir = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / '..' / 'videos'
        else:
            self.base_dir = Path(base_dir)
        
        # 저장 디렉토리가 없으면 생성
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 각 토론 단계별 서브디렉토리 생성
        self.debate_dirs = {
            'opening': self.base_dir / 'opening',
            'rebuttal': self.base_dir / 'rebuttal',
            'counter_rebuttal': self.base_dir / 'counter_rebuttal',
            'closing': self.base_dir / 'closing',
            'interview': self.base_dir / 'interview'
        }
        
        for dir_path in self.debate_dirs.values():
            dir_path.mkdir(exist_ok=True)
        
        self.cache_expiry = cache_expiry
        logger.info(f"영상 관리자 초기화 완료: {self.base_dir}")
    
    def get_video_path(self, debate_id, phase, is_ai=True):
        """
        특정 토론 영상의 경로 가져오기
        
        Args:
            debate_id (int): 토론 ID
            phase (str): 토론 단계 ('opening', 'rebuttal', 'counter_rebuttal', 'closing')
            is_ai (bool, optional): AI 영상 여부. True면 AI 영상, False면 사용자 영상. 기본값은 True입니다.
            
        Returns:
            Path: 영상 파일 경로
        """
        prefix = 'ai' if is_ai else 'user'
        filename = f"{prefix}_{phase}_{debate_id}.mp4"
        return self.debate_dirs[phase] / filename
    
    def get_interview_video_path(self, interview_id, question_type, is_ai=True):
        """
        특정 면접 영상의 경로 가져오기
        
        Args:
            interview_id (int): 면접 ID
            question_type (str): 질문 유형 (예: 'intro', 'experience', 'skill')
            is_ai (bool, optional): AI 영상 여부. True면 AI 영상, False면 사용자 영상. 기본값은 True입니다.
            
        Returns:
            Path: 영상 파일 경로
        """
        prefix = 'ai' if is_ai else 'user'
        filename = f"{prefix}_interview_{interview_id}_{question_type}.mp4"
        return self.debate_dirs['interview'] / filename
    
    def save_video(self, source_path, debate_id=None, interview_id=None, phase=None, question_type=None, is_ai=True):
        """
        영상 파일 저장
        
        Args:
            source_path (str): 소스 영상 파일 경로
            debate_id (int, optional): 토론 ID. 토론 영상인 경우 필수입니다.
            interview_id (int, optional): 면접 ID. 면접 영상인 경우 필수입니다.
            phase (str, optional): 토론 단계. 토론 영상인 경우 필수입니다.
            question_type (str, optional): 질문 유형. 면접 영상인 경우 필수입니다.
            is_ai (bool, optional): AI 영상 여부. 기본값은 True입니다.
            
        Returns:
            str: 저장된 영상 파일 경로
            
        Raises:
            ValueError: 필수 인자가 누락된 경우 발생
        """
        # 인자 검증
        if debate_id is not None and phase is not None:
            # 토론 영상
            target_path = self.get_video_path(debate_id, phase, is_ai)
        elif interview_id is not None and question_type is not None:
            # 면접 영상
            target_path = self.get_interview_video_path(interview_id, question_type, is_ai)
        else:
            raise ValueError("debate_id와 phase 또는 interview_id와 question_type이 필요합니다.")
        
        # 소스 파일 복사
        try:
            source_path = Path(source_path)
            if not source_path.exists():
                raise FileNotFoundError(f"소스 파일이 존재하지 않습니다: {source_path}")
            
            import shutil
            shutil.copy2(source_path, target_path)
            logger.info(f"영상 저장 완료: {target_path}")
            
            return str(target_path)
        except Exception as e:
            logger.error(f"영상 저장 중 오류 발생: {str(e)}")
            raise
    
    def clean_expired_videos(self):
        """
        만료된 영상 파일 정리
        
        오래된(만료된) 영상 파일을 삭제합니다.
        
        Returns:
            int: 삭제된 파일 수
        """
        count = 0
        now = time.time()
        
        for dir_path in self.debate_dirs.values():
            for video_file in dir_path.glob("*.mp4"):
                if now - video_file.stat().st_mtime > self.cache_expiry:
                    try:
                        video_file.unlink()
                        count += 1
                        logger.info(f"만료된 영상 삭제: {video_file}")
                    except Exception as e:
                        logger.error(f"영상 삭제 중 오류 발생: {str(e)}")
        
        return count
    
    def get_video_if_exists(self, debate_id=None, interview_id=None, phase=None, question_type=None, is_ai=True):
        """
        영상 파일이 존재하는 경우 경로 반환
        
        Args:
            debate_id (int, optional): 토론 ID
            interview_id (int, optional): 면접 ID
            phase (str, optional): 토론 단계
            question_type (str, optional): 질문 유형
            is_ai (bool, optional): AI 영상 여부. 기본값은 True입니다.
            
        Returns:
            str or None: 영상 파일 경로 또는 None (파일이 없는 경우)
        """
        try:
            if debate_id is not None and phase is not None:
                # 토론 영상
                target_path = self.get_video_path(debate_id, phase, is_ai)
            elif interview_id is not None and question_type is not None:
                # 면접 영상
                target_path = self.get_interview_video_path(interview_id, question_type, is_ai)
            else:
                return None
            
            if target_path.exists():
                return str(target_path)
            
            return None
        except Exception as e:
            logger.error(f"영상 확인 중 오류 발생: {str(e)}")
            return None
    
    def create_temp_video_file(self):
        """
        임시 영상 파일 생성 (테스트용)
        
        Returns:
            str: 임시 영상 파일 경로
        """
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False, dir=self.base_dir)
        temp_file.close()
        logger.warning(f"임시 영상 파일 생성: {temp_file.name}")
        return temp_file.name
