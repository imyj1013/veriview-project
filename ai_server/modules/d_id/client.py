#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 클라이언트
실사 느낌 AI 아바타 영상 생성
"""

import requests
import json
import time
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DIDClient:
    """D-ID API 클라이언트 클래스"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.d-id.com"):
        """
        D-ID 클라이언트 초기화
        
        Args:
            api_key: D-ID API 키
            base_url: D-ID API 베이스 URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Basic {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 기본 아바타 이미지 (면접관용/토론자용)
        self.default_avatars = {
            'interviewer_male': 'https://create-images-results.d-id.com/DefaultPresenters/Noam_front_thumbnail.jpg',
            'interviewer_female': 'https://create-images-results.d-id.com/DefaultPresenters/Maya_front_thumbnail.jpg',
            'debater_male': 'https://create-images-results.d-id.com/DefaultPresenters/David_front_thumbnail.jpg',
            'debater_female': 'https://create-images-results.d-id.com/DefaultPresenters/Sarah_front_thumbnail.jpg'
        }
        
        logger.info(f"D-ID 클라이언트 초기화 완료: {base_url}")
    
    def test_connection(self) -> bool:
        """API 연결 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/clips",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                logger.info("D-ID API 연결 성공")
                return True
            else:
                logger.error(f"D-ID API 연결 실패: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"D-ID API 연결 테스트 중 오류: {str(e)}")
            return False
    
    def create_avatar_video(
        self,
        script: str,
        avatar_type: str = 'interviewer_male',
        voice_id: str = 'ko-KR-Neural2-A',
        custom_avatar_url: Optional[str] = None
    ) -> Optional[str]:
        """
        아바타 영상 생성
        
        Args:
            script: 읽을 텍스트 (한국어)
            avatar_type: 아바타 유형 (interviewer_male, interviewer_female, debater_male, debater_female)
            voice_id: 음성 ID (한국어 TTS)
            custom_avatar_url: 커스텀 아바타 이미지 URL
            
        Returns:
            생성된 영상의 다운로드 URL 또는 None
        """
        try:
            # 아바타 이미지 URL 결정
            source_url = custom_avatar_url or self.default_avatars.get(avatar_type, self.default_avatars['interviewer_male'])
            
            # D-ID API 요청 데이터
            data = {
                "script": {
                    "type": "text",
                    "subtitles": "false",
                    "provider": {
                        "type": "microsoft",
                        "voice_id": voice_id
                    },
                    "ssml": "false",
                    "input": script
                },
                "config": {
                    "fluent": "false",
                    "pad_audio": "0.0"
                },
                "source_url": source_url
            }
            
            logger.info(f"D-ID 영상 생성 시작: script={script[:50]}..., avatar={avatar_type}")
            
            # 영상 생성 요청
            response = requests.post(
                f"{self.base_url}/talks",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 201:
                logger.error(f"D-ID 영상 생성 요청 실패: {response.status_code}, {response.text}")
                return None
            
            # 작업 ID 추출
            result = response.json()
            talk_id = result.get('id')
            
            if not talk_id:
                logger.error("D-ID 응답에서 talk_id를 찾을 수 없음")
                return None
            
            logger.info(f"D-ID 영상 생성 작업 시작: talk_id={talk_id}")
            
            # 영상 생성 완료 대기
            video_url = self._wait_for_video_completion(talk_id)
            
            if video_url:
                logger.info(f"D-ID 영상 생성 완료: {video_url}")
                return video_url
            else:
                logger.error(f"D-ID 영상 생성 실패: talk_id={talk_id}")
                return None
                
        except Exception as e:
            logger.error(f"D-ID 영상 생성 중 오류: {str(e)}")
            return None
    
    def _wait_for_video_completion(self, talk_id: str, max_wait_time: int = 300) -> Optional[str]:
        """
        영상 생성 완료 대기
        
        Args:
            talk_id: D-ID talk ID
            max_wait_time: 최대 대기 시간 (초)
            
        Returns:
            완성된 영상의 다운로드 URL 또는 None
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(
                    f"{self.base_url}/talks/{talk_id}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.error(f"영상 상태 확인 실패: {response.status_code}")
                    time.sleep(5)
                    continue
                
                result = response.json()
                status = result.get('status')
                
                logger.info(f"D-ID 영상 생성 상태: {status} (경과 시간: {int(time.time() - start_time)}초)")
                
                if status == 'done':
                    video_url = result.get('result_url')
                    if video_url:
                        return video_url
                    else:
                        logger.error("완료된 영상의 URL을 찾을 수 없음")
                        return None
                        
                elif status == 'error':
                    error_msg = result.get('error', {}).get('description', 'Unknown error')
                    logger.error(f"D-ID 영상 생성 오류: {error_msg}")
                    return None
                    
                elif status in ['created', 'started']:
                    # 아직 진행 중
                    time.sleep(10)
                    continue
                else:
                    logger.warning(f"알 수 없는 상태: {status}")
                    time.sleep(5)
                    continue
                    
            except Exception as e:
                logger.error(f"영상 상태 확인 중 오류: {str(e)}")
                time.sleep(5)
                continue
        
        logger.error(f"영상 생성 시간 초과: {max_wait_time}초")
        return None
    
    def download_video(self, video_url: str, save_path: str) -> bool:
        """
        영상 다운로드
        
        Args:
            video_url: 영상 다운로드 URL
            save_path: 저장할 경로
            
        Returns:
            다운로드 성공 여부
        """
        try:
            logger.info(f"영상 다운로드 시작: {video_url} -> {save_path}")
            
            response = requests.get(video_url, timeout=60)
            
            if response.status_code == 200:
                # 디렉토리 생성
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"영상 다운로드 완료: {save_path}")
                return True
            else:
                logger.error(f"영상 다운로드 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"영상 다운로드 중 오류: {str(e)}")
            return False
    
    def generate_interview_video(self, question_text: str, interviewer_gender: str = 'male') -> Optional[str]:
        """
        면접관 영상 생성
        
        Args:
            question_text: 면접 질문 텍스트
            interviewer_gender: 면접관 성별 ('male' 또는 'female')
            
        Returns:
            생성된 영상 파일 경로 또는 None
        """
        try:
            # 면접관 아바타 및 음성 설정
            avatar_type = f'interviewer_{interviewer_gender}'
            voice_id = 'ko-KR-Neural2-A' if interviewer_gender == 'female' else 'ko-KR-Neural2-B'
            
            # 면접관 톤으로 텍스트 가공
            interview_script = f"안녕하세요. {question_text}"
            
            # 영상 생성
            video_url = self.create_avatar_video(
                script=interview_script,
                avatar_type=avatar_type,
                voice_id=voice_id
            )
            
            if not video_url:
                return None
            
            # 영상 다운로드
            timestamp = int(time.time())
            filename = f"interview_{interviewer_gender}_{timestamp}.mp4"
            save_path = os.path.join('videos', 'interviews', filename)
            
            if self.download_video(video_url, save_path):
                return save_path
            else:
                return None
                
        except Exception as e:
            logger.error(f"면접관 영상 생성 중 오류: {str(e)}")
            return None
    
    def generate_debate_video(self, debate_text: str, debater_gender: str = 'male', debate_phase: str = 'opening') -> Optional[str]:
        """
        토론자 영상 생성
        
        Args:
            debate_text: 토론 텍스트
            debater_gender: 토론자 성별 ('male' 또는 'female')
            debate_phase: 토론 단계 ('opening', 'rebuttal', 'closing')
            
        Returns:
            생성된 영상 파일 경로 또는 None
        """
        try:
            # 토론자 아바타 및 음성 설정
            avatar_type = f'debater_{debater_gender}'
            voice_id = 'ko-KR-Neural2-C' if debater_gender == 'female' else 'ko-KR-Neural2-D'
            
            # 토론 단계에 맞는 톤으로 텍스트 가공
            if debate_phase == 'opening':
                debate_script = f"안녕하세요. 저는 다음과 같이 주장하겠습니다. {debate_text}"
            elif debate_phase == 'rebuttal':
                debate_script = f"상대측 주장에 대해 반박하겠습니다. {debate_text}"
            elif debate_phase == 'closing':
                debate_script = f"마지막으로 정리하자면, {debate_text}"
            else:
                debate_script = debate_text
            
            # 영상 생성
            video_url = self.create_avatar_video(
                script=debate_script,
                avatar_type=avatar_type,
                voice_id=voice_id
            )
            
            if not video_url:
                return None
            
            # 영상 다운로드
            timestamp = int(time.time())
            filename = f"debate_{debate_phase}_{debater_gender}_{timestamp}.mp4"
            save_path = os.path.join('videos', 'debates', filename)
            
            if self.download_video(video_url, save_path):
                return save_path
            else:
                return None
                
        except Exception as e:
            logger.error(f"토론자 영상 생성 중 오류: {str(e)}")
            return None
