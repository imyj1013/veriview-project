from flask import Blueprint, request, jsonify
import logging
import random

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

recruitment_bp = Blueprint('recruitment', __name__)

# 샘플 기업 공고 데이터 (DB 연동 전 테스트용)
sample_postings = [
    {
        "id": 1,
        "category": "ICT",
        "company": "서울대학교 산학협력단",
        "deadline": "~06.02 (월)",
        "education": "학력무관",
        "skills": "빅데이터·AI(인공지능), ERP·시스템분석·설계, 데이터베이스·DBA, 금융사무·심사·추심, 투자·분석·증권·외환",
        "title": "제 11기 서울대학교 빅데이터 핀테크 AI 고급 전문가 과정",
        "experience": "경력무관",
        "employment_type": "교육생(연수생)",
        "location": "서울 관악구 외"
    },
    {
        "id": 2,
        "category": "ICT",
        "company": "서울보증보험 (주)",
        "deadline": "~06.02 (월)",
        "education": "학력무관",
        "skills": "네트워크·서버·보안, 공무원·공직, 금융사무·심사·추심, 금융·보험영업, 투자·분석·증권·외환",
        "title": "2025 SGI서울보증 전문경력직 채용",
        "experience": "경력 1년↑",
        "employment_type": "계약직",
        "location": "서울 종로구"
    },
    {
        "id": 3,
        "category": "ICT",
        "company": "한국수자원공사",
        "deadline": "~06.02 (월)",
        "education": "학력무관",
        "skills": "전산·IT기술지원, 일반사무·사무지원, 경영·기획·전략, 총무·법무·특허, 기계·금속·재료",
        "title": "2025년 한국수자원공사 하반기 체험형 인턴 공개 채용",
        "experience": "경력무관",
        "employment_type": "인턴",
        "location": "전국"
    },
    {
        "id": 4,
        "category": "RND",
        "company": "삼성전자",
        "deadline": "~06.10 (화)",
        "education": "대졸이상",
        "skills": "프론트엔드, 백엔드, 소프트웨어 엔지니어링, 인공지능",
        "title": "삼성전자 소프트웨어 개발자 채용",
        "experience": "신입",
        "employment_type": "정규직",
        "location": "서울 강남구"
    },
    {
        "id": 5,
        "category": "RND",
        "company": "LG전자",
        "deadline": "~06.15 (일)",
        "education": "대졸이상",
        "skills": "AI, 머신러닝, 딥러닝, 데이터 사이언스",
        "title": "LG전자 AI 연구원 채용",
        "experience": "경력 3년↑",
        "employment_type": "정규직",
        "location": "서울 서초구"
    }
]

@recruitment_bp.route('/posting', methods=['POST'])
def recommend_job_postings():
    """사용자 정보 기반 기업 공고 추천 API"""
    try:
        # 사용자 입력 데이터
        data = request.json
        logger.info(f"기업공고 추천 요청 받음: {data}")
        
        category = data.get('category', '')
        education = data.get('education', '')
        employment_type = data.get('employmenttype', '')
        location = data.get('location', '')
        major = data.get('major', '')
        qualification = data.get('qualification', '')
        tech_stack = data.get('tech_stack', '')
        work_experience = data.get('workexperience', '')
        
        # 추천 로직
        # 1. 카테고리 필터링
        filtered_postings = [post for post in sample_postings]
        if category:
            filtered_postings = [post for post in filtered_postings if post["category"] == category]
        
        # 2. 위치 필터링 (부분 일치)
        if location:
            location_part = location.split()[0]  # "서울 강남구" -> "서울"
            filtered_postings = [post for post in filtered_postings 
                               if location_part in post["location"]]
        
        # 3. 근무 형태 필터링
        if employment_type:
            filtered_postings = [post for post in filtered_postings 
                               if post["employment_type"] == employment_type]
        
        # 4. 경력 필터링
        if work_experience == "신입":
            filtered_postings = [post for post in filtered_postings 
                               if "신입" in post["experience"] or "경력무관" in post["experience"]]
        elif work_experience:
            filtered_postings = [post for post in filtered_postings 
                               if work_experience in post["experience"] or "경력무관" in post["experience"]]
        
        # 기술 스택 점수 계산
        scored_postings = []
        for post in filtered_postings:
            score = 100  # 기본 점수
            
            # 기술 스택 매칭
            if tech_stack and tech_stack in post["skills"]:
                score += 30
            
            # 자격증 매칭
            if qualification and "자격증" in post["skills"]:
                score += 20
            
            # 학력 매칭
            if education and (education in post["education"] or "학력무관" in post["education"]):
                score += 20
            
            # 전공 가산점
            if major and ("공학" in post["skills"] or "컴퓨터" in post["skills"]):
                score += 10
            
            scored_postings.append({
                "posting": post,
                "score": score
            })
        
        # 점수 기준 내림차순 정렬
        scored_postings.sort(key=lambda x: x["score"], reverse=True)
        
        # 결과가 없는 경우 모든 공고 반환
        if not scored_postings:
            scored_postings = [{"posting": post, "score": 50} for post in sample_postings]
        
        # 최종 추천 결과
        recommendations = [
            {
                "id": item["posting"]["id"],
                "category": item["posting"]["category"],
                "company": item["posting"]["company"],
                "deadline": item["posting"]["deadline"],
                "education": item["posting"]["education"],
                "skills": item["posting"]["skills"],
                "title": item["posting"]["title"],
                "experience": item["posting"]["experience"],
                "employment_type": item["posting"]["employment_type"],
                "location": item["posting"]["location"],
                "match_score": item["score"]
            } for item in scored_postings[:3]  # 상위 3개만 반환
        ]
        
        logger.info(f"추천 결과: {len(recommendations)}개 공고")
        return jsonify({"recommended_postings": recommendations})
        
    except Exception as e:
        logger.error(f"기업공고 추천 오류: {str(e)}")
        # 오류 발생 시 기본 추천
        default_recommendations = [
            {
                "id": post["id"],
                "category": post["category"],
                "company": post["company"],
                "deadline": post["deadline"],
                "education": post["education"],
                "skills": post["skills"],
                "title": post["title"],
                "experience": post["experience"],
                "employment_type": post["employment_type"],
                "location": post["location"],
                "match_score": 50
            } for post in sample_postings[:3]
        ]
        return jsonify({"recommended_postings": default_recommendations})
