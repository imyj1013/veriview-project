"""
토론면접용 LLM 통합 모듈
OpenFace 및 Librosa 분석 결과를 활용하여 LLM과 상호작용
"""
import logging
import json
import time
from typing import Dict, Any, List, Optional
import asyncio

# LLM 클라이언트 임포트 (예시 - 실제 사용할 LLM에 따라 변경)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)

class DebateLLMModule:
    def __init__(self, llm_provider="openai", api_key=None, model="gpt-4"):
        """토론면접용 LLM 모듈 초기화"""
        self.llm_provider = llm_provider.lower()
        self.model = model
        self.api_key = api_key
        self.client = None
        self.is_available = False
        
        self._initialize_llm_client()
        
        # 토론 컨텍스트 관리
        self.debate_context = {
            "topic": "",
            "position": "",
            "phase_history": [],
            "participant_profile": {},
            "performance_tracking": {}
        }
        
        logger.info(f"토론 LLM 모듈 초기화 - 제공자: {self.llm_provider}, 사용 가능: {self.is_available}")

    def _initialize_llm_client(self):
        """LLM 클라이언트 초기화"""
        try:
            if self.llm_provider == "openai" and OPENAI_AVAILABLE:
                if self.api_key:
                    openai.api_key = self.api_key
                self.client = openai
                self.is_available = True
                logger.info("OpenAI 클라이언트 초기화 완료")
                
            elif self.llm_provider == "anthropic" and ANTHROPIC_AVAILABLE:
                if self.api_key:
                    self.client = anthropic.Anthropic(api_key=self.api_key)
                    self.is_available = True
                    logger.info("Anthropic 클라이언트 초기화 완료")
                
            else:
                logger.warning(f"지원되지 않는 LLM 제공자 또는 라이브러리 없음: {self.llm_provider}")
                self.is_available = False
                
        except Exception as e:
            logger.error(f"LLM 클라이언트 초기화 실패: {str(e)}")
            self.is_available = False

    def initialize_debate_context(self, topic: str, position: str = "PRO", participant_info: Dict = None):
        """토론 컨텍스트 초기화"""
        self.debate_context = {
            "topic": topic,
            "position": position,
            "phase_history": [],
            "participant_profile": participant_info or {},
            "performance_tracking": {
                "overall_scores": {},
                "phase_performances": {},
                "improvement_areas": []
            }
        }
        logger.info(f"토론 컨텍스트 초기화 - 주제: {topic}, 입장: {position}")

    def generate_ai_opening(self, topic: str, position: str = "CON", context: Dict = None) -> Dict[str, Any]:
        """AI 입론 생성"""
        if not self.is_available:
            return self._get_fallback_response("opening", topic)
        
        try:
            prompt = self._create_opening_prompt(topic, position, context)
            response = self._call_llm(prompt)
            
            result = {
                "phase": "opening",
                "topic": topic,
                "position": position,
                "ai_response": response,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "reasoning": self._extract_reasoning_from_response(response)
            }
            
            # 컨텍스트 업데이트
            self.debate_context["phase_history"].append(result)
            
            logger.info(f"AI 입론 생성 완료 - 길이: {len(response)}")
            return result
            
        except Exception as e:
            logger.error(f"AI 입론 생성 오류: {str(e)}")
            return self._get_fallback_response("opening", topic)

    def analyze_user_response_and_generate_rebuttal(self, user_transcription: str, 
                                                   facial_analysis: Dict, 
                                                   audio_analysis: Dict,
                                                   debate_phase: str = "rebuttal") -> Dict[str, Any]:
        """사용자 응답 분석 및 반박 생성"""
        if not self.is_available:
            return self._get_fallback_response(debate_phase, "")
        
        try:
            # 다중 모달 분석 데이터 통합
            integrated_analysis = self._integrate_multimodal_data(
                user_transcription, facial_analysis, audio_analysis
            )
            
            # LLM 프롬프트 생성
            prompt = self._create_rebuttal_prompt(
                user_transcription, integrated_analysis, debate_phase
            )
            
            # LLM 호출
            llm_response = self._call_llm(prompt)
            
            # 결과 구조화
            result = {
                "phase": debate_phase,
                "user_input": {
                    "transcription": user_transcription,
                    "facial_analysis_summary": self._summarize_facial_analysis(facial_analysis),
                    "audio_analysis_summary": self._summarize_audio_analysis(audio_analysis)
                },
                "ai_response": llm_response,
                "analysis_insights": integrated_analysis,
                "performance_feedback": self._generate_performance_feedback(integrated_analysis),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 컨텍스트 업데이트
            self.debate_context["phase_history"].append(result)
            self._update_performance_tracking(integrated_analysis)
            
            logger.info(f"사용자 응답 분석 및 {debate_phase} 생성 완료")
            return result
            
        except Exception as e:
            logger.error(f"사용자 응답 분석 오류: {str(e)}")
            return self._get_fallback_response(debate_phase, user_transcription)

    def generate_comprehensive_feedback(self, debate_summary: Dict) -> Dict[str, Any]:
        """종합적인 토론 피드백 생성"""
        if not self.is_available:
            return self._get_fallback_feedback()
        
        try:
            # 전체 토론 데이터 집계
            comprehensive_data = self._aggregate_debate_data()
            
            # 피드백 생성 프롬프트
            prompt = self._create_feedback_prompt(comprehensive_data, debate_summary)
            
            # LLM 호출
            feedback_response = self._call_llm(prompt)
            
            # 구조화된 피드백 생성
            result = {
                "overall_performance": self._extract_overall_score(feedback_response),
                "detailed_feedback": feedback_response,
                "strengths": self._extract_strengths(feedback_response),
                "improvement_areas": self._extract_improvements(feedback_response),
                "specific_recommendations": self._extract_recommendations(feedback_response),
                "phase_by_phase_analysis": self._analyze_phase_progression(),
                "nonverbal_communication_insights": self._summarize_nonverbal_insights(),
                "debate_strategy_evaluation": self._evaluate_debate_strategy(),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info("종합 토론 피드백 생성 완료")
            return result
            
        except Exception as e:
            logger.error(f"종합 피드백 생성 오류: {str(e)}")
            return self._get_fallback_feedback()

    def _integrate_multimodal_data(self, transcription: str, facial_data: Dict, audio_data: Dict) -> Dict[str, Any]:
        """다중 모달 데이터 통합"""
        integrated = {
            "content_analysis": {
                "text_length": len(transcription.split()),
                "key_arguments": self._extract_key_arguments(transcription),
                "logical_structure": self._analyze_logical_structure(transcription),
                "persuasiveness_indicators": self._detect_persuasive_elements(transcription)
            },
            "delivery_analysis": {
                "confidence_level": facial_data.get("llm_input_data", {}).get("participant_metrics", {}).get("overall_confidence", 0.5),
                "engagement_score": facial_data.get("llm_input_data", {}).get("participant_metrics", {}).get("engagement_score", 2.5),
                "emotional_state": facial_data.get("llm_input_data", {}).get("participant_metrics", {}).get("emotional_state", "중립"),
                "nonverbal_effectiveness": facial_data.get("llm_input_data", {}).get("participant_metrics", {}).get("nonverbal_effectiveness", 0.5)
            },
            "vocal_analysis": {
                "voice_stability": audio_data.get("voice_stability", 0.5),
                "speaking_pace": audio_data.get("speaking_rate_wpm", 120),
                "vocal_confidence": audio_data.get("volume_consistency", 0.5),
                "fluency_score": audio_data.get("fluency_score", 0.5)
            },
            "overall_coherence": self._calculate_multimodal_coherence(transcription, facial_data, audio_data)
        }
        
        return integrated

    def _create_opening_prompt(self, topic: str, position: str, context: Dict = None) -> str:
        """AI 입론 프롬프트 생성"""
        return f"""
당신은 숙련된 토론자입니다. 다음 주제에 대해 {position} 입장에서 설득력 있는 입론을 작성해주세요.

토론 주제: {topic}
입장: {position}
목표: 상대방을 설득하고 청중에게 강한 인상을 남기는 입론

다음 구조를 따라 작성해주세요:
1. 주제에 대한 명확한 입장 표명
2. 핵심 논거 2-3개 제시 (각각 구체적 근거 포함)
3. 상대방 예상 반박에 대한 예방적 대응
4. 강력한 결론으로 마무리

답변은 자연스럽고 설득력 있게 작성해주세요. 길이는 150-200단어 정도로 해주세요.
"""

    def _create_rebuttal_prompt(self, user_text: str, analysis: Dict, phase: str) -> str:
        """반박 프롬프트 생성"""
        confidence_level = analysis["delivery_analysis"]["confidence_level"]
        engagement_score = analysis["delivery_analysis"]["engagement_score"]
        key_arguments = analysis["content_analysis"]["key_arguments"]
        
        return f"""
당신은 토론에서 상대방의 주장에 대해 반박해야 합니다.

상대방의 주장:
"{user_text}"

상대방의 발표 분석:
- 자신감 수준: {confidence_level:.2f} (0-1 척도)
- 참여도: {engagement_score:.2f} (0-5 척도)
- 주요 논점: {', '.join(key_arguments)}

다음 사항을 고려하여 효과적인 반박을 작성해주세요:
1. 상대방 논리의 약점 지적
2. 반대 근거와 사례 제시
3. 상대방의 발표 태도나 논리적 허점 활용
4. 자신의 입장 강화

토론 단계: {phase}
답변 길이: 120-180단어
톤: 정중하되 확고함, 논리적이고 설득력 있게
"""

    def _create_feedback_prompt(self, debate_data: Dict, summary: Dict) -> str:
        """종합 피드백 프롬프트 생성"""
        return f"""
토론면접 전문가로서 참가자의 전체 토론 수행에 대해 종합적인 피드백을 제공해주세요.

토론 데이터:
{json.dumps(debate_data, ensure_ascii=False, indent=2)}

다음 항목들에 대해 구체적이고 건설적인 피드백을 제공해주세요:

1. 전반적 수행 평가 (10점 만점)
2. 주요 강점 3가지
3. 개선 필요 영역 3가지
4. 구체적 개선 방안
5. 비언어적 소통 분석
6. 토론 전략 평가
7. 향후 발전을 위한 권고사항

각 항목에 대해 구체적인 예시와 함께 설명해주세요.
피드백은 격려적이면서도 정확한 평가가 되도록 해주세요.
"""

    def _call_llm(self, prompt: str, max_tokens: int = 500) -> str:
        """LLM 호출"""
        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "당신은 전문적인 토론 코치이자 면접관입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
                
            elif self.llm_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text.strip()
                
        except Exception as e:
            logger.error(f"LLM 호출 오류: {str(e)}")
            raise

    def _extract_key_arguments(self, text: str) -> List[str]:
        """주요 논점 추출"""
        # 간단한 키워드 기반 논점 추출
        key_phrases = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(word in sentence.lower() for word in 
                                        ['때문에', '이유는', '근거는', '따라서', '그러므로']):
                key_phrases.append(sentence[:50] + "..." if len(sentence) > 50 else sentence)
        
        return key_phrases[:3]  # 최대 3개

    def _analyze_logical_structure(self, text: str) -> str:
        """논리적 구조 분석"""
        logical_indicators = ['첫째', '둘째', '셋째', '먼저', '다음으로', '마지막으로', '결론적으로']
        found_indicators = [ind for ind in logical_indicators if ind in text]
        
        if len(found_indicators) >= 3:
            return "체계적 구조"
        elif len(found_indicators) >= 1:
            return "부분적 구조"
        else:
            return "자유 형식"

    def _detect_persuasive_elements(self, text: str) -> List[str]:
        """설득 요소 감지"""
        persuasive_elements = []
        
        if any(word in text for word in ['예를 들어', '사례', '연구', '통계']):
            persuasive_elements.append("구체적 예시 활용")
        
        if any(word in text for word in ['반드시', '확실히', '명백히', '분명히']):
            persuasive_elements.append("강한 어조 사용")
        
        if any(word in text for word in ['우리', '함께', '모두']):
            persuasive_elements.append("공감대 형성")
        
        return persuasive_elements

    def _calculate_multimodal_coherence(self, text: str, facial: Dict, audio: Dict) -> float:
        """다중 모달 일관성 계산"""
        text_confidence = 0.7 if len(text.split()) > 50 else 0.4
        facial_confidence = facial.get("llm_input_data", {}).get("participant_metrics", {}).get("overall_confidence", 0.5)
        audio_confidence = audio.get("voice_stability", 0.5)
        
        return (text_confidence + facial_confidence + audio_confidence) / 3.0

    def _summarize_facial_analysis(self, facial_data: Dict) -> str:
        """얼굴 분석 요약"""
        if not facial_data:
            return "얼굴 분석 데이터 없음"
        
        metrics = facial_data.get("llm_input_data", {}).get("participant_metrics", {})
        confidence = metrics.get("overall_confidence", 0.5)
        emotional_state = metrics.get("emotional_state", "중립")
        eye_contact = metrics.get("eye_contact_quality", 0.5)
        
        return f"자신감: {confidence:.2f}, 감정상태: {emotional_state}, 아이컨택: {eye_contact:.2f}"

    def _summarize_audio_analysis(self, audio_data: Dict) -> str:
        """음성 분석 요약"""
        if not audio_data:
            return "음성 분석 데이터 없음"
        
        stability = audio_data.get("voice_stability", 0.5)
        pace = audio_data.get("speaking_rate_wpm", 120)
        fluency = audio_data.get("fluency_score", 0.5)
        
        return f"음성안정성: {stability:.2f}, 말하기속도: {pace}wpm, 유창성: {fluency:.2f}"

    def _generate_performance_feedback(self, analysis: Dict) -> Dict[str, Any]:
        """수행 피드백 생성"""
        return {
            "content_quality": "우수" if len(analysis["content_analysis"]["key_arguments"]) >= 2 else "보통",
            "delivery_effectiveness": "우수" if analysis["delivery_analysis"]["confidence_level"] > 0.7 else "보통",
            "overall_coherence": "우수" if analysis["overall_coherence"] > 0.7 else "보통"
        }

    def _update_performance_tracking(self, analysis: Dict):
        """성과 추적 업데이트"""
        phase_count = len(self.debate_context["phase_history"])
        
        self.debate_context["performance_tracking"]["phase_performances"][phase_count] = {
            "confidence": analysis["delivery_analysis"]["confidence_level"],
            "engagement": analysis["delivery_analysis"]["engagement_score"],
            "coherence": analysis["overall_coherence"]
        }

    def _aggregate_debate_data(self) -> Dict:
        """토론 데이터 집계"""
        return {
            "total_phases": len(self.debate_context["phase_history"]),
            "topic": self.debate_context["topic"],
            "position": self.debate_context["position"],
            "performance_trend": self.debate_context["performance_tracking"]["phase_performances"],
            "average_metrics": self._calculate_average_metrics()
        }

    def _calculate_average_metrics(self) -> Dict:
        """평균 메트릭 계산"""
        performances = self.debate_context["performance_tracking"]["phase_performances"]
        if not performances:
            return {"confidence": 0.5, "engagement": 2.5, "coherence": 0.5}
        
        confidences = [p["confidence"] for p in performances.values()]
        engagements = [p["engagement"] for p in performances.values()]
        coherences = [p["coherence"] for p in performances.values()]
        
        return {
            "confidence": sum(confidences) / len(confidences),
            "engagement": sum(engagements) / len(engagements),
            "coherence": sum(coherences) / len(coherences)
        }

    def _extract_overall_score(self, feedback: str) -> float:
        """전체 점수 추출"""
        # 간단한 패턴 매칭으로 점수 추출
        import re
        score_pattern = r'(\d+(?:\.\d+)?)\s*[점/10]'
        match = re.search(score_pattern, feedback)
        return float(match.group(1)) if match else 7.0

    def _extract_strengths(self, feedback: str) -> List[str]:
        """강점 추출"""
        # 간단한 패턴 매칭
        strengths = []
        lines = feedback.split('\n')
        in_strengths_section = False
        
        for line in lines:
            if '강점' in line or 'strengths' in line.lower():
                in_strengths_section = True
                continue
            elif in_strengths_section and line.strip():
                if line.strip().startswith(('1.', '2.', '3.', '-', '•')):
                    strengths.append(line.strip())
                elif '개선' in line or 'improvement' in line.lower():
                    break
        
        return strengths[:3]

    def _extract_improvements(self, feedback: str) -> List[str]:
        """개선사항 추출"""
        improvements = []
        lines = feedback.split('\n')
        in_improvements_section = False
        
        for line in lines:
            if '개선' in line or 'improvement' in line.lower():
                in_improvements_section = True
                continue
            elif in_improvements_section and line.strip():
                if line.strip().startswith(('1.', '2.', '3.', '-', '•')):
                    improvements.append(line.strip())
                elif '권고' in line or 'recommendation' in line.lower():
                    break
        
        return improvements[:3]

    def _extract_recommendations(self, feedback: str) -> List[str]:
        """권고사항 추출"""
        recommendations = []
        lines = feedback.split('\n')
        in_recommendations_section = False
        
        for line in lines:
            if '권고' in line or 'recommendation' in line.lower():
                in_recommendations_section = True
                continue
            elif in_recommendations_section and line.strip():
                if line.strip().startswith(('1.', '2.', '3.', '-', '•')):
                    recommendations.append(line.strip())
        
        return recommendations[:5]

    def _analyze_phase_progression(self) -> Dict:
        """단계별 진행 분석"""
        phases = self.debate_context["phase_history"]
        if len(phases) < 2:
            return {"trend": "insufficient_data"}
        
        # 간단한 트렌드 분석
        first_half = phases[:len(phases)//2]
        second_half = phases[len(phases)//2:]
        
        return {
            "trend": "improving" if len(second_half) > len(first_half) else "consistent",
            "total_phases": len(phases),
            "progression_notes": "토론 전반에 걸쳐 일관된 수행을 보임"
        }

    def _summarize_nonverbal_insights(self) -> Dict:
        """비언어적 통찰 요약"""
        return {
            "eye_contact": "적절한 아이컨택 유지",
            "facial_expressions": "자연스러운 표정 변화",
            "overall_presence": "안정적인 토론 태도"
        }

    def _evaluate_debate_strategy(self) -> Dict:
        """토론 전략 평가"""
        return {
            "argument_structure": "체계적인 논리 구성",
            "persuasion_techniques": "효과적인 설득 기법 사용",
            "adaptability": "상황에 따른 적절한 대응"
        }

    def _get_fallback_response(self, phase: str, topic: str = "") -> Dict[str, Any]:
        """LLM 사용 불가시 대체 응답"""
        fallback_responses = {
            "opening": f"안녕하세요. {topic}에 대해 말씀드리겠습니다. 이 주제는 현재 사회에서 중요한 이슈이며, 신중한 접근이 필요한 사안입니다.",
            "rebuttal": "상대방의 의견을 경청했습니다. 하지만 몇 가지 다른 관점에서 살펴볼 필요가 있다고 생각합니다.",
            "counter_rebuttal": "제기하신 점들을 고려했지만, 여전히 제 입장을 유지하는 이유가 있습니다.",
            "closing": "지금까지의 논의를 종합해보면, 제 입장이 더 타당하다고 생각합니다."
        }
        
        return {
            "phase": phase,
            "ai_response": fallback_responses.get(phase, "죄송합니다. 응답을 생성할 수 없습니다."),
            "is_fallback": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _get_fallback_feedback(self) -> Dict[str, Any]:
        """대체 피드백"""
        return {
            "overall_performance": 7.0,
            "detailed_feedback": "전반적으로 양호한 토론 수행을 보여주셨습니다. 논리적 구성과 표현력에서 좋은 모습을 보였습니다.",
            "strengths": ["명확한 의견 표현", "적절한 근거 제시", "안정적인 발표 태도"],
            "improvement_areas": ["더 구체적인 예시 활용", "상대방 논리에 대한 심화 분석", "감정적 호소력 강화"],
            "specific_recommendations": ["실제 사례 연구", "반박 기법 연습", "표현력 향상 훈련"],
            "is_fallback": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_module_status(self) -> Dict[str, Any]:
        """모듈 상태 반환"""
        return {
            "module_name": "Debate LLM Integration",
            "is_available": self.is_available,
            "llm_provider": self.llm_provider,
            "model": self.model,
            "features": [
                "ai_opening_generation",
                "multimodal_analysis_integration",
                "context_aware_rebuttal",
                "comprehensive_feedback",
                "performance_tracking"
            ],
            "current_context": {
                "topic": self.debate_context["topic"],
                "phases_completed": len(self.debate_context["phase_history"])
            }
        }
