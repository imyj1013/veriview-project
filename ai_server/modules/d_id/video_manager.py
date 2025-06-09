#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID 영상 관리 모듈
캐싱 및 파일 관리
"""

import os
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DIDVideoManager:
    """D-ID 영상 캐싱 및 관리 클래스"""
    
    def __init__(self, base_dir: str = 'videos'):
        """
        영상 관리자 초기화
        
        Args:
            base_dir: 기본 저장 디렉토리
        """
        self.base_dir = base_dir
        self.cache_dir = os.path.join(base_dir, 'cache')
        self.interviews_dir = os.path.join(base_dir, 'interviews')
        self.debates_dir = os.path.join(base_dir, 'debates')
        self.metadata_file = os.path.join(base_dir, 'video_metadata.json')
        
        # 디렉토리 생성
        for directory in [self.cache_dir, self.interviews_dir, self.debates_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # 메타데이터 로드
        self.metadata = self._load_metadata()
        
        logger.info(f"D-ID 영상 관리자 초기화: {base_dir}")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """메타데이터 파일 로드"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"메타데이터 로드 실패: {str(e)}")
            return {}
    
    def _save_metadata(self):
        """메타데이터 파일 저장"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"메타데이터 저장 실패: {str(e)}")
    
    def _generate_cache_key(self, content: str, params: Dict[str, Any]) -> str:
        """캐시 키 생성"""
        # 텍스트와 매개변수를 조합해서 고유 키 생성
        combined = content + json.dumps(params, sort_keys=True)
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def get_cached_video(self, content: str, video_type: str, **params) -> Optional[str]:
        """
        캐시된 영상 조회
        
        Args:
            content: 영상 내용 (질문 텍스트 등)
            video_type: 영상 유형 ('interview' 또는 'debate')
            **params: 추가 매개변수 (성별, 단계 등)
            
        Returns:
            캐시된 영상 파일 경로 또는 None
        """
        try:
            cache_key = self._generate_cache_key(content, params)
            
            if cache_key in self.metadata:
                video_info = self.metadata[cache_key]
                file_path = video_info.get('file_path')
                
                # 파일 존재 확인
                if file_path and os.path.exists(file_path):
                    # 캐시 만료 확인 (7일)
                    created_time = datetime.fromisoformat(video_info.get('created_at'))
                    if datetime.now() - created_time < timedelta(days=7):
                        logger.info(f"캐시된 영상 반환: {file_path}")
                        return file_path
                    else:
                        logger.info(f"캐시 만료된 영상 삭제: {file_path}")
                        self._remove_cached_video(cache_key)
                else:
                    # 파일이 없으면 메타데이터에서 삭제
                    self._remove_cached_video(cache_key)
            
            return None
            
        except Exception as e:
            logger.error(f"캐시 조회 중 오류: {str(e)}")
            return None
    
    def save_video(self, video_path: str, content: str, video_type: str, **params) -> str:
        """
        영상 저장 및 캐시 등록
        
        Args:
            video_path: 원본 영상 파일 경로
            content: 영상 내용
            video_type: 영상 유형
            **params: 추가 매개변수
            
        Returns:
            최종 저장된 영상 파일 경로
        """
        try:
            # 저장 디렉토리 결정
            if video_type == 'interview':
                target_dir = self.interviews_dir
            elif video_type == 'debate':
                target_dir = self.debates_dir
            else:
                target_dir = self.cache_dir
            
            # 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{video_type}_{timestamp}.mp4"
            final_path = os.path.join(target_dir, filename)
            
            # 파일 복사 또는 이동
            if os.path.exists(video_path):
                import shutil
                shutil.copy2(video_path, final_path)
                
                # 캐시 키 생성 및 메타데이터 저장
                cache_key = self._generate_cache_key(content, params)
                self.metadata[cache_key] = {
                    'file_path': final_path,
                    'content': content,
                    'video_type': video_type,
                    'params': params,
                    'created_at': datetime.now().isoformat(),
                    'file_size': os.path.getsize(final_path)
                }
                
                self._save_metadata()
                logger.info(f"영상 저장 완료: {final_path}")
                
                return final_path
            else:
                logger.error(f"원본 영상 파일을 찾을 수 없음: {video_path}")
                return video_path
                
        except Exception as e:
            logger.error(f"영상 저장 중 오류: {str(e)}")
            return video_path
    
    def _remove_cached_video(self, cache_key: str):
        """캐시된 영상 삭제"""
        try:
            if cache_key in self.metadata:
                video_info = self.metadata[cache_key]
                file_path = video_info.get('file_path')
                
                # 파일 삭제
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"캐시 파일 삭제: {file_path}")
                
                # 메타데이터에서 삭제
                del self.metadata[cache_key]
                self._save_metadata()
                
        except Exception as e:
            logger.error(f"캐시 영상 삭제 중 오류: {str(e)}")
    
    def cleanup_old_videos(self, days: int = 7):
        """오래된 영상 파일 정리"""
        try:
            current_time = datetime.now()
            removed_count = 0
            
            for cache_key, video_info in list(self.metadata.items()):
                try:
                    created_time = datetime.fromisoformat(video_info.get('created_at'))
                    if current_time - created_time > timedelta(days=days):
                        self._remove_cached_video(cache_key)
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"영상 정리 중 오류 (키: {cache_key}): {str(e)}")
                    continue
            
            logger.info(f"오래된 영상 {removed_count}개 정리 완료")
            
        except Exception as e:
            logger.error(f"영상 정리 중 오류: {str(e)}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """저장소 정보 조회"""
        try:
            total_files = len(self.metadata)
            total_size = sum(info.get('file_size', 0) for info in self.metadata.values())
            
            # 타입별 통계
            type_stats = {}
            for video_info in self.metadata.values():
                video_type = video_info.get('video_type', 'unknown')
                if video_type not in type_stats:
                    type_stats[video_type] = {'count': 0, 'size': 0}
                type_stats[video_type]['count'] += 1
                type_stats[video_type]['size'] += video_info.get('file_size', 0)
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'type_stats': type_stats,
                'base_dir': self.base_dir
            }
            
        except Exception as e:
            logger.error(f"저장소 정보 조회 중 오류: {str(e)}")
            return {}
