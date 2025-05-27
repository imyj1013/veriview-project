#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 실행 스크립트
환경 변수 SERVER_MODE를 통해 메인 서버 또는 테스트 서버 모드 선택

실행 방법:
- 메인 서버 실행: python run.py --mode main
- 테스트 서버 실행: python run.py --mode test
- 환경 변수 사용: SERVER_MODE=main python run.py

사용 가능한 모드:
- main: LLM, OpenFace, Whisper, TTS, Librosa 등 실제 AI 모듈 사용 (포트: 5001)
- test: LLM 제외, 고정 응답 반환 (OpenFace, Whisper, TTS, Librosa 모듈 사용 가능) (포트: 5000)
"""
import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional, List, Tuple

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ai_server.log")
    ]
)
logger = logging.getLogger("ai_server")

# 서버 모드 설정
SERVER_MODES = {
    "main": {
        "name": "Main Server",
        "description": "LLM, OpenFace, Whisper, TTS, Librosa 등 실제 AI 모듈 사용",
        "module": "main_server",
        "port": 5001
    },
    "test": {
        "name": "Test Server",
        "description": "LLM 제외, 고정 응답 반환 (OpenFace, Whisper, TTS, Librosa 모듈 사용 가능)",
        "module": "test_server",
        "port": 5000
    }
}

def check_dependencies() -> Dict[str, bool]:
    """
    의존성 패키지 설치 여부 확인
    
    Returns:
        Dict[str, bool]: 패키지별 설치 여부
    """
    dependencies = {
        "flask": False,
        "flask_cors": False,
        "gtts": False,
        "pyttsx3": False,
        "whisper": False,
        "librosa": False,
        "openai": False,
        "numpy": False,
        "pandas": False,
        "matplotlib": False,
        "scikit-learn": False,
        "torch": False
    }
    
    for package in dependencies.keys():
        try:
            # importlib을 사용한 패키지 임포트 시도
            if package == 'whisper':
                try:
                    import whisper
                    dependencies[package] = True
                except ImportError:
                    dependencies[package] = False
            else:
                __import__(package)
                dependencies[package] = True
        except ImportError:
            dependencies[package] = False
    
    return dependencies

def print_dependencies_status(dependencies: Dict[str, bool]) -> None:
    """
    의존성 패키지 설치 상태 출력
    
    Args:
        dependencies: 패키지별 설치 여부
    """
    print("\n=== 의존성 패키지 설치 상태 ===")
    
    # 카테고리별 패키지 분류
    categories = {
        "서버": ["flask", "flask_cors"],
        "TTS": ["gtts", "pyttsx3"],
        "음성 분석": ["whisper", "librosa"],
        "AI/ML": ["openai", "numpy", "pandas", "matplotlib", "scikit-learn", "torch"]
    }
    
    for category, packages in categories.items():
        print(f"\n[{category}]")
        for package in packages:
            status = "설치됨" if dependencies.get(package, False) else "설치 필요"
            print(f"  {package}: {status}")
    
    # 필수 패키지 설치 확인
    essential_packages = ["flask", "flask_cors"]
    essential_missing = [pkg for pkg in essential_packages if not dependencies.get(pkg, False)]
    
    if essential_missing:
        print("\n 필수 패키지가 설치되지 않았습니다. 다음 명령어로 설치해주세요:")
        print(f"  pip install {' '.join(essential_missing)}")
    
    print("\n추가 패키지 설치 방법:")
    print("  pip install gtts                  # TTS 모듈 설치 (경량)")
    print("  pip install pyttsx3              # TTS 모듈 설치 (오프라인)")
    print("  pip install openai-whisper        # 음성 인식 모듈 설치")
    print("  pip install librosa              # 음성 분석 모듈 설치")
    print("  pip install openai               # OpenAI LLM 모듈 설치")
    print("  pip install -r requirements.txt   # 모든 의존성 설치")
    print("")

def get_server_mode() -> Tuple[str, int]:
    """
    서버 모드 및 포트 설정 가져오기
    - 명령줄 인자 > 환경 변수 > 기본값 순으로 설정
    
    Returns:
        Tuple[str, int]: (서버 모드, 포트 번호)
    """
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description="VeriView AI 서버 실행")
    parser.add_argument("--mode", type=str, choices=["main", "test"], 
                        help="서버 모드 (main: 실제 AI 모듈, test: 테스트 모드)")
    parser.add_argument("--port", type=int, help="서버 포트 번호")
    args = parser.parse_args()
    
    # 서버 모드 설정 (명령줄 인자 > 환경 변수 > 기본값)
    mode = args.mode or os.environ.get("SERVER_MODE", "test")
    if mode not in SERVER_MODES:
        logger.warning(f"유효하지 않은 서버 모드: {mode}, 기본값(test)으로 설정합니다.")
        mode = "test"
    
    # 포트 설정 (명령줄 인자 > 환경 변수 > 모드별 기본값)
    port = args.port or int(os.environ.get("SERVER_PORT", SERVER_MODES[mode]["port"]))
    
    return mode, port

def run_server(mode: str, port: int) -> None:
    """
    지정된 모드와 포트로 서버 실행
    
    Args:
        mode: 서버 모드 ("main" 또는 "test")
        port: 서버 포트 번호
    """
    server_info = SERVER_MODES[mode]
    module_name = server_info["module"]
    
    try:
        # 환경 변수 설정
        os.environ["SERVER_MODE"] = mode
        os.environ["SERVER_PORT"] = str(port)
        
        # 서버 모듈 임포트 및 실행
        if os.path.exists(f"{module_name}.py"):
            logger.info(f"{server_info['name']} 실행 중 (포트: {port})...")
            print(f"\n {server_info['name']} 시작...")
            print(f"서버 주소: http://localhost:{port}")
            print(f"테스트 엔드포인트: http://localhost:{port}/ai/test")
            print(f"상태 확인 엔드포인트: http://localhost:{port}/ai/health")
            print(f"TTS 테스트 엔드포인트: http://localhost:{port}/ai/tts-test?text=안녕하세요")
            
            # 서버 모듈 실행
            if mode == "main":
                import main_server
                main_server.app.run(host="0.0.0.0", port=port, debug=True)
            else:
                import test_server
                test_server.app.run(host="0.0.0.0", port=port, debug=True)
        else:
            logger.error(f"서버 모듈을 찾을 수 없습니다: {module_name}.py")
            print(f"오류: {module_name}.py 파일을 찾을 수 없습니다.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"서버 실행 중 오류 발생: {str(e)}")
        print(f"서버 실행 오류: {str(e)}")
        sys.exit(1)

def main() -> None:
    """메인 함수"""
    print("\n=== VeriView AI 서버 ===")
    
    # 의존성 확인
    dependencies = check_dependencies()
    print_dependencies_status(dependencies)
    
    # 서버 모드 및 포트 설정
    mode, port = get_server_mode()
    
    # 모드 정보 출력
    server_info = SERVER_MODES[mode]
    print(f"\n선택된 서버: {server_info['name']}")
    print(f"설명: {server_info['description']}")
    print(f"포트: {port}")
    
    # 서버 실행
    run_server(mode, port)

if __name__ == "__main__":
    main()
