#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 서버 통합 테스트 러너
전체 시스템의 연동 상태를 확인합니다.
"""

import requests
import json
import time
import logging
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class AIServerTester:
    def __init__(self, ai_server_url="http://localhost:5000", backend_url="http://localhost:4000"):
        self.ai_server_url = ai_server_url
        self.backend_url = backend_url
        self.test_results = {}
    
    def test_ai_server_health(self) -> bool:
        """AI 서버 헬스 체크"""
        try:
            logger.info("AI 서버 헬스 체크 중...")
            response = requests.get(f"{self.ai_server_url}/ai/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("AI 서버 정상 작동")
                logger.info(f"   - 서비스 상태: {data.get('services', {})}")
                self.test_results["ai_health"] = {"status": "success", "data": data}
                return True
            else:
                logger.error(f"AI 서버 헬스 체크 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"AI 서버 연결 실패: {str(e)}")
            self.test_results["ai_health"] = {"status": "failed", "error": str(e)}
            return False
    
    def test_backend_connection(self) -> bool:
        """백엔드 서버 연결 테스트"""
        try:
            logger.info("백엔드 서버 연결 테스트 중...")
            response = requests.get(f"{self.backend_url}/api/test", timeout=5)
            
            if response.status_code == 200:
                logger.info("백엔드 서버 정상 작동")
                self.test_results["backend_health"] = {"status": "success"}
                return True
            else:
                logger.warning(f"백엔드 서버 응답: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"백엔드 서버 연결 실패: {str(e)}")
            self.test_results["backend_health"] = {"status": "failed", "error": str(e)}
            return False
    
    def test_job_recommendation_api(self) -> bool:
        """공고추천 API 테스트"""
        try:
            logger.info("🔍 공고추천 API 테스트 중...")
            
            # 1. 카테고리 목록 조회 테스트
            response = requests.get(f"{self.ai_server_url}/ai/jobs/categories", timeout=10)
            if response.status_code == 200:
                categories = response.json()
                logger.info(f"✅ 카테고리 조회 성공: {len(categories.get('categories', {}))}개")
            else:
                logger.error(f"❌ 카테고리 조회 실패: HTTP {response.status_code}")
                return False
            
            # 2. ICT 카테고리 추천 테스트
            test_data = {
                "category": "ICT",
                "limit": 5
            }
            response = requests.post(
                f"{self.ai_server_url}/ai/jobs/recommend",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                recommendations = result.get('recommendations', [])
                logger.info(f"✅ ICT 공고추천 성공: {len(recommendations)}개 추천")
                
                # 샘플 추천 결과 출력
                if recommendations:
                    sample = recommendations[0]
                    logger.info(f"   - 샘플: {sample.get('company')} - {sample.get('title')}")
                
                self.test_results["job_recommendation"] = {"status": "success", "count": len(recommendations)}
                return True
            else:
                logger.error(f"❌ 공고추천 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 공고추천 API 테스트 실패: {str(e)}")
            self.test_results["job_recommendation"] = {"status": "failed", "error": str(e)}
            return False
    
    def test_backend_integration(self) -> bool:
        """백엔드 연동 테스트 (공고추천)"""
        try:
            logger.info("🔍 백엔드 연동 테스트 중...")
            
            # 백엔드 형식에 맞는 요청 데이터
            test_data = {
                "user_id": "test_user",
                "category": "ICT",
                "workexperience": "경력무관",
                "education": "대졸",
                "major": "컴퓨터공학",
                "location": "서울",
                "employmenttype": "정규직"
            }
            
            response = requests.post(
                f"{self.ai_server_url}/ai/recruitment/posting",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                posting_list = result.get('posting', [])
                logger.info(f"✅ 백엔드 연동 성공: {len(posting_list)}개 공고 반환")
                
                # 응답 형식 확인
                if posting_list:
                    sample = posting_list[0]
                    required_fields = ['job_posting_id', 'title', 'keyword', 'corporation']
                    missing_fields = [field for field in required_fields if field not in sample]
                    
                    if not missing_fields:
                        logger.info("✅ 응답 형식 검증 성공")
                        logger.info(f"   - 샘플: {sample.get('corporation')} - {sample.get('title')}")
                        self.test_results["backend_integration"] = {"status": "success", "count": len(posting_list)}
                        return True
                    else:
                        logger.error(f"❌ 응답 형식 오류: 누락된 필드 {missing_fields}")
                        return False
                
            else:
                logger.error(f"❌ 백엔드 연동 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 백엔드 연동 테스트 실패: {str(e)}")
            self.test_results["backend_integration"] = {"status": "failed", "error": str(e)}
            return False
    
    def test_debate_api(self) -> bool:
        """토론면접 API 테스트"""
        try:
            logger.info("🔍 토론면접 API 테스트 중...")
            
            # AI 입론 생성 테스트
            test_data = {
                "topic": "인공지능",
                "position": "PRO"
            }
            
            response = requests.post(
                f"{self.ai_server_url}/ai/debate/1/ai-opening",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result.get('ai_opening_text', '')
                
                if ai_text and len(ai_text) > 10:
                    logger.info("✅ 토론면접 AI 입론 생성 성공")
                    logger.info(f"   - AI 응답 길이: {len(ai_text)}자")
                    self.test_results["debate_api"] = {"status": "success", "response_length": len(ai_text)}
                    return True
                else:
                    logger.error("❌ AI 입론 텍스트가 비어있음")
                    return False
            else:
                logger.error(f"❌ 토론면접 API 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 토론면접 API 테스트 실패: {str(e)}")
            self.test_results["debate_api"] = {"status": "failed", "error": str(e)}
            return False
    
    def test_interview_api(self) -> bool:
        """개인면접 API 테스트"""
        try:
            logger.info("🔍 개인면접 API 테스트 중...")
            
            # 개인면접 시작 테스트
            response = requests.post(
                f"{self.ai_server_url}/ai/interview/start",
                json={},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                interview_id = result.get('interview_id')
                
                if interview_id:
                    logger.info(f"✅ 개인면접 시작 성공: ID {interview_id}")
                    
                    # 질문 생성 테스트
                    question_response = requests.get(
                        f"{self.ai_server_url}/ai/interview/{interview_id}/question?type=general",
                        timeout=10
                    )
                    
                    if question_response.status_code == 200:
                        question_data = question_response.json()
                        question = question_data.get('question', '')
                        
                        if question:
                            logger.info("✅ 개인면접 질문 생성 성공")
                            logger.info(f"   - 질문: {question[:50]}...")
                            self.test_results["interview_api"] = {"status": "success", "interview_id": interview_id}
                            return True
                        else:
                            logger.error("❌ 질문이 비어있음")
                            return False
                    else:
                        logger.error(f"❌ 질문 생성 실패: HTTP {question_response.status_code}")
                        return False
                else:
                    logger.error("❌ interview_id가 없음")
                    return False
            else:
                logger.error(f"❌ 개인면접 시작 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 개인면접 API 테스트 실패: {str(e)}")
            self.test_results["interview_api"] = {"status": "failed", "error": str(e)}
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        logger.info("🚀 AI 서버 통합 테스트 시작")
        logger.info("=" * 60)
        
        start_time = time.time()
        test_results = {
            "ai_server_health": self.test_ai_server_health(),
            "backend_connection": self.test_backend_connection(),
            "job_recommendation": self.test_job_recommendation_api(),
            "backend_integration": self.test_backend_integration(),
            "debate_api": self.test_debate_api(),
            "interview_api": self.test_interview_api()
        }
        
        end_time = time.time()
        
        # 결과 요약
        logger.info("=" * 60)
        logger.info("📊 테스트 결과 요약")
        logger.info("=" * 60)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name:<20}: {status}")
        
        logger.info("-" * 60)
        logger.info(f"총 테스트: {total_tests}")
        logger.info(f"성공: {passed_tests}")
        logger.info(f"실패: {total_tests - passed_tests}")
        logger.info(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"실행 시간: {end_time - start_time:.2f}초")
        
        # 상세 결과
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "execution_time": end_time - start_time,
            "test_results": test_results,
            "detailed_results": self.test_results
        }
        
        return summary
    
    def print_troubleshooting_guide(self):
        """문제 해결 가이드 출력"""
        logger.info("\n🔧 문제 해결 가이드")
        logger.info("=" * 40)
        logger.info("1. AI 서버가 실행 중인지 확인: python server_runner.py")
        logger.info("2. 백엔드 서버가 실행 중인지 확인: gradlew bootRun")
        logger.info("3. 포트 충돌 확인: 5000(AI), 4000(백엔드)")
        logger.info("4. 방화벽 설정 확인")
        logger.info("5. 필요한 모듈이 모두 설치되었는지 확인")


def main():
    """메인 실행 함수"""
    print("\n🧪 VeriView AI 서버 통합 테스트")
    print("=" * 50)
    
    tester = AIServerTester()
    
    try:
        # 전체 테스트 실행
        results = tester.run_all_tests()
        
        # 실패한 테스트가 있으면 문제 해결 가이드 출력
        if results["failed_tests"] > 0:
            tester.print_troubleshooting_guide()
        
        # 테스트 완료 메시지
        if results["success_rate"] == 100:
            print("\n🎉 모든 테스트가 성공했습니다!")
            print("시스템이 정상적으로 연동되어 작동합니다.")
        elif results["success_rate"] >= 80:
            print("\n⚠️ 대부분의 테스트가 성공했습니다.")
            print("일부 기능에 문제가 있을 수 있습니다.")
        else:
            print("\n❌ 여러 테스트가 실패했습니다.")
            print("시스템 설정을 확인해주세요.")
        
        return results
        
    except Exception as e:
        logger.error(f"테스트 실행 중 오류 발생: {str(e)}")
        return None


if __name__ == "__main__":
    results = main()
    
    # 스크리프트 종료 코드 설정
    if results and results["success_rate"] == 100:
        exit(0)  # 모든 테스트 성공
    else:
        exit(1)  # 일부 또는 모든 테스트 실패
