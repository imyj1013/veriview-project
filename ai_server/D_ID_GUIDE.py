#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 실행 가이드
D-ID API를 통한 AI 아바타 영상 생성

실행 방법:
1. 환경 변수 설정 (.env 파일)
   D_ID_API_KEY=your_actual_d_id_api_key_here

2. 서버 실행
   python run.py
"""

import os
import sys

def print_guide():
    print("="*80)
    print("VeriView AI 서버 - D-ID API 통합")
    print("="*80)
    
    print("\n📋 사전 준비:")
    print("1. D-ID API 키 발급")
    print("   - https://studio.d-id.com 에서 회원가입")
    print("   - API Keys 메뉴에서 키 생성")
    print("   - 무료 플랜: 월 5분 제한")
    
    print("\n2. 환경 변수 설정")
    print("   .env 파일에 API 키 추가:")
    print("   D_ID_API_KEY=your_actual_api_key_here")
    
    print("\n3. 필수 패키지 설치")
    print("   pip install -r requirements.txt")
    
    print("\n🚀 서버 실행:")
    print("python run.py")
    print("또는")
    print("python run.py --mode test  (D-ID API 연결 테스트)")
    
    print("\n📡 주요 기능:")
    
    print("\n1. 개인면접 AI 면접관")
    print("   - 면접 질문 영상 생성")
    print("   - 한국어 음성 (TTS 포함)")
    print("   - 실사 느낌 아바타")
    
    print("\n2. 토론면접 AI 토론자")
    print("   - 입론/반론/재반론/최종변론 영상")
    print("   - 찬성/반대 입장별 아바타")
    print("   - 자연스러운 토론 진행")
    
    print("\n📌 D-ID API 특징:")
    print("- TTS 기능 내장 (별도 TTS 불필요)")
    print("- 한국어 음성 지원")
    print("- 실사 아바타 영상 생성")
    print("- 영상 생성 시간: 약 30초-1분")
    
    print("\n💡 문제 해결:")
    print("- API 키 오류: .env 파일 확인")
    print("- 401 인증 오류: API 키 형식 확인 (username:password)")
    print("- 429 제한 오류: 무료 플랜 한도 초과")
    print("- 영상 생성 실패: 자동으로 샘플 영상 반환")
    
    print("\n🧪 테스트 방법:")
    print("1. 서버 시작 후 http://localhost:5000/ai/test 접속")
    print("2. D-ID 연결 상태 확인")
    print("3. 백엔드 서버 시작 (localhost:4000)")
    print("4. 프론트엔드에서 면접/토론 시작")
    
    print("\n" + "="*80)

def check_env():
    """환경 설정 확인"""
    env_path = '.env'
    api_key = os.getenv('D_ID_API_KEY')
    
    print("\n환경 설정 확인:")
    if os.path.exists(env_path):
        print("✅ .env 파일 존재")
    else:
        print("❌ .env 파일 없음")
        
    if api_key and api_key != 'your_actual_d_id_api_key_here':
        print(f"✅ D_ID_API_KEY 설정됨: {api_key[:20]}...")
    else:
        print("❌ D_ID_API_KEY 미설정")
        print("   .env 파일에 추가하세요:")
        print("   D_ID_API_KEY=your_actual_api_key_here")

if __name__ == "__main__":
    print_guide()
    check_env()
    
    print("\n서버를 시작하려면:")
    print("python run.py")
