#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실행 가이드 및 시스템 상태 확인 스크립트
VeriView AI 서버 시스템의 전체적인 실행 가이드를 제공합니다.
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def print_banner():
    """VeriView 시스템 배너 출력"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    VeriView AI 서버 시스템                    ║
    ║              면접 및 토론 연습을 위한 AI 플랫폼               ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_file_exists(file_path, description):
    """파일 존재 여부 확인"""
    if os.path.exists(file_path):
        print(f" {description}: {file_path}")
        return True
    else:
        print(f" {description}: {file_path} (파일 없음)")
        return False

def check_system_status():
    """시스템 상태 확인"""
    print("\n" + "="*60)
    print(" 시스템 상태 확인")
    print("="*60)
    
    # 현재 작업 디렉터리 확인
    current_dir = os.getcwd()
    print(f" 현재 디렉터리: {current_dir}")
    
    # 필수 파일들 확인
    essential_files = [
        ("main_server.py", "메인 AI 서버"),
        ("test_server.py", "테스트 AI 서버"),
        ("backend_integration_test.py", "통합 테스트 스크립트"),
        ("job_recommendation_module.py", "공고추천 모듈"),
        ("requirements.txt", "필요 패키지 목록")
    ]
    
    missing_files = []
    for file_path, description in essential_files:
        if not check_file_exists(file_path, description):
            missing_files.append(file_path)
    
    # 디렉터리 구조 확인
    directories = [
        ("test_features", "테스트 기능 모듈"),
        ("test_features/debate", "토론 테스트 모듈"),
        ("test_features/personal_interview", "개인면접 테스트 모듈"),
        ("interview_features", "실제 면접 기능 모듈"),
        ("models", "AI 모델 파일"),
        ("tools", "외부 도구")
    ]
    
    for dir_path, description in directories:
        if os.path.exists(dir_path):
            print(f" {description}: {dir_path}/")
        else:
            print(f" {description}: {dir_path}/ (디렉터리 없음)")
    
    return len(missing_files) == 0

def check_dependencies():
    """Python 패키지 의존성 확인"""
    print("\n" + "="*60)
    print("📦 Python 패키지 의존성 확인")
    print("="*60)
    
    required_packages = [
        ("flask", "Flask 웹 프레임워크"),
        ("flask_cors", "CORS 지원"),
        ("requests", "HTTP 요청 라이브러리"),
        ("numpy", "수치 계산"),
        ("pandas", "데이터 처리"),
        ("opencv-python", "컴퓨터 비전"),
        ("librosa", "오디오 분석"),
        ("openai-whisper", "음성 인식"),
        ("TTS", "음성 합성")
    ]
    
    missing_packages = []
    
    for package_name, description in required_packages:
        try:
            __import__(package_name.replace("-", "_"))
            print(f" {description}: {package_name}")
        except ImportError:
            print(f" {description}: {package_name} (설치 필요)")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n 설치가 필요한 패키지: {', '.join(missing_packages)}")
        print("설치 명령어: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_server_status(url, server_name):
    """서버 상태 확인"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f" {server_name}: 정상 작동 중")
            return True
        else:
            print(f" {server_name}: HTTP {response.status_code}")
            return False
    except requests.ConnectionError:
        print(f" {server_name}: 연결 실패 (서버 미실행)")
        return False
    except Exception as e:
        print(f" {server_name}: 오류 ({str(e)})")
        return False

def check_running_servers():
    """실행 중인 서버 확인"""
    print("\n" + "="*60)
    print(" 서버 실행 상태 확인")
    print("="*60)
    
    ai_server_status = check_server_status("http://localhost:5000/ai/health", "AI 서버")
    backend_status = check_server_status("http://localhost:4000/api/test", "백엔드 서버")
    
    return ai_server_status, backend_status

def show_execution_guide():
    """실행 가이드 출력"""
    print("\n" + "="*60)
    print(" VeriView 시스템 실행 가이드")
    print("="*60)
    
    print("\n1️ AI 서버 실행:")
    print("   메인 서버 (모든 AI 기능 포함):")
    print("   $ python main_server.py")
    print("   ")
    print("   테스트 서버 (LLM 제외, 고정 응답):")
    print("   $ python test_server.py")
    
    print("\n2️ 백엔드 서버 실행:")
    print("   $ cd ../backend")
    print("   $ ./gradlew bootRun")
    print("   (또는 IDE에서 BackendApplication.java 실행)")
    
    print("\n3️ 프론트엔드 실행:")
    print("   $ cd ../frontend")
    print("   $ npm start")
    
    print("\n4️ 통합 테스트 실행:")
    print("   $ python backend_integration_test.py")

def show_troubleshooting():
    """일반적인 문제 해결 가이드"""
    print("\n" + "="*60)
    print(" 일반적인 문제 해결")
    print("="*60)
    
    print("\n 포트 충돌 문제:")
    print("   - AI 서버: 5000번 포트")
    print("   - 백엔드: 4000번 포트")  
    print("   - 프론트엔드: 3000번 포트")
    print("   포트 사용 확인: netstat -an | grep :5000")
    
    print("\n 패키지 설치 문제:")
    print("   $ pip install -r requirements.txt")
    print("   $ pip install --upgrade pip")
    
    print("\n OpenFace 도구 문제:")
    print("   - tools/FeatureExtraction.exe 파일 확인")
    print("   - OpenFace 공식 사이트에서 다운로드 필요")
    
    print("\n 메모리 부족 문제:")
    print("   - 대용량 AI 모델 사용 시 8GB 이상 RAM 권장")
    print("   - test_server.py 사용 (LLM 모델 제외)")
    
    print("\n 백엔드 연동 문제:")
    print("   - 백엔드 서버가 먼저 실행되어 있어야 함")
    print("   - application.properties 설정 확인")

