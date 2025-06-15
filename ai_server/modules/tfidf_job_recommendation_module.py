"""
TF-IDF 기반 공고추천 기능 모듈
기술스택, 자격증, 전공, 경력, 학력을 기준으로 한 개인화 추천 시스템
백엔드 JobPosting 엔티티와 완전 호환
"""
import logging
import requests
import random
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TFIDFJobRecommendationModule:
    def __init__(self, backend_url: str = "http://localhost:4000"):
        """TF-IDF 기반 공고추천 모듈 초기화"""
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
        
        # TF-IDF 벡터라이저 초기화
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            token_pattern=r'\b[a-zA-Z가-힣]+\b',
            ngram_range=(1, 2),
            max_features=5000,
            min_df=1
        )
        
        # 희소 기술 정보 (희소도가 0.7 이상인 기술)
        self.rare_skills = {
            "pytorch": 0.8,
            "tensorflow": 0.75,
            "nvidia_deepstream": 0.95,
            "openface": 0.9,
            "hadoop": 0.85,
            "spark": 0.75,
            "flutter": 0.78,
            "kubernetes": 0.83,
            "istio": 0.92,
            "graphql": 0.82
        }
        
        # 캐시 초기화
        self.job_posting_cache = []
        self.cache_last_updated = None
        self.tfidf_matrix = None
        self.job_features = None
        
        # 캐시 업데이트
        self._update_job_posting_cache()
        
        logger.info("TF-IDF 기반 공고추천 모듈 초기화 완료")

    def get_module_status(self) -> Dict[str, Any]:
        """모듈 상태 정보 반환"""
        return {
            "is_available": True,
            "module_name": "TFIDFJobRecommendationModule",
            "backend_url": self.backend_url,
            "cache_status": {
                "last_updated": self.cache_last_updated,
                "cache_size": len(self.job_posting_cache)
            },
            "rare_skills": list(self.rare_skills.keys()),
            "functions": [
                "get_recommendations_by_skills",
                "get_recommendations_by_profile", 
                "get_rare_skills_info",
                "update_job_posting_cache"
            ],
            "supported_categories": list(self.categories.keys())
        }

    def _update_job_posting_cache(self) -> bool:
        """백엔드에서 최신 채용공고 데이터 가져오기"""
        try:
            logger.info("백엔드에서 채용공고 데이터 가져오는 중...")
            
            # 먼저 백엔드에 CSV 데이터가 있는지 확인하고 없으면 임포트
            try:
                import_response = requests.post(f"{self.backend_url}/api/job-postings/import", timeout=30)
                if import_response.status_code == 200:
                    logger.info("백엔드 CSV 데이터 임포트 완료")
            except Exception as e:
                logger.warning(f"백엔드 CSV 임포트 시도 실패: {str(e)}")
            
            # 백엔드 API 호출 - 임시로 샘플 데이터 생성
            response = requests.get(f"{self.backend_url}/api/job-postings/all", timeout=10)
            
            if response.status_code == 200:
                job_postings = response.json()
                
                if isinstance(job_postings, list) and len(job_postings) > 0:
                    self.job_posting_cache = job_postings
                    self.cache_last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # TF-IDF 행렬 업데이트
                    self._update_tfidf_matrix()
                    
                    logger.info(f"채용공고 캐시 업데이트 완료: {len(job_postings)}개 공고")
                    return True
                else:
                    logger.warning("백엔드에서 받은 채용공고 데이터가 없습니다. 샘플 데이터 사용")
                    self._generate_sample_job_postings()
                    return False
            else:
                logger.error(f"백엔드 API 호출 실패: {response.status_code}")
                self._generate_sample_job_postings()
                return False
            
                
        except Exception as e:
            logger.error(f"채용공고 캐시 업데이트 오류: {str(e)}")
            self._generate_sample_job_postings()
            return False

    def _generate_sample_job_postings(self) -> None:
        """샘플 채용공고 데이터 생성 (백엔드 연결 실패 시)"""
        logger.info("샘플 채용공고 데이터 생성 중...")
        
        sample_postings = []
        categories = list(self.categories.keys())
        
        for i in range(100):  # 100개 샘플 생성
            category = random.choice(categories)
            
            tech_stacks = []
            if category == "ICT":
                tech_stacks = random.sample([
                    "Java", "Python", "JavaScript", "React", "Vue.js", "Angular",
                    "Spring", "Django", "Flask", "Node.js", "Express", "MySQL",
                    "MongoDB", "PostgreSQL", "AWS", "Azure", "GCP", "Docker",
                    "Kubernetes", "CI/CD", "Git", "Linux", "Windows", "MacOS",
                    "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy"
                ], k=random.randint(3, 8))
            
            # 희소 기술 추가 (10% 확률)
            if category == "ICT" and random.random() < 0.1:
                rare_skill = random.choice(list(self.rare_skills.keys()))
                if rare_skill not in tech_stacks:
                    tech_stacks.append(rare_skill)
            
            job_posting = {
                "id": i + 1,
                "title": f"Sample Job {i+1}",
                "company": f"Company {i+1}",
                "category": category,
                "techStacks": tech_stacks,
                "certificateList": [],
                "majorList": [],
                "careerYear": random.randint(0, 10),
                "educationLevel": random.choice(["고졸이상", "초대졸이상", "대졸이상", "석사이상", "박사이상"]),
                "description": f"This is a sample job posting for {category} category."
            }
            
            sample_postings.append(job_posting)
        
        self.job_posting_cache = sample_postings
        self.cache_last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # TF-IDF 행렬 업데이트
        self._update_tfidf_matrix()
        
        logger.info(f"샘플 채용공고 데이터 생성 완료: {len(sample_postings)}개 공고")

    def _update_tfidf_matrix(self) -> None:
        """채용공고 데이터로 TF-IDF 행렬 생성"""
        try:
            if not self.job_posting_cache:
                logger.warning("채용공고 캐시가 비어있어 TF-IDF 행렬을 생성할 수 없습니다.")
                return
            
            # 각 채용공고의 특성을 추출하여 문서 생성
            job_features = []
            
            for job in self.job_posting_cache:
                # 기술 스택, 자격증, 전공 등을 하나의 문서로 결합
                features = []
                
                # 기술 스택 추가
                tech_stacks = job.get("techStacks", [])
                if tech_stacks:
                    features.extend(tech_stacks)
                
                # 자격증 추가
                certificates = job.get("certificateList", [])
                if certificates:
                    features.extend(certificates)
                
                # 전공 추가
                majors = job.get("majorList", [])
                if majors:
                    features.extend(majors)
                
                # 경력 추가
                career_year = job.get("careerYear")
                if career_year is not None:
                    features.append(f"경력{career_year}년")
                
                # 학력 추가
                education = job.get("educationLevel")
                if education:
                    features.append(education)
                
                # 카테고리 추가
                category = job.get("category")
                if category:
                    features.append(category)
                
                # 문서로 결합
                job_features.append(" ".join(features))
            
            # TF-IDF 벡터라이저 적합 및 변환
            self.job_features = job_features
            tfidf_matrix = self.vectorizer.fit_transform(job_features)
            self.tfidf_matrix = tfidf_matrix
            
            logger.info(f"TF-IDF 행렬 생성 완료: {tfidf_matrix.shape}")
            
        except Exception as e:
            logger.error(f"TF-IDF 행렬 생성 오류: {str(e)}")

    def get_recommendations_by_skills(self, skills: List[str], limit: int = 10) -> Dict[str, Any]:
        """기술 스택 기반 공고 추천"""
        try:
            if not self.tfidf_matrix or not self.job_posting_cache:
                self._update_job_posting_cache()
                
            if not skills:
                return {
                    "status": "error",
                    "message": "추천을 위한 기술 스택이 필요합니다."
                }
            
            # 사용자 기술 스택을 TF-IDF 벡터로 변환
            user_features = " ".join(skills)
            user_vector = self.vectorizer.transform([user_features])
            
            # 코사인 유사도 계산
            similarities = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
            
            # 희소 기술에 보너스 점수 부여
            for i, job in enumerate(self.job_posting_cache):
                tech_stacks = job.get("techStacks", [])
                for tech in tech_stacks:
                    if tech.lower() in self.rare_skills and self.rare_skills[tech.lower()] > 0.7:
                        # 희소도가 0.7 이상인 기술에는 보너스 점수 부여
                        bonus = self.rare_skills[tech.lower()] * 0.3  # 최대 0.3 보너스
                        similarities[i] += bonus
            
            # 유사도가 높은 순서대로 정렬
            job_indices = similarities.argsort()[::-1][:limit]
            
            # 추천 결과 생성
            recommendations = []
            for idx in job_indices:
                job = self.job_posting_cache[idx]
                
                # 희소 기술 표시
                rare_techs = []
                tech_stacks = job.get("techStacks", [])
                for tech in tech_stacks:
                    if tech.lower() in self.rare_skills and self.rare_skills[tech.lower()] > 0.7:
                        rare_techs.append({
                            "name": tech,
                            "rarity": self.rare_skills[tech.lower()]
                        })
                
                recommendations.append({
                    "id": job.get("id"),
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "category": job.get("category", ""),
                    "category_name": self.categories.get(job.get("category", ""), "기타"),
                    "similarity_score": float(similarities[idx]),
                    "tech_stacks": tech_stacks,
                    "rare_skills": rare_techs,
                    "certificates": job.get("certificateList", []),
                    "majors": job.get("majorList", []),
                    "career_year": job.get("careerYear"),
                    "education_level": job.get("educationLevel", "")
                })
            
            return {
                "status": "success",
                "total_count": len(recommendations),
                "recommendations": recommendations,
                "user_skills": skills,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"기술 스택 기반 추천 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"추천 생성 오류: {str(e)}"
            }

    def get_recommendations_by_profile(self, profile: Dict[str, Any], limit: int = 10) -> Dict[str, Any]:
        """사용자 프로필 기반 공고 추천 (백엔드 RecruitmentRequest/Response 형식 지원)"""
        try:
            if not self.tfidf_matrix or not self.job_posting_cache:
                self._update_job_posting_cache()
            
            # 프로필에서 특성 추출
            features = []
            
            # 기술 스택 추출
            skills = profile.get("techStacks", [])
            if skills:
                features.extend(skills)
            
            # 자격증 추출
            certificates = profile.get("certificateList", [])
            if certificates:
                features.extend(certificates)
            
            # 전공 추출
            majors = profile.get("majorList", [])
            if majors:
                features.extend(majors)
            
            # 경력 추출
            career_year = profile.get("careerYear")
            if career_year is not None:
                features.append(f"경력{career_year}년")
            
            # 학력 추출
            education = profile.get("educationLevel")
            if education:
                features.append(education)
            
            # 특성이 없는 경우
            if not features:
                return {
                    "status": "error",
                    "message": "추천을 위한 프로필 정보가 충분하지 않습니다."
                }
            
            # 사용자 특성을 TF-IDF 벡터로 변환
            user_features = " ".join(features)
            user_vector = self.vectorizer.transform([user_features])
            
            # 코사인 유사도 계산
            similarities = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
            
            # 희소 기술에 보너스 점수 부여
            for i, job in enumerate(self.job_posting_cache):
                tech_stacks = job.get("techStacks", [])
                for tech in tech_stacks:
                    if tech.lower() in self.rare_skills and self.rare_skills[tech.lower()] > 0.7:
                        # 희소도가 0.7 이상인 기술에는 보너스 점수 부여
                        bonus = self.rare_skills[tech.lower()] * 0.3  # 최대 0.3 보너스
                        similarities[i] += bonus
            
            # 유사도가 높은 순서대로 정렬
            job_indices = similarities.argsort()[::-1][:limit]
            
            # 추천 결과 생성 (백엔드 Response 형식)
            recommendations = []
            for idx in job_indices:
                job = self.job_posting_cache[idx]
                
                # 희소 기술 표시
                rare_techs = []
                tech_stacks = job.get("techStacks", [])
                for tech in tech_stacks:
                    if tech.lower() in self.rare_skills and self.rare_skills[tech.lower()] > 0.7:
                        rare_techs.append({
                            "name": tech,
                            "rarity": self.rare_skills[tech.lower()]
                        })
                
                # 백엔드 응답 형식에 맞게 구성
                recommendations.append({
                    "jobPostingId": job.get("id"),
                    "title": job.get("title", ""),
                    "corporation": job.get("company", ""),
                    "similarity": float(similarities[idx]),
                    "techStacks": tech_stacks,
                    "rare_skills": rare_techs,
                    "certificates": job.get("certificateList", []),
                    "majors": job.get("majorList", []),
                    "careerYear": job.get("careerYear"),
                    "educationLevel": job.get("educationLevel", "")
                })
            
            return {
                "status": "success",
                "posting": recommendations,
                "totalCount": len(recommendations),
                "userId": profile.get("userId", None),
                "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"프로필 기반 추천 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"추천 생성 오류: {str(e)}"
            }

    def get_rare_skills_info(self) -> Dict[str, Any]:
        """희소 기술 정보 반환"""
        try:
            # 희소도 기준으로 정렬
            sorted_skills = sorted(
                self.rare_skills.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            rare_skills_info = []
            for skill, rarity in sorted_skills:
                # 해당 기술을 가진 공고 수 계산
                job_count = sum(
                    1 for job in self.job_posting_cache 
                    if skill in [tech.lower() for tech in job.get("techStacks", [])]
                )
                
                # 인재 수요 정도 계산 (희소도에 비례)
                demand_level = "상" if rarity > 0.85 else "중" if rarity > 0.75 else "하"
                
                rare_skills_info.append({
                    "name": skill,
                    "rarity": rarity,
                    "job_count": job_count,
                    "demand_level": demand_level,
                    "description": self._get_skill_description(skill)
                })
            
            return {
                "status": "success",
                "rare_skills": rare_skills_info,
                "total_count": len(rare_skills_info),
                "last_updated": self.cache_last_updated
            }
            
        except Exception as e:
            logger.error(f"희소 기술 정보 조회 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"희소 기술 정보 조회 오류: {str(e)}"
            }

    def _get_skill_description(self, skill: str) -> str:
        """기술 설명 생성"""
        descriptions = {
            "pytorch": "딥러닝 프레임워크로, 동적 계산 그래프를 지원하며 연구 및 산업 분야에서 널리 사용됩니다.",
            "tensorflow": "구글에서 개발한 머신러닝 프레임워크로, 대규모 딥러닝 모델 개발에 활용됩니다.",
            "nvidia_deepstream": "NVIDIA의 동영상 분석 SDK로, 실시간 영상 처리 및 AI 추론에 특화되어 있습니다.",
            "openface": "얼굴 인식 및 표정 분석을 위한 오픈소스 라이브러리입니다.",
            "hadoop": "대용량 데이터 분산 처리를 위한 오픈소스 프레임워크입니다.",
            "spark": "인메모리 기반의 빅데이터 처리 엔진으로, 데이터 분석에 널리 사용됩니다.",
            "flutter": "구글에서 개발한 크로스 플랫폼 모바일 애플리케이션 개발 프레임워크입니다.",
            "kubernetes": "컨테이너화된 애플리케이션의 자동 배포, 스케일링 등을 관리하는 오픈소스 시스템입니다.",
            "istio": "마이크로서비스 간의 트래픽 및 API를 관리하는 서비스 메시 솔루션입니다.",
            "graphql": "API를 위한 쿼리 언어로, 클라이언트가 필요한 데이터를 정확히 요청할 수 있게 해줍니다."
        }
        
        return descriptions.get(skill, f"{skill}은(는) 소프트웨어 개발 분야에서 희소한 기술입니다.")

    def trigger_crawling(self) -> Dict[str, Any]:
        """백엔드 채용공고 크롤링 트리거"""
        try:
            logger.info("백엔드 채용공고 크롤링 요청 중...")
            response = requests.post(f"{self.backend_url}/api/job-postings/crawl", timeout=300)
            
            if response.status_code == 200:
                logger.info("채용공고 크롤링 성공")
                
                # 크롤링 성공 후 캐시 업데이트
                self._update_job_posting_cache()
                
                return {
                    "status": "success",
                    "message": "채용공고 크롤링 및 캐시 업데이트가 완료되었습니다.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cache_size": len(self.job_posting_cache)
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

    def test_module(self) -> Dict[str, Any]:
        """모듈 테스트"""
        test_results = {
            "module_status": self.get_module_status(),
            "skills_recommendations": None,
            "profile_recommendations": None,
            "rare_skills_info": None,
            "overall_status": "success"
        }
        
        try:
            # 기술 스택 기반 추천 테스트
            test_skills = ["Python", "React", "AWS"]
            skills_result = self.get_recommendations_by_skills(test_skills, 3)
            test_results["skills_recommendations"] = skills_result
            
            # 프로필 기반 추천 테스트
            test_profile = {
                "userId": 1,
                "techStacks": ["Java", "Spring", "MySQL"],
                "certificateList": ["정보처리기사"],
                "majorList": ["컴퓨터공학"]
            }
            profile_result = self.get_recommendations_by_profile(test_profile, 3)
            test_results["profile_recommendations"] = profile_result
            
            # 희소 기술 정보 테스트
            rare_skills_result = self.get_rare_skills_info()
            test_results["rare_skills_info"] = rare_skills_result
            
            return test_results
            
        except Exception as e:
            logger.error(f"모듈 테스트 오류: {str(e)}")
            test_results["overall_status"] = "error"
            test_results["error"] = str(e)
            return test_results


# 실행 예시
if __name__ == "__main__":
    print("TF-IDF 기반 공고추천 모듈 테스트")
    
    recommender = TFIDFJobRecommendationModule()
    
    # 모듈 상태 확인
    status = recommender.get_module_status()
    print(f"모듈 상태: {status}")
    
    # 기술 스택 기반 추천 테스트
    print("\n기술 스택 기반 추천 테스트:")
    skills_result = recommender.get_recommendations_by_skills(["Python", "React", "AWS"], 3)
    print(f"추천 결과: {skills_result.get('total_count')}개 공고")
    
    # 프로필 기반 추천 테스트
    print("\n프로필 기반 추천 테스트:")
    test_profile = {
        "userId": 1,
        "techStacks": ["Java", "Spring", "MySQL"],
        "certificateList": ["정보처리기사"],
        "majorList": ["컴퓨터공학"]
    }
    profile_result = recommender.get_recommendations_by_profile(test_profile, 3)
    print(f"추천 결과: {profile_result.get('totalCount')}개 공고")
    
    # 희소 기술 정보 테스트
    print("\n희소 기술 정보 테스트:")
    rare_skills_result = recommender.get_rare_skills_info()
    print(f"희소 기술: {rare_skills_result.get('total_count')}개")
    
    print("\nTF-IDF 기반 공고추천 모듈 테스트 완료!")
