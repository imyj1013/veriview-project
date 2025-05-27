"""
개인면접을 위한 고정 응답 모듈
LLM 미사용 환경에서 개인면접 질문과 피드백을 제공
"""
import logging
import random
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalInterviewFixedResponsesModule:
    def __init__(self):
        """개인면접 고정 응답 모듈 초기화"""
        logger.info("개인면접 고정 응답 모듈 초기화")
        
        # 질문 유형별 질문 풀
        self.interview_questions = {
            "general": [
                "자기소개를 간단히 해주세요.",
                "우리 회사에 지원한 이유는 무엇인가요?",
                "본인의 장점과 단점에 대해 말씀해주세요.",
                "5년 후 본인의 모습은 어떨 것 같나요?",
                "팀워크 경험에 대해 말씀해주세요.",
                "스트레스 해소 방법은 무엇인가요?",
                "실패했던 경험과 그로부터 배운 점은 무엇인가요?"
            ],
            "technical": [
                "본인의 전공 분야에서 가장 관심 있는 기술은 무엇인가요?",
                "최근에 진행한 프로젝트에 대해 설명해주세요.",
                "기술적 문제를 해결할 때 어떤 접근 방식을 사용하나요?",
                "새로운 기술을 학습할 때 어떤 방법을 사용하나요?",
                "코드 리뷰의 중요성에 대해 어떻게 생각하나요?",
                "알고리즘과 자료구조 중 가장 자신 있는 분야는 무엇인가요?"
            ],
            "behavioral": [
                "갈등 상황에서 어떻게 대처하나요?",
                "압박감이 있는 상황에서 일해본 경험이 있나요?",
                "리더십을 발휘했던 경험에 대해 말씀해주세요.",
                "동료와 의견이 다를 때 어떻게 해결하나요?",
                "새로운 환경에 적응하는 본인만의 방법이 있나요?",
                "윤리적 딜레마에 직면했을 때 어떻게 판단하나요?"
            ]
        }
        
        # 피드백 템플릿
        self.feedback_templates = {
            "communication": {
                "excellent": "의사소통 능력이 매우 뛰어납니다. 명확하고 체계적으로 답변하셨습니다.",
                "good": "의사소통이 원활합니다. 답변이 이해하기 쉬웠습니다.",
                "average": "의사소통은 무난합니다. 좀 더 구체적인 설명이 있으면 좋겠습니다.",
                "needs_improvement": "의사소통 부분에서 개선이 필요합니다. 더 명확한 표현을 연습해보세요."
            },
            "confidence": {
                "excellent": "자신감이 넘치는 모습이 인상적입니다.",
                "good": "적절한 자신감을 보여주셨습니다.",
                "average": "자신감이 보통 수준입니다. 좀 더 당당한 모습을 보여주세요.",
                "needs_improvement": "자신감 부족이 느껴집니다. 충분한 준비와 연습이 필요합니다."
            },
            "relevance": {
                "excellent": "질문에 매우 적절하고 구체적으로 답변하셨습니다.",
                "good": "질문에 잘 맞는 답변이었습니다.",
                "average": "질문과 관련된 답변이지만 더 구체적이면 좋겠습니다.",
                "needs_improvement": "질문의 핵심을 파악하고 더 관련성 있는 답변이 필요합니다."
            },
            "technical": {
                "excellent": "기술적 지식이 매우 뛰어나고 실무 경험이 풍부해 보입니다.",
                "good": "기술적 이해도가 좋습니다.",
                "average": "기본적인 기술 지식은 갖추고 있습니다.",
                "needs_improvement": "기술적 역량 강화를 위한 추가 학습이 필요합니다."
            }
        }
        
        # 전체 피드백 템플릿
        self.overall_feedback_templates = {
            "excellent": [
                "전반적으로 매우 우수한 면접 수행을 보여주셨습니다. 자신감 있는 태도와 명확한 답변이 인상적이었습니다.",
                "뛰어난 의사소통 능력과 전문성을 잘 보여주셨습니다. 우리 회사에 적합한 인재라고 생각됩니다.",
                "모든 질문에 체계적이고 구체적으로 답변해주셨습니다. 매우 긍정적인 인상을 받았습니다."
            ],
            "good": [
                "전반적으로 좋은 면접이었습니다. 성실한 자세와 적극적인 모습이 좋았습니다.",
                "답변 내용이 충실했고 준비를 잘 해오신 것 같습니다. 몇 가지 부분에서 더 발전시킬 여지가 있습니다.",
                "면접에 임하는 자세가 좋았고 대답도 성의 있게 해주셨습니다."
            ],
            "average": [
                "기본적인 면접 수행은 무난했습니다. 좀 더 적극적인 자세와 구체적인 경험 공유가 필요합니다.",
                "준비는 하고 오셨지만 더 깊이 있는 답변과 자신감 있는 모습을 보여주시면 좋겠습니다.",
                "전반적으로 평균적인 수준입니다. 추가적인 준비와 연습을 통해 발전시켜 보세요."
            ],
            "needs_improvement": [
                "면접 준비와 연습이 더 필요해 보입니다. 충분한 준비를 통해 다시 도전해보세요.",
                "답변이 다소 부족했습니다. 구체적인 경험과 사례를 준비하여 다시 면접에 임해주세요.",
                "전반적인 개선이 필요합니다. 면접 스킬 향상을 위한 노력이 필요합니다."
            ]
        }

    def get_module_status(self) -> Dict[str, Any]:
        """모듈 상태 정보 반환"""
        return {
            "is_available": True,
            "module_name": "PersonalInterviewFixedResponsesModule",
            "functions": [
                "get_interview_question",
                "get_feedback",
                "test_all_responses"
            ],
            "question_types": list(self.interview_questions.keys()),
            "total_questions": sum(len(questions) for questions in self.interview_questions.values())
        }

    def get_interview_question(self, question_type: str = "general") -> str:
        """면접 질문 생성"""
        try:
            if question_type not in self.interview_questions:
                logger.warning(f"알 수 없는 질문 유형: {question_type}, 기본값 사용")
                question_type = "general"
            
            questions = self.interview_questions[question_type]
            selected_question = random.choice(questions)
            
            logger.info(f"면접 질문 생성 완료 - 유형: {question_type}, 질문: {selected_question}")
            return selected_question
            
        except Exception as e:
            logger.error(f"면접 질문 생성 오류: {str(e)}")
            return "자기소개를 간단히 해주세요."

    def get_feedback(self, analysis_data: Dict[str, Any], question_type: str = "general") -> Dict[str, Any]:
        """면접 답변에 대한 피드백 생성"""
        try:
            # 분석 데이터에서 기본 정보 추출
            word_count = analysis_data.get("word_count", 30)
            confidence = analysis_data.get("confidence", 0.7)
            
            # 점수 계산 (0.0 ~ 5.0)
            communication_score = self._calculate_communication_score(word_count, confidence)
            confidence_score = self._calculate_confidence_score(confidence)
            relevance_score = self._calculate_relevance_score(question_type, word_count)
            technical_score = self._calculate_technical_score(question_type, confidence)
            overall_score = (communication_score + confidence_score + relevance_score + technical_score) / 4
            
            # 피드백 생성
            feedback = {
                "communication_score": round(communication_score, 1),
                "confidence_score": round(confidence_score, 1),
                "relevance_score": round(relevance_score, 1),
                "technical_score": round(technical_score, 1),
                "overall_score": round(overall_score, 1),
                
                "communication_feedback": self._get_score_feedback("communication", communication_score),
                "confidence_feedback": self._get_score_feedback("confidence", confidence_score),
                "relevance_feedback": self._get_score_feedback("relevance", relevance_score),
                "technical_feedback": self._get_score_feedback("technical", technical_score),
                
                "overall_feedback": self._get_overall_feedback(overall_score),
                
                "strengths": self._identify_strengths(communication_score, confidence_score, relevance_score, technical_score),
                "improvements": self._identify_improvements(communication_score, confidence_score, relevance_score, technical_score),
                "recommendations": self._get_recommendations(question_type, overall_score)
            }
            
            logger.info(f"피드백 생성 완료 - 전체 점수: {overall_score}")
            return feedback
            
        except Exception as e:
            logger.error(f"피드백 생성 오류: {str(e)}")
            return self._get_default_feedback()

    def _calculate_communication_score(self, word_count: int, confidence: float) -> float:
        """의사소통 점수 계산"""
        # 적정 단어 수: 50-150단어
        if 50 <= word_count <= 150:
            length_score = 4.0
        elif 30 <= word_count < 50 or 150 < word_count <= 200:
            length_score = 3.0
        elif 20 <= word_count < 30 or 200 < word_count <= 250:
            length_score = 2.5
        else:
            length_score = 2.0
        
        confidence_factor = confidence * 2.0  # 0.0 ~ 2.0
        
        score = (length_score + confidence_factor) / 2
        return min(5.0, max(1.0, score))

    def _calculate_confidence_score(self, confidence: float) -> float:
        """자신감 점수 계산"""
        if confidence >= 0.9:
            return 5.0
        elif confidence >= 0.8:
            return 4.5
        elif confidence >= 0.7:
            return 4.0
        elif confidence >= 0.6:
            return 3.5
        elif confidence >= 0.5:
            return 3.0
        else:
            return 2.5

    def _calculate_relevance_score(self, question_type: str, word_count: int) -> float:
        """질문 관련성 점수 계산"""
        base_score = 3.5
        
        # 질문 유형별 가중치
        if question_type == "technical":
            if word_count >= 80:  # 기술 질문은 더 자세한 답변 기대
                base_score += 0.5
        elif question_type == "behavioral":
            if word_count >= 100:  # 행동 질문은 구체적인 사례 필요
                base_score += 0.5
        
        # 답변 길이에 따른 조정
        if word_count < 20:
            base_score -= 1.0
        elif word_count > 200:
            base_score -= 0.3
        
        return min(5.0, max(1.0, base_score))

    def _calculate_technical_score(self, question_type: str, confidence: float) -> float:
        """기술적 역량 점수 계산"""
        if question_type == "technical":
            return confidence * 4.0 + 1.0  # 기술 질문의 경우 높은 가중치
        else:
            return confidence * 2.0 + 2.0  # 일반 질문의 경우 기본 점수

    def _get_score_feedback(self, category: str, score: float) -> str:
        """점수에 따른 피드백 반환"""
        if score >= 4.5:
            level = "excellent"
        elif score >= 3.5:
            level = "good"
        elif score >= 2.5:
            level = "average"
        else:
            level = "needs_improvement"
        
        return self.feedback_templates[category][level]

    def _get_overall_feedback(self, overall_score: float) -> str:
        """전체 점수에 따른 종합 피드백"""
        if overall_score >= 4.5:
            level = "excellent"
        elif overall_score >= 3.5:
            level = "good"
        elif overall_score >= 2.5:
            level = "average"
        else:
            level = "needs_improvement"
        
        return random.choice(self.overall_feedback_templates[level])

    def _identify_strengths(self, comm: float, conf: float, rel: float, tech: float) -> List[str]:
        """강점 식별"""
        strengths = []
        scores = {"의사소통": comm, "자신감": conf, "관련성": rel, "기술적 역량": tech}
        
        for area, score in scores.items():
            if score >= 4.0:
                strengths.append(area)
        
        if not strengths:
            # 가장 높은 점수 영역을 강점으로 선택
            best_area = max(scores, key=scores.get)
            strengths.append(best_area)
        
        return strengths

    def _identify_improvements(self, comm: float, conf: float, rel: float, tech: float) -> List[str]:
        """개선점 식별"""
        improvements = []
        scores = {"의사소통": comm, "자신감": conf, "관련성": rel, "기술적 역량": tech}
        
        for area, score in scores.items():
            if score < 3.0:
                improvements.append(area)
        
        if not improvements and min(scores.values()) < 4.0:
            # 가장 낮은 점수 영역을 개선점으로 선택
            worst_area = min(scores, key=scores.get)
            improvements.append(worst_area)
        
        return improvements

    def _get_recommendations(self, question_type: str, overall_score: float) -> List[str]:
        """추천 사항 생성"""
        recommendations = []
        
        if overall_score < 3.0:
            recommendations.extend([
                "면접 전 충분한 준비 시간을 가지세요.",
                "모의 면접을 통해 실전 감각을 기르세요.",
                "자주 묻는 질문들에 대한 답변을 미리 준비하세요."
            ])
        elif overall_score < 4.0:
            recommendations.extend([
                "답변을 더 구체적이고 상세하게 해보세요.",
                "자신의 경험을 바탕으로 한 사례를 준비하세요.",
                "면접에서의 자신감을 기르기 위해 연습하세요."
            ])
        else:
            recommendations.extend([
                "현재 수준을 유지하며 더욱 발전시켜 나가세요.",
                "다양한 질문 유형에 대비한 준비를 계속하세요.",
                "면접관과의 자연스러운 대화를 연습하세요."
            ])
        
        # 질문 유형별 특화 추천
        if question_type == "technical":
            recommendations.append("최신 기술 트렌드에 대한 지식을 지속적으로 업데이트하세요.")
        elif question_type == "behavioral":
            recommendations.append("STAR 기법(Situation, Task, Action, Result)을 활용한 답변을 연습하세요.")
        
        return recommendations[:3]  # 최대 3개 추천

    def _get_default_feedback(self) -> Dict[str, Any]:
        """기본 피드백 반환 (오류 시 사용)"""
        return {
            "communication_score": 3.0,
            "confidence_score": 3.0,
            "relevance_score": 3.0,
            "technical_score": 3.0,
            "overall_score": 3.0,
            "communication_feedback": "의사소통이 무난합니다.",
            "confidence_feedback": "적절한 자신감을 보여주셨습니다.",
            "relevance_feedback": "질문과 관련된 답변이었습니다.",
            "technical_feedback": "기본적인 역량을 갖추고 있습니다.",
            "overall_feedback": "전반적으로 무난한 면접이었습니다.",
            "strengths": ["성실한 자세"],
            "improvements": ["더 구체적인 답변"],
            "recommendations": ["충분한 준비를 통해 면접에 임하세요."]
        }

    def test_all_responses(self) -> Dict[str, Any]:
        """모든 응답 기능 테스트"""
        test_results = {
            "question_generation": {},
            "feedback_generation": {},
            "overall_status": "success"
        }
        
        try:
            # 각 질문 유형별 테스트
            for question_type in self.interview_questions.keys():
                # 질문 생성 테스트
                question = self.get_interview_question(question_type)
                test_results["question_generation"][question_type] = {
                    "success": len(question) > 10,
                    "question": question
                }
                
                # 피드백 생성 테스트
                test_data = {"word_count": 75, "confidence": 0.8}
                feedback = self.get_feedback(test_data, question_type)
                test_results["feedback_generation"][question_type] = {
                    "success": "overall_score" in feedback,
                    "overall_score": feedback.get("overall_score", 0)
                }
            
            logger.info("모든 응답 기능 테스트 완료")
            
        except Exception as e:
            logger.error(f"응답 기능 테스트 오류: {str(e)}")
            test_results["overall_status"] = "error"
            test_results["error"] = str(e)
        
        return test_results


