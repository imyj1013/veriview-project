#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
피드백 API 빠른 진단 도구
"""
import requests
import json

def test_interview_feedback():
    """면접 피드백 API 테스트"""
    print("🎯 면접 피드백 API 진단")
    print("=" * 50)
    
    # 1. 백엔드 피드백 API 테스트
    print("1. 백엔드 피드백 API 테스트")
    try:
        response = requests.get("http://localhost:4000/api/interview/1/feedback", timeout=10)
        print(f"   상태: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 백엔드 피드백 API 정상")
        elif response.status_code == 500:
            print("   ❌ 백엔드 500 에러 - 데이터베이스 문제 가능성")
            print(f"   응답: {response.text[:200]}...")
        else:
            print(f"   ⚠️ 백엔드 응답: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 백엔드 연결 실패: {str(e)}")
    
    # 2. AI 서버 테스트
    print("\n2. AI 서버 상태 테스트")
    try:
        response = requests.get("http://localhost:5000/ai/test", timeout=5)
        print(f"   상태: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ AI 서버 정상")
            result = response.json()
            print(f"   모듈 상태: {result.get('modules', {})}")
        else:
            print(f"   ❌ AI 서버 오류: {response.status_code}")
    except Exception as e:
        print(f"   ❌ AI 서버 연결 실패: {str(e)}")
    
    # 3. AI 서버 면접 답변 처리 테스트
    print("\n3. AI 서버 답변 처리 테스트")
    try:
        # 더미 파일 생성 (빈 파일로 테스트)
        files = {'file': ('test.mp4', b'dummy video data', 'video/mp4')}
        response = requests.post(
            "http://localhost:5000/ai/interview/1/INTRO/answer-video",
            files=files,
            timeout=30
        )
        print(f"   상태: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ AI 답변 처리 정상")
            result = response.json()
            print(f"   점수: {result.get('content_score', 'N/A')}/{result.get('voice_score', 'N/A')}/{result.get('action_score', 'N/A')}")
        else:
            print(f"   ❌ AI 답변 처리 실패: {response.status_code}")
            print(f"   응답: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ AI 답변 처리 오류: {str(e)}")

def diagnose_ports():
    """포트 상태 진단"""
    print("\n🔌 포트 상태 진단")
    print("=" * 30)
    
    import socket
    
    ports_to_check = [
        (3000, "React 프론트엔드"),
        (4000, "Spring 백엔드"),
        (5000, "Flask AI 서버"),
        (3306, "MySQL 데이터베이스")
    ]
    
    for port, service in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"   ✅ 포트 {port} ({service}): 열림")
        else:
            print(f"   ❌ 포트 {port} ({service}): 닫힘")

if __name__ == "__main__":
    print("🚨 VeriView 피드백 시스템 긴급 진단")
    print("=" * 60)
    
    diagnose_ports()
    test_interview_feedback()
    
    print("\n" + "=" * 60)
    print("📋 문제 해결 체크리스트:")
    print("1. 모든 서버가 실행 중인가?")
    print("   - React: npm start (포트 3000)")
    print("   - Spring: ./gradlew bootRun (포트 4000)")
    print("   - Flask AI: python run.py --mode test (포트 5000)")
    print("   - MySQL: 서비스 실행 중 (포트 3306)")
    print("\n2. 데이터베이스 스키마가 올바른가?")
    print("   - job_posting 테이블에 올바른 컬럼이 있는가?")
    print("   - 면접 데이터가 저장되어 있는가?")
    print("\n3. 네트워크 연결이 정상인가?")
    print("   - localhost 주소로 접근 가능한가?")
    print("   - 방화벽이 포트를 차단하지 않는가?")
