#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 서버 테스트 실행 스크립트

사용법:
    python test_runner.py [video_path]

예시:
    python test_runner.py test_video.mp4
    python test_runner.py ../videos/sample.mp4
"""

import sys
import os

# 현재 파일의 상위 디렉터리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from tests.test_debate import DebateTester

def main():
    if len(sys.argv) < 2:
        print("사용법: python test_runner.py [video_path]")
        print("예시: python test_runner.py test_video.mp4")
        return
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"오류: 영상 파일을 찾을 수 없습니다: {video_path}")
        return
    
    try:
        print("AI 서버 테스트 시작...")
        print(f"영상 파일: {video_path}")
        print("-" * 50)
        
        tester = DebateTester()
        tester.run_test(video_path)
        
        print("-" * 50)
        print("테스트 완료!")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
