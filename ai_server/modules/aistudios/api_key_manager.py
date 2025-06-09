"""
환경별 API 키 관리 시스템
다양한 환경(로컬, AWS, Docker, CI/CD)에서 안전하게 API 키를 관리합니다.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class APIKeyManager:
    """
    다양한 환경에서 API 키를 안전하게 관리하는 클래스
    """
    
    def __init__(self):
        self.api_keys = {}
        self._load_priority = [
            'runtime_config',     # 1순위: 런타임 설정
            'environment_vars',   # 2순위: 환경 변수  
            'secrets_manager',    # 3순위: AWS Secrets Manager
            'config_file',        # 4순위: 설정 파일
            'env_file',          # 5순위: .env 파일
            'default_config'     # 6순위: 기본 설정
        ]
    
    def get_aistudios_api_key(self) -> Optional[str]:
        """
        AIStudios API 키를 우선순위에 따라 가져옵니다.
        
        Returns:
            str or None: AIStudios API 키
        """
        return self._get_api_key('AISTUDIOS_API_KEY')
    
    def _get_api_key(self, key_name: str) -> Optional[str]:
        """
        우선순위에 따라 API 키를 가져옵니다.
        
        Args:
            key_name (str): API 키 이름
            
        Returns:
            str or None: API 키 값
        """
        for method in self._load_priority:
            try:
                value = getattr(self, f'_get_from_{method}')(key_name)
                if value:
                    logger.info(f"API 키 로드 성공: {method} 방식으로 {key_name}")
                    return value
            except Exception as e:
                logger.debug(f"{method} 방식으로 {key_name} 로드 실패: {e}")
                continue
        
        logger.warning(f"API 키를 찾을 수 없습니다: {key_name}")
        return None
    
    def _get_from_runtime_config(self, key_name: str) -> Optional[str]:
        """런타임 설정에서 API 키 가져오기"""
        return self.api_keys.get(key_name)
    
    def _get_from_environment_vars(self, key_name: str) -> Optional[str]:
        """환경 변수에서 API 키 가져오기"""
        # 다양한 환경 변수 이름 시도
        possible_names = [
            key_name,
            key_name.upper(),
            key_name.lower(),
            f"VERIVIEW_{key_name}",
            f"AI_SERVER_{key_name}"
        ]
        
        for name in possible_names:
            value = os.environ.get(name)
            if value and value != 'your_actual_api_key_here':
                return value
        
        return None
    
    def _get_from_secrets_manager(self, key_name: str) -> Optional[str]:
        """AWS Secrets Manager에서 API 키 가져오기"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # AWS 리전 확인
            region = os.environ.get('AWS_DEFAULT_REGION', 'ap-northeast-2')
            
            # Secrets Manager 클라이언트 생성
            client = boto3.client('secretsmanager', region_name=region)
            
            # 시크릿 이름들 시도
            secret_names = [
                'veriview/aistudios',
                'ai-server/api-keys',
                f'veriview/{key_name.lower()}'
            ]
            
            for secret_name in secret_names:
                try:
                    response = client.get_secret_value(SecretId=secret_name)
                    secret_data = json.loads(response['SecretString'])
                    
                    # 다양한 키 이름 시도
                    possible_keys = [
                        key_name,
                        key_name.lower(),
                        'aistudios_api_key',
                        'api_key'
                    ]
                    
                    for key in possible_keys:
                        if key in secret_data:
                            return secret_data[key]
                            
                except ClientError as e:
                    if e.response['Error']['Code'] != 'ResourceNotFoundException':
                        logger.debug(f"Secrets Manager 오류: {e}")
                    continue
            
        except ImportError:
            logger.debug("boto3가 설치되지 않음 - AWS Secrets Manager 건너뛰기")
        except Exception as e:
            logger.debug(f"AWS Secrets Manager 접근 실패: {e}")
        
        return None
    
    def _get_from_config_file(self, key_name: str) -> Optional[str]:
        """설정 파일에서 API 키 가져오기"""
        config_files = [
            'config/api_keys.json',
            'config/production.json',
            'api_config.json'
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # 중첩된 구조에서 키 찾기
                    possible_paths = [
                        [key_name],
                        ['api_keys', key_name],
                        ['aistudios', 'api_key'],
                        ['keys', key_name.lower()]
                    ]
                    
                    for path in possible_paths:
                        value = config_data
                        for key in path:
                            if isinstance(value, dict) and key in value:
                                value = value[key]
                            else:
                                value = None
                                break
                        
                        if value and isinstance(value, str):
                            return value
                            
                except (json.JSONDecodeError, IOError) as e:
                    logger.debug(f"설정 파일 읽기 실패 {config_file}: {e}")
                    continue
        
        return None
    
    def _get_from_env_file(self, key_name: str) -> Optional[str]:
        """.env 파일에서 API 키 가져오기"""
        env_files = ['.env', '.env.local', '.env.production']
        
        for env_file in env_files:
            env_path = Path(env_file)
            if env_path.exists():
                try:
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"\'')
                                
                                if key == key_name and value != 'your_actual_api_key_here':
                                    return value
                except IOError as e:
                    logger.debug(f".env 파일 읽기 실패 {env_file}: {e}")
                    continue
        
        return None
    
    def _get_from_default_config(self, key_name: str) -> Optional[str]:
        """기본 설정에서 API 키 가져오기 (개발용)"""
        # 개발 환경에서만 사용하는 기본값들
        defaults = {
            'AISTUDIOS_API_KEY': os.environ.get('DEV_AISTUDIOS_API_KEY')
        }
        
        return defaults.get(key_name)
    
    def set_api_key(self, key_name: str, value: str):
        """런타임에서 API 키 설정"""
        self.api_keys[key_name] = value
        logger.info(f"런타임 API 키 설정: {key_name}")
    
    def set_aistudios_api_key(self, api_key: str):
        """AIStudios API 키 런타임 설정"""
        self.set_api_key('AISTUDIOS_API_KEY', api_key)
    
    def get_all_sources_status(self) -> Dict[str, Any]:
        """모든 API 키 소스의 상태를 확인합니다."""
        status = {}
        
        for method in self._load_priority:
            try:
                result = getattr(self, f'_get_from_{method}')('AISTUDIOS_API_KEY')
                status[method] = {
                    'available': bool(result),
                    'key_preview': f"{result[:10]}***" if result else None
                }
            except Exception as e:
                status[method] = {
                    'available': False,
                    'error': str(e)
                }
        
        return status

# 전역 인스턴스
api_key_manager = APIKeyManager()
