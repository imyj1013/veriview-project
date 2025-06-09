#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIStudios 통합 테스트 스크립트
run.py의 test 모드와 main 모드에서 AIStudios 기능이 정상 작동하는지 확인

사용법: python test_aistudios_integration.py
"""

import os
import sys
import requests
import time
import json
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:5000"
TEST_TIMEOUT = 10

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_test(test_name):
    """테스트 이름 출력"""
    print(f"\n🔍 테스트: {test_name}")

def print_result(success, message):
    """테스트 결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"   {status}: {message}")

def check_server_status():
    """서버 상태 확인"""
    print_test("서버 연결 상태 확인")
    try:
        response = requests.get(f"{BASE_URL}/ai/test", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"서버 응답 정상 - {data.get('server_type', 'Unknown')}")
            
            # AIStudios 모듈 상태 확인
            aistudios_status = data.get('modules', {}).get('aistudios', 'Unknown')
            aistudios_info = data.get('aistudios_info', {})
            
            print(f"   📊 AIStudios 모듈: {aistudios_status}")
            print(f"   📊 클라이언트 초기화: {'✅' if aistudios_info.get('client_initialized') else '❌'}")
            print(f"   📊 영상 관리자 초기화: {'✅' if aistudios_info.get('video_manager_initialized') else '❌'}")
            print(f"   📊 API 키 설정: {'✅' if aistudios_info.get('api_key_configured') else '❌'}")
            
            return True, data
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False, None
    except Exception as e:
        print_result(False, f"연결 실패: {str(e)}")
        return False, None

def test_aistudios_status():
    """AIStudios 상태 확인"""
    print_test("AIStudios 상태 API 테스트")
    try:
        response = requests.get(f"{BASE_URL}/api/aistudios/status", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_result(True, "AIStudios 상태 API 정상")
            print(f"   📊 상세 정보: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"요청 실패: {str(e)}")
        return False

def test_interview_question_video():
    """면접관 질문 영상 생성 테스트"""
    print_test("면접관 질문 영상 생성")
    try:
        payload = {
            "question": "안녕하세요. 자기소개를 해주세요.",
            "interview_id": int(time.time()),
            "question_type": "INTRO"
        }
        
        response = requests.post(
            f"{BASE_URL}/ai/interview/next-question-video",
            json=payload,
            timeout=30  # 영상 생성은 시간이 오래 걸릴 수 있음
        )
        
        if response.status_code == 200:
            # 영상 파일 응답인지 확인
            content_type = response.headers.get('content-type', '')
            if 'video' in content_type:
                print_result(True, f"영상 생성 성공 (크기: {len(response.content)} bytes)")
                
                # 임시 파일로 저장하여 확인
                test_video_path = f"test_interview_video_{int(time.time())}.mp4"
                with open(test_video_path, 'wb') as f:
                    f.write(response.content)
                print(f"   💾 테스트 영상 저장: {test_video_path}")
                return True
            else:
                # JSON 응답인 경우
                try:
                    data = response.json()
                    if 'video_path' in data:
                        print_result(True, f"영상 경로 반환: {data['video_path']}")
                        return True
                    else:
                        print_result(False, f"영상 경로 없음: {data}")
                        return False
                except:
                    print_result(False, "응답 형식 오류")
                    return False
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"요청 실패: {str(e)}")
        return False

def test_interview_feedback_video():
    """면접 피드백 영상 생성 테스트"""
    print_test("면접 피드백 영상 생성")
    try:
        payload = {
            "feedback": "답변을 잘 해주셨습니다. 좀 더 구체적인 사례가 있다면 더 좋겠습니다.",
            "interview_id": int(time.time())
        }
        
        response = requests.post(
            f"{BASE_URL}/ai/interview/feedback-video",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'video' in content_type:
                print_result(True, f"피드백 영상 생성 성공 (크기: {len(response.content)} bytes)")
                return True
            else:
                try:
                    data = response.json()
                    if 'video_path' in data:
                        print_result(True, f"피드백 영상 경로: {data['video_path']}")
                        return True
                    else:
                        print_result(False, f"영상 경로 없음: {data}")
                        return False
                except:
                    print_result(False, "응답 형식 오류")
                    return False
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"요청 실패: {str(e)}")
        return False

def test_debate_ai_video():
    """토론 AI 영상 생성 테스트"""
    print_test("토론 AI 영상 생성")
    try:
        payload = {
            "ai_opening_text": "인공지능의 발전은 인류에게 많은 이익을 가져다 줄 것입니다.",
            "debate_id": int(time.time())
        }
        
        response = requests.post(
            f"{BASE_URL}/ai/debate/ai-opening-video",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'video' in content_type:
                print_result(True, f"토론 AI 영상 생성 성공 (크기: {len(response.content)} bytes)")
                return True
            else:
                try:
                    data = response.json()
                    print_result(False, f"예상과 다른 응답: {data}")
                    return False
                except:
                    print_result(False, "응답 형식 오류")
                    return False
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"요청 실패: {str(e)}")
        return False

def test_cache_management():
    """캐시 관리 기능 테스트"""
    print_test("캐시 관리 기능")
    try:
        payload = {"hours": 1}  # 1시간 이전 캐시 정리
        
        response = requests.post(
            f"{BASE_URL}/api/admin/cache/clear",
            json=payload,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cleared_files = data.get('cleared_files', 0)
                print_result(True, f"캐시 정리 완료 - {cleared_files}개 파일 삭제")
                return True
            else:
                print_result(False, f"캐시 정리 실패: {data}")
                return False
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"요청 실패: {str(e)}")
        return False

def test_environment_setup():
    """환경 설정 확인"""
    print_test("환경 설정 확인")
    
    # API 키 확인
    api_key = os.environ.get('AISTUDIOS_API_KEY')
    if api_key and api_key not in ['your_api_key', 'YOUR_API_KEY', 'your_actual_api_key_here']:
        print_result(True, "AISTUDIOS_API_KEY 환경 변수 설정됨")
        api_key_ok = True
    else:
        print_result(False, "AISTUDIOS_API_KEY 환경 변수가 설정되지 않았거나 기본값 사용 중")
        api_key_ok = False
    
    # 필요한 디렉토리 확인
    required_dirs = ['aistudios_cache', 'videos', 'videos/interview', 'videos/opening']
    dirs_ok = True
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print_result(True, f"디렉토리 존재: {dir_path}")
        else:
            print_result(False, f"디렉토리 없음: {dir_path}")
            dirs_ok = False
    
    return api_key_ok and dirs_ok

def generate_test_report(results):
    """테스트 결과 보고서 생성"""
    print_section("📊 테스트 결과 요약")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results if result['success'])
    failed_tests = total_tests - passed_tests
    
    print(f"📈 전체 테스트: {total_tests}개")
    print(f"✅ 성공: {passed_tests}개")
    print(f"❌ 실패: {failed_tests}개")
    print(f"📊 성공률: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ 실패한 테스트:")
        for result in results:
            if not result['success']:
                print(f"   - {result['name']}: {result['message']}")
    
    print("\n💡 권장사항:")
    if failed_tests == 0:
        print("   🎉 모든 테스트가 성공했습니다! AIStudios 통합이 완료되었습니다.")
    else:
        print("   🔧 실패한 테스트를 확인하고 설정을 점검해주세요.")
        print("   📖 상세한 설정 방법은 README_AISTUDIOS.md를 참고하세요.")

