#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 모듈 - 언어 모델 기반 AI 응답 생성
OpenAI GPT, Claude 등의 LLM을 사용한 토론 및 면접 응답 생성
"""
import logging
import time
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class LLMModule:
    def __init__(self, provider: str = "openai", model: str = "gpt-4"):
        """
        LLM 모듈 초기화
        
        Args:
            provider: LLM 제공자 (openai, anthropic, etc.)
            model: 사용할 모델명
        """
        self.provider = provider
        self.model = model
        self.client = None
        self.available = False
        
        try:
            self._initialize_client()
            self.available = True
            logger.info(f"LLM 모듈 초기화 성공: {provider} - {model}")
        except Exception as e:
            logger.error(f"LLM 모듈 초기화 실패: {str(e)}")
            self.available = False
    
    def _initialize_client(self):
        """LLM 클라이언트 초기화"""
        try:
            if self.provider.lower() == "openai":
                import openai
                # OpenAI API 키 설정이 필요합니다
                # openai.api_key = "your-api-key-here"
                self.client = openai
            elif self.provider.lower() == "anthropic":
                import anthropic
                # Anthropic API 키 설정이 필요합니다
                # self.client = anthropic.Anthropic(api_key="your-api-key-here")
                self.client = anthropic
            else:
                raise ValueError(f"지원하지 않는 LLM 제공자: {self.provider}")
                
        except ImportError as e:
            raise ImportError(f"LLM 라이브러리를 찾을 수 없습니다: {str(e)}")
    
    def is_available(self) -> bool:
        """LLM 모듈 사용 가능 여부 확인"""
        return self.available
    
    def generate_debate_opening(self, topic: str, position: str, context: Dict = None) -> Dict[str, Any]:
        """
        토론 입론 생성
        
        Args:
            topic: 토론 주제
            position: 찬성(PRO) 또는 반대(CON) 입장
            context: 추가 컨텍스트 정보
            
        Returns:
            Dict containing AI response and metadata
        """
        if not self.available:
            return {"error": "LLM 모듈을 사용할 수 없습니다."}
        
        try:
            prompt = self._create_debate_opening_prompt(topic, position, context)
            response = self._generate_response(prompt)
            
            return {
                "ai_response": response,
                "topic": topic,
                "position": position,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "reasoning": f"{topic}에 대한 {position} 입장의 논리적 근거를 제시했습니다."
            }
            
        except Exception as e:
            logger.error(f"토론 입론 생성 오류: {str(e)}")
            return {"error": f"입론 생성 실패: {str(e)}"}
    
    def generate_debate_response(self, stage: str, topic: str, user_text: str, 
                               facial_analysis: Dict = None, audio_analysis: Dict = None) -> Dict[str, Any]:
        """
        토론 단계별 AI 응답 생성
        
        Args:
            stage: 토론 단계 (rebuttal, counter_rebuttal, closing)
            topic: 토론 주제
            user_text: 사용자 발언 내용
            facial_analysis: 얼굴 분석 결과
            audio_analysis: 음성 분석 결과
            
        Returns:
            Dict containing AI response and analysis insights
        """
        if not self.available:
            return {"error": "LLM 모듈을 사용할 수 없습니다."}
        
        try:
            prompt = self._create_debate_response_prompt(stage, topic, user_text, 
                                                       facial_analysis, audio_analysis)
            response = self._generate_response(prompt)
            
            # 사용자 응답 분석 추가
            analysis_insights = self._analyze_user_response(user_text, facial_analysis, audio_analysis)
            
            return {
                "ai_response": response,
                "stage": stage,
                "topic": topic,
                "analysis_insights": analysis_insights,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"토론 응답 생성 오류: {str(e)}")
            return {"error": f"응답 생성 실패: {str(e)}"}
    
    def generate_interview_question(self, question_type: str, context: Dict = None) -> Dict[str, Any]:
        """
        면접 질문 생성
        
        Args:
            question_type: 질문 유형 (general, technical, behavioral, etc.)
            context: 면접자 정보 및 컨텍스트
            
        Returns:
            Dict containing generated question and metadata
        """
        if not self.available:
            return {"error": "LLM 모듈을 사용할 수 없습니다."}
        
        try:
            prompt = self._create_interview_question_prompt(question_type, context)
            response = self._generate_response(prompt)
            
            return {
                "question": response,
                "question_type": question_type,
                "difficulty": self._assess_question_difficulty(response),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"면접 질문 생성 오류: {str(e)}")
            return {"error": f"질문 생성 실패: {str(e)}"}
    
    def analyze_interview_answer(self, question: str, answer_text: str, 
                               facial_analysis: Dict = None, audio_analysis: Dict = None) -> Dict[str, Any]:
        """
        면접 답변 분석 및 피드백 생성
        
        Args:
            question: 면접 질문
            answer_text: 사용자 답변
            facial_analysis: 얼굴 분석 결과
            audio_analysis: 음성 분석 결과
            
        Returns:
            Dict containing analysis scores and feedback
        """
        if not self.available:
            return {"error": "LLM 모듈을 사용할 수 없습니다."}
        
        try:
            prompt = self._create_interview_analysis_prompt(question, answer_text, 
                                                          facial_analysis, audio_analysis)
            response = self._generate_response(prompt)
            
            # 구조화된 분석 결과 파싱
            analysis_result = self._parse_interview_analysis(response)
            
            return {
                "content_analysis": analysis_result.get("content_score", 3.5),
                "delivery_analysis": analysis_result.get("delivery_score", 3.5),
                "overall_feedback": analysis_result.get("feedback", "답변을 잘 해주셨습니다."),
                "improvement_suggestions": analysis_result.get("suggestions", []),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"면접 답변 분석 오류: {str(e)}")
            return {"error": f"답변 분석 실패: {str(e)}"}
    
    def _generate_response(self, prompt: str) -> str:
        """LLM 응답 생성"""
        try:
            if self.provider.lower() == "openai":
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
                
            elif self.provider.lower() == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
            
            else:
                return "LLM 응답을 생성할 수 없습니다."
                
        except Exception as e:
            logger.error(f"LLM 응답 생성 실패: {str(e)}")
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _create_debate_opening_prompt(self, topic: str, position: str, context: Dict = None) -> str:
        """토론 입론 프롬프트 생성"""
        base_prompt = f"""
