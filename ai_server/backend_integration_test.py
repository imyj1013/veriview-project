#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 서버와 백엔드 연동 테스트 스크립트

백엔드가 AI 서버로 영상을 전송하여 분석 결과를 받는 기능을 테스트합니다.
"""

import requests
import json
import os
import sys
from pathlib import Path

def test_ai_server_connection():
    """AI 서버 연결 테스트"""
    try:
        response = requests.get("http://localhost:5000/ai/test")
        if response.status_code == 200:
            print("✅ AI 서버 연결 성공")
            print(f"   응답: {response.json()}")
            return True
        else:
            print(f"❌ AI 서버 연결 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI 서버 연결 오류: {str(e)}")
        return False

def test_ai_opening():
    """AI 입론 생성 테스트"""
    try:
        data = {
            "topic": "인공지능은 인간의 일자리를 대체할 것인가",
            "position": "CON"
        }
        response = requests.post("http://localhost:5000/ai/debate/999/ai-opening", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ AI 입론 생성 성공")
            print(f"   AI 입론: {result.get('ai_opening_text')}")
            return True
        else:
            print(f"❌ AI 입론 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI 입론 생성 오류: {str(e)}")
        return False

def test_video_analysis(video_path, phase="opening"):
    """영상 분석 테스트"""
    if not os.path.exists(video_path):
        print(f"❌ 영상 파일을 찾을 수 없습니다: {video_path}")
        return False
    
    try:
        with open(video_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"http://localhost:5000/ai/debate/999/{phase}-video", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {phase} 영상 분석 성공")
            print(f"   사용자 텍스트: {result.get(f'user_{phase}_text', '없음')}")
            print(f"   적극성 점수: {result.get('initiative_score', 0)}")
            print(f"   의사소통 점수: {result.get('communication_score', 0)}")
            print(f"   피드백: {result.get('feedback', '없음')}")
            
            if phase != "closing":
                ai_next_phase = {"opening": "rebuttal", "rebuttal": "counter_rebuttal", "counter-rebuttal": "closing"}.get(phase)
                if ai_next_phase:
                    ai_text_key = f"ai_{ai_next_phase}_text"
                    print(f"   AI {ai_next_phase}: {result.get(ai_text_key, '없음')}")
            return True
        else:
            print(f"❌ {phase} 영상 분석 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {phase} 영상 분석 오류: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("AI 서버 백엔드 연동 테스트 시작")
    print("=" * 50)
    
    # 1. AI 서버 연결 테스트
    print("\n1. AI 서버 연결 테스트")
    if not test_ai_server_connection():
        print("AI 서버가 실행중인지 확인하세요: python server_runner.py")
        return
    
    # 2. AI 입론 생성 테스트
    print("\n2. AI 입론 생성 테스트")
    test_ai_opening()
    
    # 3. 영상 분석 테스트 (영상 파일이 있는 경우)
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        print(f"\n3. 영상 분석 테스트: {video_path}")
        
        phases = ["opening", "rebuttal", "counter-rebuttal", "closing"]
        for phase in phases:
            print(f"\n3.{phases.index(phase)+1}. {phase} 분석 테스트")
            test_video_analysis(video_path, phase)
    else:
        print("\n3. 영상 분석 테스트")
        print("   영상 파일 경로가 제공되지 않아 스킵합니다.")
        print("   사용법: python backend_integration_test.py [영상파일경로]")
    
    print("\n" + "=" * 50)
    print("테스트 완료!")
    print("=" * 50)

if __name__ == "__main__":
    main()
