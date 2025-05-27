"""
개인면접을 위한 LLM 통합 모듈
실제 프로덕션 환경에서 개인면접 기능을 위한 LLM 통합 모듈
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
            "interviewee_profile": {},
            "question_history": [],
            "performance_tracking": {},
            "session_data": {}
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

    def initialize_interview_session(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """면접 세션 초기화"""
        try:
            self.interview_context = {
                "interviewee_profile": profile,
                "question_history": [],
                "performance_tracking": {
                    "strengths": [],
                    "improvements": [],
                    "overall_scores": {},
                    "question_responses": []
                },
                "session_data": {
                    "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "session_id": f"interview_{int(time.time())}",
                    "total_questions": 0
                }
            }
            
            logger.info(f"면접 세션 초기화 완료 - ID: {self.interview_context['session_data']['session_id']}")
            
            return {
                "status": "success",
                "session_id": self.interview_context['session_data']['session_id'],
                "message": "면접 세션이 성공적으로 초기화되었습니다."
            }
            
        except Exception as e:
            logger.error(f"면접 세션 초기화 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"세션 초기화 실패: {str(e)}"
            }

    def generate_personalized_question(self, question_type: str, context: Dict = None) -> Dict[str, Any]:
        """개인화된 면접 질문 생성"""
        if not self.is_available:
            return self._get_fallback_question(question_type)
        
        try:
            profile = self.interview_context.get("interviewee_profile", {})
            question_history = self.interview_context.get("question_history", [])
            
            prompt = self._create_question_prompt(question_type, profile, question_history, context)
            
            response = self._call_llm(prompt, max_tokens=200)
            
            # 질문 히스토리에 추가
            question_data = {
                "type": question_type,
                "question": response,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "context": context or {}
            }
            
            self.interview_context["question_history"].append(question_data)
            self.interview_context["session_data"]["total_questions"] += 1
            
            result = {
                "question_type": question_type,
                "question": response,
                "question_id": len(question_history) + 1,
                "personalization_applied": True,
                "generated_by": "llm",
                "timestamp": question_data["generated_at"]
            }
            
            logger.info(f"개인화된 질문 생성 완료 - 유형: {question_type}")
            return result
            
        except Exception as e:
            logger.error(f"개인화된 질문 생성 오류: {str(e)}")
            return self._get_fallback_question(question_type)

    def analyze_answer_and_provide_feedback(self, 
                                          answer_text: str,
                                          question_type: str,
                                          multimodal_data: Dict = None) -> Dict[str, Any]:
        """답변 분석 및 피드백 제공"""
        if not self.is_available:
            return self._get_fallback_feedback(answer_text, question_type)
        
        try:
            # 다중 모달 데이터 통합
            integrated_analysis = self._integrate_answer_data(answer_text, multimodal_data)
            
            # 피드백 생성 프롬프트
            prompt = self._create_feedback_prompt(answer_text, question_type, integrated_analysis)
            
            # LLM 호출
            feedback_response = self._call_llm(prompt, max_tokens=400)
            
            # 구조화된 피드백 생성
result = self._parse_feedback_response(feedback_response, integrated_analysis)
            
            # 성과 추적 업데이트
            self._update_performance_tracking(result, question_type)
            
            logger.info(f"답변 분석 및 피드백 생성 완료 - 유형: {question_type}")
            return result
            
        except Exception as e:
            logger.error(f"답변 분석 오류: {str(e)}")
            return self._get_fallback_feedback(answer_text, question_type)

    def generate_followup_question(self, previous_answer: str, original_question_type: str) -> Dict[str, Any]:
        """이전 답변을 바탕으로 한 후속 질문 생성"""
        if not self.is_available:
            return self._get_fallback_followup(original_question_type)
        
        try:
            profile = self.interview_context.get("interviewee_profile", {})
            
            prompt = self._create_followup_prompt(previous_answer, original_question_type, profile)
            
            response = self._call_llm(prompt, max_tokens=150)
            
            # 후속 질문 데이터
            followup_data = {
                "type": "followup",
                "original_type": original_question_type,
                "question": response,
                "based_on_answer": previous_answer[:100] + "..." if len(previous_answer) > 100 else previous_answer,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.interview_context["question_history"].append(followup_data)
            
            result = {
                "question_type": "followup",
                "original_question_type": original_question_type,
                "question": response,
                "is_followup": True,
                "generated_by": "llm",
                "timestamp": followup_data["generated_at"]
            }
            
            logger.info(f"후속 질문 생성 완료 - 원본 유형: {original_question_type}")
            return result
            
        except Exception as e:
            logger.error(f"후속 질문 생성 오류: {str(e)}")
            return self._get_fallback_followup(original_question_type)

    def generate_comprehensive_interview_report(self) -> Dict[str, Any]:
        """종합 면접 보고서 생성"""
        if not self.is_available:
            return self._get_fallback_report()
        
        try:
            # 전체 면접 데이터 집계
            interview_summary = self._aggregate_interview_data()
            
            # 보고서 생성 프롬프트
            prompt = self._create_report_prompt(interview_summary)
            
            # LLM 호출
            report_response = self._call_llm(prompt, max_tokens=600)
            
            # 구조화된 보고서 생성
            result = {
                "interview_summary": interview_summary,
                "comprehensive_feedback": report_response,
                "performance_analysis": self._analyze_overall_performance(),
                "skill_assessment": self._assess_core_skills(),
                "development_recommendations": self._generate_development_plan(),
                "interview_statistics": self._compile_interview_statistics(),
                "report_generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info("종합 면접 보고서 생성 완료")
            return result
            
        except Exception as e:
            logger.error(f"종합 보고서 생성 오류: {str(e)}")
            return self._get_fallback_report()

    def _create_question_prompt(self, question_type: str, profile: Dict, history: List, context: Dict = None) -> str:
        """질문 생성 프롬프트 작성"""
        base_prompt = f"""
