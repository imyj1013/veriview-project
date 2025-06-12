@echo off
chcp 65001 > nul
echo ====================================
echo VeriView AI Server - 디버그 모드
echo ====================================
echo.

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았거나 PATH에 등록되지 않았습니다.
    pause
    exit /b 1
)

if not exist "run_windows.py" (
    echo ❌ run_windows.py 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

echo 🐛 디버그 모드로 VeriView AI 서버를 시작합니다...
echo 📍 모드: 디버그 모드 (상세 로깅)
echo 📍 주소: http://localhost:5000
echo 📍 로그: logs/ai_server_debug.log
echo.

python run_windows.py --mode debug

echo.
echo 👋 디버그 서버가 종료되었습니다.
pause
