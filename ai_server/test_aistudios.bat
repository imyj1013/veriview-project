@echo off
echo 🎬 VeriView AIStudios 통합 테스트 시작
echo ========================================
echo.

echo 📁 현재 디렉토리: %CD%
echo.

echo 🔧 1단계: 통합 테스트 실행
echo.
python quick_integration_test.py

echo.
echo ========================================
echo 📋 테스트 완료!
echo.

echo 💡 다음 실행 가능한 명령어들:
echo.
echo   🔹 전체 시스템 테스트:
echo      python run.py --mode test
echo.
echo   🔹 메인 서버 실행:
echo      python run.py --mode main
echo.
echo   🔹 영상 생성 테스트:
echo      python test_video_generation.py
echo.

pause