당신은 경험이 풍부한 면접관입니다. 다음 정보를 바탕으로 {question_type} 유형의 개인화된 면접 질문을 생성해주세요.

지원자 프로필:
- 직무 카테고리: {profile.get('job_category', '일반')}
- 경력: {profile.get('workexperience', '신입')}
- 학력: {profile.get('education', '대졸')}
- 기술 스택: {profile.get('tech_stack', '없음')}
- 성격: {profile.get('personality', '성실함')}

이미 질문한 내용 (중복 방지):
{[q['question'][:50] + '...' for q in history[-3:]] if history else '없음'}

질문 유형별 가이드라인:
- general: 기본적인 인성과 적합성을 평가하는 질문
- technical: 전문 기술과 실무 경험을 확인하는 질문  
- behavioral: 특정 상황에서의 행동과 문제해결 능력을 평가하는 질문
- fit: 회사와 직무에 대한 적합성과 동기를 확인하는 질문

요구사항:
1. 지원자의 배경에 맞는 구체적이고 개인화된 질문
2. 너무 일반적이지 않은, 깊이 있는 답변을 유도하는 질문
3. 한 문장으로 명확하게 표현
4. 존중하는 톤으로 작성

질문:"""
        
        return base_prompt

    def _create_feedback_prompt(self, answer: str, question_type: str, analysis: Dict) -> str:
        """피드백 생성 프롬프트 작성"""
        return f"""
면접관으로서 다음 답변에 대해 상세하고 건설적인 피드백을 제공해주세요.

질문 유형: {question_type}
지원자 답변: "{answer}"

음성 및 비언어적 분석:
- 음성 안정성: {analysis.get('voice_stability', 0.8)}
- 말하기 속도: {analysis.get('speaking_rate', 120)} WPM
- 자신감 수준: {analysis.get('confidence_level', 0.7)}
- 감정 상태: {analysis.get('emotional_state', '중립')}

다음 기준으로 평가해주세요:
1. 내용의 적절성과 구체성 (5점 만점)
2. 표현의 명확성과 논리성 (5점 만점)  
3. 전문성과 경험의 깊이 (5점 만점)
4. 의사소통 능력 (5점 만점)

피드백 형식:
- 주요 강점 2-3가지
- 개선이 필요한 부분 2-3가지
- 구체적인 개선 방안
- 격려의 메시지

피드백:"""

    def _create_followup_prompt(self, previous_answer: str, question_type: str, profile: Dict) -> str:
        """후속 질문 생성 프롬프트"""
        return f"""
면접관으로서 지원자의 이전 답변을 바탕으로 더 깊이 있는 후속 질문을 만들어주세요.

이전 답변: "{previous_answer[:200]}..."
질문 유형: {question_type}
지원자 배경: {profile.get('job_category', '일반')} 분야, {profile.get('workexperience', '신입')} 경력

후속 질문 목적:
- 이전 답변의 구체적인 세부사항 확인
- 실제 경험이나 역량의 깊이 파악
- 문제해결 과정이나 학습 경험 탐구

한 문장으로 명확하고 자연스러운 후속 질문을 만들어주세요.

후속 질문:"""

    def _create_report_prompt(self, summary: Dict) -> str:
        """보고서 생성 프롬프트"""
        return f"""
면접관으로서 전체 면접 세션에 대한 종합적인 평가 보고서를 작성해주세요.