다음 주제에 대해 {position} 입장에서 토론 입론을 작성해주세요.

주제: {topic}
입장: {position}

요구사항:
1. 명확하고 논리적인 주장 전개
2. 구체적인 근거와 예시 제시
3. 상대방 입장에 대한 예상 반박 고려
4. 2-3분 분량의 적절한 길이
5. 한국어로 작성

입론을 작성해주세요:
"""
        
        if context:
            base_prompt += f"\n추가 정보: {context}"
        
        return base_prompt
    
    def _create_debate_response_prompt(self, stage: str, topic: str, user_text: str,
                                     facial_analysis: Dict = None, audio_analysis: Dict = None) -> str:
        """토론 응답 프롬프트 생성"""
        stage_descriptions = {
            "rebuttal": "반론",
            "counter_rebuttal": "재반론", 
            "closing": "최종 변론"
        }
        
        stage_korean = stage_descriptions.get(stage, stage)
        
        prompt = f"""
토론 주제: {topic}
현재 단계: {stage_korean}

사용자의 발언:
{user_text}

위 발언에 대해 논리적이고 설득력 있는 {stage_korean}을 작성해주세요.

요구사항:
1. 사용자 발언의 핵심 포인트 파악 및 대응
2. 논리적 근거와 반박 제시
3. 새로운 관점이나 정보 추가
4. 2분 내외의 적절한 길이
5. 한국어로 작성

{stage_korean}:
"""
        
        if facial_analysis or audio_analysis:
            prompt += f"\n\n참고 정보:"
            if facial_analysis:
                prompt += f"\n- 얼굴 표정 분석: {facial_analysis.get('emotion', '중립')}"
            if audio_analysis:
                prompt += f"\n- 음성 분석: 안정성 {audio_analysis.get('voice_stability', 0.8):.1f}"
        
        return prompt
    
    def _create_interview_question_prompt(self, question_type: str, context: Dict = None) -> str:
        """면접 질문 생성 프롬프트"""
        type_descriptions = {
            "general": "일반적인 자기소개 및 경험",
            "technical": "기술적 역량 및 전문성",
            "behavioral": "행동 및 상황 대처",
            "fit": "회사 적합성 및 동기",
            "personality": "성격 및 개인적 특성"
        }
        
        question_guide = type_descriptions.get(question_type, "일반적인")
        
        prompt = f"""
{question_guide}에 관한 면접 질문을 하나 생성해주세요.

