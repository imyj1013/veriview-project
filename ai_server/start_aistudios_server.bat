@echo off
echo 🚀 VeriView AIStudios 서버 시작
echo ===============================
echo.

echo 📁 현재 디렉토리: %CD%
echo ⏰ 시작 시간: %DATE% %TIME%
echo.

echo 🔑 환경 변수 확인 중...
if not defined AISTUDIOS_API_KEY (
    echo ⚠️  AISTUDIOS_API_KEY 환경 변수가 설정되지 않았습니다.
    echo 📝 .env 파일을 확인하거나 다음 명령으로 설정하세요:
    echo    set AISTUDIOS_API_KEY=your_actual_api_key
    echo.
) else (
    echo ✅ AISTUDIOS_API_KEY 설정 확인
    echo.
)

echo 🎬 AIStudios 통합 서버 시작 중...
echo.
echo 📋 사용 가능한 엔드포인트:
echo   🔹 서버 상태: http://localhost:5000/health
echo   🔹 AI 상태: http://localhost:5000/ai/status
echo   🔹 토론 입론: POST /ai/debate/ai-opening-video
echo   🔹 토론 반론: POST /ai/debate/ai-rebuttal-video
echo   🔹 면접 질문: POST /ai/interview/next-question-video
echo   🔹 면접 피드백: POST /ai/interview/feedback-video
echo.

echo 🛑 서버를 중지하려면 Ctrl+C를 누르세요.
echo ===============================
echo.

python run.py --mode main

echo.
echo 🛑 서버가 종료되었습니다.
pause