def main():
    """메인 테스트 실행"""
    print_section("🚀 AIStudios 통합 테스트 시작")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 테스트 대상: {BASE_URL}")
    
    results = []
    
    # 환경 설정 확인
    print_section("🔧 환경 설정 확인")
    env_ok = test_environment_setup()
    results.append({
        'name': '환경 설정',
        'success': env_ok,
        'message': '환경 변수 및 디렉토리 설정'
    })
    
    # 서버 상태 확인
    print_section("🌐 서버 연결 테스트")
    server_ok, server_data = check_server_status()
    results.append({
        'name': '서버 연결',
        'success': server_ok,
        'message': '기본 API 연결 확인'
    })
    
    if not server_ok:
        print("\n❌ 서버에 연결할 수 없습니다.")
        print("   서버가 실행 중인지 확인해주세요:")
        print("   python run.py --mode test  또는  python run.py --mode main")
        return
    
    # AIStudios 기능별 테스트
    print_section("🎬 AIStudios 기능 테스트")
    
    # AIStudios 상태 API
    status_ok = test_aistudios_status()
    results.append({
        'name': 'AIStudios 상태 API',
        'success': status_ok,
        'message': '상태 조회 API 동작'
    })
    
    # 면접관 질문 영상 생성
    interview_question_ok = test_interview_question_video()
    results.append({
        'name': '면접관 질문 영상',
        'success': interview_question_ok,
        'message': '면접관 질문 영상 생성'
    })
    
    # 면접 피드백 영상 생성
    interview_feedback_ok = test_interview_feedback_video()
    results.append({
        'name': '면접 피드백 영상',
        'success': interview_feedback_ok,
        'message': '면접 피드백 영상 생성'
    })
    
    # 토론 AI 영상 생성
    debate_ok = test_debate_ai_video()
    results.append({
        'name': '토론 AI 영상',
        'success': debate_ok,
        'message': '토론 AI 영상 생성'
    })
    
    # 캐시 관리
    cache_ok = test_cache_management()
    results.append({
        'name': '캐시 관리',
        'success': cache_ok,
        'message': '캐시 정리 기능'
    })
    
    # 테스트 결과 보고서
    generate_test_report(results)
    
    print(f"\n⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
