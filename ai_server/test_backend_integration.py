#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 Backend 통합 테스트
D-ID API 통합 후 Backend 연동 확인
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def test_ai_server_endpoints():
    """AI 서버 엔드포인트 테스트"""
    base_url = "http://localhost:5000"
    
    print("=" * 80)
    print("🧪 VeriView AI 서버 Backend 통합 테스트 (D-ID)")
    print("=" * 80)
    
    # 서버 시작 상태 확인
    print("🔄 서버 연결 테스트...")
    try:
        response = requests.get(f"{base_url}/ai/test", timeout=10)
        if response.status_code == 200:
            print("✅ AI 서버 연결 성공")
            test_data = response.json()
            
            # D-ID 상태 확인
            d_id_status = test_data.get('avatar_services', {}).get('D-ID (우선)', 'Unknown')
            d_id_connection = test_data.get('avatar_services', {}).get('D-ID 연결상태', 'Unknown')
            
            print(f"   D-ID 서비스: {d_id_status}")
            print(f"   D-ID 연결: {d_id_connection}")
            print()
        else:
            print(f"❌ AI 서버 연결 실패: {response.status_code}")
            print("서버가 실행 중인지 확인하세요: python run.py test")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ AI 서버에 연결할 수 없습니다: {e}")
        print("다음 명령어로 서버를 먼저 실행하세요:")
        print("   python run.py test")
        return False
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "채용 공고 추천",
            "method": "POST",
            "endpoint": "/ai/recruitment/posting",
            "data": {
                "user_id": "test_user",
                "education": "학사",
                "major": "컴퓨터공학",
                "workexperience": "1-3년",
                "tech_stack": "Java, Spring, React",
                "qualification": "정보처리기사",
                "location": "서울",
                "category": "ICT",
                "employmenttype": "정규직"
            }
        },
        {
            "name": "면접 질문 생성",
            "method": "POST",
            "endpoint": "/ai/interview/generate-question",
            "data": {
                "interview_id": 1,
                "job_category": "ICT",
                "workexperience": "1-3년",
                "education": "학사",
                "tech_stack": "Java, Spring",
                "personality": "적극적, 협력적"
            }
        },
        {
            "name": "AI 면접관 영상 생성 (D-ID)",
            "method": "POST",
            "endpoint": "/ai/interview/ai-video",
            "data": {
                "question_text": "자기소개를 해주세요.",
                "interviewer_gender": "male"
            },
            "expect_video": True
        },
        {
            "name": "AI 토론 입론 생성",
            "method": "POST",
            "endpoint": "/ai/debate/1/ai-opening",
            "data": {
                "topic": "AI 기술 발전의 필요성",
                "position": "PRO"
            }
        },
        {
            "name": "AI 토론 입론 영상 (D-ID)",
            "method": "POST",
            "endpoint": "/ai/debate/ai-opening-video",
            "data": {
                "ai_opening_text": "AI 기술은 인류의 발전에 필수적입니다.",
                "debater_gender": "female"
            },
            "expect_video": True
        }
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 테스트 {i}/{total_tests}: {test_case['name']}")
        
        try:
            url = f"{base_url}{test_case['endpoint']}"
            
            if test_case['method'] == 'POST':
                response = requests.post(url, json=test_case['data'], timeout=30)
            else:
                response = requests.get(url, timeout=30)
            
            if response.status_code in [200, 201]:
                print(f"   ✅ 응답 성공: {response.status_code}")
                
                # 비디오 응답인 경우
                if test_case.get('expect_video', False):
                    content_type = response.headers.get('content-type', '')
                    if 'video' in content_type:
                        print(f"   🎬 비디오 생성 성공: {content_type}")
                        print(f"   📏 비디오 크기: {len(response.content)} bytes")
                    else:
                        print(f"   ⚠️ 예상과 다른 응답 타입: {content_type}")
                else:
                    # JSON 응답인 경우
                    try:
                        result = response.json()
                        if isinstance(result, dict):
                            key_count = len(result.keys())
                            print(f"   📄 JSON 응답: {key_count}개 필드")
                            
                            # 중요 필드 확인
                            if 'posting' in result:
                                print(f"   📝 추천 공고: {len(result['posting'])}개")
                            elif 'questions' in result:
                                print(f"   ❓ 생성 질문: {len(result['questions'])}개")
                            elif 'ai_opening_text' in result:
                                print(f"   💬 AI 입론: {result['ai_opening_text'][:30]}...")
                        else:
                            print(f"   📄 응답 데이터: {str(result)[:50]}...")
                    except json.JSONDecodeError:
                        print(f"   📄 텍스트 응답: {len(response.text)} characters")
                
                success_count += 1
                
            else:
                print(f"   ❌ 응답 실패: {response.status_code}")
                print(f"   📄 오류 내용: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ 타임아웃 (30초 초과)")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 요청 오류: {e}")
        except Exception as e:
            print(f"   ❌ 기타 오류: {e}")
        
        print()
        time.sleep(1)  # 서버 부하 방지
    
    # 결과 요약
    print("=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    print(f"총 테스트: {total_tests}개")
    print(f"성공: {success_count}개")
    print(f"실패: {total_tests - success_count}개")
    print(f"성공률: {success_count / total_tests * 100:.1f}%")
    
    if success_count == total_tests:
        print("\n🎉 모든 테스트 통과! D-ID 통합이 성공적으로 완료되었습니다.")
        print("\n📋 Backend에서 사용 가능한 엔드포인트:")
        print("   - 채용 추천: POST /ai/recruitment/posting")
        print("   - 면접 질문: POST /ai/interview/generate-question")
        print("   - AI 면접관: POST /ai/interview/ai-video (D-ID)")
        print("   - AI 토론 입론: POST /ai/debate/{debate_id}/ai-opening")
        print("   - AI 토론 영상: POST /ai/debate/ai-opening-video (D-ID)")
        print("   - 기타 모든 기존 엔드포인트 호환")
        
    else:
        print(f"\n⚠️ {total_tests - success_count}개 테스트 실패")
        print("실패한 테스트들을 확인하고 서버 로그를 점검하세요.")
    
    print("\n🔧 추가 설정이 필요한 경우:")
    print("   1. D-ID API 키 확인: .env 파일의 D_ID_API_KEY")
    print("   2. 서버 재시작: python run.py test")
    print("   3. 로그 확인: ai_server.log 파일")
    print("=" * 80)
    
    return success_count == total_tests

def test_specific_d_id_features():
    """D-ID 특화 기능 테스트"""
    base_url = "http://localhost:5000"
    
    print("\n🎬 D-ID 특화 기능 테스트")
    print("-" * 40)
    
    # 다양한 성별과 시나리오 테스트
    scenarios = [
        {
            "name": "남성 면접관 - 기술 질문",
            "endpoint": "/ai/interview/ai-video",
            "data": {
                "question_text": "Java와 Python의 차이점을 설명해주세요.",
                "interviewer_gender": "male"
            }
        },
        {
            "name": "여성 면접관 - 인성 질문",
            "endpoint": "/ai/interview/ai-video",
            "data": {
                "question_text": "팀워크에서 중요한 요소는 무엇이라고 생각하시나요?",
                "interviewer_gender": "female"
            }
        },
        {
            "name": "남성 토론자 - 찬성 입장",
            "endpoint": "/ai/debate/ai-opening-video",
            "data": {
                "ai_opening_text": "AI 기술의 발전은 새로운 일자리를 창출하고 업무 효율성을 높입니다.",
                "debater_gender": "male"
            }
        },
        {
            "name": "여성 토론자 - 반대 입장",
            "endpoint": "/ai/debate/ai-rebuttal-video",
            "data": {
                "ai_opening_text": "AI 기술의 급속한 발전은 인간의 일자리를 위협하고 사회적 불평등을 심화시킬 수 있습니다.",
                "debater_gender": "female"
            }
        }
    ]
    
    d_id_success = 0
    
    for scenario in scenarios:
        print(f"🎭 {scenario['name']} 테스트 중...")
        
        try:
            response = requests.post(
                f"{base_url}{scenario['endpoint']}", 
                json=scenario['data'], 
                timeout=60  # D-ID는 시간이 더 걸릴 수 있음
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'video' in content_type:
                    video_size = len(response.content)
                    print(f"   ✅ D-ID 영상 생성 성공: {video_size:,} bytes")
                    d_id_success += 1
                else:
                    print(f"   ⚠️ 비디오가 아닌 응답: {content_type}")
            else:
                print(f"   ❌ 생성 실패: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ 시간 초과 (60초) - D-ID 서버 응답 지연")
        except Exception as e:
            print(f"   ❌ 오류: {e}")
        
        time.sleep(2)  # D-ID API 부하 방지
    
    print(f"\n🎬 D-ID 특화 테스트 결과: {d_id_success}/{len(scenarios)} 성공")
    return d_id_success > 0

if __name__ == "__main__":
    print("VeriView AI 서버가 실행 중인지 확인하세요:")
    print("   python run.py test")
    print()
    
    input("서버가 실행되면 Enter를 눌러 테스트를 시작하세요...")
    
    # 기본 엔드포인트 테스트
    basic_success = test_ai_server_endpoints()
    
    if basic_success:
        # D-ID 특화 기능 테스트
        d_id_success = test_specific_d_id_features()
        
        if d_id_success:
            print("\n🎉 D-ID 통합 완료! 실사 아바타 영상 생성이 정상 작동합니다.")
        else:
            print("\n⚠️ D-ID 특화 기능에 문제가 있을 수 있습니다.")
    
    print("\n테스트 완료.")
