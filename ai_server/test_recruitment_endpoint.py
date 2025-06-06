#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
채용 공고 추천 엔드포인트 테스트 스크립트
"""

import requests
import json
import time

def test_recruitment_endpoint():
    """채용 공고 추천 엔드포인트 테스트"""
    
    # AI 서버 URL
    base_url = "http://localhost:5000"
    
    print("🧪 채용 공고 추천 엔드포인트 테스트 시작")
    print("=" * 60)
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "ICT 신입 개발자",
            "data": {
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
        },
        {
            "name": "경영/사무 경력자",
            "data": {
                "user_id": "test_user_2",
                "education": "학사",
                "major": "경영학",
                "double_major": "회계학",
                "workexperience": "3-5년",
                "tech_stack": "",
                "qualification": "회계사",
                "location": "경기",
                "category": "BM",
                "employmenttype": "정규직"
            }
        },
        {
            "name": "프론트엔드 개발자",
            "data": {
                "user_id": "test_user_3",
                "education": "학사",
                "major": "정보통신공학",
                "double_major": "",
                "workexperience": "1-3년",
                "tech_stack": "React, JavaScript, TypeScript",
                "qualification": "",
                "location": "서울",
                "category": "ICT",
                "employmenttype": "정규직"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 테스트 케이스 {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # POST 요청 전송
            response = requests.post(
                f"{base_url}/ai/recruitment/posting",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 요청 성공!")
                print(f"추천 채용공고 수: {len(result.get('posting', []))}")
                
                for j, posting in enumerate(result.get('posting', []), 1):
                    print(f"  {j}. {posting.get('title', 'N/A')} - {posting.get('corporation', 'N/A')}")
                    print(f"     키워드: {posting.get('keyword', 'N/A')}")
                    print(f"     ID: {posting.get('job_posting_id', 'N/A')}")
                
            else:
                print(f"❌ 요청 실패: {response.status_code}")
                print(f"응답: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 연결 실패: AI 서버가 실행 중인지 확인하세요")
            print("   서버 시작: python server_runner.py")
            break
        except requests.exceptions.Timeout:
            print("❌ 요청 시간 초과")
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
        
        time.sleep(1)  # 요청 간 간격
    
    print("\n" + "=" * 60)
    print("🏁 테스트 완료")

def test_connection():
    """서버 연결 테스트"""
    print("🔗 서버 연결 테스트")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:5000/ai/test", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ 서버 연결 성공!")
            print(f"상태: {result.get('status', 'N/A')}")
            
            endpoints = result.get('endpoints', {})
            print("\n사용 가능한 엔드포인트:")
            for name, path in endpoints.items():
                print(f"  - {name}: {path}")
            
            return True
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다")
        print("   서버 시작 명령: python server_runner.py")
        return False
    except Exception as e:
        print(f"❌ 연결 테스트 오류: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 AI 서버 채용 추천 기능 테스트")
    print("=" * 60)
    
    # 서버 연결 테스트
    if test_connection():
        print()
        # 채용 추천 엔드포인트 테스트
        test_recruitment_endpoint()
    else:
        print("\n⚠️  서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요:")
        print("   cd ai_server")
        print("   python server_runner.py")
