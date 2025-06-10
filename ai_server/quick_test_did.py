#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID TTS 빠른 테스트 스크립트
ai_server/ 디렉토리에서 실행: python quick_test_did.py
"""

import requests
import json
import time
import os
from pathlib import Path

def test_server_status():
    """서버 상태 테스트"""
    print("🔍 1. 서버 상태 확인 중...")
    
    try:
        response = requests.get("http://localhost:5000/ai/test", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 서버 응답 정상")
            
            # D-ID 상태 확인
            did_details = data.get('d_id_details', {})
            print(f"📊 D-ID 연결 상태: {did_details.get('connection_status', '알 수 없음')}")
            print(f"🎤 한국어 음성: {did_details.get('korean_voices', '설정 안됨')}")
            
            if did_details.get('connection_status') == '성공':
                print("✅ D-ID 연결 성공!")
                return True
            else:
                print("❌ D-ID 연결 실패")
                print(f"상세 정보: {did_details}")
                return False
        else:
            print(f"❌ 서버 오류: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다")
        print("서버가 실행 중인지 확인하세요: python run.py --mode test")
        return False
    except Exception as e:
        print(f"❌ 테스트 중 오류: {str(e)}")
        return False

def test_direct_did_api():
    """D-ID API 직접 테스트"""
    print("\n🔍 2. D-ID API 직접 테스트...")
    
    # 환경 변수에서 API 키 가져오기
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get('D_ID_API_KEY')
    if not api_key:
        print("❌ D_ID_API_KEY 환경 변수가 설정되지 않음")
        return False
    
    print(f"🔑 API 키: {api_key[:20]}...{api_key[-10:]}")
    
    url = "https://api.d-id.com/talks"
    payload = {
        "source_url": "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg",
        "script": {
            "type": "text",
            "subtitles": "false",
            "provider": {
                "type": "microsoft",
                "voice_id": "ko-KR-SunHiNeural"  # 한국어 여성 음성
            },
            "input": "안녕하세요. D-ID 테스트입니다.",
            "ssml": "false"
        },
        "config": {"fluent": "false"}
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {api_key}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📡 D-ID API 응답 코드: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            talk_id = result.get('id')
            print(f"✅ D-ID 영상 생성 요청 성공! talk_id: {talk_id}")
            
            # 생성된 테스트 작업 삭제 (크레딧 절약)
            try:
                delete_response = requests.delete(
                    f"https://api.d-id.com/talks/{talk_id}",
                    headers=headers,
                    timeout=10
                )
                print(f"🗑️ 테스트 작업 삭제: {delete_response.status_code}")
            except:
                pass
            
            return True
        else:
            print(f"❌ D-ID API 오류: {response.status_code}")
            print(f"응답: {response.text}")
            
            # 일반적인 오류 해석
            if response.status_code == 401:
                print("💡 해결 방법: API 키를 확인하세요")
            elif response.status_code == 402:
                print("💡 해결 방법: D-ID 계정 크레딧을 확인하세요")
            elif response.status_code == 429:
                print("💡 해결 방법: 요청 한도 초과, 잠시 후 다시 시도하세요")
            
            return False
            
    except Exception as e:
        print(f"❌ D-ID API 테스트 중 오류: {str(e)}")
        return False

def test_ai_opening_video():
    """AI 입론 영상 생성 테스트"""
    print("\n🔍 3. AI 입론 영상 생성 테스트...")
    
    url = "http://localhost:5000/ai/debate/ai-opening-video"
    payload = {
        "ai_opening_text": "보편적 기본소득은 경제적으로 실현 가능한가?에 대해 반대하는 입장에서 말씀드리겠습니다. 이 주제의 문제점들을 지적하고자 합니다.",
        "debate_id": 9999,
        "topic": "보편적 기본소득은 경제적으로 실현가능한가",
        "position": "CON"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("⏳ 영상 생성 중... (30초-2분 소요)")
        start_time = time.time()
        
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        
        end_time = time.time()
        elapsed = int(end_time - start_time)
        
        print(f"📡 응답 코드: {response.status_code} (소요 시간: {elapsed}초)")
        
        if response.status_code == 200:
            # 영상 파일 저장
            video_path = "test_ai_opening.mp4"
            with open(video_path, 'wb') as f:
                f.write(response.content)
            
            # 파일 크기 확인
            file_size = os.path.getsize(video_path)
            print(f"💾 영상 파일 저장: {video_path}")
            print(f"📏 파일 크기: {file_size:,} bytes")
            
            if file_size == 0:
                print("❌ 파일 크기가 0입니다! TTS 처리 실패")
                return False
            elif file_size < 10000:  # 10KB 미만
                print("⚠️ 파일 크기가 너무 작습니다. 영상이 제대로 생성되지 않았을 수 있습니다")
                return False
            else:
                print("✅ 영상 생성 성공!")
                print(f"🎬 재생 명령: ffplay {video_path}")
                return True
        else:
            print(f"❌ 영상 생성 실패: {response.status_code}")
            try:
                error_data = response.json()
                print(f"오류 내용: {error_data}")
            except:
                print(f"응답 내용: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과 (5분)")
        print("💡 D-ID 서버가 느리거나 오류가 발생했을 수 있습니다")
        return False
    except Exception as e:
        print(f"❌ 영상 생성 테스트 중 오류: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    print("🚀 D-ID TTS 통합 테스트 시작")
    print("=" * 50)
    
    # 단계별 테스트
    tests = [
        ("서버 상태", test_server_status),
        ("D-ID API 직접 호출", test_direct_did_api),
        ("AI 입론 영상 생성", test_ai_opening_video)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            if not result:
                print(f"\n❌ {test_name} 실패 - 다음 테스트 건너뜀")
                break
        except Exception as e:
            print(f"\n❌ {test_name} 중 예외 발생: {str(e)}")
            results.append((test_name, False))
            break
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약:")
    
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 모든 테스트 통과! D-ID TTS가 정상 작동합니다.")
        print("💡 이제 프론트엔드에서 AI 입론 영상이 정상적으로 재생될 것입니다.")
    else:
        print("\n🚨 일부 테스트 실패. 위의 오류 메시지를 확인하고 수정하세요.")
        print("\n📋 체크리스트:")
        print("1. 서버가 실행 중인가? (python run.py --mode test)")
        print("2. .env 파일에 D_ID_API_KEY가 설정되어 있는가?")
        print("3. D-ID 계정에 크레딧이 있는가?")
        print("4. 인터넷 연결이 정상인가?")

if __name__ == "__main__":
    main()