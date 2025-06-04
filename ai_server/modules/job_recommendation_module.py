"""
공고추천 기능 모듈
백엔드의 채용공고 크롤링 데이터를 활용한 개인화 추천 시스템
"""
import logging
import requests
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobRecommendationModule:
    def __init__(self, backend_url: str = "http://localhost:4000"):
        """공고추천 모듈 초기화"""
        self.backend_url = backend_url
        self.categories = {
            "BM": "경영/관리직",
            "SM": "영업/마케팅", 
            "PS": "생산/기술직",
            "RND": "연구개발",
            "ICT": "IT/정보통신",
            "ARD": "디자인/예술",
            "MM": "미디어/방송"
        }
        logger.info("공고추천 모듈 초기화 완료")

    def get_module_status(self) -> Dict[str, Any]:
        """모듈 상태 정보 반환"""
        return {
            "is_available": True,
            "module_name": "JobRecommendationModule",
            "backend_url": self.backend_url,
            "functions": [
                "get_recommendations_by_category",
                "get_recommendations_by_interview_result", 
                "trigger_crawling",
                "get_category_statistics"
            ],
            "supported_categories": list(self.categories.keys())
        }

    def trigger_crawling(self) -> Dict[str, Any]:
        """백엔드 채용공고 크롤링 트리거"""
        try:
            logger.info("백엔드 채용공고 크롤링 요청 중...")
            response = requests.post(f"{self.backend_url}/api/job-postings/crawl", timeout=300)
            
            if response.status_code == 200:
                logger.info("채용공고 크롤링 성공")
                return {
                    "status": "success",
                    "message": "채용공고 크롤링이 완료되었습니다.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                logger.error(f"크롤링 요청 실패: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"크롤링 요청 실패: HTTP {response.status_code}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
        except Exception as e:
            logger.error(f"크롤링 트리거 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"크롤링 트리거 오류: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def get_recommendations_by_category(self, category: str, limit: int = 10) -> Dict[str, Any]:
        """카테고리별 공고 추천"""
        try:
            if category.upper() not in self.categories:
                return {
                    "status": "error",
                    "message": f"지원하지 않는 카테고리: {category}",
                    "available_categories": list(self.categories.keys())
                }

            # 실제 백엔드에서 데이터를 가져올 수 없으므로 시뮬레이션
            logger.info(f"{category} 카테고리 공고 추천 생성 중...")
            
            # 샘플 공고 데이터 생성 (실제로는 백엔드 DB에서 조회)
            sample_jobs = self._generate_sample_jobs(category, limit)
            
            return {
                "status": "success",
                "category": category,
                "category_name": self.categories[category.upper()],
                "total_count": len(sample_jobs),
                "recommendations": sample_jobs,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"카테고리별 추천 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"추천 생성 오류: {str(e)}"
            }

    def get_recommendations_by_interview_result(self, interview_scores: Dict[str, float], 
                                              limit: int = 10) -> Dict[str, Any]:
        """면접 결과 기반 맞춤 공고 추천"""
        try:
            logger.info("면접 결과 기반 맞춤 추천 생성 중...")
            
            # 점수 기반 카테고리 매칭
            recommended_category = self._match_category_by_scores(interview_scores)
            
            # 해당 카테고리의 공고 추천
            category_recommendations = self.get_recommendations_by_category(
                recommended_category, limit
            )
            
            # 개인화 메시지 추가
            personalized_message = self._generate_personalized_message(
                interview_scores, recommended_category
            )
            
            return {
                "status": "success",
                "recommended_category": recommended_category,
                "category_name": self.categories[recommended_category],
                "personalized_message": personalized_message,
                "interview_scores": interview_scores,
                "recommendations": category_recommendations.get("recommendations", []),
                "total_count": len(category_recommendations.get("recommendations", [])),
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"면접 결과 기반 추천 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"맞춤 추천 생성 오류: {str(e)}"
            }

    def get_category_statistics(self) -> Dict[str, Any]:
        """카테고리별 통계 정보"""
        try:
            logger.info("카테고리별 통계 정보 생성 중...")
            
            # 실제로는 백엔드 API를 호출하여 실제 통계를 가져와야 함
            statistics = {}
            
            for category, name in self.categories.items():
                # 샘플 통계 데이터 (실제로는 백엔드에서 조회)
                statistics[category] = {
                    "category_name": name,
                    "total_jobs": random.randint(500, 1000),
                    "new_jobs_this_week": random.randint(20, 100),
                    "avg_experience_required": f"{random.randint(1, 5)}년 이상",
                    "top_keywords": self._get_sample_keywords(category),
                    "salary_range": f"{random.randint(2500, 4000)}-{random.randint(4500, 7000)}만원"
                }
            
            return {
                "status": "success",
                "statistics": statistics,
                "total_categories": len(self.categories),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"통계 정보 생성 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"통계 정보 생성 오류: {str(e)}"
            }

    def _generate_sample_jobs(self, category: str, limit: int) -> List[Dict[str, Any]]:
        """샘플 공고 데이터 생성 (테스트용)"""
        sample_jobs = []
        
        # 카테고리별 샘플 회사 및 직무
        job_templates = {
            "BM": [
                {"company": "삼성전자", "title": "경영기획 담당자", "experience": "3년 이상"},
                {"company": "LG전자", "title": "사업개발 매니저", "experience": "5년 이상"},
                {"company": "현대자동차", "title": "전략기획 전문가", "experience": "7년 이상"},
            ],
            "ICT": [
                {"company": "네이버", "title": "백엔드 개발자", "experience": "2년 이상"},
                {"company": "카카오", "title": "프론트엔드 개발자", "experience": "3년 이상"},
                {"company": "라인", "title": "풀스택 개발자", "experience": "4년 이상"},
                {"company": "토스", "title": "데이터 엔지니어", "experience": "3년 이상"},
                {"company": "쿠팡", "title": "DevOps 엔지니어", "experience": "2년 이상"},
                {"company": "당근마켓", "title": "Android 개발자", "experience": "4년 이상"},
            ],
            "SM": [
                {"company": "아모레퍼시픽", "title": "마케팅 전문가", "experience": "3년 이상"},
                {"company": "롯데", "title": "영업 매니저", "experience": "2년 이상"},
                {"company": "신세계", "title": "브랜드 매니저", "experience": "5년 이상"},
            ]
        }
        
        templates = job_templates.get(category, job_templates["ICT"])
        
        for i in range(min(limit, len(templates) * 3)):
            template = templates[i % len(templates)]
            job = {
                "id": str(i+1),  # 백엔드 연동을 위해 문자열로 변경
                "title": template['title'],
                "company": template["company"],
                "category": category,
                "category_name": self.categories.get(category, "기타"),
                "experience": template["experience"],
                "education": random.choice(["대졸 이상", "고졸 이상", "학력무관"]),
                "deadline": self._generate_deadline(),
                "keywords": self._get_sample_keywords(category)[:3],
                "salary": f"{random.randint(3000, 6000)}만원",
                "location": random.choice(["서울", "경기", "부산", "대구", "광주"]),
                "posted_date": self._generate_posted_date()
            }
            sample_jobs.append(job)
            
        return sample_jobs[:limit]

    def _match_category_by_scores(self, scores: Dict[str, float]) -> str:
        """면접 점수를 기반으로 적합한 카테고리 매칭"""
        
        # 점수 기반 카테고리 매칭 로직
        if scores.get("technical_score", 0) >= 4.0:
            return "ICT"  # 기술 점수가 높으면 IT 추천
        elif scores.get("communication_score", 0) >= 4.0:
            return "SM"   # 의사소통이 좋으면 영업/마케팅 추천
        elif scores.get("logic_score", 0) >= 4.0:
            return "BM"   # 논리성이 좋으면 경영/관리 추천
        elif scores.get("collaborative_score", 0) >= 4.0:
            return "PS"   # 협력성이 좋으면 생산/기술 추천
        elif scores.get("problem_solving_score", 0) >= 4.0:
            return "RND"  # 문제해결능력이 좋으면 연구개발 추천
        else:
            # 종합 점수를 고려한 기본 추천
            avg_score = sum(scores.values()) / len(scores) if scores else 3.0
            if avg_score >= 4.0:
                return "ICT"
            elif avg_score >= 3.5:
                return "BM"
            else:
                return "SM"

    def _generate_personalized_message(self, scores: Dict[str, float], category: str) -> str:
        """개인화된 추천 메시지 생성"""
        
        # 가장 높은 점수 영역 찾기
        if not scores:
            return f"{self.categories[category]} 분야의 채용공고를 추천드립니다."
        
        max_score_area = max(scores, key=scores.get)
        max_score = scores[max_score_area]
        
        messages = {
            "communication_score": f"뛰어난 의사소통 능력을 바탕으로 {self.categories[category]} 분야에서 성공하실 수 있을 것입니다.",
            "technical_score": f"우수한 기술적 역량을 인정받아 {self.categories[category]} 분야의 전문가로 성장하세요.",
            "logic_score": f"논리적 사고력이 돋보이는 만큼 {self.categories[category]} 분야에서 핵심 인재가 되실 수 있습니다.",
            "collaborative_score": f"협업 능력이 뛰어나 {self.categories[category]} 분야의 팀 중심 업무에 적합합니다.",
            "problem_solving_score": f"문제 해결 능력이 우수하여 {self.categories[category]} 분야에서 혁신을 이끌 수 있습니다."
        }
        
        base_message = messages.get(max_score_area, f"{self.categories[category]} 분야를 추천드립니다.")
        
        if max_score >= 4.5:
            return f"🌟 {base_message} (상위 10% 수준)"
        elif max_score >= 4.0:
            return f"⭐ {base_message} (상위 25% 수준)"
        else:
            return f"📈 {base_message} 추가 역량 개발을 통해 더욱 성장하실 수 있습니다."

    def _get_sample_keywords(self, category: str) -> List[str]:
        """카테고리별 샘플 키워드"""
        keywords = {
            "BM": ["경영기획", "사업개발", "전략기획", "경영분석", "기획관리"],
            "SM": ["마케팅", "영업", "브랜드", "고객관리", "시장분석"],
            "PS": ["생산관리", "품질관리", "공정개선", "제조", "기술지원"],
            "RND": ["연구개발", "신제품개발", "기술연구", "실험", "분석"],
            "ICT": ["개발", "프로그래밍", "시스템", "네트워크", "데이터베이스"],
            "ARD": ["디자인", "UI/UX", "그래픽", "웹디자인", "브랜딩"],
            "MM": ["미디어", "콘텐츠", "방송", "영상", "편집"]
        }
        return keywords.get(category, ["일반", "기타", "사무"])

    def _generate_deadline(self) -> str:
        """마감일 생성"""
        future_date = datetime.now() + timedelta(days=random.randint(7, 30))
        return future_date.strftime("%m/%d")

    def _generate_posted_date(self) -> str:
        """게시일 생성"""
        past_date = datetime.now() - timedelta(days=random.randint(1, 14))
        return past_date.strftime("%Y-%m-%d")

    def test_all_functions(self) -> Dict[str, Any]:
        """모든 기능 테스트"""
        test_results = {
            "module_status": self.get_module_status(),
            "category_recommendations": {},
            "statistics": {},
            "interview_based_recommendation": {},
            "overall_status": "success"
        }
        
        try:
            # 카테고리별 추천 테스트
            for category in ["ICT", "BM", "SM"]:
                result = self.get_recommendations_by_category(category, 3)
                test_results["category_recommendations"][category] = result
            
            # 통계 정보 테스트
            test_results["statistics"] = self.get_category_statistics()
            
            # 면접 결과 기반 추천 테스트
            sample_scores = {
                "communication_score": 4.2,
                "technical_score": 3.8,
                "logic_score": 4.0
            }
            test_results["interview_based_recommendation"] = self.get_recommendations_by_interview_result(sample_scores, 5)
            
            logger.info("모든 공고추천 기능 테스트 완료")
            
        except Exception as e:
            logger.error(f"공고추천 기능 테스트 오류: {str(e)}")
            test_results["overall_status"] = "error"
            test_results["error"] = str(e)
        
        return test_results


# 실행 예시
if __name__ == "__main__":
    print("공고추천 모듈 테스트 시작...")
    
    recommender = JobRecommendationModule()
    
    # 모듈 상태 확인
    print("=== 모듈 상태 ===")
    status = recommender.get_module_status()
    print(f"모듈 상태: {status}")
    
    # 카테고리별 추천 테스트
    print("\n=== ICT 카테고리 추천 ===")
    ict_jobs = recommender.get_recommendations_by_category("ICT", 3)
    for job in ict_jobs.get("recommendations", []):
        print(f"- {job['company']}: {job['title']} ({job['experience']})")
    
    # 면접 결과 기반 추천 테스트
    print("\n=== 면접 결과 기반 추천 ===")
    sample_scores = {
        "communication_score": 4.2,
        "technical_score": 3.8,
        "logic_score": 4.0,
        "collaborative_score": 3.5
    }
    
    personalized = recommender.get_recommendations_by_interview_result(sample_scores, 3)
    print(f"추천 카테고리: {personalized.get('category_name')}")
    print(f"개인화 메시지: {personalized.get('personalized_message')}")
    
    # 통계 정보 테스트
    print("\n=== 카테고리 통계 ===")
    stats = recommender.get_category_statistics()
    for category, info in stats.get("statistics", {}).items():
        print(f"{info['category_name']}: {info['total_jobs']}개 공고")
    
    print("\n공고추천 모듈 테스트 완료!")
