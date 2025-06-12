#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 실행 스크립트
D-ID API 통합 버전

사용법:
    python run.py                  # 기본 실행 (프로덕션 모드)
    python run.py --mode test      # 테스트 모드
    python run.py --mode debug     # 디버그 모드
    python run.py --port 5001      # 포트 변경
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def set_test_mode():
    """테스트 모드 설정"""
    print("\n=== 테스트 모드 실행 ===")
    print("D-ID API 연결 테스트 모드")
    print("실제 D-ID API를 호출하여 AI 아바타 생성\n")
    
    # 테스트 모드에서도 D-ID API 사용
    os.environ['PREFERRED_AVATAR_SERVICE'] = 'D_ID'
    os.environ['USE_FALLBACK_SERVICE'] = 'True'
    
    # 로깅 레벨 설정
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def set_production_mode():
    """프로덕션 모드 설정"""
    print("\n=== 프로덕션 모드 실행 ===")
    print("D-ID API 사용 (API 키 필요)")
    print("AI 아바타 영상 생성 및 TTS 기능 포함\n")
    
    # 프로덕션 모드에서는 D-ID 사용
    os.environ['PREFERRED_AVATAR_SERVICE'] = 'D_ID'
    os.environ['USE_FALLBACK_SERVICE'] = 'True'
    
    # 로깅 레벨 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def set_debug_mode():
    """디버그 모드 설정"""
    print("\n=== 디버그 모드 실행 ===")
    print("상세 로깅 활성화")
    print("Flask 디버그 모드 활성화\n")
    
    # 디버그 모드에서도 테스트를 위해 샘플 사용 가능
    current_service = os.environ.get('PREFERRED_AVATAR_SERVICE', 'D_ID')
    print(f"현재 아바타 서비스: {current_service}")
    
    # 로깅 레벨 설정
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='VeriView AI 서버 실행')
    parser.add_argument(
        '--mode', 
        choices=['main', 'production', 'test', 'debug'], 
        default='production',
        help='실행 모드 선택 (기본값: production)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=5000,
        help='서버 포트 (기본값: 5000)'
    )
    parser.add_argument(
        '--host', 
        default='0.0.0.0',
        help='서버 호스트 (기본값: 0.0.0.0)'
    )
    
    args = parser.parse_args()
    
    # 모드에 따른 설정
    if args.mode == 'main':
        set_production_mode()  # 메인 모드는 프로덕션 설정 사용
        debug_mode = False
        print("\n=== 메인 모드 실행 ===\n")
    elif args.mode == 'test':
        set_test_mode()
        debug_mode = True
    elif args.mode == 'debug':
        set_debug_mode()
        debug_mode = True
    else:
        set_production_mode()
        debug_mode = False
    
    # 환경 변수 확인
    print("=== 환경 변수 확인 ===")
    print(f"D_ID_API_KEY: {'설정됨' if os.environ.get('D_ID_API_KEY') else '설정 안됨'}")
    print(f"PREFERRED_AVATAR_SERVICE: {os.environ.get('PREFERRED_AVATAR_SERVICE', 'D_ID')}")
    print(f"USE_FALLBACK_SERVICE: {os.environ.get('USE_FALLBACK_SERVICE', 'True')}")
    print()
    
    # 서버 모듈 임포트 및 실행
    try:
        if args.mode == 'main':
            # 메인 모드: 완전 통합 서버 실행
            from veriview_main_server import app, initialize_d_id, initialize_analyzers, initialize_ai_systems
        else:
            # 테스트/디버그 모드: 기존 서버 실행
            from server_runner_d_id import app, initialize_d_id, initialize_analyzers
        
        # 초기화
        print("=== 모듈 초기화 ===")
        
        # 테스트 모드가 아닐 때만 D-ID 초기화
        if args.mode != 'test':
            if initialize_d_id():
                print("D-ID 모듈 초기화 성공")
            else:
                print("D-ID 모듈 초기화 실패 - 폴백 모드 사용")
        else:
            if initialize_d_id():
                print("테스트 모드: D-ID 모듈 초기화 성공")
        
        # 분석기 초기화
        initialize_analyzers()
        print("분석기 초기화 완료")
        
        # 메인 모드에서는 AI 시스템도 초기화
        if args.mode == 'main' and 'initialize_ai_systems' in globals():
            initialize_ai_systems()
            print("AI 시스템 초기화 완료 (LLM, OpenFace 등)")
        
        print()
        
        # 서버 실행
        print(f"=== 서버 시작 ===")
        print(f"주소: http://{args.host}:{args.port}")
        print(f"테스트 엔드포인트: http://localhost:{args.port}/ai/test")
        print("\n서버를 종료하려면 Ctrl+C를 누르세요.\n")
        
        app.run(
            host=args.host, 
            port=args.port, 
            debug=debug_mode
        )
        
    except ImportError as e:
        print(f"서버 모듈 임포트 실패: {e}")
        print("server_runner_d_id.py 파일이 같은 디렉토리에 있는지 확인하세요.")
        sys.exit(1)
    except Exception as e:
        print(f"서버 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
