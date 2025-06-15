@echo off
echo.
echo === VeriView AI 서버 테스트 모드 실행 ===
echo.

REM Python 실행 파일 확인
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 오류: Python이 설치되어 있지 않습니다.
    echo Python을 설치하고 PATH에 추가해주세요.
    pause
    exit /b 1
)

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call .venv\Scripts\activate.bat
)

REM 테스트 모드로 서버 실행
echo 테스트 모드로 서버를 시작합니다...
echo (D-ID API 대신 샘플 비디오 사용)
echo.
python run.py --mode test

REM 오류 발생 시 대기
if %errorlevel% neq 0 (
    echo.
    echo 오류가 발생했습니다.
    pause
)
