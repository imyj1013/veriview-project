#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 백엔드 연동 테스트 스크립트
main_server.py와 test_server.py의 백엔드 연동 상태를 확인하는 통합 테스트

실행 방법: python backend_integration_test.py
"""
import requests
import json
import time
import sys
import subprocess
import logging
from typing import Dict, Any, Optional
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class BackendIntegrationTester:
    def __init__(self, ai_server_url="http://localhost:5000", backend_url="http://localhost:4000"):
        """백엔드 연동 테스터 초기화"""
        self.ai_server_url = ai_server_url
        self.backend_url = backend_url
        self.test_results = {}
        
    def test_server_availability(self, server_type: str = "both") -> Dict[str, Any]:
        """서버 가용성 테스트"""
        results = {}
        
        # AI 서버 테스트
        if server_type in ["both", "ai"]:
            try:
                response = requests.get(f"{self.ai_server_url}/ai/health", timeout=5)
                results["ai_server"] = {
                    "status": "available" if response.status_code == 200 else "error",
                    "response_code": response.status_code,
                    "data": response.json() if response.status_code == 200 else None
                }
                logger.info(f"AI 서버 상태: {results['ai_server']['status']}")
            except Exception as e:
                results["ai_server"] = {
                    "status": "unavailable",
                    "error": str(e)
                }
                logger.error(f"AI 서버 연결 실패: {str(e)}")
        
        # 백엔드 서버 테스트
        if server_type in ["both", "backend"]:
            try:
                response = requests.get(f"{self.backend_url}/api/test", timeout=5)
                results["backend_server"] = {
                    "status": "available" if response.status_code == 200 else "error",
                    "response_code": response.status_code,
                    "data": response.json() if response.status_code == 200 else None
                }
                logger.info(f"백엔드 서버 상태: {results['backend_server']['status']}")
            except Exception as e:
                results["backend_server"] = {
                    "status": "unavailable", 
                    "error": str(e)
                }
                logger.error(f"백엔드 서버 연결 실패: {str(e)}")
        
        return results

    def test_job_recommendation_integration(self) -> Dict[str, Any]:
        """공고추천 백엔드 연동 테스트"""
        logger.info("🔍 공고추천 백엔드 연동 테스트 시작")
        
        test_data = {
            "user_id": "test_user",
            "category": "ICT",
            "workexperience": "경력무관",
            "education": "대졸",
            "major": "컴퓨터공학",
            "location": "서울",
            "employmenttype": "정규직"
        }
        
        results = {
            "test_name": "job_recommendation_integration",
            "test_data": test_data,
            "backend_request": {},
            "ai_server_request": {}
        }
        
        try:
            # 1. 백엔드로 직접 요청
            logger.info("1단계: 백엔드로 직접 공고추천 요청")
            backend_response = requests.post(
                f"{self.backend_url}/api/recruitment/start",
                json=test_data,
                timeout=10
            )
            
            results["backend_request"] = {
                "status_code": backend_response.status_code,
                "success": backend_response.status_code == 200,
                "response": backend_response.json() if backend_response.status_code == 200 else backend_response.text,
                "response_time": backend_response.elapsed.total_seconds()
            }
            
            if backend_response.status_code == 200:
                backend_data = backend_response.json()
                posting_count = len(backend_data.get("posting", []))
                logger.info(f"✅ 백엔드 응답 성공 - {posting_count}개 공고 반환")
            else:
                logger.error(f"❌ 백엔드 응답 실패 - HTTP {backend_response.status_code}")
            
            # 2. AI 서버로 직접 요청
            logger.info("2단계: AI 서버로 직접 공고추천 요청")
            ai_response = requests.post(
                f"{self.ai_server_url}/ai/recruitment/posting",
                json=test_data,
                timeout=10
            )
            
            results["ai_server_request"] = {
                "status_code": ai_response.status_code,
                "success": ai_response.status_code == 200,
                "response": ai_response.json() if ai_response.status_code == 200 else ai_response.text,
                "response_time": ai_response.elapsed.total_seconds()
            }
            
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                ai_posting_count = len(ai_data.get("posting", []))
                logger.info(f"✅ AI 서버 응답 성공 - {ai_posting_count}개 공고 반환")
            else:
                logger.error(f"❌ AI 서버 응답 실패 - HTTP {ai_response.status_code}")
            
            # 결과 비교
            if results["backend_request"]["success"] and results["ai_server_request"]["success"]:
                backend_posting_count = len(results["backend_request"]["response"].get("posting", []))
                ai_posting_count = len(results["ai_server_request"]["response"].get("posting", []))
                
                results["comparison"] = {
                    "backend_count": backend_posting_count,
                    "ai_server_count": ai_posting_count,
                    "counts_match": backend_posting_count == ai_posting_count,
                    "integration_working": True
                }
                
                if backend_posting_count == ai_posting_count:
                    logger.info("✅ 백엔드-AI 서버 연동 정상 작동")
                else:
                    logger.warning(f"⚠️ 응답 개수 불일치: 백엔드({backend_posting_count}) vs AI서버({ai_posting_count})")
            else:
                results["comparison"] = {
                    "integration_working": False,
                    "error": "한쪽 또는 양쪽 서버 응답 실패"
                }
                
        except Exception as e:
            logger.error(f"❌ 공고추천 연동 테스트 오류: {str(e)}")
            results["error"] = str(e)
        
        return results

    def test_debate_integration(self) -> Dict[str, Any]:
        """토론면접 백엔드 연동 테스트"""
        logger.info("🔍 토론면접 백엔드 연동 테스트 시작")
        
        results = {
            "test_name": "debate_integration",
            "steps": {}
        }
        
        try:
            # 1. 토론 시작 요청 (백엔드)
            logger.info("1단계: 백엔드로 토론 시작 요청")
            debate_start_data = {"user_id": "test_user"}
            
            backend_start_response = requests.post(
                f"{self.backend_url}/api/debate/start",
                json=debate_start_data,
                timeout=10
            )
            
            results["steps"]["debate_start"] = {
                "status_code": backend_start_response.status_code,
                "success": backend_start_response.status_code == 200,
                "response": backend_start_response.json() if backend_start_response.status_code == 200 else backend_start_response.text
            }
            
            if backend_start_response.status_code == 200:
                start_data = backend_start_response.json()
                debate_id = start_data.get("debate_id", 1)
                logger.info(f"✅ 토론 시작 성공 - ID: {debate_id}")
                
                # 2. AI 입론 요청 (AI 서버)
                logger.info("2단계: AI 서버로 입론 생성 요청")
                ai_opening_data = {
                    "topic": start_data.get("topic", "인공지능"),
                    "position": "CON"
                }
                
                ai_opening_response = requests.post(
                    f"{self.ai_server_url}/ai/debate/{debate_id}/ai-opening",
                    json=ai_opening_data,
                    timeout=10
                )
                
                results["steps"]["ai_opening"] = {
                    "status_code": ai_opening_response.status_code,
                    "success": ai_opening_response.status_code == 200,
                    "response": ai_opening_response.json() if ai_opening_response.status_code == 200 else ai_opening_response.text
                }
                
                if ai_opening_response.status_code == 200:
                    opening_data = ai_opening_response.json()
                    ai_text = opening_data.get("ai_opening_text", "")
                    logger.info(f"✅ AI 입론 생성 성공 - 길이: {len(ai_text)}자")
                else:
                    logger.error(f"❌ AI 입론 생성 실패 - HTTP {ai_opening_response.status_code}")
                
                # 3. 백엔드 AI 입론 조회 테스트
                logger.info("3단계: 백엔드로 AI 입론 조회 요청")
                backend_opening_response = requests.get(f"{self.backend_url}/api/debate/{debate_id}/ai-opening")
                
                results["steps"]["backend_ai_opening"] = {
                    "status_code": backend_opening_response.status_code,
                    "success": backend_opening_response.status_code == 200,
                    "response": backend_opening_response.json() if backend_opening_response.status_code == 200 else backend_opening_response.text
                }
                
                if backend_opening_response.status_code == 200:
                    logger.info("✅ 백엔드 AI 입론 조회 성공")
                else:
                    logger.error(f"❌ 백엔드 AI 입론 조회 실패 - HTTP {backend_opening_response.status_code}")
                
            else:
                logger.error(f"❌ 토론 시작 실패 - HTTP {backend_start_response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ 토론면접 연동 테스트 오류: {str(e)}")
            results["error"] = str(e)
        
        return results

    def test_interview_integration(self) -> Dict[str, Any]:
        """개인면접 백엔드 연동 테스트"""
        logger.info("🔍 개인면접 백엔드 연동 테스트 시작")
        
        results = {
            "test_name": "interview_integration",
            "steps": {}
        }
        
        try:
            # 1. 포ート폴리오 제출 (백엔드)
            logger.info("1단계: 백엔드로 포트폴리오 제출")
            portfolio_data = {
                "user_id": "test_user",
                "job_category": "ICT",
                "workexperience": "경력무관",
                "education": "대졸",
                "experience_description": "웹 개발 프로젝트 경험",
                "tech_stack": "React, Spring Boot",
                "personality": "적극적이고 책임감이 강함"
            }
            
            portfolio_response = requests.post(
                f"{self.backend_url}/api/interview/portfolio",
                json=portfolio_data,
                timeout=10
            )
            
            results["steps"]["portfolio_submission"] = {
                "status_code": portfolio_response.status_code,
                "success": portfolio_response.status_code == 200,
                "response": portfolio_response.json() if portfolio_response.status_code == 200 else portfolio_response.text
            }
            
            if portfolio_response.status_code == 200:
                portfolio_result = portfolio_response.json()
                interview_id = portfolio_result.get("interview_id", 1)
                logger.info(f"✅ 포트폴리오 제출 성공 - Interview ID: {interview_id}")
                
                # 2. 면접 질문 조회 (백엔드)
                logger.info("2단계: 백엔드로 면접 질문 조회")
                questions_response = requests.get(f"{self.backend_url}/api/interview/{interview_id}/question")
                
                results["steps"]["questions_retrieval"] = {
                    "status_code": questions_response.status_code,
                    "success": questions_response.status_code == 200,
                    "response": questions_response.json() if questions_response.status_code == 200 else questions_response.text
                }
                
                if questions_response.status_code == 200:
                    questions_data = questions_response.json()
                    question_count = len(questions_data.get("questions", []))
                    logger.info(f"✅ 면접 질문 조회 성공 - {question_count}개 질문")
                else:
                    logger.error(f"❌ 면접 질문 조회 실패 - HTTP {questions_response.status_code}")
                
                # 3. AI 서버로 직접 면접 시작
                logger.info("3단계: AI 서버로 면접 시작")
                ai_interview_response = requests.post(f"{self.ai_server_url}/ai/interview/start", json={})
                
                results["steps"]["ai_interview_start"] = {
                    "status_code": ai_interview_response.status_code,
                    "success": ai_interview_response.status_code == 200,
                    "response": ai_interview_response.json() if ai_interview_response.status_code == 200 else ai_interview_response.text
                }
                
                if ai_interview_response.status_code == 200:
                    ai_interview_data = ai_interview_response.json()
                    ai_interview_id = ai_interview_data.get("interview_id")
                    first_question = ai_interview_data.get("first_question", "")
                    logger.info(f"✅ AI 면접 시작 성공 - ID: {ai_interview_id}, 첫 질문: {first_question}")
                else:
                    logger.error(f"❌ AI 면접 시작 실패 - HTTP {ai_interview_response.status_code}")
                
            else:
                logger.error(f"❌ 포트폴리오 제출 실패 - HTTP {portfolio_response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ 개인면접 연동 테스트 오류: {str(e)}")
            results["error"] = str(e)
        
        return results

    def test_ai_server_endpoints(self) -> Dict[str, Any]:
        """AI 서버 엔드포인트 전체 테스트"""
        logger.info("🔍 AI 서버 엔드포인트 전체 테스트 시작")
        
        endpoints_to_test = [
            {"method": "GET", "url": "/ai/health", "name": "헬스 체크"},
            {"method": "GET", "url": "/ai/test", "name": "연결 테스트"},
            {"method": "GET", "url": "/ai/jobs/categories", "name": "공고 카테고리"},
            {"method": "GET", "url": "/ai/jobs/stats", "name": "공고 통계"},
            {"method": "GET", "url": "/ai/debate/modules-status", "name": "모듈 상태"},
            {"method": "POST", "url": "/ai/jobs/recommend", "name": "공고 추천", "data": {"category": "ICT"}},
            {"method": "POST", "url": "/ai/interview/start", "name": "면접 시작", "data": {}},
            {"method": "GET", "url": "/ai/interview/1/question?type=general", "name": "면접 질문"},
            {"method": "POST", "url": "/ai/debate/1/ai-opening", "name": "AI 입론", "data": {"topic": "인공지능"}},
        ]
        
        results = {"endpoint_tests": {}}
        
        for endpoint in endpoints_to_test:
            endpoint_name = endpoint["name"]
            logger.info(f"테스트 중: {endpoint_name}")
            
            try:
                if endpoint["method"] == "GET":
                    response = requests.get(f"{self.ai_server_url}{endpoint['url']}", timeout=5)
                else:  # POST
                    data = endpoint.get("data", {})
                    response = requests.post(f"{self.ai_server_url}{endpoint['url']}", json=data, timeout=5)
                
                results["endpoint_tests"][endpoint_name] = {
                    "method": endpoint["method"],
                    "url": endpoint["url"],
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_size": len(response.text),
                    "response_time": response.elapsed.total_seconds()
                }
                
                if response.status_code == 200:
                    logger.info(f"✅ {endpoint_name} 성공")
                else:
                    logger.error(f"❌ {endpoint_name} 실패 - HTTP {response.status_code}")
                    
            except Exception as e:
                results["endpoint_tests"][endpoint_name] = {
                    "method": endpoint["method"],
                    "url": endpoint["url"],
                    "success": False,
                    "error": str(e)
                }
                logger.error(f"❌ {endpoint_name} 오류: {str(e)}")
        
        return results

    def run_comprehensive_test(self, server_type: str = "both") -> Dict[str, Any]:
        """종합 테스트 실행"""
        logger.info("🚀 VeriView 백엔드 연동 종합 테스트 시작")
        logger.info("=" * 60)
        
        comprehensive_results = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "server_type_tested": server_type,
            "tests": {}
        }
        
        # 1. 서버 가용성 테스트
        logger.info("1️⃣ 서버 가용성 테스트")
        comprehensive_results["tests"]["server_availability"] = self.test_server_availability(server_type)
        
        # AI 서버가 사용 가능한 경우에만 추가 테스트 진행
        if comprehensive_results["tests"]["server_availability"].get("ai_server", {}).get("status") == "available":
            
            # 2. AI 서버 엔드포인트 테스트
            logger.info("2️⃣ AI 서버 엔드포인트 테스트")
            comprehensive_results["tests"]["ai_endpoints"] = self.test_ai_server_endpoints()
            
            # 3. 공고추천 연동 테스트
            logger.info("3️⃣ 공고추천 백엔드 연동 테스트")
            comprehensive_results["tests"]["job_recommendation_integration"] = self.test_job_recommendation_integration()
            
            # 백엔드가 사용 가능한 경우에만 백엔드 연동 테스트 진행
            if comprehensive_results["tests"]["server_availability"].get("backend_server", {}).get("status") == "available":
                
                # 4. 토론면접 연동 테스트
                logger.info("4️⃣ 토론면접 백엔드 연동 테스트")
                comprehensive_results["tests"]["debate_integration"] = self.test_debate_integration()
                
                # 5. 개인면접 연동 테스트
                logger.info("5️⃣ 개인면접 백엔드 연동 테스트")
                comprehensive_results["tests"]["interview_integration"] = self.test_interview_integration()
        
        # 결과 요약
        comprehensive_results["summary"] = self._generate_test_summary(comprehensive_results["tests"])
        
        logger.info("=" * 60)
        logger.info("🏁 VeriView 백엔드 연동 종합 테스트 완료")
        
        return comprehensive_results

    def _generate_test_summary(self, test_results: Dict) -> Dict[str, Any]:
        """테스트 결과 요약 생성"""
        summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "success_rate": 0.0,
            "critical_issues": [],
            "recommendations": []
        }
        
        # 서버 가용성 체크
        server_availability = test_results.get("server_availability", {})
        ai_server_status = server_availability.get("ai_server", {}).get("status")
        backend_server_status = server_availability.get("backend_server", {}).get("status")
        
        if ai_server_status == "available":
            summary["passed_tests"] += 1
        else:
            summary["failed_tests"] += 1
            summary["critical_issues"].append("AI 서버 연결 불가")
        
        if backend_server_status == "available":
            summary["passed_tests"] += 1
        else:
            summary["failed_tests"] += 1
            summary["critical_issues"].append("백엔드 서버 연결 불가")
        
        summary["total_tests"] += 2
        
        # AI 엔드포인트 테스트 체크
        endpoint_tests = test_results.get("ai_endpoints", {}).get("endpoint_tests", {})
        for endpoint_name, result in endpoint_tests.items():
            summary["total_tests"] += 1
            if result.get("success", False):
                summary["passed_tests"] += 1
            else:
                summary["failed_tests"] += 1
        
        # 연동 테스트 체크
        integration_tests = ["job_recommendation_integration", "debate_integration", "interview_integration"]
        for test_name in integration_tests:
            if test_name in test_results:
                summary["total_tests"] += 1
                test_result = test_results[test_name]
                
                if "error" not in test_result and self._is_integration_successful(test_result):
                    summary["passed_tests"] += 1
                else:
                    summary["failed_tests"] += 1
                    summary["critical_issues"].append(f"{test_name} 연동 실패")
        
        # 성공률 계산
        if summary["total_tests"] > 0:
            summary["success_rate"] = (summary["passed_tests"] / summary["total_tests"]) * 100
        
        # 권장사항 생성
        if ai_server_status != "available":
            summary["recommendations"].append("AI 서버(main_server.py 또는 test_server.py)를 실행하세요.")
        
        if backend_server_status != "available":
            summary["recommendations"].append("백엔드 서버(Spring Boot)를 실행하세요.")
        
        if summary["success_rate"] < 80:
            summary["recommendations"].append("시스템 설정과 네트워크 연결을 확인하세요.")
        
        if summary["success_rate"] == 100:
            summary["recommendations"].append("모든 시스템이 정상 작동 중입니다.")
        
        return summary

    def _is_integration_successful(self, test_result: Dict) -> bool:
        """연동 테스트 성공 여부 판단"""
        if "comparison" in test_result:
            return test_result["comparison"].get("integration_working", False)
        
        if "steps" in test_result:
            steps = test_result["steps"]
            return all(step.get("success", False) for step in steps.values())
        
        return False

    def print_detailed_results(self, results: Dict[str, Any]):
        """상세 결과 출력"""
        print("\n" + "="*80)
        print("🔍 VeriView 백엔드 연동 테스트 상세 결과")
        print("="*80)
        
        # 요약 정보
        summary = results.get("summary", {})
        print(f"\n📊 요약")
        print(f"   총 테스트: {summary.get('total_tests', 0)}")
        print(f"   성공: {summary.get('passed_tests', 0)}")
        print(f"   실패: {summary.get('failed_tests', 0)}")
        print(f"   성공률: {summary.get('success_rate', 0):.1f}%")
        
        # 중요 이슈
        critical_issues = summary.get("critical_issues", [])
        if critical_issues:
            print(f"\n🚨 중요 이슈:")
            for issue in critical_issues:
                print(f"   ❌ {issue}")
        
        # 권장사항
        recommendations = summary.get("recommendations", [])
        if recommendations:
            print(f"\n💡 권장사항:")
            for rec in recommendations:
                print(f"   📌 {rec}")
        
        # 서버 상태
        server_availability = results.get("tests", {}).get("server_availability", {})
        print(f"\n🖥️ 서버 상태:")
        
        ai_server = server_availability.get("ai_server", {})
        ai_status = ai_server.get("status", "unknown")
        print(f"   AI 서버: {'✅' if ai_status == 'available' else '❌'} {ai_status}")
        
        backend_server = server_availability.get("backend_server", {})
        backend_status = backend_server.get("status", "unknown")
        print(f"   백엔드 서버: {'✅' if backend_status == 'available' else '❌'} {backend_status}")
        
        # AI 서버 타입 정보
        if ai_status == "available" and ai_server.get("data"):
            server_type = ai_server["data"].get("server_type", "unknown")
            print(f"   AI 서버 타입: {server_type}")
        
        print("\n" + "="*80)


def main():
    """메인 실행 함수"""
    print("🚀 VeriView AI 서버 백엔드 연동 테스트를 시작합니다...")
    
    # 명령행 인수 처리
    server_type = "both"  # both, ai, backend
    if len(sys.argv) > 1:
        if sys.argv[1] in ["both", "ai", "backend"]:
            server_type = sys.argv[1]
        else:
            print("사용법: python backend_integration_test.py [both|ai|backend]")
            sys.exit(1)
    
    # 테스터 초기화
    tester = BackendIntegrationTester()
    
    try:
        # 종합 테스트 실행
        results = tester.run_comprehensive_test(server_type)
        
        # 결과 출력
        tester.print_detailed_results(results)
        
        # 결과 파일 저장
        timestamp = int(time.time())
        result_filename = f"backend_integration_test_results_{timestamp}.json"
        
        try:
            with open(result_filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n📄 상세 결과가 {result_filename}에 저장되었습니다.")
        except Exception as e:
            print(f"⚠️ 결과 파일 저장 실패: {str(e)}")
        
        # 성공률에 따른 종료 코드
        success_rate = results.get("summary", {}).get("success_rate", 0)
        if success_rate == 100:
            print("\n🎉 모든 테스트가 성공했습니다!")
            sys.exit(0)
        elif success_rate >= 80:
            print("\n⚠️ 대부분의 테스트가 성공했지만 일부 이슈가 있습니다.")
            sys.exit(1)
        else:
            print("\n❌ 여러 테스트가 실패했습니다. 시스템 설정을 확인하세요.")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자가 테스트를 중단했습니다.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
