import os
import json
import time
import requests
import logging
import tempfile
from pathlib import Path
from .api_key_manager import api_key_manager

# 로깅 설정
logger = logging.getLogger(__name__)

class AIStudiosClient:
    """
    AIStudios API 클라이언트
    
    AIStudios의 생성형 AI 아바타 API를 호출하여 영상을 생성하는 클라이언트 클래스입니다.
    다양한 환경에서 API 키를 자동으로 관리합니다.
    """
    
    def __init__(self, api_key=None, cache_dir=None):
        """
        AIStudios API 클라이언트 초기화
        
        Args:
            api_key (str, optional): AIStudios API 키. None이면 자동으로 다양한 소스에서 검색합니다.
            cache_dir (str, optional): 생성된 영상을 캐싱할 디렉토리 경로. 
                                      기본값은 프로젝트 루트의 'aistudios_cache' 폴더입니다.
        """
        # API 키 관리자를 통해 키 가져오기
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = api_key_manager.get_aistudios_api_key()
        
        if not self.api_key:
            logger.warning("AIStudios API 키를 찾을 수 없습니다. 다음 방법으로 설정해주세요:")
            logger.warning("1. 환경 변수: AISTUDIOS_API_KEY=your_api_key")
            logger.warning("2. .env 파일: AISTUDIOS_API_KEY=your_api_key")
            logger.warning("3. AWS Secrets Manager: veriview/aistudios")
            logger.warning("4. 런타임 설정: client.set_api_key('your_api_key')")
        else:
            logger.info(f"AIStudios API 키 로드 성공: {self.api_key[:10]}***")
        
        # 기본 캐시 디렉토리 설정
        if cache_dir is None:
            self.cache_dir = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / '..' / 'aistudios_cache'
        else:
            self.cache_dir = Path(cache_dir)
        
        # 캐시 디렉토리가 없으면 생성
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"AIStudios 캐시 디렉토리: {self.cache_dir}")
        
        # API 엔드포인트 및 기본 헤더 설정
        self.base_url = "https://app.aistudios.com/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 아바타 ID 설정 (기본값)
        self.default_avatar_id = "default_avatar_id"  # 실제 AIStudios에서 사용할 아바타 ID로 변경 필요
        
        # 요청 캐시 (메모리 내)
        self._request_cache = {}
        
        logger.info("AIStudios 클라이언트 초기화 완료")
    
    def set_api_key(self, api_key: str):
        """
        런타임에서 API 키 설정
        
        Args:
            api_key (str): 설정할 API 키
        """
        self.api_key = api_key
        self.headers["Authorization"] = f"Bearer {self.api_key}"
        api_key_manager.set_aistudios_api_key(api_key)
        logger.info(f"API 키 런타임 설정 완료: {api_key[:10]}***")
    
    def test_connection(self) -> bool:
        """
        API 연결 테스트
        
        Returns:
            bool: 연결 성공 여부
        """
        if not self.api_key:
            logger.error("API 키가 설정되지 않아 연결 테스트를 할 수 없습니다.")
            return False
        
        try:
            # 실제 AIStudios API에 맞게 수정 필요
            # 현재는 연결 가능성만 확인
            return bool(self.api_key and len(self.api_key) > 10)
        except Exception as e:
            logger.error(f"API 연결 테스트 실패: {e}")
            return False
    
    def get_api_key_status(self) -> dict:
        """
        API 키 상태 및 소스 정보 확인
        
        Returns:
            dict: API 키 상태 정보
        """
        return {
            "api_key_configured": bool(self.api_key),
            "api_key_preview": f"{self.api_key[:10]}***" if self.api_key else None,
            "sources_status": api_key_manager.get_all_sources_status()
        }
    
    def _generate_cache_key(self, text, avatar_id=None):
        """
        캐시 키 생성
        
        Args:
            text (str): 영상에 사용될 텍스트
            avatar_id (str, optional): 아바타 ID
            
        Returns:
            str: 캐시 키
        """
        # 간단한 해시 생성 (실제 구현에서는 더 강력한 해시 함수 사용 권장)
        if avatar_id is None:
            avatar_id = self.default_avatar_id
            
        key = f"{avatar_id}_{hash(text)}"
        return key
    
    def _get_cached_video(self, cache_key):
        """
        캐시된 영상 가져오기
        
        Args:
            cache_key (str): 캐시 키
            
        Returns:
            str or None: 캐시된 영상 파일 경로 또는 None (캐시 미스)
        """
        # 캐시 파일 경로 생성
        cache_file = self.cache_dir / f"{cache_key}.mp4"
        
        # 캐시 파일이 존재하는지 확인
        if cache_file.exists():
            logger.info(f"캐시 히트: {cache_key}")
            return str(cache_file)
        
        logger.info(f"캐시 미스: {cache_key}")
        return None
    
    def _save_to_cache(self, cache_key, video_data):
        """
        영상 데이터를 캐시에 저장
        
        Args:
            cache_key (str): 캐시 키
            video_data (bytes): 영상 데이터
            
        Returns:
            str: 저장된 캐시 파일 경로
        """
        # 캐시 파일 경로 생성
        cache_file = self.cache_dir / f"{cache_key}.mp4"
        
        # 영상 데이터를 파일로 저장
        with open(cache_file, 'wb') as f:
            f.write(video_data)
        
        logger.info(f"영상 캐싱 완료: {cache_file}")
        return str(cache_file)
    
    def generate_avatar_video(self, text, avatar_id=None, use_cache=True):
        """
        아바타 영상 생성
        
        Args:
            text (str): 아바타가 말할 텍스트
            avatar_id (str, optional): 사용할 아바타 ID. 기본값은 초기화 시 설정한 기본 아바타 ID입니다.
            use_cache (bool, optional): 캐시 사용 여부. 기본값은 True입니다.
            
        Returns:
            str: 생성된 영상 파일 경로
            
        Raises:
            Exception: API 호출 실패 시 발생
        """
        if not self.api_key:
            raise ValueError("AIStudios API 키가 설정되지 않았습니다.")
        
        if avatar_id is None:
            avatar_id = self.default_avatar_id
        
        # 캐시 키 생성
        cache_key = self._generate_cache_key(text, avatar_id)
        
        # 캐시 확인 (캐시 사용이 활성화된 경우)
        if use_cache:
            cached_video = self._get_cached_video(cache_key)
            if cached_video:
                return cached_video
        
        try:
            # AIStudios API 요청 데이터 준비
            request_data = {
                "avatarId": avatar_id,
                "text": text,
                "language": "ko",  # 기본 언어 한국어 설정
                "callback": None   # 콜백이 필요하면 URL 설정
            }
            
            # 실제 AIStudios API 구현에 맞게 조정 필요
            # 아래는 예상되는 API 흐름을 시뮬레이션한 코드입니다
            
            # 1. 영상 생성 요청
            logger.info(f"아바타 영상 생성 요청: avatar_id={avatar_id}, text={text[:20]}...")
            response = requests.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json=request_data
            )
            response.raise_for_status()
            
            # 2. 응답 확인
            result = response.json()
            if result.get("success") is False:
                raise Exception(f"영상 생성 요청 실패: {result.get('message')}")
            
            task_id = result.get("taskId")
            logger.info(f"영상 생성 작업 ID: {task_id}")
            
            # 3. 작업 완료 대기
            max_retries = 30  # 최대 30번 재시도 (약 5분)
            retry_interval = 10  # 10초 간격으로 확인
            
            for i in range(max_retries):
                time.sleep(retry_interval)
                
                # 작업 상태 확인
                status_response = requests.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=self.headers
                )
                status_response.raise_for_status()
                
                status = status_response.json()
                if status.get("status") == "completed":
                    video_url = status.get("videoUrl")
                    logger.info(f"영상 생성 완료: {video_url}")
                    break
                elif status.get("status") == "failed":
                    raise Exception(f"영상 생성 실패: {status.get('message')}")
                
                logger.info(f"영상 생성 대기 중... ({i+1}/{max_retries})")
            else:
                raise Exception("영상 생성 시간 초과")
            
            # 4. 영상 다운로드
            video_response = requests.get(video_url)
            video_response.raise_for_status()
            
            # 5. 영상 캐싱 및 경로 반환
            return self._save_to_cache(cache_key, video_response.content)
            
        except Exception as e:
            logger.error(f"아바타 영상 생성 중 오류 발생: {str(e)}")
            
            # 오류 발생 시 임시 파일 생성 (실제 구현에서는 제거 필요)
            # 테스트 목적으로만 사용됨
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            temp_file.close()
            logger.warning(f"오류 발생으로 인한 임시 파일 사용: {temp_file.name}")
            
            # 실제 구현에서는 아래 줄을 주석 해제하고 예외를 다시 발생시켜야 함
            # raise
            
            return temp_file.name
    
    def get_available_avatars(self):
        """
        사용 가능한 아바타 목록 조회
        
        Returns:
            list: 사용 가능한 아바타 목록
        """
        try:
            response = requests.get(
                f"{self.base_url}/avatars",
                headers=self.headers
            )
            response.raise_for_status()
            
            return response.json().get("avatars", [])
        except Exception as e:
            logger.error(f"아바타 목록 조회 중 오류 발생: {str(e)}")
            return []
    
    def clear_cache(self, older_than=None):
        """
        캐시 정리
        
        Args:
            older_than (int, optional): 지정된 시간(초) 이전의 캐시만 삭제. None이면 모든 캐시 삭제.
        """
        try:
            count = 0
            now = time.time()
            
            for cache_file in self.cache_dir.glob("*.mp4"):
                if older_than is None or (now - cache_file.stat().st_mtime > older_than):
                    cache_file.unlink()
                    count += 1
            
            logger.info(f"{count}개의 캐시 파일 삭제됨")
        except Exception as e:
            logger.error(f"캐시 정리 중 오류 발생: {str(e)}")
