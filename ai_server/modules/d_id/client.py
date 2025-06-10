#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 클라이언트 - 수정된 버전
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
        
        # D-ID API 인증 헤더 설정 (Basic Authentication)
        self.headers = {
            'Authorization': f'Basic {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 기본 아바타 이미지 URLs - D-ID에서 제공하는 샘플 이미지 사용
        self.default_avatars = {
            'interviewer_male': 'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg',
            'interviewer_female': 'https://create-images-results.d-id.com/DefaultPresenters/Emma_f/image.jpeg', 
            'debater_male': 'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg',
            'debater_female': 'https://create-images-results.d-id.com/DefaultPresenters/Emma_f/image.jpeg'
        }
        
        # 한국어 음성 ID 설정 (Microsoft Azure TTS)
        self.korean_voices = {
            'male': 'ko-KR-InJoonNeural',      # 한국어 남성 음성 (자연스럽고 안정적)
            'female': 'ko-KR-SunHiNeural'     # 한국어 여성 음성 (명확하고 전문적)
        }
        
        # 용도별 음성 매핑 (안정적인 Azure TTS 음성 사용)
        self.voice_mapping = {
            'interviewer_male': 'ko-KR-InJoonNeural',    # 면접관 남성 (안정적)
            'interviewer_female': 'ko-KR-SunHiNeural',  # 면접관 여성 (전문적)
            'debater_male': 'ko-KR-InJoonNeural',       # 토론자 남성 (동일 음성)
            'debater_female': 'ko-KR-SunHiNeural'       # 토론자 여성 (동일 음성)
        }
        
        logger.info(f"D-ID 클라이언트 초기화 완료: {base_url}")
    
    def test_connection(self) -> bool:
        """API 연결 테스트"""
        try:
            logger.info("D-ID API 연결 테스트 시작")
            response = requests.get(
                f"{self.base_url}/talks",
                headers=self.headers,
                timeout=10
            )
            
            logger.info(f"D-ID API 응답 코드: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("D-ID API 연결 성공")
                return True
            elif response.status_code == 401:
                logger.error("D-ID API 인증 실패 (401): API 키를 확인하세요")
                logger.error(f"응답: {response.text}")
            elif response.status_code == 403:
                logger.error("D-ID API 권한 없음 (403): API 플랜을 확인하세요")
            else:
                logger.error(f"D-ID API 연결 실패: {response.status_code}")
                logger.error(f"응답 내용: {response.text[:500]}")
                    
        except requests.exceptions.Timeout:
            logger.error("D-ID API 연결 시간 초과")
        except requests.exceptions.ConnectionError:
            logger.error("D-ID API 연결 실패: 네트워크 오류")
        except Exception as e:
            logger.error(f"D-ID API 연결 테스트 중 오류: {str(e)}")
        
        return False
    
    def create_avatar_video(
        self,
        script: str,
        avatar_type: str = 'interviewer_male',
        custom_avatar_url: Optional[str] = None
    ) -> Optional[str]:
        """
        아바타 영상 생성
        
        Args:
            script: 읽을 텍스트 (한국어)
            avatar_type: 아바타 유형 (interviewer_male, interviewer_female, debater_male, debater_female)
            custom_avatar_url: 커스텀 아바타 이미지 URL
            
        Returns:
            생성된 영상의 다운로드 URL 또는 None
        """
        try:
            # 텍스트 길이 검증
            if not script or len(script.strip()) < 10:
                logger.error(f"텍스트가 너무 짧습니다: {len(script)} 글자")
                return None
            
            if len(script) > 500:
                logger.warning(f"텍스트가 길어서 처리 시간이 오래 걸릴 수 있습니다: {len(script)} 글자")
                # 너무 긴 텍스트는 잘라서 처리
                script = script[:500] + "..."
            
            # 아바탄 이미지 URL 결정
            source_url = custom_avatar_url or self.default_avatars.get(avatar_type, self.default_avatars['interviewer_male'])
            
            # 용도와 성별에 따른 최적 한국어 음성 선택
            voice_id = self.voice_mapping.get(avatar_type)
            if not voice_id:
                # 폴백: 기본 음성 사용
                gender = 'female' if 'female' in avatar_type else 'male'
                voice_id = self.korean_voices[gender]
            
            # D-ID API 요청 데이터 - 공식 문서 형식에 정확히 맞춤
            data = {
                "source_url": source_url,
                "script": {
                    "type": "text",
                    "input": script,
                    "provider": {
                        "type": "microsoft",
                        "voice_id": voice_id
                    }
                },
                "config": {
                    "fluent": False,  # boolean 값으로 수정
                    "result_format": "mp4"
                }
            }
            
            logger.info(f"🎬 D-ID 영상 생성 시작")
            logger.info(f"   📝 스크립트: {script[:50]}{'...' if len(script) > 50 else ''}")
            logger.info(f"   👤 아바타: {avatar_type}")
            logger.info(f"   🔊 D-ID TTS 음성: {voice_id}")
            logger.info(f"   📄 텍스트 길이: {len(script)} 글자")
            
            # 영상 생성 요청
            response = requests.post(
                f"{self.base_url}/talks",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            logger.info(f"D-ID API 응답 코드: {response.status_code}")
            
            # 응답 처리
            if response.status_code == 201:
                result = response.json()
                talk_id = result.get('id')
                
                if not talk_id:
                    logger.error("D-ID 응답에서 talk_id를 찾을 수 없음")
                    return None
                
                logger.info(f"D-ID 영상 생성 작업 시작: talk_id={talk_id}")
                
                # 영상 생성 완료 대기
                video_url = self._wait_for_video_completion(talk_id)
                
                if video_url:
                    logger.info(f"D-ID 영상 생성 완료: {video_url[:50]}...")
                    return video_url
                else:
                    logger.error(f"D-ID 영상 생성 실패: talk_id={talk_id}")
                    return None
                    
            elif response.status_code == 401:
                logger.error("D-ID API 인증 실패 (401)")
                logger.error(f"사용된 API 키: {self.api_key[:20]}...{self.api_key[-10:]}")
                logger.error(f"응답: {response.text}")
                return None
                
            elif response.status_code == 400:
                logger.error("D-ID 잘못된 요청 (400)")
                logger.error(f"요청 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
                logger.error(f"응답: {response.text}")
                return None
                
            elif response.status_code == 402:
                logger.error("D-ID 크레딧 부족 (402)")
                logger.error("D-ID 계정의 크레딧을 확인하세요")
                return None
                
            elif response.status_code == 429:
                logger.error("D-ID 요청 한도 초과 (429)")
                logger.error("잠시 후 다시 시도하세요")
                return None
                
            else:
                logger.error(f"D-ID 영상 생성 요청 실패: {response.status_code}")
                logger.error(f"응답 내용: {response.text}")
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
        check_interval = 5  # 5초마다 확인
        
        logger.info(f"D-ID 영상 생성 대기 중...")
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(
                    f"{self.base_url}/talks/{talk_id}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.warning(f"⚠️ 영상 상태 확인 실패: {response.status_code}")
                    time.sleep(check_interval)
                    continue
                
                result = response.json()
                status = result.get('status')
                elapsed_time = int(time.time() - start_time)
                
                logger.info(f"D-ID 영상 생성 상태: {status} (경과: {elapsed_time}초)")
                
                if status == 'done':
                    video_url = result.get('result_url')
                    duration = result.get('duration', 0)
                    
                    logger.info(f"D-ID 영상 생성 완료!")
                    logger.info(f"   ⏱영상 길이: {duration}초")
                    logger.info(f"   생성 시간: {elapsed_time}초")
                    
                    # 영상 길이가 0인 경우 상세 로그
                    if duration == 0:
                        logger.error("⚠️ 영상 길이가 0초입니다!")
                        logger.error(f"결과 세부사항: {json.dumps(result, ensure_ascii=False, indent=2)}")
                        
                        # 메타데이터 확인
                        metadata = result.get('metadata', {})
                        logger.error(f"메타데이터:")
                        logger.error(f"   - 프레임 수: {metadata.get('num_frames', 'N/A')}")
                        logger.error(f"   - 해상도: {metadata.get('resolution', 'N/A')}")
                        logger.error(f"   - 파일 크기: {metadata.get('size_kib', 'N/A')} KB")
                        
                        # 가능한 원인 분석
                        if metadata.get('num_frames', 0) == 0:
                            logger.error("프레임이 생성되지 않음 - 텍스트나 음성 처리 실패")
                        elif metadata.get('size_kib', 0) < 10:
                            logger.error("파일 크기가 너무 작음 - 처리 실패")
                        
                    if video_url:
                        return video_url
                    else:
                        logger.error("완료된 영상의 URL을 찾을 수 없음")
                        return None
                        
                elif status == 'error':
                    error_details = result.get('error', {})
                    error_msg = error_details.get('description', 'Unknown error')
                    error_type = error_details.get('kind', 'Unknown type')
                    
                    logger.error(f"D-ID 영상 생성 오류: {error_type}")
                    logger.error(f"   오류 메시지: {error_msg}")
                    logger.error(f"   전체 응답: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    # 특정 에러 타입별 안내
                    if 'credit' in error_msg.lower():
                        logger.error("해결방법: D-ID 계정에서 크레딧을 충전하세요")
                    elif 'quota' in error_msg.lower():
                        logger.error("해결방법: 요청 한도를 확인하고 잠시 후 재시도하세요")
                    elif 'voice' in error_msg.lower():
                        logger.error(f"해결방법: voice_id '{self.korean_voices}' 확인 필요")
                    elif 'source' in error_msg.lower():
                        logger.error("해결방법: 아바타 이미지 URL을 확인하세요")
                    
                    return None
                    
                elif status in ['created', 'started']:
                    # 아직 진행 중
                    if status == 'started':
                        logger.info("영상 처리 중...")
                    time.sleep(check_interval)
                    continue
                else:
                    logger.warning(f"⚠️ 알 수 없는 상태: {status}")
                    time.sleep(check_interval)
                    continue
                    
            except Exception as e:
                logger.error(f"영상 상태 확인 중 오류: {str(e)}")
                time.sleep(check_interval)
                continue
        
        logger.error(f"영상 생성 시간 초과: {max_wait_time}초")
        logger.error("해결방법:")
        logger.error("  1. 텍스트 길이를 줄여보세요 (현재 최대 500자)")
        logger.error("  2. D-ID 서비스 상태를 확인하세요")
        logger.error("  3. 네트워크 연결을 확인하세요")
        logger.error("  4. API 크레딧을 확인하세요")
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
            logger.info(f"영상 다운로드 시작: {save_path}")
            
            response = requests.get(video_url, timeout=120)  # 다운로드 시간 증가
            
            if response.status_code == 200:
                # 디렉토리 생성
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                # 파일 크기 확인
                file_size = os.path.getsize(save_path)
                logger.info(f"영상 다운로드 완료: {save_path}")
                logger.info(f"   파일 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                # 파일 크기 검증
                if file_size == 0:
                    logger.error("다운로드된 파일이 0바이트입니다!")
                    return False
                elif file_size < 1000:  # 1KB 미만
                    logger.warning(f"영상 파일이 매우 작습니다: {file_size} bytes")
                    logger.warning("이는 영상 생성 실패를 의미할 수 있습니다")
                
                return True
            else:
                logger.error(f"영상 다운로드 실패: HTTP {response.status_code}")
                logger.error(f"응답: {response.text[:200]}")
                return False
                
        except Exception as e:
            logger.error(f"영상 다운로드 중 오류: {str(e)}")
            return False
    
    def generate_interview_video(self, question_text: str, interviewer_gender: str = 'male') -> Optional[str]:
        """
        면접관 영상 생성 - D-ID 자체 TTS 사용
        
        Args:
            question_text: 면접 질문 텍스트
            interviewer_gender: 면접관 성별 ('male' 또는 'female')
            
        Returns:
            생성된 영상 파일 경로 또는 None
        """
        try:
            # 면접관 아바타 설정
            avatar_type = f'interviewer_{interviewer_gender}'
            
            # 면접관 톤으로 텍스트 가공 (중복 인사말 방지)
            interview_script = question_text
            
            logger.info(f"🎤 면접관 영상 생성: {avatar_type}")
            logger.info(f"   🔊 TTS: {self.voice_mapping.get(avatar_type, self.korean_voices[interviewer_gender])}")
            
            # 영상 생성 (D-ID 자체 TTS 사용)
            video_url = self.create_avatar_video(
                script=interview_script,
                avatar_type=avatar_type
            )
            
            if not video_url:
                return None
            
            # 영상 다운로드
            timestamp = int(time.time())
            filename = f"interview_{interviewer_gender}_{timestamp}.mp4"
            save_path = os.path.join('videos', 'interviews', filename)
            
            if self.download_video(video_url, save_path):
                logger.info(f"✅ 면접관 영상 생성 완료: {save_path}")
                return save_path
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ 면접관 영상 생성 중 오류: {str(e)}")
            return None
    
    def generate_debate_video(self, debate_text: str, debater_gender: str = 'male', debate_phase: str = 'opening') -> Optional[str]:
        """
        토론자 영상 생성 - D-ID 자체 TTS 사용
        
        Args:
            debate_text: 토론 텍스트
            debater_gender: 토론자 성별 ('male' 또는 'female')
            debate_phase: 토론 단계 ('opening', 'rebuttal', 'counter_rebuttal', 'closing')
            
        Returns:
            생성된 영상 파일 경로 또는 None
        """
        try:
            # 토론자 아바타 설정
            avatar_type = f'debater_{debater_gender}'
            
            # 토론 단계에 맞는 톤으로 텍스트 가공
            if debate_phase == 'opening':
                debate_script = debate_text
            elif debate_phase == 'rebuttal':
                debate_script = f"{debate_text}"
            elif debate_phase == 'counter_rebuttal':
                debate_script = f"{debate_text}"
            elif debate_phase == 'closing':
                debate_script = f"{debate_text}"
            else:
                debate_script = debate_text
            
            logger.info(f"🎤 토론자 영상 생성: {avatar_type} ({debate_phase})")
            logger.info(f"   🔊 TTS: {self.voice_mapping.get(avatar_type, self.korean_voices[debater_gender])}")
            
            # 영상 생성 (D-ID 자체 TTS 사용)
            video_url = self.create_avatar_video(
                script=debate_script,
                avatar_type=avatar_type
            )
            
            if not video_url:
                return None
            
            # 영상 다운로드
            timestamp = int(time.time())
            filename = f"debate_{debate_phase}_{debater_gender}_{timestamp}.mp4"
            save_path = os.path.join('videos', 'debates', filename)
            
            if self.download_video(video_url, save_path):
                logger.info(f"✅ 토론자 영상 생성 완료: {save_path}")
                return save_path
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ 토론자 영상 생성 중 오류: {str(e)}")
            return None