# AI 서버 실행 파일
# 테스트 환경에서는 src/tests의 기능들을 사용
import sys
import os

# src 디렉터리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# 환경에 따라 다른 모듈 사용
USE_TEST_MODE = os.getenv('USE_TEST_MODE', 'true').lower() == 'true'

if USE_TEST_MODE:
    # 테스트 모드: src/tests 디렉터리의 기능 사용
    print("테스트 모드로 실행 중...")
    from tests.test_debate import DebateTester
    
    if __name__ == "__main__":
        tester = DebateTester()
        print("AI 서버 테스트 실행을 위해 test_debate.py 모듈을 확인하세요.")
        print("영상 파일 경로를 지정하고 tester.run_test(video_path)를 호출하세요.")
else:
    # 프로덕션 모드: src/app 디렉터리의 Flask 서버 사용
    from app.debate_server import app
    
    if __name__ == "__main__":
        print("프로덕션 모드로 Flask 서버 실행 중...")
        app.run(host="0.0.0.0", port=5000, debug=True)
