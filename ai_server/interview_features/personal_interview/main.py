"""
개인면접을 위한 LLM 통합 모듈 (실제 AI 모듈)
OpenFace, Librosa, Whisper와 함께 LLM을 활용한 개인면접 시스템
"""
import logging
import json
import time
from typing import Dict, Any, List, Optional
import asyncio

# LLM 클라이언트 임포트
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

class PersonalInterviewLLMModule:
    def __init__(self, llm_provider="openai", api_key=None, model="gpt-4"):
        """개인면접용 LLM 모듈 초기화"""
        self.llm_provider = llm_provider.lower()
        self.model = model
        self.api_key = api_key
        self.client = None
        self.is_available = False
        
        self._initialize_llm_client()
        
        # 면접 컨텍스트 관리
        self.interview_context = {
            "interview_id": None,
            "participant_profile": {},
            "questions_asked": [],
            "answers_given": [],
            "performance_tracking": {}
        }
        
        logger.info(f"개인면접 LLM 모듈 초기화 - 제공자: {self.llm_provider}, 사용 가능: {self.is_available}")

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

    def initialize_interview_context(self, interview_id: int, participant_info: Dict = None):
        """면접 컨텍스트 초기화"""
        self.interview_context = {
            "interview_id": interview_id,
            "participant_profile": participant_info or {},
            "questions_asked": [],
            "answers_given": [],
            "performance_tracking": {
                "overall_scores": {},
                "question_performances": {},
                "improvement_areas": []
            },
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        logger.info(f"개인면접 컨텍스트 초기화 - ID: {interview_id}")

    def generate_personalized_question(self, question_type: str = "general", 
                                     participant_profile: Dict = None) -> Dict[str, Any]:
        """개인화된 면접 질문 생성"""
        if not self.is_available:
            return self._get_fallback_question(question_type)
        
        try:
            # 참가자 프로필 기반 맞춤 질문 생성
            profile = participant_profile or self.interview_context.get("participant_profile", {})
            
            prompt = self._create_question_prompt(question_type, profile)
            response = self._call_llm(prompt)
            
            result = {
                "question_type": question_type,
                "question": response,
                "generated_by": "llm",
                "personalized": bool(profile),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "context_used": list(profile.keys()) if profile else []
            }
            
            # 컨텍스트 업데이트
            self.interview_context["questions_asked"].append(result)
            
            logger.info(f"개인화된 질문 생성 완료 - 유형: {question_type}")
            return result
            
        except Exception as e:
            logger.error(f"개인화된 질문 생성 오류: {str(e)}")
            return self._get_fallback_question(question_type)

    def analyze_answer_and_generate_followup(self, user_transcription: str,
                                           facial_analysis: Dict,
                                           audio_analysis: Dict,
                                           question_context: Dict) -> Dict[str, Any]:
        """답변 분석 및 후속 질문 생성"""
        if not self.is_available:
            return self._get_fallback_analysis_and_followup(user_transcription)
        
        try:
            # 다중 모달 분석 데이터 통합
            integrated_analysis = self._integrate_multimodal_analysis(
                user_transcription, facial_analysis, audio_analysis
            )
            
            # LLM 기반 답변 분석 및 후속 질문 생성
            analysis_prompt = self._create_analysis_prompt(
                user_transcription, integrated_analysis, question_context
            )
            followup_prompt = self._create_followup_prompt(
                user_transcription, integrated_analysis, question_context
            )
            
            # 병렬로 분석과 후속 질문 생성
            analysis_response = self._call_llm(analysis_prompt)
            followup_response = self._call_llm(followup_prompt)
            
            # 결과 구조화
            result = {
                "answer_analysis": {
                    "transcription": user_transcription,
                    "llm_analysis": analysis_response,
                    "multimodal_insights": integrated_analysis,
                    "content_quality": self._evaluate_content_quality(user_transcription, analysis_response),
                    "delivery_quality": self._evaluate_delivery_quality(facial_analysis, audio_analysis)
                },
                "followup_question": {
                    "question": followup_response,
                    "question_type": "followup",
                    "based_on_answer": user_transcription[:100] + "..." if len(user_transcription) > 100 else user_transcription
                },
                "performance_metrics": self._calculate_performance_metrics(integrated_analysis),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 컨텍스트 업데이트
            self.interview_context["answers_given"].append(result)
            self._update_performance_tracking(result["performance_metrics"])
            
            logger.info("답변 분석 및 후속 질문 생성 완료")
            return result
            
        except Exception as e:
            logger.error(f"답변 분석 오류: {str(e)}")
            return self._get_fallback_analysis_and_followup(user_transcription)

    def generate_comprehensive_feedback(self, interview_summary: Dict) -> Dict[str, Any]:
        """종합적인 면접 피드백 생성"""
        if not self.is_available:
            return self._get_fallback_comprehensive_feedback()
        
        try:
            # 전체 면접 데이터 집계
            comprehensive_data = self._aggregate_interview_data()
            
            # 종합 피드백 생성 프롬프트
            prompt = self._create_comprehensive_feedback_prompt(comprehensive_data, interview_summary)
            
            # LLM 호출
            feedback_response = self._call_llm(prompt, max_tokens=800)
            
            # 구조화된 피드백 생성
            result = {
                "overall_performance": self._extract_overall_performance(feedback_response),
                "detailed_feedback": feedback_response,
                "category_scores": self._calculate_category_scores(),
                "strengths": self._extract_strengths_from_feedback(feedback_response),
                "improvement_areas": self._extract_improvements_from_feedback(feedback_response),
                "specific_recommendations": self._extract_recommendations_from_feedback(feedback_response),
                "question_by_question_analysis": self._analyze_question_progression(),
                "communication_insights": self._summarize_communication_insights(),
                "career_guidance": self._generate_career_guidance(comprehensive_data),
                "overall_score": self._calculate_overall_interview_score(),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info("종합 면접 피드백 생성 완료")
            return result
            
        except Exception as e:
            logger.error(f"종합 피드백 생성 오류: {str(e)}")
            return self._get_fallback_comprehensive_feedback()

    def _integrate_multimodal_analysis(self, transcription: str, facial_data: Dict, audio_data: Dict) -> Dict[str, Any]:
        """다중 모달 데이터 통합 분석"""
        integrated = {
            "content_analysis": {
                "word_count": len(transcription.split()),
                "sentence_count": len([s for s in transcription.split('.') if s.strip()]),
                "key_concepts": self._extract_key_concepts(transcription),
                "complexity_score": self._calculate_text_complexity(transcription),
                "coherence_score": self._calculate_coherence(transcription)
            },
            "delivery_analysis": {
                "confidence_indicators": facial_data.get("confidence", 0.5),
                "emotional_state": facial_data.get("emotion", "중립"),
                "eye_contact_quality": facial_data.get("gaze_stability", 0.5),
                "facial_expressiveness": facial_data.get("expression_variety", 0.5)
            },
            "vocal_analysis": {
                "speech_clarity": audio_data.get("voice_stability", 0.5),
                "speaking_pace": audio_data.get("speaking_rate_wpm", 120),
                "volume_consistency": audio_data.get("volume_consistency", 0.5),
                "fluency_indicators": audio_data.get("fluency_score", 0.5)
            },
            "overall_coherence": self._calculate_multimodal_coherence(transcription, facial_data, audio_data)
        }
        return integrated

    def _create_question_prompt(self, question_type: str, profile: Dict) -> str:
        """질문 생성 프롬프트 생성"""
        profile_info = ""
        if profile:
            profile_info = f"""
참가자 정보:
- 전공: {profile.get('major', '정보 없음')}
- 경력: {profile.get('workexperience', '정보 없음')}
- 관심 기술: {profile.get('tech_stack', '정보 없음')}
- 성격: {profile.get('personality', '정보 없음')}
"""
        
        type_descriptions = {
            "general": "일반적인 인성 및 적성을 파악하는 질문",
            "technical": "전문 기술 지식과 실무 능력을 평가하는 질문",
            "behavioral": "과거 경험을 통해 행동 패턴을 파악하는 질문",
            "situational": "가상 상황에서의 판단력과 문제해결 능력을 보는 질문"
        }
        
        return f"""
당신은 경험이 풍부한 면접관입니다. 다음 조건에 맞는 면접 질문을 하나 생성해주세요.

질문 유형: {question_type} - {type_descriptions.get(question_type, '일반 질문')}
{profile_info}

요구사항:
1. 참가자의 배경을 고려한 개인화된 질문
2. 구체적이고 답변하기 명확한 질문
3. 해당 유형에 적합한 평가 요소 포함
4. 자연스럽고 친근한 톤

답변은 질문만 작성해주세요. 추가 설명은 불필요합니다.
"""

    def _create_analysis_prompt(self, user_text: str, analysis: Dict, question_context: Dict) -> str:
        """답변 분석 프롬프트 생성"""
        multimodal_summary = f"""
답변 내용: "{user_text}"

전달 방식 분석:
- 자신감 수준: {analysis['delivery_analysis']['confidence_indicators']:.2f}
- 감정 상태: {analysis['delivery_analysis']['emotional_state']}
- 음성 명료도: {analysis['vocal_analysis']['speech_clarity']:.2f}
- 말하기 속도: {analysis['vocal_analysis']['speaking_pace']}wpm

내용 분석:
- 단어 수: {analysis['content_analysis']['word_count']}
- 복잡도: {analysis['content_analysis']['complexity_score']:.2f}
- 일관성: {analysis['content_analysis']['coherence_score']:.2f}
"""
        
        return f"""
면접 전문가로서 다음 답변을 종합적으로 분석해주세요.

{multimodal_summary}

분석 요소:
1. 내용의 적절성과 완성도
2. 논리적 구성과 일관성
3. 구체성과 예시 활용
4. 전달력과 설득력
5. 전문성과 통찰력

각 요소에 대해 객관적이고 건설적인 평가를 제공하고, 
강점과 개선점을 균형있게 제시해주세요.

평가는 격려적이면서도 정확한 피드백이 되도록 작성해주세요.
"""

    def _create_followup_prompt(self, user_text: str, analysis: Dict, question_context: Dict) -> str:
        """후속 질문 생성 프롬프트"""
        return f"""
면접관으로서 다음 답변에 기반하여 적절한 후속 질문을 생성해주세요.

참가자의 답변: "{user_text}"

답변 특성:
- 내용 깊이: {analysis['content_analysis']['complexity_score']:.2f}
- 구체성: {"높음" if analysis['content_analysis']['word_count'] > 80 else "보통"}
- 핵심 개념: {', '.join(analysis['content_analysis']['key_concepts'][:3])}

후속 질문 생성 기준:
1. 답변에서 더 깊이 탐색할 만한 부분 식별
2. 구체적인 경험이나 사례 요청
3. 비슷한 상황에서의 다른 접근법 질문
4. 학습한 교훈이나 성장 과정 탐구

자연스럽고 대화형식의 후속 질문 하나만 생성해주세요.
"""

    def _create_comprehensive_feedback_prompt(self, comprehensive_data: Dict, summary: Dict) -> str:
        """종합 피드백 프롬프트 생성"""
        return f"""
면접 전문가로서 전체 면접에 대한 종합적인 피드백을 제공해주세요.

면접 데이터:
{json.dumps(comprehensive_data, ensure_ascii=False, indent=2)}

다음 항목들에 대해 체계적인 피드백을 제공해주세요:

1. 전반적인 면접 수행 평가 (5점 만점)
2. 주요 강점 3가지 (구체적 예시 포함)
3. 개선이 필요한 영역 3가지 (개선 방법 제시)
4. 의사소통 능력 평가
5. 전문성 및 역량 평가
6. 면접 태도 및 인상 평가
7. 향후 발전을 위한 구체적 조언

피드백은 건설적이고 격려적이며, 실행 가능한 개선 방안을 포함해야 합니다.
각 평가에는 근거를 제시하고, 긍정적인 톤을 유지하면서도 정확한 평가를 해주세요.
"""

    def _call_llm(self, prompt: str, max_tokens: int = 500) -> str:
        """LLM 호출"""
        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "당신은 전문적인 면접관이자 HR 전문가입니다."},
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

    def _extract_key_concepts(self, text: str) -> List[str]:
        """핵심 개념 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용 가능)
        important_words = []
        words = text.split()
        
        # 길이가 4자 이상인 단어들 중에서 선택
        for word in words:
            word = word.strip('.,!?')
            if len(word) >= 4 and word not in ['그래서', '하지만', '때문에', '그런데']:
                important_words.append(word)
        
        # 빈도순으로 정렬하여 상위 5개 반환
        from collections import Counter
        word_counts = Counter(important_words)
        return [word for word, count in word_counts.most_common(5)]

    def _calculate_text_complexity(self, text: str) -> float:
        """텍스트 복잡도 계산"""
        if not text:
            return 0.0
        
        words = text.split()
        sentences = [s for s in text.split('.') if s.strip()]
        
        # 평균 단어 길이
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # 평균 문장 길이
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # 복잡도 점수 (0-1 범위로 정규화)
        complexity = min(1.0, (avg_word_length / 10 + avg_sentence_length / 30) / 2)
        return complexity

    def _calculate_coherence(self, text: str) -> float:
        """텍스트 일관성 계산"""
        if not text:
            return 0.0
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if len(sentences) < 2:
            return 0.8  # 문장이 적으면 기본 점수
        
        # 연결어 사용 확인
        connectors = ['그래서', '따라서', '하지만', '그러나', '또한', '예를 들어', '결론적으로']
        connector_count = sum(1 for connector in connectors if connector in text)
        
        # 일관성 점수
        coherence = min(1.0, 0.5 + (connector_count / len(sentences)))
        return coherence

    def _calculate_multimodal_coherence(self, text: str, facial: Dict, audio: Dict) -> float:
        """다중 모달 일관성 계산"""
        text_confidence = 0.7 if len(text.split()) > 30 else 0.4
        facial_confidence = facial.get("confidence", 0.5)
        audio_confidence = audio.get("voice_stability", 0.5)
        
        return (text_confidence + facial_confidence + audio_confidence) / 3.0

    def _evaluate_content_quality(self, transcription: str, llm_analysis: str) -> Dict[str, float]:
        """내용 품질 평가"""
        word_count = len(transcription.split())
        
        return {
            "completeness": min(1.0, word_count / 100),  # 완성도
            "relevance": 0.8,  # 관련성 (LLM 분석 기반으로 더 정교하게 가능)
            "specificity": 0.7 if "예를 들어" in transcription else 0.5,  # 구체성
            "depth": min(1.0, word_count / 150)  # 깊이
        }

    def _evaluate_delivery_quality(self, facial: Dict, audio: Dict) -> Dict[str, float]:
        """전달 품질 평가"""
        return {
            "confidence": facial.get("confidence", 0.5),
            "clarity": audio.get("voice_stability", 0.5),
            "engagement": facial.get("eye_contact_quality", 0.5),
            "fluency": audio.get("fluency_score", 0.5)
        }

    def _calculate_performance_metrics(self, analysis: Dict) -> Dict[str, float]:
        """성과 메트릭 계산"""
        content = analysis["content_analysis"]
        delivery = analysis["delivery_analysis"] 
        vocal = analysis["vocal_analysis"]
        
        return {
            "content_score": (content["complexity_score"] + content["coherence_score"]) / 2,
            "delivery_score": delivery["confidence_indicators"],
            "communication_score": (vocal["speech_clarity"] + vocal["fluency_indicators"]) / 2,
            "overall_effectiveness": analysis["overall_coherence"]
        }

    def _update_performance_tracking(self, metrics: Dict):
        """성과 추적 업데이트"""
        tracking = self.interview_context["performance_tracking"]
        question_number = len(self.interview_context["answers_given"])
        
        tracking["question_performances"][question_number] = metrics
        
        # 전체 평균 계산
        all_scores = list(tracking["question_performances"].values())
        if all_scores:
            for key in ["content_score", "delivery_score", "communication_score", "overall_effectiveness"]:
                scores = [score.get(key, 0) for score in all_scores]
                tracking["overall_scores"][key] = sum(scores) / len(scores)

    def _aggregate_interview_data(self) -> Dict:
        """면접 데이터 집계"""
        return {
            "interview_id": self.interview_context["interview_id"],
            "total_questions": len(self.interview_context["questions_asked"]),
            "total_answers": len(self.interview_context["answers_given"]),
            "participant_profile": self.interview_context["participant_profile"],
            "performance_summary": self.interview_context["performance_tracking"]["overall_scores"],
            "duration": "면접 진행 시간 계산 필요"
        }

    def _calculate_category_scores(self) -> Dict[str, float]:
        """카테고리별 점수 계산"""
        tracking = self.interview_context["performance_tracking"]["overall_scores"]
        
        return {
            "내용_완성도": tracking.get("content_score", 3.0) * 5,
            "전달_능력": tracking.get("delivery_score", 0.6) * 5,
            "의사소통": tracking.get("communication_score", 0.7) * 5,
            "전체_효과성": tracking.get("overall_effectiveness", 0.65) * 5
        }

    def _calculate_overall_interview_score(self) -> float:
        """전체 면접 점수 계산"""
        category_scores = self._calculate_category_scores()
        if category_scores:
            return sum(category_scores.values()) / len(category_scores)
        return 3.5

    # 폴백 메서드들
    def _get_fallback_question(self, question_type: str) -> Dict[str, Any]:
        """대체 질문 반환"""
        fallback_questions = {
            "general": "자신의 장점과 단점에 대해 구체적인 예시와 함께 말씀해주세요.",
            "technical": "최근에 진행한 프로젝트에서 가장 기술적으로 도전적이었던 부분은 무엇이었나요?",
            "behavioral": "팀 프로젝트에서 갈등이 발생했을 때 어떻게 해결하셨는지 구체적인 경험을 말씀해주세요.",
            "situational": "우선순위가 다른 여러 업무를 동시에 처리해야 할 때 어떻게 접근하시겠습니까?"
        }
        
        return {
            "question_type": question_type,
            "question": fallback_questions.get(question_type, fallback_questions["general"]),
            "generated_by": "fallback",
            "personalized": False,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _get_fallback_analysis_and_followup(self, user_text: str) -> Dict[str, Any]:
        """대체 분석 및 후속 질문"""
        return {
            "answer_analysis": {
                "transcription": user_text,
                "llm_analysis": "전반적으로 성의있게 답변해주셨습니다. 구체적인 경험과 사례가 더 포함되면 더욱 좋을 것 같습니다.",
                "content_quality": {"completeness": 0.7, "relevance": 0.8, "specificity": 0.6, "depth": 0.7},
                "delivery_quality": {"confidence": 0.75, "clarity": 0.8, "engagement": 0.7, "fluency": 0.8}
            },
            "followup_question": {
                "question": "방금 말씀하신 내용에 대해 좀 더 구체적인 예시를 들어주실 수 있나요?",
                "question_type": "followup",
                "based_on_answer": user_text[:100] + "..." if len(user_text) > 100 else user_text
            },
            "performance_metrics": {
                "content_score": 0.7,
                "delivery_score": 0.75,
                "communication_score": 0.8,
                "overall_effectiveness": 0.75
            },
            "is_fallback": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _get_fallback_comprehensive_feedback(self) -> Dict[str, Any]:
        """대체 종합 피드백"""
        return {
            "overall_performance": 3.7,
            "detailed_feedback": "전반적으로 성실하고 진솔한 면접 태도를 보여주셨습니다. 질문에 대해 성의있게 답변해주셨고, 기본적인 의사소통 능력도 갖추고 계신 것 같습니다. 앞으로 더 구체적인 경험 사례를 준비하시고, 자신감을 가지고 면접에 임하신다면 더욱 좋은 결과를 얻으실 수 있을 것입니다.",
            "category_scores": {"내용_완성도": 3.5, "전달_능력": 3.8, "의사소통": 4.0, "전체_효과성": 3.7},
            "strengths": ["성실한 답변 태도", "기본적인 의사소통 능력", "질문에 대한 이해도"],
            "improvement_areas": ["더 구체적인 사례 제시", "자신감 있는 표현", "답변의 논리적 구성"],
            "specific_recommendations": [
                "STAR 기법을 활용한 경험 서술 연습",
                "모의면접을 통한 실전 감각 향상",
                "자주 묻는 질문에 대한 답변 준비"
            ],
            "overall_score": 3.7,
            "is_fallback": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_module_status(self) -> Dict[str, Any]:
        """모듈 상태 반환"""
        return {
            "module_name": "Personal Interview LLM Integration",
            "is_available": self.is_available,
            "llm_provider": self.llm_provider,
            "model": self.model,
            "features": [
                "personalized_question_generation",
                "multimodal_answer_analysis",
                "intelligent_followup_questions",
                "comprehensive_feedback_generation",
                "performance_tracking"
            ],
            "current_context": {
                "interview_id": self.interview_context["interview_id"],
                "questions_asked": len(self.interview_context["questions_asked"]),
                "answers_analyzed": len(self.interview_context["answers_given"])
            }
        }


# 사용 예시 및 테스트
if __name__ == "__main__":
    # 모듈 테스트
    print("개인면접 LLM 통합 모듈 테스트 시작...")
    
    # 모듈 초기화 (API 키 없이 테스트)
    interview_llm = PersonalInterviewLLMModule()
    
    # 모듈 상태 확인
    status = interview_llm.get_module_status()
    print(f"모듈 상태: {status}")
    
    # 면접 컨텍스트 초기화
    participant_profile = {
        "major": "컴퓨터공학",
        "workexperience": "신입",
        "tech_stack": "Python, React",
        "personality": "적극적이고 학습 의욕이 강함"
    }
    
    interview_llm.initialize_interview_context(1, participant_profile)
    
    # 질문 생성 테스트
    print("\n=== 질문 생성 테스트 ===")
    for question_type in ["general", "technical", "behavioral"]:
        question_result = interview_llm.generate_personalized_question(question_type, participant_profile)
        print(f"{question_type}: {question_result['question']}")
        print(f"생성 방식: {question_result['generated_by']}")
    
    # 답변 분석 테스트
    print("\n=== 답변 분석 테스트 ===")
    sample_answer = "저는 대학에서 컴퓨터공학을 전공하면서 다양한 프로젝트를 경험했습니다. 특히 팀 프로젝트에서 협업의 중요성을 배웠고, 문제 해결 능력을 기를 수 있었습니다."
    
    sample_facial = {"confidence": 0.8, "emotion": "긍정적", "gaze_stability": 0.75}
    sample_audio = {"voice_stability": 0.85, "speaking_rate_wpm": 130, "fluency_score": 0.8}
    sample_question = {"question_type": "general", "question": "자기소개를 해주세요."}
    
    analysis_result = interview_llm.analyze_answer_and_generate_followup(
        sample_answer, sample_facial, sample_audio, sample_question
    )
    
    print(f"답변 분석: {analysis_result['answer_analysis']['llm_analysis'][:100]}...")
    print(f"후속 질문: {analysis_result['followup_question']['question']}")
    
    # 종합 피드백 테스트
    print("\n=== 종합 피드백 테스트 ===")
    comprehensive_feedback = interview_llm.generate_comprehensive_feedback({})
    print(f"전체 점수: {comprehensive_feedback['overall_score']}")
    print(f"주요 강점: {', '.join(comprehensive_feedback['strengths'])}")
    print(f"개선 영역: {', '.join(comprehensive_feedback['improvement_areas'])}")
    
    print("\n개인면접 LLM 통합 모듈 테스트 완료!")
