"""
고정 응답 생성기
LLM 없이 고정된 응답을 생성하는 모듈
"""
import time
from typing import Dict, Any, List, Optional, Union

def get_debate_response(stage: str, topic: str = "인공지능", user_text: str = "", debate_id: Optional[int] = None) -> Dict[str, Any]:
    """
    토론 단계별 고정 AI 응답 생성
    
    Args:
        stage: 토론 단계 ("opening", "rebuttal", "counter_rebuttal", "closing")
        topic: 토론 주제 (기본값: "인공지능")
        user_text: 사용자 텍스트 (반론/재반론에 활용)
        debate_id: 토론 ID
        
    Returns:
        Dict[str, Any]: 응답 데이터
    """
    responses = {
        "opening": f"{topic}의 발전은 인류에게 긍정적인 영향을 미칠 것입니다. 효율성 증대와 새로운 가능성을 제공하기 때문입니다.",
        "rebuttal": f"말씀하신 우려사항도 있지만, {topic}의 장점이 더 크다고 생각합니다. 적절한 규제와 함께 발전시켜 나가면 될 것입니다.",
        "counter_rebuttal": f"규제만으로는 한계가 있을 수 있지만, {topic} 기술 자체의 발전을 통해 문제를 해결할 수 있습니다.",
        "closing": f"결론적으로 {topic}은 인류의 미래를 위한 필수적인 기술입니다. 신중한 접근과 함께 적극적으로 활용해야 합니다."
    }
    
    # 기본 응답 선택
    ai_response = responses.get(stage, f"{topic}에 대한 의견을 말씀드리겠습니다.")
    
    # 사용자 텍스트가 있는 경우 응답 조정
    if user_text and len(user_text) > 0:
        if stage == "rebuttal":
            ai_response = f"'{user_text[:30]}...'라는 의견에 대해, {ai_response}"
        elif stage == "counter_rebuttal":
            ai_response = f"반론에 대한 의견 감사합니다. 하지만 {ai_response}"
    
    # 응답 데이터 구성
    response_data = {
        "text": ai_response,
        "generated_by": "fixed_template",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 토론 ID가 있는 경우 추가
    if debate_id is not None:
        response_data["debate_id"] = debate_id
        
    # 단계별 응답 키 설정
    if stage == "opening":
        response_data["ai_opening_text"] = ai_response
    elif stage == "rebuttal":
        response_data["ai_rebuttal_text"] = ai_response
    elif stage == "counter_rebuttal":
        response_data["ai_counter_rebuttal_text"] = ai_response
    elif stage == "closing":
        response_data["ai_closing_text"] = ai_response
    
    return response_data

def get_interview_response(question_type: str, job_category: str = "ICT") -> Dict[str, Any]:
    """
    면접 질문 유형별 고정 질문 생성
    
    Args:
        question_type: 질문 유형 ("INTRO", "FIT", "PERSONALITY", "TECH", "FOLLOWUP")
        job_category: 직무 카테고리 (기본값: "ICT")
        
    Returns:
        Dict[str, Any]: 질문 데이터
    """
    # 기본 질문
    general_questions = {
        "INTRO": "자기소개를 간단히 해주세요.",
        "FIT": "이 직무에 지원한 이유는 무엇인가요?",
        "PERSONALITY": "본인의 강점과 약점은 무엇인가요?",
        "TECH": "최근에 관심을 가지고 있는 기술 트렌드가 있다면 설명해주세요.",
        "FOLLOWUP": "방금 말씀해주신 내용에 대해 좀 더 자세히 설명해주실 수 있을까요?"
    }
    
    # 직무별 추가 질문
    job_questions = {
        "ICT": {
            "INTRO": "IT 분야에서의 경험과 함께 자기소개를 해주세요.",
            "FIT": f"{job_category} 분야에서 본인이 가장 관심있는 세부 분야는 무엇인가요?",
            "PERSONALITY": "팀 프로젝트에서 갈등이 발생했을 때 어떻게 해결했는지 경험을 말씀해주세요.",
            "TECH": "최근 IT 기술 중 가장 주목하고 있는 기술과 그 이유를 설명해주세요.",
            "FOLLOWUP": "그 기술이 실제 업무에서 어떻게 활용될 수 있을지 구체적으로 말씀해주세요."
        },
        "BM": {
            "INTRO": "경영/관리직 경험과 함께 자기소개를 해주세요.",
            "FIT": "경영/관리직에서 가장 중요하다고 생각하는 역량은 무엇인가요?",
            "PERSONALITY": "리더십을 발휘했던 경험에 대해 말씀해주세요.",
            "TECH": "경영/관리 분야에서 최근 디지털 전환의 흐름에 대해 어떻게 생각하시나요?",
            "FOLLOWUP": "디지털 전환이 조직 문화에 어떤 영향을 미칠 것으로 보시나요?"
        }
    }
    
    # 직무 카테고리별 질문 선택
    selected_questions = job_questions.get(job_category, general_questions)
    
    # 질문 선택 (해당 직무 카테고리에 없으면 기본 질문 사용)
    question = selected_questions.get(question_type, general_questions.get(question_type, general_questions["INTRO"]))
    
    return {
        "question_type": question_type,
        "question_text": question,
        "generated_by": "fixed_template"
    }

def get_job_recommendation_response(category: str = "ICT", limit: int = 10) -> Dict[str, Any]:
    """
    직무 카테고리별 고정 채용공고 추천 생성
    
    Args:
        category: 직무 카테고리 (기본값: "ICT")
        limit: 추천 결과 수 (기본값: 10)
        
    Returns:
        Dict[str, Any]: 추천 결과 데이터
    """
    # 기본 추천 결과
    recommendations = {
        "ICT": [
            {"job_posting_id": 1, "title": "백엔드 개발자", "keywords": ["Python", "Django", "AWS"], "company": "네이버"},
            {"job_posting_id": 2, "title": "프론트엔드 개발자", "keywords": ["React", "JavaScript", "TypeScript"], "company": "카카오"},
            {"job_posting_id": 3, "title": "풀스택 개발자", "keywords": ["Java", "Spring", "React"], "company": "라인"},
            {"job_posting_id": 4, "title": "데이터 엔지니어", "keywords": ["Python", "Hadoop", "Spark"], "company": "쿠팡"},
            {"job_posting_id": 5, "title": "DevOps 엔지니어", "keywords": ["Docker", "Kubernetes", "Jenkins"], "company": "토스"},
            {"job_posting_id": 6, "title": "모바일 앱 개발자", "keywords": ["iOS", "Swift", "Android"], "company": "당근마켓"},
            {"job_posting_id": 7, "title": "데이터 사이언티스트", "keywords": ["Python", "TensorFlow", "데이터 분석"], "company": "뱅크샐러드"},
            {"job_posting_id": 8, "title": "보안 엔지니어", "keywords": ["네트워크 보안", "침투 테스트", "보안 감사"], "company": "SK인포섹"},
            {"job_posting_id": 9, "title": "클라우드 아키텍트", "keywords": ["AWS", "Azure", "GCP"], "company": "NHN"},
            {"job_posting_id": 10, "title": "QA 엔지니어", "keywords": ["테스트 자동화", "Selenium", "JUnit"], "company": "우아한형제들"}
        ],
        "BM": [
            {"job_posting_id": 1, "title": "경영 컨설턴트", "keywords": ["전략 컨설팅", "비즈니스 분석", "프로젝트 관리"], "company": "매킨지"},
            {"job_posting_id": 2, "title": "프로젝트 매니저", "keywords": ["프로젝트 관리", "일정 관리", "위험 관리"], "company": "삼성SDS"},
            {"job_posting_id": 3, "title": "사업 기획자", "keywords": ["사업 전략", "시장 분석", "경쟁사 분석"], "company": "LG CNS"},
            {"job_posting_id": 4, "title": "운영 관리자", "keywords": ["운영 최적화", "프로세스 개선", "성과 관리"], "company": "롯데정보통신"},
            {"job_posting_id": 5, "title": "인사 관리자", "keywords": ["인재 채용", "인사 평가", "조직 문화"], "company": "SK C&C"}
        ],
        "SM": [
            {"job_posting_id": 1, "title": "마케팅 매니저", "keywords": ["디지털 마케팅", "브랜드 관리", "마케팅 전략"], "company": "현대자동차"},
            {"job_posting_id": 2, "title": "영업 관리자", "keywords": ["B2B 영업", "고객 관계 관리", "영업 전략"], "company": "SK텔레콤"},
            {"job_posting_id": 3, "title": "상품 기획자", "keywords": ["시장 조사", "상품 전략", "고객 니즈 분석"], "company": "LG전자"},
            {"job_posting_id": 4, "title": "디지털 마케터", "keywords": ["SEO", "소셜 미디어", "콘텐츠 마케팅"], "company": "CJ ENM"},
            {"job_posting_id": 5, "title": "고객 성공 매니저", "keywords": ["고객 만족", "고객 유지", "고객 경험"], "company": "쿠팡"}
        ]
    }
    
    # 카테고리별 추천 결과 선택
    category_recommendations = recommendations.get(category, recommendations["ICT"])
    
    # 결과 수 제한
    limited_recommendations = category_recommendations[:min(limit, len(category_recommendations))]
    
    # 응답 데이터 구성
    return {
        "status": "success",
        "category": category,
        "recommendations": limited_recommendations,
        "total_count": len(limited_recommendations),
        "generated_by": "fixed_template"
    }

def get_debate_scores() -> Dict[str, Any]:
    """
    기본 토론 점수 생성
    
    Returns:
        Dict[str, Any]: 토론 점수 데이터
    """
    return {
        "initiative_score": 3.5,
        "collaborative_score": 3.2,
        "communication_score": 3.8,
        "logic_score": 3.3,
        "problem_solving_score": 3.5,
        "voice_score": 3.7,
        "action_score": 3.9,
        "initiative_feedback": "적극성: 보통",
        "collaborative_feedback": "협력성: 보통",
        "communication_feedback": "의사소통: 양호",
        "logic_feedback": "논리성: 보통",
        "problem_solving_feedback": "문제해결: 보통",
        "voice_feedback": "음성품질: 양호",
        "action_feedback": "행동표현: 양호",
        "feedback": "전반적으로 양호한 수행을 보여주었습니다.",
        "sample_answer": "구체적인 예시와 근거를 들어 논리적으로 설명해보세요."
    }

def get_interview_feedback() -> Dict[str, Any]:
    """
    기본 면접 피드백 생성
    
    Returns:
        Dict[str, Any]: 면접 피드백 데이터
    """
    return {
        "content_score": 3.8,
        "voice_score": 4.0,
        "action_score": 3.5,
        "content_feedback": "내용 구성이 전반적으로 양호합니다.",
        "voice_feedback": "발음이 명확하고 목소리 톤이 안정적입니다.",
        "action_feedback": "시선 처리와 표정 관리가 필요합니다.",
        "feedback": "전반적으로 양호한 면접 수행을 보여주었습니다."
    }
