@echo off
chcp 65001 > nul
echo ====================================
echo VeriView AI Server - Windows Edition
echo ====================================
echo.

:: Python 설치 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았거나 PATH에 등록되지 않았습니다.
    echo 💡 Python 3.8 이상을 설치하고 PATH에 추가하세요.
    pause
    exit /b 1
)

:: 현재 디렉토리 확인
if not exist "run_windows.py" (
    echo ❌ run_windows.py 파일을 찾을 수 없습니다.
    echo 💡 ai_server 디렉토리에서 실행하세요.
    pause
    exit /b 1
)

echo ✅ Python 환경 확인 완료
echo ✅ 스크립트 파일 확인 완료
echo.

:: 기본 모드로 실행
echo 🚀 VeriView AI 서버를 시작합니다...
echo 📍 모드: 메인 모드 (완전 통합)
echo 📍 주소: http://localhost:5000
echo.
echo ⏳ 서버 시작 중... (몇 초 정도 소요됩니다)
echo.

python run_windows.py --mode main

echo.
echo 👋 서버가 종료되었습니다.
pause