# 실행 예시 및 테스트
if __name__ == "__main__":
    # 모듈 테스트
    print("개인면접 고정 응답 모듈 테스트 시작...")
    
    responses_module = PersonalInterviewFixedResponsesModule()
    
    # 모듈 상태 확인
    status = responses_module.get_module_status()
    print(f"모듈 상태: {status}")
    
    # 각 질문 유형별 테스트
    question_types = ["general", "technical", "behavioral"]
    
    for q_type in question_types:
        print(f"\n=== {q_type.upper()} 질문 테스트 ===")
        
        # 질문 생성
        question = responses_module.get_interview_question(q_type)
        print(f"질문: {question}")
        
        # 샘플 데이터로 피드백 생성
        sample_data = {
            "word_count": 85,
            "confidence": 0.75
        }
        
        feedback = responses_module.get_feedback(sample_data, q_type)
        print(f"전체 점수: {feedback['overall_score']}")
        print(f"종합 피드백: {feedback['overall_feedback']}")
        print(f"강점: {', '.join(feedback['strengths'])}")
        print(f"개선점: {', '.join(feedback['improvements'])}")
    
    # 전체 기능 테스트
    print("\n=== 전체 기능 테스트 ===")
    test_results = responses_module.test_all_responses()
    print(f"테스트 결과: {test_results['overall_status']}")
    
    print("개인면접 고정 응답 모듈 테스트 완료!")
