#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 실행 파일
사용법: python run.py [--mode test|main]
"""
import sys
import os
import argparse

# 현재 디렉터리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'src'))

def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(description='VeriView AI 서버 실행')
    parser.add_argument('--mode', type=str, choices=['test', 'main'], 
                       default='main', help='실행 모드 선택 (test: 테스트 서버, main: 메인 서버)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # 기존 server_runner.py 사용 (스트리밍 기능 포함)
    try:
        from server_runner import app, initialize_analyzers
        
        print("=" * 80)
        print(f" VeriView AI 서버 시작 (모드: {args.mode})")
        print("=" * 80)
        print(" 서버 주소: http://localhost:5000")
        print(" 주요 엔드포인트:")
        print("   - 연결 테스트: http://localhost:5000/ai/test")
        print("   - 스트리밍 AI 응답: http://localhost:5000/ai/debate/{debate_id}/ai-response-stream")
        print("   - 면접 실시간 피드백: http://localhost:5000/ai/interview/{interview_id}/answer-stream")
        print("   - 개인면접 질문 생성: http://localhost:5000/ai/interview/generate-question")
        print("   - 개인면접 답변 분석: http://localhost:5000/ai/interview/{interview_id}/{question_type}/answer-video")
        print("   - 공고추천: http://localhost:5000/ai/recruitment/posting")
        print("=" * 80)
        
        # 분석기 초기화
        initialize_analyzers()
        
        # Flask 서버 실행
        app.run(host="0.0.0.0", port=5000, debug=True)
        
    except ImportError as e:
        print(f"서버 모듈 로드 실패: {e}")
        print("server_runner.py 파일이 존재하는지 확인하세요.")
        sys.exit(1)
    except Exception as e:
        print(f"서버 실행 중 오류 발생: {e}")
        sys.exit(1)