요구사항:
1. 구체적이고 명확한 질문
2. 응답자의 역량을 평가할 수 있는 내용
3. 너무 어렵지 않으면서도 의미있는 답변을 유도
4. 한국의 면접 문화에 적합
5. 한국어로 작성

질문:
"""
        
        if context:
            prompt += f"\n\n응답자 정보:\n"
            for key, value in context.items():
                if value:
                    prompt += f"- {key}: {value}\n"
        
        return prompt
    
    def _create_interview_analysis_prompt(self, question: str, answer_text: str,
                                        facial_analysis: Dict = None, audio_analysis: Dict = None) -> str:
        """면접 답변 분석 프롬프트"""
        prompt = f"""
다음 면접 질문과 답변을 분석하고 피드백을 제공해주세요.

질문: {question}

답변: {answer_text}

다음 항목들을 JSON 형태로 분석해주세요:
1. content_score (1-5): 내용의 충실도와 논리성
2. delivery_score (1-5): 전달력과 표현력
3. feedback: 전반적인 피드백 (2-3문장)
4. suggestions: 개선 제안사항 (리스트)

분석 결과를 JSON 형태로 작성해주세요:
"""
        
        if facial_analysis or audio_analysis:
            prompt += f"\n\n추가 분석 정보:"
            if facial_analysis:
                prompt += f"\n- 표정/자세: {facial_analysis.get('emotion', '안정적')}"
            if audio_analysis:
                prompt += f"\n- 음성 품질: 안정성 {audio_analysis.get('voice_stability', 0.8):.1f}, 유창성 {audio_analysis.get('fluency_score', 0.8):.1f}"
        
        return prompt
    
    def _analyze_user_response(self, user_text: str, facial_analysis: Dict = None, 
                             audio_analysis: Dict = None) -> Dict[str, Any]:
        """사용자 응답 종합 분석"""
        insights = {
            "text_length": len(user_text.split()) if user_text else 0,
            "confidence_level": "보통",
            "engagement_level": "보통",
            "key_points": []
        }
        
        # 텍스트 길이 기반 분석
        word_count = insights["text_length"]
        if word_count > 100:
            insights["engagement_level"] = "높음"
        elif word_count < 30:
            insights["engagement_level"] = "낮음"
        
        # 얼굴 분석 기반 신뢰도 평가
        if facial_analysis:
            confidence = facial_analysis.get("confidence", 0.5)
            if confidence > 0.8:
                insights["confidence_level"] = "높음"
            elif confidence < 0.5:
                insights["confidence_level"] = "낮음"
        
        # 주요 키워드 추출 (간단한 버전)
        if user_text:
            key_phrases = ["예를 들어", "구체적으로", "경험", "생각", "중요한"]
            for phrase in key_phrases:
                if phrase in user_text:
                    insights["key_points"].append(phrase)
        
        return insights
    
    def _assess_question_difficulty(self, question: str) -> str:
        """질문 난이도 평가"""
        complex_indicators = ["분석", "전략", "복잡한", "다각도", "심화"]
        basic_indicators = ["소개", "간단", "기본", "일반적"]
        
        if any(indicator in question for indicator in complex_indicators):
            return "높음"
        elif any(indicator in question for indicator in basic_indicators):
            return "낮음"
        else:
            return "보통"
    
    def _parse_interview_analysis(self, response: str) -> Dict[str, Any]:
        """면접 분석 응답 파싱"""
        try:
            # JSON 형태로 파싱 시도
            if "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # JSON이 아닌 경우 기본값 반환
                return {
                    "content_score": 3.5,
                    "delivery_score": 3.5,
                    "feedback": response[:200] if response else "분석 결과를 파싱할 수 없습니다.",
                    "suggestions": ["더 구체적인 예시 추가", "논리적 구조 개선"]
                }
        except Exception as e:
            logger.error(f"면접 분석 파싱 오류: {str(e)}")
            return {
                "content_score": 3.0,
                "delivery_score": 3.0,
                "feedback": "분석 중 오류가 발생했습니다.",
                "suggestions": []
            }

# 편의를 위한 함수들
def create_llm_module(provider: str = "openai", model: str = "gpt-4") -> LLMModule:
    """LLM 모듈 생성 팩토리 함수"""
    return LLMModule(provider, model)

def is_llm_available() -> bool:
    """LLM 모듈 사용 가능 여부 확인"""
    try:
        test_module = LLMModule()
        return test_module.is_available()
    except Exception:
        return False