면접 개요:
- 총 질문 수: {summary.get('total_questions', 0)}
- 면접 시간: {summary.get('duration', '30분')}
- 질문 유형: {', '.join(summary.get('question_types', []))}

성과 요약:
- 전체 평균 점수: {summary.get('average_score', 3.5)}/5
- 강점 영역: {', '.join(summary.get('strengths', []))}
- 개선 영역: {', '.join(summary.get('improvements', []))}

다음 내용을 포함한 종합 평가를 작성해주세요:
1. 전반적인 면접 수행 평가
2. 직무 적합성 판단
3. 핵심 역량 평가
4. 성장 가능성 분석
5. 최종 추천 사항

평가 보고서:"""

    def _call_llm(self, prompt: str, max_tokens: int = 300) -> str:
        """LLM 호출"""
        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "당신은 전문적이고 경험이 풍부한 면접관입니다."},
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

    def _integrate_answer_data(self, text: str, multimodal_data: Dict = None) -> Dict[str, Any]:
        """답변 데이터 통합"""
        if not multimodal_data:
            multimodal_data = {}
        
        return {
            "text_analysis": {
                "word_count": len(text.split()),
                "sentence_count": len([s for s in text.split('.') if s.strip()]),
                "key_points": self._extract_key_points(text),
                "complexity_score": min(5.0, len(text.split()) / 20)
            },
            "voice_analysis": multimodal_data.get("audio_analysis", {}),
            "visual_analysis": multimodal_data.get("facial_analysis", {}),
            "overall_delivery": self._assess_delivery_quality(text, multimodal_data)
        }

    def _extract_key_points(self, text: str) -> List[str]:
        """주요 내용 추출"""
        sentences = [s.strip() for s in text.split('.') if s.strip() and len(s.strip()) > 10]
        return sentences[:3]  # 처음 3개 문장

    def _assess_delivery_quality(self, text: str, multimodal: Dict) -> Dict[str, float]:
        """전달 품질 평가"""
        audio = multimodal.get("audio_analysis", {})
        visual = multimodal.get("facial_analysis", {})
        
        return {
            "content_score": min(5.0, len(text.split()) / 15),
            "voice_score": audio.get("voice_stability", 0.7) * 5,
            "confidence_score": visual.get("confidence", 0.7) * 5,
            "overall_score": (len(text.split()) / 15 + audio.get("voice_stability", 0.7) + visual.get("confidence", 0.7)) / 3 * 5
        }

    def _parse_feedback_response(self, response: str, analysis: Dict) -> Dict[str, Any]:
        """피드백 응답 파싱"""
        delivery = analysis.get("overall_delivery", {})
        
        return {
            "feedback_text": response,
            "scores": {
                "content_score": delivery.get("content_score", 3.5),
                "voice_score": delivery.get("voice_score", 3.5),
                "confidence_score": delivery.get("confidence_score", 3.5),
                "overall_score": delivery.get("overall_score", 3.5)
            },
            "key_insights": analysis.get("text_analysis", {}).get("key_points", []),
            "delivery_assessment": delivery,
            "generated_by": "llm",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _update_performance_tracking(self, feedback: Dict, question_type: str):
        """성과 추적 업데이트"""
        tracking = self.interview_context["performance_tracking"]
        
        scores = feedback.get("scores", {})
        overall_score = scores.get("overall_score", 3.5)
        
        # 점수 기록
        if question_type not in tracking["overall_scores"]:
            tracking["overall_scores"][question_type] = []
        tracking["overall_scores"][question_type].append(overall_score)
        
        # 응답 기록
        tracking["question_responses"].append({
            "type": question_type,
            "score": overall_score,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    def _aggregate_interview_data(self) -> Dict[str, Any]:
        """면접 데이터 집계"""
        tracking = self.interview_context["performance_tracking"]
        session = self.interview_context["session_data"]
        
        # 전체 점수 계산
        all_scores = []
        for scores_list in tracking["overall_scores"].values():
            all_scores.extend(scores_list)
        
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 3.5
        
        return {
            "total_questions": session["total_questions"],
            "question_types": list(tracking["overall_scores"].keys()),
            "average_score": avg_score,
            "score_range": {"min": min(all_scores), "max": max(all_scores)} if all_scores else {"min": 3.0, "max": 4.0},
            "strengths": self._identify_performance_strengths(tracking),
            "improvements": self._identify_performance_improvements(tracking)
        }

    def _identify_performance_strengths(self, tracking: Dict) -> List[str]:
        """성과 강점 식별"""
        strengths = []
        
        for question_type, scores in tracking["overall_scores"].items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 4.0:
                type_names = {
                    "general": "일반 역량",
                    "technical": "기술적 전문성",
                    "behavioral": "행동 역량",
                    "fit": "직무 적합성"
                }
                strengths.append(type_names.get(question_type, question_type))
        
        if not strengths:
            strengths.append("전반적으로 균형잡힌 수행")
        
        return strengths

    def _identify_performance_improvements(self, tracking: Dict) -> List[str]:
        """성과 개선점 식별"""
        improvements = []
        
        for question_type, scores in tracking["overall_scores"].items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 3.5:
                type_names = {
                    "general": "기본 소양",
                    "technical": "기술 역량",
                    "behavioral": "상황 대응",
                    "fit": "동기 및 적합성"
                }
                improvements.append(type_names.get(question_type, question_type))
        
        if not improvements:
            improvements.append("지속적인 역량 개발")
        
        return improvements

    def _analyze_overall_performance(self) -> Dict[str, Any]:
        """전체 성과 분석"""
        tracking = self.interview_context["performance_tracking"]
        
        # 시간에 따른 성과 변화
        responses = tracking["question_responses"]
        if len(responses) >= 2:
            early_scores = [r["score"] for r in responses[:len(responses)//2]]
            later_scores = [r["score"] for r in responses[len(responses)//2:]]
            
            trend = "향상" if sum(later_scores)/len(later_scores) > sum(early_scores)/len(early_scores) else "일정"
        else:
            trend = "데이터 부족"
        
        return {
            "performance_trend": trend,
            "consistency": "일관적" if all(abs(r["score"] - 3.5) < 1.0 for r in responses) else "변동적",
            "peak_performance": max([r["score"] for r in responses]) if responses else 3.5,
            "improvement_potential": "높음" if trend == "향상" else "보통"
        }

    def _assess_core_skills(self) -> Dict[str, Any]:
        """핵심 스킬 평가"""
        tracking = self.interview_context["performance_tracking"]
        
        skills = {
            "communication": 0,
            "technical_competency": 0,
            "problem_solving": 0,
            "cultural_fit": 0
        }
        
        for question_type, scores in tracking["overall_scores"].items():
            avg_score = sum(scores) / len(scores)
            
            if question_type == "general":
                skills["communication"] = avg_score
                skills["cultural_fit"] = avg_score
            elif question_type == "technical":
                skills["technical_competency"] = avg_score
            elif question_type == "behavioral":
                skills["problem_solving"] = avg_score
        
        return skills

    def _generate_development_plan(self) -> List[str]:
        """개발 계획 생성"""
        improvements = self.interview_context["performance_tracking"].get("improvements", [])
        
        development_plans = {
            "기본 소양": "면접 기본기 강화를 위한 모의면접 연습 권장",
            "기술 역량": "관련 기술 스택 학습 및 프로젝트 경험 축적 필요",
            "상황 대응": "다양한 상황별 대응 시나리오 연습 권장",
            "동기 및 적합성": "해당 기업과 직무에 대한 심화 연구 필요"
        }
        
        plans = []
        for improvement in improvements:
            if improvement in development_plans:
                plans.append(development_plans[improvement])
        
        if not plans:
            plans.append("현재 수준을 유지하며 지속적인 성장 추구")
        
        return plans

    def _compile_interview_statistics(self) -> Dict[str, Any]:
        """면접 통계 편집"""
        session = self.interview_context["session_data"]
        tracking = self.interview_context["performance_tracking"]
        
        return {
            "session_duration": "약 30분",  # 실제로는 시작-종료 시간 계산 필요
            "total_questions": session["total_questions"],
            "question_type_distribution": {qtype: len(scores) for qtype, scores in tracking["overall_scores"].items()},
            "average_response_time": "약 2분",  # 실제로는 각 응답 시간 측정 필요
            "session_completion_rate": "100%"
        }

    def _get_fallback_question(self, question_type: str) -> Dict[str, Any]:
        """LLM 사용 불가시 기본 질문"""
        fallback_questions = {
            "general": "자신의 장점과 단점에 대해 구체적인 예시와 함께 설명해주세요.",
            "technical": "지금까지의 프로젝트 경험 중 가장 도전적이었던 기술적 문제는 무엇이었나요?",
            "behavioral": "팀 프로젝트에서 갈등이 발생했을 때 어떻게 해결한 경험이 있나요?",
            "fit": "우리 회사에 지원한 이유와 기여할 수 있는 부분에 대해 말씀해주세요."
        }
        
        return {
            "question_type": question_type,
            "question": fallback_questions.get(question_type, "자기소개를 해주세요."),
            "question_id": 1,
            "personalization_applied": False,
            "generated_by": "fallback",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _get_fallback_feedback(self, answer: str, question_type: str) -> Dict[str, Any]:
        """기본 피드백"""
        return {
            "feedback_text": "전반적으로 성실하게 답변해주셨습니다. 좀 더 구체적인 예시와 경험을 공유해주시면 더욱 좋은 인상을 남길 수 있을 것 같습니다.",
            "scores": {
                "content_score": 3.5,
                "voice_score": 3.5,
                "confidence_score": 3.5,
                "overall_score": 3.5
            },
            "key_insights": ["성실한 답변 태도", "기본적인 내용 전달"],
            "delivery_assessment": {"overall_score": 3.5},
            "generated_by": "fallback",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _get_fallback_followup(self, original_type: str) -> Dict[str, Any]:
        """기본 후속 질문"""
        followup_questions = {
            "general": "방금 말씀하신 경험에서 가장 중요하게 배운 점은 무엇인가요?",
            "technical": "그 문제를 해결하는 과정에서 어떤 새로운 기술이나 방법을 학습하셨나요?",
            "behavioral": "비슷한 상황이 다시 발생한다면 어떻게 다르게 접근하시겠습니까?",
            "fit": "우리 회사에서 그 경험을 어떻게 활용하실 수 있을까요?"
        }
        
        return {
            "question_type": "followup",
            "original_question_type": original_type,
            "question": followup_questions.get(original_type, "더 자세히 설명해 주실 수 있나요?"),
            "is_followup": True,
            "generated_by": "fallback",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _get_fallback_report(self) -> Dict[str, Any]:
        """기본 보고서"""
        return {
            "interview_summary": {
                "total_questions": 5,
                "average_score": 3.5,
                "strengths": ["성실한 태도"],
                "improvements": ["더 구체적인 답변"]
            },
            "comprehensive_feedback": "전반적으로 면접에 성실하게 임해주셨습니다. 기본적인 소양을 갖추고 있으며, 앞으로 더 많은 경험을 쌓으시면 좋은 성과를 낼 수 있을 것 같습니다.",
            "performance_analysis": {"performance_trend": "일정", "improvement_potential": "보통"},
            "skill_assessment": {"communication": 3.5, "technical_competency": 3.5, "problem_solving": 3.5, "cultural_fit": 3.5},
            "development_recommendations": ["다양한 프로젝트 경험 축적", "면접 기본기 연습"],
            "interview_statistics": {"total_questions": 5, "session_completion_rate": "100%"},
            "report_generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_fallback": True
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
                "dynamic_followup_questions",
                "comprehensive_interview_reports",
                "performance_tracking",
                "development_recommendations"
            ],
            "current_session": self.interview_context.get("session_data", {}),
            "question_history_count": len(self.interview_context.get("question_history", []))
        }


# 실행 예시
if __name__ == "__main__":
    print("개인면접 LLM 통합 모듈 테스트 시작...")
    
    # 모듈 초기화
    llm_module = PersonalInterviewLLMModule()
    
    # 모듈 상태 확인
    status = llm_module.get_module_status()
    print(f"모듈 상태: {status}")
    
    # 테스트 프로필
    test_profile = {
        "job_category": "ICT",
        "workexperience": "신입",
        "education": "대졸",
        "tech_stack": "Python, Java",
        "personality": "성실함, 책임감"
    }
    
    # 면접 세션 초기화
    session_result = llm_module.initialize_interview_session(test_profile)
    print(f"세션 초기화: {session_result}")
    
    # 질문 생성 테스트
    question_types = ["general", "technical", "behavioral"]
    
    for q_type in question_types:
        print(f"\n=== {q_type.upper()} 질문 테스트 ===")
        
        # 질문 생성
        question_result = llm_module.generate_personalized_question(q_type)
        print(f"질문: {question_result['question']}")
        
        # 샘플 답변으로 피드백 테스트
        sample_answer = f"이것은 {q_type} 유형의 샘플 답변입니다. 저는 항상 최선을 다하려고 노력합니다."
        
        feedback_result = llm_module.analyze_answer_and_provide_feedback(sample_answer, q_type)
        print(f"피드백: {feedback_result['feedback_text'][:100]}...")
        print(f"점수: {feedback_result['scores']['overall_score']:.1f}/5")
    
    # 종합 보고서 생성
    print("\n=== 종합 보고서 생성 ===")
    report = llm_module.generate_comprehensive_interview_report()
    print(f"보고서 요약: {report['interview_summary']}")
    
    print("\n개인면접 LLM 통합 모듈 테스트 완료!")
