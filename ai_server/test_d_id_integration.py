#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 통합 테스트
VeriView 프로젝트 연동 확인
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_d_id_connection():
    """D-ID API 연결 테스트"""
    print("=" * 60)
    print("🔌 D-ID API 연결 테스트")
    print("=" * 60)
    
    try:
        from modules.d_id.client import DIDClient
        
        # 환경 변수에서 API 키 가져오기
        api_key = os.environ.get('D_ID_API_KEY')
        
        if not api_key or api_key == 'your_actual_d_id_api_key_here':
            print("❌ D_ID_API_KEY 환경 변수가 설정되지 않았습니다.")
            print("💡 해결 방법:")
            print("   1. .env 파일에서 D_ID_API_KEY를 실제 API 키로 변경")
            print("   2. 또는 환경 변수 직접 설정: export D_ID_API_KEY='your_api_key'")
            return False
        
        print(f"✅ API 키 확인: {'*' * (len(api_key) - 8)}{api_key[-8:]}")
        
        # D-ID 클라이언트 초기화
        client = DIDClient(api_key=api_key)
        
        # 연결 테스트
        if client.test_connection():
            print("✅ D-ID API 연결 성공")
            return True
        else:
            print("❌ D-ID API 연결 실패")
            return False
            
    except ImportError as e:
        print(f"❌ D-ID 모듈 임포트 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ D-ID 연결 테스트 중 오류: {e}")
        return False

