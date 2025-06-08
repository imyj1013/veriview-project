#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS 관리 모듈
한국어 음성 합성 지원
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class TTSManager:
    """TTS 음성 관리 클래스"""
    
    def __init__(self):
        """TTS 관리자 초기화"""
        # 한국어 음성 목록 (Microsoft Azure TTS)
        self.korean_voices = {
            # 여성 음성
            'female_1': 'ko-KR-SunHiNeural',     # 선희 (표준 여성)
            'female_2': 'ko-KR-JiMinNeural',     # 지민 (밝은 여성)
            'female_3': 'ko-KR-SeoHyeonNeural',  # 서현 (친근한 여성)
            
            # 남성 음성
            'male_1': 'ko-KR-InJoonNeural',      # 인준 (표준 남성)
            'male_2': 'ko-KR-BongJinNeural',     # 봉진 (안정감 있는 남성)
            'male_3': 'ko-KR-GookMinNeural',     # 국민 (친근한 남성)
        }
        
        # 면접관용 음성 매핑
        self.interviewer_voices = {
            'male': 'ko-KR-InJoonNeural',        # 신뢰감 있는 남성
            'female': 'ko-KR-SunHiNeural'       # 전문적인 여성
        }
        
        # 토론자용 음성 매핑
        self.debater_voices = {
            'male': 'ko-KR-BongJinNeural',       # 설득력 있는 남성
            'female': 'ko-KR-JiMinNeural'       # 역동적인 여성
        }
        
        logger.info("TTS 관리자 초기화 완료 - 한국어 음성 지원")
    
    def get_voice_for_interviewer(self, gender: str = 'male') -> str:
        """
        면접관용 음성 ID 반환
        
        Args:
            gender: 성별 ('male' 또는 'female')
            
        Returns:
            음성 ID
        """
        return self.interviewer_voices.get(gender, self.interviewer_voices['male'])
    
    def get_voice_for_debater(self, gender: str = 'male') -> str:
        """
        토론자용 음성 ID 반환
        
        Args:
            gender: 성별 ('male' 또는 'female')
            
        Returns:
            음성 ID
        """
        return self.debater_voices.get(gender, self.debater_voices['male'])
    
    def get_available_voices(self) -> Dict[str, str]:
        """사용 가능한 한국어 음성 목록 반환"""
        return self.korean_voices.copy()
    
    def format_script_for_interview(self, question_text: str) -> str:
        """
        면접 질문을 자연스러운 음성으로 변환하기 위한 텍스트 포맷팅
        
        Args:
            question_text: 원본 질문 텍스트
            
        Returns:
            포맷팅된 텍스트
        """
        # 면접관 톤으로 조정
        if not question_text.endswith(('?', '.', '요', '까', '세요')):
            question_text += '?'
        
        # 자연스러운 면접관 멘트 추가
        formatted_script = f"안녕하세요. 면접에 참여해 주셔서 감사합니다. {question_text}"
        
        # SSML 태그 추가 (자연스러운 억양)
        ssml_script = f'<speak><prosody rate="0.9" pitch="+5%">{formatted_script}</prosody></speak>'
        
        return formatted_script  # D-ID는 일반 텍스트 사용
    
    def format_script_for_debate(self, debate_text: str, phase: str = 'opening') -> str:
        """
        토론 텍스트를 자연스러운 음성으로 변환하기 위한 텍스트 포맷팅
        
        Args:
            debate_text: 원본 토론 텍스트
            phase: 토론 단계 ('opening', 'rebuttal', 'counter_rebuttal', 'closing')
            
        Returns:
            포맷팅된 텍스트
        """
        # 토론 단계별 인사말
        phase_greetings = {
            'opening': '안녕하세요. 저는 다음과 같이 주장하겠습니다.',
            'rebuttal': '상대측 주장에 대해 반박하겠습니다.',
            'counter_rebuttal': '추가로 반박 논리를 제시하겠습니다.',
            'closing': '마지막으로 정리하자면 다음과 같습니다.'
        }
        
        greeting = phase_greetings.get(phase, '다음과 같이 말씀드리겠습니다.')
        
        # 토론자 톤으로 조정
        formatted_script = f"{greeting} {debate_text}"
        
        return formatted_script
    
    def validate_script_length(self, script: str) -> bool:
        """
        스크립트 길이 검증 (D-ID 제한사항 고려)
        
        Args:
            script: 검증할 스크립트
            
        Returns:
            유효성 여부
        """
        # D-ID는 일반적으로 최대 500자 정도 권장
        if len(script) > 500:
            logger.warning(f"스크립트가 너무 깁니다: {len(script)}자 (권장: 500자 이하)")
            return False
        
        if len(script.strip()) == 0:
            logger.warning("빈 스크립트입니다")
            return False
        
        return True
    
    def optimize_script_for_speech(self, script: str) -> str:
        """
        음성 합성에 최적화된 스크립트로 변환
        
        Args:
            script: 원본 스크립트
            
        Returns:
            최적화된 스크립트
        """
        # 숫자를 한글로 변환
        import re
        
        # 간단한 숫자 변환 (1-10)
        number_mapping = {
            '1': '일', '2': '이', '3': '삼', '4': '사', '5': '오',
            '6': '육', '7': '칠', '8': '팔', '9': '구', '10': '십'
        }
        
        optimized = script
        for num, hangul in number_mapping.items():
            optimized = re.sub(rf'\b{num}\b', hangul, optimized)
        
        # 특수 문자 정리
        optimized = re.sub(r'[^\w\s가-힣.,!?]', ' ', optimized)
        
        # 연속 공백 제거
        optimized = re.sub(r'\s+', ' ', optimized).strip()
        
        return optimized