def run_quick_test():
    """빠른 기능 테스트"""
    print("\n" + "="*60)
    print(" 빠른 기능 테스트")
    print("="*60)
    
    ai_status, backend_status = check_running_servers()
    
    if ai_status:
        print("\n AI 서버 기능 테스트...")
        try:
            # AI 서버 기본 테스트
            response = requests.get("http://localhost:5000/ai/test", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f" AI 서버 테스트 성공")
                print(f"   서버 타입: {data.get('server_type', 'unknown')}")
                print(f"   모드: {data.get('mode', 'unknown')}")
                
                # 각 모듈 상태 출력
                modules = data.get('modules', {})
                for module, status in modules.items():
                    status_icon = "사용 가능" if status == "사용 가능" else "사용 불가"
                    print(f"   {status_icon} {module}: {status}")
            else:
                print(f" AI 서버 테스트 실패: HTTP {response.status_code}")
        except Exception as e:
            print(f" AI 서버 테스트 오류: {str(e)}")
    
    if backend_status:
        print("\n 백엔드 서버 기능 테스트...")
        try:
            response = requests.get("http://localhost:4000/api/test", timeout=10)
            if response.status_code == 200:
                print(" 백엔드 서버 테스트 성공")
            else:
                print(f" 백엔드 서버 테스트 실패: HTTP {response.status_code}")
        except Exception as e:
            print(f" 백엔드 서버 테스트 오류: {str(e)}")
    
    if ai_status and backend_status:
        print("\n AI-백엔드 연동 테스트...")
        try:
            # 공고추천 연동 테스트
            test_data = {
                "user_id": "test_user",
                "category": "ICT",
                "workexperience": "경력무관",
                "education": "대졸",
                "major": "컴퓨터공학",
                "location": "서울"
            }
            
            response = requests.post(
                "http://localhost:4000/api/recruitment/start",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                posting_count = len(result.get("posting", []))
                print(f" AI-백엔드 연동 테스트 성공 ({posting_count}개 공고 추천)")
            else:
                print(f" AI-백엔드 연동 테스트 실패: HTTP {response.status_code}")
        except Exception as e:
            print(f" AI-백엔드 연동 테스트 오류: {str(e)}")

def show_api_endpoints():
    """API 엔드포인트 정보"""
    print("\n" + "="*60)
    print(" 주요 API 엔드포인트")
    print("="*60)
    
    print("\n AI 서버 (http://localhost:5000):")
    print("   GET  /ai/health               - 서버 상태 확인")
    print("   GET  /ai/test                 - 연결 테스트")
    print("   POST /ai/jobs/recommend       - 공고 추천")
    print("   POST /ai/interview/start      - 개인면접 시작")
    print("   POST /ai/debate/{id}/ai-opening - AI 토론 입론")
    
    print("\n 백엔드 서버 (http://localhost:4000):")
    print("   GET  /api/test                - 연결 테스트")
    print("   POST /api/recruitment/start   - 공고추천 시작")
    print("   POST /api/debate/start        - 토론면접 시작")
    print("   POST /api/interview/portfolio - 개인면접 시작")
    
    print("\n 프론트엔드 (http://localhost:3000):")
    print("   /                             - 메인 페이지")
    print("   /login                        - 로그인")
    print("   /debate                       - 토론면접")
    print("   /interview                    - 개인면접")
    print("   /jobs                         - 공고추천")

def main():
    """메인 실행 함수"""
    print_banner()
    
    print("VeriView AI 서버 시스템 상태를 확인합니다...\n")
    
    # 시스템 파일 상태 확인
    system_ok = check_system_status()
    
    # 패키지 의존성 확인
    deps_ok = check_dependencies()
    
    # 서버 실행 상태 확인
    ai_status, backend_status = check_running_servers()
    
    # 전체 상태 평가
    if system_ok and deps_ok and ai_status and backend_status:
        print("\n 모든 시스템이 정상 작동 중입니다!")
        run_quick_test()
    else:
        print("\n 일부 시스템에 문제가 있습니다.")
        
        if not system_ok:
            print("   - 필수 파일이 누락되었습니다.")
        if not deps_ok:
            print("   - Python 패키지를 설치해야 합니다.")
        if not ai_status:
            print("   - AI 서버를 실행해야 합니다.")
        if not backend_status:
            print("   - 백엔드 서버를 실행해야 합니다.")
    
    # 실행 가이드 출력
    show_execution_guide()
    
    # API 엔드포인트 정보
    show_api_endpoints()
    
    # 문제 해결 가이드
    show_troubleshooting()
    
    print("\n" + "="*60)
    print("💡 추가 도움이 필요하시면 다음 명령어를 실행하세요:")
    print("   python backend_integration_test.py  # 전체 통합 테스트")
    print("="*60)

if __name__ == "__main__":
    main()
