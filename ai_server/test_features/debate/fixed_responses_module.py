"""
고정 응답 모듈
LLM 미사용 환경에서 사용할 고정된 AI 응답을 관리
"""
import logging
import random
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FixedResponsesModule:
    def __init__(self):
        """고정 응답 모듈 초기화"""
        self.debate_responses = self._initialize_debate_responses()
        self.interview_responses = self._initialize_interview_responses()
        logger.info("고정 응답 모듈 초기화 완료")

    def _initialize_debate_responses(self) -> Dict:
        """토론 단계별 고정 응답 초기화"""
        return {
            "opening": [
                "인공지능은 인간의 일자리를 대체하는 위험을 내포하고 있습니다. 기술의 발전으로 반복적이고 예측 가능한 일자리부터 자동화되어 사라질 것입니다.",
                "인공지능 기술의 급속한 발전은 많은 산업 분야에서 인간의 역할을 축소시키고 있습니다. 제조업, 서비스업, 심지어 창작 분야까지 AI가 침투하고 있는 현실을 직시해야 합니다.",
                "현재 AI는 단순 반복 업무를 넘어 복잡한 판단이 필요한 업무까지 처리할 수 있게 되었습니다. 이는 많은 직업군이 위험에 처했음을 의미합니다."
            ],
            "rebuttal": [
                "인공지능이 일부 일자리를 대체할 수 있다는 점은 인정합니다만, 동시에 새로운 일자리도 창출합니다. 기술 발전으로 인한 일자리 변화는 역사적으로 항상 있어왔습니다.",
                "일자리 대체 우려는 과거 산업혁명 시기에도 제기되었지만, 결과적으로는 더 많은 새로운 직업이 생겨났습니다. AI 시대에도 마찬가지로 새로운 기회가 창출될 것입니다.",
                "AI는 인간의 능력을 대체하는 것이 아니라 보완하는 역할을 합니다. 인간과 AI의 협업을 통해 더 높은 생산성과 창의성을 발휘할 수 있습니다."
            ],
            "counter_rebuttal": [
                "새로운 일자리 창출 가능성은 인정하지만, 그 속도와 규모가 일자리 손실을 따라가지 못합니다. 인공지능이 점점 더 복잡한 업무를 수행할 수 있게 되어 직업 전반에 영향을 미칠 것입니다.",
                "과거의 기술 변화와 AI 혁명은 근본적으로 다릅니다. AI는 인간의 인지 능력까지 모방할 수 있어, 이전과는 차원이 다른 도전을 가져올 것입니다.",
                "새로운 일자리가 생겨날 수 있지만, 기존 근로자들이 그 일자리에 적응하기까지는 상당한 시간과 비용이 필요합니다. 이 과도기의 사회적 비용을 간과해서는 안 됩니다."
            ],
            "closing": [
                "결론적으로, 인공지능은 일자리를 대체할 위험이 크며 이에 대한 사회적 대비가 필요합니다. 재교육과 새로운 경제 체제에 대한 논의가 시급합니다.",
                "인공지능 시대를 맞아 우리는 교육 시스템의 근본적 변화와 사회 안전망 구축에 집중해야 합니다. 기술 발전의 혜택이 모든 계층에게 골고루 돌아갈 수 있는 방안을 모색해야 합니다.",
                "AI 기술의 발전은 불가피하지만, 그 과정에서 발생할 수 있는 사회적 충격을 최소화하기 위한 정책적 대응이 반드시 필요합니다."
            ]
        }

    def _initialize_interview_responses(self) -> Dict:
        """면접 질문별 고정 응답 초기화"""
        return {
            "followup_questions": [
                "방금 말씀하신 내용에 대해 좀 더 구체적인 예시를 들어주실 수 있나요?",
                "그런 경험을 통해 어떤 것을 배우셨고, 앞으로 어떻게 활용하실 계획인가요?",
                "비슷한 상황이 다시 발생한다면 어떻게 다르게 접근하시겠습니까?",
                "팀워크 상황에서 어려움이 있었다면 어떻게 해결하셨나요?",
                "해당 프로젝트에서 가장 큰 도전은 무엇이었고, 어떻게 극복하셨나요?"
            ],
            "technical_followups": [
                "사용하신 기술 스택 중에서 가장 인상 깊었던 부분은 무엇인가요?",
                "프로젝트 진행 중 기술적 한계에 부딪혔을 때 어떻게 해결하셨나요?",
                "코드 품질 향상을 위해 어떤 노력을 하셨는지 말씀해주세요.",
                "성능 최적화나 보안 측면에서 고려했던 부분이 있다면 설명해주세요.",
                "최신 기술 트렌드에 대해 어떻게 학습하고 적용하시는지 궁금합니다."
            ],
            "behavioral_followups": [
                "스트레스가 많은 상황에서 어떻게 대처하시는 편인가요?",
                "동료와 의견 충돌이 있을 때 어떻게 조율하시나요?",
                "새로운 환경에 적응하는 본인만의 방법이 있으신가요?",
                "업무 우선순위를 정하는 기준은 무엇인가요?",
                "실패한 경험에서 얻은 가장 큰 교훈은 무엇인가요?"
            ]
        }

    def get_debate_response(self, phase: str, topic: Optional[str] = None, user_text: Optional[str] = None, variation: bool = True) -> str:
        """토론 단계별 응답 반환"""
        try:
            if phase not in self.debate_responses:
                logger.warning(f"알 수 없는 토론 단계: {phase}")
                return "죄송합니다. 해당 단계의 응답을 준비하지 못했습니다."
            
            responses = self.debate_responses[phase]
            
            if variation and len(responses) > 1:
                # 랜덤 선택으로 다양성 제공
                selected_response = random.choice(responses)
            else:
                # 첫 번째 응답 사용
                selected_response = responses[0]
            
            # 주제나 사용자 텍스트 기반 응답 커스터마이징 (선택적)
            if topic and "인공지능" not in selected_response:
                selected_response = f"'{topic}' 주제와 관련하여, " + selected_response
            
            logger.info(f"토론 응답 반환 - 단계: {phase}, 길이: {len(selected_response)}")
            return selected_response
            
        except Exception as e:
            logger.error(f"토론 응답 생성 오류: {str(e)}")
            return "기술적 문제로 응답을 생성할 수 없습니다."

    def get_interview_followup(self, question_type: str = "general", user_answer: Optional[str] = None) -> str:
        """면접 추가 질문 반환"""
        try:
            # 질문 유형에 따른 카테고리 선택
            if question_type.lower() in ["technical", "tech", "기술"]:
                followups = self.interview_responses["technical_followups"]
            elif question_type.lower() in ["behavioral", "behavior", "인성", "행동"]:
                followups = self.interview_responses["behavioral_followups"]
            else:
                followups = self.interview_responses["followup_questions"]
            
            # 랜덤 선택
            selected_question = random.choice(followups)
            
            logger.info(f"면접 추가 질문 반환 - 유형: {question_type}, 길이: {len(selected_question)}")
            return selected_question
            
        except Exception as e:
            logger.error(f"면접 질문 생성 오류: {str(e)}")
            return "추가 질문을 준비하지 못했습니다. 다른 부분에 대해 말씀해 주세요."

    def get_feedback_comments(self, score_type: str, score_value: float) -> str:
        """점수 기반 피드백 코멘트 반환"""
        try:
            feedback_templates = {
                "initiative": {
                    "high": ["매우 적극적인 자세를 보여주었습니다", "리더십과 추진력이 돋보입니다", "주도적인 모습이 인상적입니다"],
                    "medium": ["적절한 적극성을 보여주었습니다", "균형잡힌 참여도를 보입니다", "안정적인 태도입니다"],
                    "low": ["좀 더 적극적인 자세가 필요합니다", "참여도를 높여보세요", "자신감을 가지고 임해보세요"]
                },
                "communication": {
                    "high": ["의사소통 능력이 뛰어납니다", "명확하고 체계적인 표현력입니다", "상대방이 이해하기 쉽게 설명합니다"],
                    "medium": ["적절한 의사소통 능력을 보입니다", "전달력이 양호합니다", "기본적인 소통은 잘 됩니다"],
                    "low": ["의사소통 능력 향상이 필요합니다", "좀 더 명확한 표현이 필요합니다", "체계적인 설명 연습이 도움될 것 같습니다"]
                },
                "logic": {
                    "high": ["논리적 사고력이 우수합니다", "체계적이고 논리적인 접근입니다", "근거 제시가 탁월합니다"],
                    "medium": ["기본적인 논리력을 갖추고 있습니다", "논리적 구성이 적절합니다", "일관된 논리를 보입니다"],
                    "low": ["논리적 사고력 보완이 필요합니다", "근거 제시를 더 명확히 해주세요", "논리적 연결고리를 강화해보세요"]
                }
            }
            
            # 점수에 따른 레벨 결정
            if score_value >= 4.0:
                level = "high"
            elif score_value >= 3.0:
                level = "medium"
            else:
                level = "low"
            
            # 해당 유형의 피드백 선택
            if score_type in feedback_templates:
                comments = feedback_templates[score_type][level]
                return random.choice(comments)
            else:
                return f"{score_type}: 점수 {score_value:.1f}점"
                
        except Exception as e:
            logger.error(f"피드백 생성 오류: {str(e)}")
            return "피드백을 생성할 수 없습니다."

    def get_sample_answers(self, question_category: str) -> List[str]:
        """질문 카테고리별 모범 답안 예시 반환"""
        sample_answers = {
            "self_introduction": [
                "안녕하세요. 저는 문제 해결을 좋아하는 개발자입니다. 대학에서 컴퓨터공학을 전공하며 다양한 프로젝트를 수행했고, 특히 팀워크와 소통을 중시하며 성장해왔습니다.",
                "저는 끊임없이 학습하며 발전하는 것을 추구하는 사람입니다. 새로운 기술에 대한 호기심이 많고, 이를 실제 프로젝트에 적용해보는 것을 좋아합니다."
            ],
            "technical_experience": [
                "최근 프로젝트에서는 React와 Spring Boot를 활용한 웹 애플리케이션을 개발했습니다. 사용자 경험을 개선하기 위해 반응형 디자인을 적용했고, API 최적화를 통해 응답 속도를 30% 향상시켰습니다.",
                "팀 프로젝트에서 데이터베이스 설계를 담당했습니다. 정규화를 통해 데이터 무결성을 보장하고, 인덱싱을 적절히 활용하여 쿼리 성능을 개선했습니다."
            ],
            "problem_solving": [
                "프로젝트 진행 중 예상보다 많은 데이터로 인해 성능 이슈가 발생했습니다. 문제를 구체적으로 분석한 후, 캐싱 전략을 도입하고 쿼리를 최적화하여 해결했습니다.",
                "팀원 간 의견 차이로 진행이 지연될 때, 각자의 관점을 정리하고 장단점을 비교 분석하여 최적의 방안을 도출했습니다."
            ]
        }
        
        return sample_answers.get(question_category, ["적절한 예시를 준비하지 못했습니다."])

    def get_topic_variations(self, base_topic: str) -> List[str]:
        """주제별 다양한 변형 토론 주제 반환"""
        topic_variations = {
            "인공지능": [
                "인공지능의 일자리 대체 효과",
                "AI 기술의 윤리적 사용",
                "인공지능과 인간의 공존",
                "AI 발전의 사회적 영향"
            ],
            "환경": [
                "기후변화 대응 정책",
                "재생에너지 전환의 필요성",
                "환경보호와 경제발전의 균형",
                "개인의 환경 실천 중요성"
            ],
            "교육": [
                "온라인 교육의 효과성",
                "입시제도 개선 방안",
                "평생교육의 중요성",
                "교육의 공평성 확보"
            ]
        }
        
        return topic_variations.get(base_topic, [base_topic])

    def get_module_status(self) -> Dict:
        """모듈 상태 정보 반환"""
        return {
            "module_name": "Fixed Responses",
            "is_available": True,
            "debate_phases": list(self.debate_responses.keys()),
            "debate_responses_count": {phase: len(responses) for phase, responses in self.debate_responses.items()},
            "interview_categories": list(self.interview_responses.keys()),
            "interview_responses_count": {category: len(responses) for category, responses in self.interview_responses.items()},
            "functions": ["get_debate_response", "get_interview_followup", "get_feedback_comments", "get_sample_answers"]
        }

    def test_all_responses(self) -> Dict:
        """모든 응답 테스트"""
        test_results = {}
        
        try:
            # 토론 응답 테스트
            debate_tests = {}
            for phase in self.debate_responses.keys():
                response = self.get_debate_response(phase)
                debate_tests[phase] = {
                    "success": len(response) > 0,
                    "length": len(response),
                    "preview": response[:50] + "..." if len(response) > 50 else response
                }
            test_results["debate_tests"] = debate_tests
            
            # 면접 질문 테스트
            interview_tests = {}
            for question_type in ["general", "technical", "behavioral"]:
                response = self.get_interview_followup(question_type)
                interview_tests[question_type] = {
                    "success": len(response) > 0,
                    "length": len(response),
                    "preview": response[:50] + "..." if len(response) > 50 else response
                }
            test_results["interview_tests"] = interview_tests
            
            # 피드백 테스트
            feedback_tests = {}
            for score_type in ["initiative", "communication", "logic"]:
                for score in [2.0, 3.5, 4.5]:
                    feedback = self.get_feedback_comments(score_type, score)
                    feedback_tests[f"{score_type}_{score}"] = {
                        "success": len(feedback) > 0,
                        "feedback": feedback
                    }
            test_results["feedback_tests"] = feedback_tests
            
            logger.info("모든 응답 테스트 완료")
            
        except Exception as e:
            logger.error(f"응답 테스트 오류: {str(e)}")
            test_results["error"] = str(e)
        
        return test_results
