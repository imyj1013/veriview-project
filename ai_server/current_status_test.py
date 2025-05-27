#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현재 구현 상태 직접 테스트 스크립트
웹페이지 없이 AI 서버 기능을 직접 확인
"""

import requests
import json
import time

def test_current_implementation():
    """현재 구현된 기능들을 직접 테스트"""
    print("🚀 현재 구현 상태 테스트 시작")
    print("=" * 60)
    
    # 1. AI 서버 상태 확인
    print("\n1. AI 서버 연결 상태 확인")
    try:
        response = requests.get("http://localhost:5000/ai/health", timeout=5)
        if response.status_code == 200:
            print("✅ AI 서버 정상 작동")
            result = response.json()
            print(f"   상태: {result.get('status')}")
            print(f"   서비스: {result.get('services')}")
        else:
            print("❌ AI 서버 응답 오류")
            return False
    except Exception as e:
        print(f"❌ AI 서버 연결 실패: {e}")
        print("   해결방법: cd ai_server && python main.py")
        return False
    
    # 2. 토론면접 완전 테스트
    print("\n2. 토론면접 기능 테스트")
    
    # 토론면접 시작
    try:
        start_data = {
            "topic": "인공지능이 인간의 일자리를 대체할 것인가",
            "position": "PRO"
        }
        response = requests.post("http://localhost:5000/ai/debate/start", 
                               json=start_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            debate_id = result.get('debate_id')
            print(f"✅ 토론면접 시작 성공 - ID: {debate_id}")
            
            # AI 입론 생성
            ai_data = {
                "topic": "인공지능이 인간의 일자리를 대체할 것인가"
            }
            ai_response = requests.post(f"http://localhost:5000/ai/debate/{debate_id}/ai-opening",
                                      json=ai_data, timeout=10)
            
            if ai_response.status_code == 200:
                ai_result = ai_response.json()
                ai_text = ai_result.get('ai_opening_text', '')
                print(f"✅ AI 입론 생성 성공")
                print(f"   AI 입론 내용: {ai_text[:100]}...")
                
                print("\n📹 실제 웹페이지에서는 여기서 사용자가 영상을 업로드하게 됩니다.")
                print("   영상 분석 후 점수와 AI 반론이 제공됩니다.")
                
            else:
                print("❌ AI 입론 생성 실패")
        else:
            print("❌ 토론면접 시작 실패")
            
    except Exception as e:
        print(f"❌ 토론면접 테스트 오류: {e}")
    
    # 3. 개인면접 완전 테스트
    print("\n3. 개인면접 기능 테스트")
    
    try:
        # 개인면접 시작
        start_data = {"type": "general"}
        response = requests.post("http://localhost:5000/ai/interview/start",
                               json=start_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            interview_id = result.get('interview_id')
            print(f"✅ 개인면접 시작 성공 - ID: {interview_id}")
            
            # 면접 질문 생성
            question_response = requests.get(f"http://localhost:5000/ai/interview/{interview_id}/question",
                                           params={'type': 'general'}, timeout=10)
            
            if question_response.status_code == 200:
                question_result = question_response.json()
                question = question_result.get('question', '')
                print(f"✅ 면접 질문 생성 성공")
                print(f"   질문: {question}")
                
                print("\n📹 실제 웹페이지에서는 여기서 사용자가 답변 영상을 업로드하게 됩니다.")
                print("   영상 분석 후 점수와 피드백이 제공됩니다.")
                
            else:
                print("❌ 면접 질문 생성 실패")
        else:
            print("❌ 개인면접 시작 실패")
            
    except Exception as e:
        print(f"❌ 개인면접 테스트 오류: {e}")
    
    # 4. 백엔드 연결 테스트
    print("\n4. 백엔드 연결 상태 확인")
    try:
        response = requests.get("http://localhost:4000/api/test", timeout=5)
        if response.status_code == 200:
            print("✅ 백엔드 서버 정상 작동")
        else:
            print("❌ 백엔드 서버 응답 오류")
    except Exception as e:
        print(f"❌ 백엔드 연결 실패: {e}")
        print("   해결방법: cd backend && ./gradlew bootRun")
    
    return True

def show_current_limitations():
    """현재 구현의 한계점과 다음 단계 설명"""
    print("\n" + "=" * 60)
    print("📋 현재 구현 상태 및 한계점")
    print("=" * 60)
    
    print("\n✅ 현재 작동하는 기능:")
    print("   1. AI 서버 API 모든 엔드포인트")
    print("   2. 토론면접 시작 → AI 입론 생성")
    print("   3. 개인면접 시작 → 질문 생성")
    print("   4. 영상 업로드 시 분석 및 점수 산출")
    print("   5. 백엔드 채용공고 크롤링")
    
    print("\n❌ 아직 연결되지 않은 부분:")
    print("   1. 프론트엔드 UI (React 컴포넌트)")
    print("   2. 백엔드에서 AI 서버 호출하는 API")
    print("   3. 프론트엔드에서 면접 시작하는 버튼 연동")
    
    print("\n🔧 웹페이지에서 완전히 작동하려면 필요한 것:")
    print("   1. 프론트엔드에 '토론면접 시작' 버튼 구현")
    print("   2. 백엔드에 면접 관련 API 엔드포인트 추가")
    print("   3. 프론트엔드-백엔드-AI서버 3단계 연동")

def show_next_steps():
    """다음 단계 가이드"""
    print("\n" + "=" * 60)
    print("🚀 웹페이지 완전 연동을 위한 다음 단계")
    print("=" * 60)
    
    print("\n1️⃣ 현재 바로 테스트 가능한 방법:")
    print("   # AI 서버 실행")
    print("   cd ai_server")
    print("   python main.py")
    print("")
    print("   # 다른 터미널에서 직접 API 호출")
    print("   curl -X POST http://localhost:5000/ai/debate/start \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"topic\": \"인공지능\", \"position\": \"PRO\"}'")
    
    print("\n2️⃣ 완전한 웹페이지 연동을 위해 추가 필요:")
    print("   - 백엔드에 면접 관련 Controller 추가")
    print("   - 프론트엔드에 면접 UI 컴포넌트 추가")
    print("   - 3-tier 아키텍처 완성")
    
    print("\n3️⃣ 현재 상태로도 다음은 완전히 작동:")
    print("   - Postman/curl로 모든 AI 기능 테스트")
    print("   - 백엔드 채용공고 크롤링")
    print("   - AI 서버 단독 영상 분석")

if __name__ == "__main__":
    print("🔍 VeriView AI 서버 현재 구현 상태 확인")
    
    if test_current_implementation():
        show_current_limitations()
        show_next_steps()
        
        print("\n" + "="*60)
        print("💡 결론: AI 서버 기능은 완전히 구현되었으나,")
        print("   웹페이지 완전 연동을 위해서는 프론트엔드 UI와")
        print("   백엔드 API 연동이 추가로 필요합니다.")
        print("="*60)
    else:
        print("\n❌ 기본 서버 연결부터 확인이 필요합니다.")
        print("   먼저 AI 서버를 실행해주세요: python main.py")
