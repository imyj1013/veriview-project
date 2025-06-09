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
import base64
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
        
        # D-ID API 인증 방식 설정
        # D-ID 공식 문서에 따르면 Basic Authentication 사용
        # https://docs.d-id.com/reference/basic-authentication
        
        # API 키가 username:password 형식인 경우 처리
        if ':' in api_key:
            # 이미 base64 인코딩된 경우
            if api_key.startswith('Basic '):
                auth_header = api_key
            else:
                # username:password를 base64로 인코딩
                import base64
                encoded = base64.b64encode(api_key.encode()).decode('ascii')
                auth_header = f'Basic {encoded}'
        else:
            # 단일 API 키인 경우 (D-ID 대시보드에서 제공하는 형식)
            auth_header = f'Basic {api_key}'
        
        self.headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 대체 헤더는 제거 (D-ID는 Basic Auth만 사용)
        self.alt_headers = None
        
        # 기본 아바타 이미지 (면접관용/토론자용) - Express Avatars 호환
        self.default_avatars = {
            'interviewer_male': 'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg',
            'interviewer_female': 'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg',
            'debater_male': 'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg',
            'debater_female': 'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg'
        }
        
        # Express Avatars presenter IDs
        self.express_presenters = {
            'amy': 'amy-jcwCkr1grs',
            'josh': 'josh-z3RBjvwgPz',
            'matt': 'matt-e3RBkfJ5si'
        }
        
        logger.info(f"D-ID 클라이언트 초기화 완료: {base_url}")
    
    def test_connection(self) -> bool:
        """API 연결 테스트"""
        # D-ID 공식 문서에 따른 엔드포인트 테스트
        test_endpoints = ['/talks']
        
        for endpoint in test_endpoints:
            try:
                logger.info(f"D-ID API 테스트: {endpoint}")
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    timeout=10
                )
                
                logger.info(f"D-ID API 응답: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info("✅ D-ID API 연결 성공")
                    return True
                elif response.status_code == 401:
                    logger.error("D-ID API 인증 실패 (401): API 키를 확인하세요")
                    logger.error(f"응답: {response.text}")
                    # 디버깅용: 헤더 확인
                    logger.debug(f"사용된 헤더: {self.headers}")
                elif response.status_code == 403:
                    logger.error("D-ID API 권한 없음 (403): API 플랜을 확인하세요")
                else:
                    logger.error(f"D-ID API 연결 실패: {response.status_code}")
                    logger.error(f"응답 내용: {response.text[:500]}")
                    
            except requests.exceptions.Timeout:
                logger.error(f"D-ID API 연결 시간 초과: {endpoint}")
            except requests.exceptions.ConnectionError:
                logger.error(f"D-ID API 연결 실패: 네트워크 오류")
            except Exception as e:
                logger.error(f"D-ID API 연결 테스트 중 오류: {str(e)}")
        
        logger.error("D-ID API 연결 실패")
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
            
            # D-ID API 요청 데이터 - 최소한의 필수 필드만 사용
            data = {
                "source_url": source_url,
                "script": {
                    "type": "text",
                    "input": script  # 최대 40초 길이로 제한
                }
            }
            
            # 스크립트 길이 제한 (D-ID Trial 제한)
            if len(script) > 200:
                script = script[:200]
                data["script"]["input"] = script
                logger.warning(f"스크립트가 너무 깁니다. 200자로 제한했습니다.")
            
            logger.info(f"D-ID 영상 생성 시작: script={script[:50]}..., avatar={avatar_type}")
            logger.info(f"D-ID 요청 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 영상 생성 요청 (기본 헤더 시도)
            response = requests.post(
                f"{self.base_url}/talks",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            logger.info(f"D-ID API 응답 코드: {response.status_code}")
            
            # 401 인증 오류 시 디버깅 정보 출력
            if response.status_code == 401:
                logger.error("D-ID API 인증 실패 (401)")
                logger.error(f"사용된 API 키: {self.api_key[:20]}...{self.api_key[-10:]}")
                logger.error(f"사용된 헤더: {self.headers.get('Authorization', 'N/A')[:50]}...")
                logger.error(f"응답: {response.text}")
                logger.error("\nD-ID 대시보드에서 API 키를 다시 확인하세요.")
                logger.error("https://studio.d-id.com → API Keys → Create New")
                return None
            
            if response.status_code != 201:
                logger.error(f"D-ID 영상 생성 요청 실패: {response.status_code}")
                logger.error(f"응답 내용: {response.text}")
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
            # Microsoft Azure TTS에서 지원하는 한국어 음성 ID 사용
            voice_id = 'ko-KR-SunHiNeural' if interviewer_gender == 'female' else 'ko-KR-InJoonNeural'
            
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
            # Microsoft Azure TTS에서 지원하는 한국어 음성 ID 사용
            voice_id = 'ko-KR-YuJinNeural' if debater_gender == 'female' else 'ko-KR-GookMinNeural'
            
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