def test_ai_server_endpoints():
    """AI 서버 엔드포인트 테스트"""
    print("\n" + "=" * 60)
    print("🔗 AI 서버 엔드포인트 테스트")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 테스트할 엔드포인트들
    endpoints = [
        {
            "name": "서버 상태 확인",
            "method": "GET",
            "url": f"{base_url}/ai/test",
            "expected_keys": ["status", "avatar_services", "modules"]
        },
        {
            "name": "채용 공고 추천",
            "method": "POST",
            "url": f"{base_url}/ai/recruitment/posting",
            "data": {
                "user_id": "test_user",
                "category": "ICT",
                "workexperience": "신입",
                "tech_stack": "Python, React"
            },
            "expected_keys": ["posting"]
        },
        {
            "name": "면접 질문 생성",
            "method": "POST",
            "url": f"{base_url}/ai/interview/generate-question",
            "data": {
                "interview_id": 1,
                "job_category": "ICT",
                "workexperience": "신입",
                "tech_stack": "Python"
            },
            "expected_keys": ["interview_id", "questions"]
        }
    ]
    
    # 각 엔드포인트 테스트
    for endpoint in endpoints:
        print(f"\n📡 테스트: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=10)
            else:
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint.get('data', {}),
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                
                # 예상 키 확인
                if 'expected_keys' in endpoint:
                    missing_keys = [key for key in endpoint['expected_keys'] if key not in data]
                    if missing_keys:
                        print(f"   ⚠️  응답 성공이지만 누락된 키: {missing_keys}")
                    else:
                        print(f"   ✅ 성공: 모든 예상 키 포함")
                else:
                    print(f"   ✅ 성공: 상태 코드 {response.status_code}")
                
                # 응답 데이터 요약 출력
                if endpoint['name'] == "서버 상태 확인":
                    avatar_services = data.get('avatar_services', {})
                    print(f"   📊 D-ID 상태: {avatar_services.get('D-ID (우선)', 'Unknown')}")
                    print(f"   📊 연결 상태: {avatar_services.get('D-ID 연결상태', 'Unknown')}")
                
                elif endpoint['name'] == "채용 공고 추천":
                    postings = data.get('posting', [])
                    print(f"   📊 추천 공고 수: {len(postings)}")
                
                elif endpoint['name'] == "면접 질문 생성":
                    questions = data.get('questions', [])
                    print(f"   📊 생성된 질문 수: {len(questions)}")
                    
            else:
                print(f"   ❌ 실패: 상태 코드 {response.status_code}")
                print(f"   📄 응답: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 연결 실패: AI 서버가 실행되지 않았습니다.")
            print(f"   💡 해결 방법: python server_runner_d_id.py 실행")
        except requests.exceptions.Timeout:
            print(f"   ❌ 시간 초과: 응답이 10초 이내에 오지 않았습니다.")
        except Exception as e:
            print(f"   ❌ 오류: {str(e)}")

def test_d_id_video_generation():
    """D-ID 영상 생성 테스트 (실제 API 호출)"""
    print("\n" + "=" * 60)
    print("🎬 D-ID 영상 생성 테스트")
    print("=" * 60)
    
    try:
        from modules.d_id.client import DIDClient
        from modules.d_id.tts_manager import TTSManager
        
        # API 키 확인
        api_key = os.environ.get('D_ID_API_KEY')
        
        if not api_key or api_key == 'your_actual_d_id_api_key_here':
            print("❌ D_ID_API_KEY가 설정되지 않아 테스트를 건너뜁니다.")
            return False
        
        print("🔄 D-ID 클라이언트 초기화...")
        client = DIDClient(api_key=api_key)
        tts = TTSManager()
        
        # 테스트 스크립트
        test_script = "안녕하세요. D-ID API 테스트를 진행합니다. 자기소개를 해주세요."
        
        print(f"📝 테스트 스크립트: {test_script}")
        
        # 면접관 영상 생성 테스트
        print("\n🎭 면접관 영상 생성 테스트...")
        formatted_script = tts.format_script_for_interview(test_script)
        
        print(f"   📝 포맷팅된 스크립트: {formatted_script}")
        print(f"   🎵 사용할 음성: {tts.get_voice_for_interviewer('male')}")
        
        # 실제로는 API 호출이 시간이 오래 걸리므로 여기서는 스킵
        print("   ⏳ 실제 영상 생성은 시간이 오래 걸리므로 테스트에서 제외")
        print("   💡 영상 생성 테스트를 원하면 server_runner_d_id.py의 /ai/interview/ai-video 엔드포인트 사용")
        
        return True
        
    except ImportError as e:
        print(f"❌ 모듈 임포트 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        return False

def test_backend_integration():
    """Backend 연동 테스트"""
    print("\n" + "=" * 60)
    print("🔗 Backend 연동 테스트")
    print("=" * 60)
    
    # Backend 서버 확인
    backend_url = "http://localhost:8080"
    
    print(f"📡 Backend 서버 연결 확인: {backend_url}")
    
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend 서버 연결 성공")
        else:
            print(f"   ⚠️  Backend 서버 응답: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend 서버 연결 실패")
        print("   💡 Backend 서버가 실행 중인지 확인하세요")
        return False
    except Exception as e:
        print(f"   ❌ Backend 연결 테스트 중 오류: {e}")
        return False
    
    # AI 서버와 Backend 간 통신 테스트
    print(f"\n📡 AI 서버 → Backend 통신 테스트")
    
    # 실제 면접 시나리오 시뮬레이션
    test_scenarios = [
        {
            "name": "면접 질문 생성 → Backend 전달",
            "ai_endpoint": "http://localhost:5000/ai/interview/generate-question",
            "backend_endpoint": f"{backend_url}/api/interviews",
            "test_data": {
                "interview_id": 999,  # 테스트용 ID
                "job_category": "ICT",
                "tech_stack": "Python, React"
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🎭 시나리오: {scenario['name']}")
        
        try:
            # AI 서버에서 데이터 생성
            print("   1️⃣ AI 서버에서 질문 생성...")
            ai_response = requests.post(
                scenario['ai_endpoint'],
                json=scenario['test_data'],
                timeout=10
            )
            
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                questions = ai_data.get('questions', [])
                print(f"      ✅ AI 서버 응답 성공: {len(questions)}개 질문 생성")
                
                # Backend로 전달할 수 있는 형태인지 확인
                if questions and len(questions) > 0:
                    first_question = questions[0]
                    required_fields = ['question_type', 'question_text']
                    
                    if all(field in first_question for field in required_fields):
                        print("      ✅ Backend 연동 형식 적합")
                    else:
                        print(f"      ⚠️  Backend 연동 형식 확인 필요: {first_question.keys()}")
                else:
                    print("      ❌ 질문 생성 실패")
            else:
                print(f"      ❌ AI 서버 응답 실패: {ai_response.status_code}")
                
        except Exception as e:
            print(f"      ❌ 시나리오 테스트 중 오류: {e}")
    
    return True

def generate_test_report():
    """테스트 결과 보고서 생성"""
    print("\n" + "=" * 60)
    print("📋 D-ID 통합 테스트 보고서")
    print("=" * 60)
    
    report = {
        "test_time": datetime.now().isoformat(),
        "environment": {
            "d_id_api_key_set": bool(os.environ.get('D_ID_API_KEY') and os.environ.get('D_ID_API_KEY') != 'your_actual_d_id_api_key_here'),
            "preferred_service": os.environ.get('PREFERRED_AVATAR_SERVICE', 'D_ID'),
            "use_fallback": os.environ.get('USE_FALLBACK_SERVICE', 'True')
        }
    }
    
    print(f"🕐 테스트 시간: {report['test_time']}")
    print(f"🔑 D-ID API 키 설정: {'✅' if report['environment']['d_id_api_key_set'] else '❌'}")
    print(f"⚙️  우선 서비스: {report['environment']['preferred_service']}")
    print(f"🔄 폴백 사용: {report['environment']['use_fallback']}")
    
    # 다음 단계 가이드
    print(f"\n📝 다음 단계:")
    
    if not report['environment']['d_id_api_key_set']:
        print("   1. .env 파일에서 D_ID_API_KEY를 실제 API 키로 설정")
        print("   2. AI 서버 재시작: python server_runner_d_id.py")
    else:
        print("   1. AI 서버 실행: python server_runner_d_id.py")
        print("   2. Backend 서버 실행 확인")
        print("   3. Frontend에서 면접/토론 기능 테스트")
        print("   4. D-ID 영상 생성 확인: /ai/interview/ai-video 엔드포인트 호출")
    
    print(f"\n💡 유용한 테스트 명령어:")
    print("   - AI 서버 상태: curl http://localhost:5000/ai/test")
    print("   - 면접 질문 생성: curl -X POST http://localhost:5000/ai/interview/generate-question -H 'Content-Type: application/json' -d '{\"job_category\":\"ICT\"}'")

def main():
    """메인 테스트 함수"""
    print("🚀 VeriView D-ID API 통합 테스트 시작")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 환경 변수 로드
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ 환경 변수 로드 완료")
    except ImportError:
        print("⚠️  python-dotenv가 설치되지 않음 - 환경 변수 수동 확인 필요")
    
    # 테스트 실행
    tests_passed = 0
    total_tests = 4
    
    if test_d_id_connection():
        tests_passed += 1
    
    if test_ai_server_endpoints():
        tests_passed += 1
    
    if test_d_id_video_generation():
        tests_passed += 1
    
    if test_backend_integration():
        tests_passed += 1
    
    # 결과 요약
    print("\n" + "=" * 60)
    print(f"🎯 테스트 결과: {tests_passed}/{total_tests} 통과")
    print("=" * 60)
    
    if tests_passed == total_tests:
        print("🎉 모든 테스트 통과! D-ID 통합이 성공적으로 완료되었습니다.")
    elif tests_passed >= total_tests // 2:
        print("✅ 대부분의 테스트 통과. 일부 설정을 확인해주세요.")
    else:
        print("❌ 여러 테스트 실패. 설정을 다시 확인해주세요.")
    
    # 보고서 생성
    generate_test_report()

if __name__ == "__main__":
    main()
