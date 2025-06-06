#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
백엔드-AI서버 연동 테스트 스크립트
Spring Boot 백엔드의 /api/recruitment/start 엔드포인트를 테스트
"""

import requests
import json
import time

def test_backend_integration():
    """백엔드 연동 테스트"""
    
    print("🔗 백엔드-AI서버 연동 테스트")
    print("=" * 50)
    
    # 백엔드 URL (Spring Boot 서버)
    backend_url = "http://localhost:4000/api/recruitment/start"
    
    # 테스트 데이터 (백엔드가 기대하는 형식)
    test_data = {
        "user_id": "test_user_1",
        "education": "학사",
        "major": "컴퓨터공학",
        "double_major": "",
        "workexperience": "신입",
        "tech_stack": "Java, Spring, MySQL",
        "qualification": "",
        "location": "서울",
        "category": "ICT",
        "employmenttype": "정규직"
    }
    
    print("📤 백엔드로 요청 전송 중...")
    print(f"URL: {backend_url}")
    print(f"데이터: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print("-" * 50)
    
    try:
        # POST 요청 전송
        response = requests.post(
            backend_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30  # 백엔드가 AI 서버 호출하므로 시간 여유
        )
        
        print(f"📥 응답 수신:")
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 연동 성공!")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 추천 결과 분석
            postings = result.get('posting', [])
            print(f"\n📊 추천 결과 분석:")
            print(f"추천 채용공고 수: {len(postings)}")
            
            for i, posting in enumerate(postings, 1):
                print(f"  {i}. {posting.get('title', 'N/A')} - {posting.get('corporation', 'N/A')}")
                print(f"     키워드: {posting.get('keyword', 'N/A')}")
                print(f"     ID: {posting.get('job_posting_id', 'N/A')}")
                
        else:
            print(f"❌ 요청 실패: {response.status_code}")
            print(f"응답 내용: {response.text}")
            
            if response.status_code == 500:
                print("\n🔍 500 에러 분석:")
                print("- 백엔드 서버가 AI 서버에 연결할 수 없음")
                print("- AI 서버가 실행되지 않았을 가능성")
                print("- 엔드포인트 경로 불일치 가능성")
                
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드 서버 연결 실패")
        print("백엔드 서버가 실행 중인지 확인하세요 (포트 4000)")
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
        print("백엔드 또는 AI 서버 응답이 느릴 수 있습니다")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")

def test_ai_server_direct():
    """AI 서버 직접 테스트"""
    
    print("\n🤖 AI 서버 직접 테스트")
    print("=" * 50)
    
    # AI 서버 URL
    ai_url = "http://localhost:5000/ai/recruitment/posting"
    
    test_data = {
        "user_id": "test_user_1",
        "education": "학사",
        "major": "컴퓨터공학",
        "double_major": "",
        "workexperience": "신입",
        "tech_stack": "Java, Spring, MySQL",
        "qualification": "",
        "location": "서울",
        "category": "ICT",
        "employmenttype": "정규직"
    }
    
    print("📤 AI 서버로 직접 요청...")
    print(f"URL: {ai_url}")
    
    try:
        response = requests.post(
            ai_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI 서버 직접 요청 성공!")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"❌ AI 서버 요청 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ AI 서버 연결 실패")
        print("AI 서버가 실행 중인지 확인하세요 (포트 5000)")
        print("실행 명령: python server_runner.py")
    except Exception as e:
        print(f"❌ AI 서버 테스트 오류: {str(e)}")

def check_servers():
    """서버 상태 확인"""
    
    print("🏥 서버 상태 확인")
    print("=" * 30)
    
    # AI 서버 확인
    try:
        ai_response = requests.get("http://localhost:5000/ai/test", timeout=5)
        if ai_response.status_code == 200:
            print("✅ AI 서버 (포트 5000): 정상")
        else:
            print(f"⚠️  AI 서버 (포트 5000): 응답 오류 ({ai_response.status_code})")
    except:
        print("❌ AI 서버 (포트 5000): 연결 실패")
    
    # 백엔드 서버 확인 (간단한 헬스체크)
    try:
        # Spring Boot 액추에이터 헬스체크 시도
        backend_health_urls = [
            "http://localhost:4000/actuator/health",
            "http://localhost:4000/health",
            "http://localhost:4000/"
        ]
        
        backend_ok = False
        for url in backend_health_urls:
            try:
                backend_response = requests.get(url, timeout=3)
                if backend_response.status_code in [200, 404]:  # 404도 서버가 살아있다는 의미
                    print("✅ 백엔드 서버 (포트 4000): 정상")
                    backend_ok = True
                    break
            except:
                continue
        
        if not backend_ok:
            print("❌ 백엔드 서버 (포트 4000): 연결 실패")
            
    except Exception as e:
        print(f"❌ 백엔드 서버 상태 확인 실패: {str(e)}")

if __name__ == "__main__":
    print("🧪 백엔드-AI서버 연동 테스트 도구")
    print("=" * 60)
    
    # 서버 상태 확인
    check_servers()
    
    print("\n" + "=" * 60)
    
    # AI 서버 직접 테스트
    test_ai_server_direct()
    
    print("\n" + "=" * 60)
    
    # 백엔드 연동 테스트
    test_backend_integration()
    
    print("\n" + "=" * 60)
    print("🏁 테스트 완료")
    print("\n📝 문제 해결 가이드:")
    print("1. AI 서버가 실행되지 않은 경우:")
    print("   cd ai_server && python server_runner.py")
    print("2. 백엔드 서버가 실행되지 않은 경우:")
    print("   cd backend && ./gradlew bootRun")
    print("3. 포트 충돌이 있는 경우:")
    print("   - AI 서버: 포트 5000")
    print("   - 백엔드: 포트 4000")
