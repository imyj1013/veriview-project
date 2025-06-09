@echo off
echo ========================================
echo VeriView AIStudios 통합 서버 시작
echo ========================================
echo.

REM 환경 변수 체크
if "%AISTUDIOS_API_KEY%"=="" (
    echo ⚠️  경고: AISTUDIOS_API_KEY 환경 변수가 설정되지 않았습니다.
    echo.
    echo API 키를 설정하세요:
    echo set AISTUDIOS_API_KEY=your_actual_api_key_here
    echo.
    set /p api_key="API 키를 입력하세요 (또는 Enter를 눌러 건너뛰기): "
    if not "!api_key!"=="" (
        set AISTUDIOS_API_KEY=!api_key!
        echo ✅ API 키가 설정되었습니다.
    )
    echo.
)

REM Python 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 🔄 Python 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

REM AIStudios 통합 확인
echo 🔍 AIStudios 모듈 확인 중...
python -c "from modules.aistudios.client import AIStudiosClient; print('✅ AIStudios 모듈 정상')" 2>nul
if errorlevel 1 (
    echo ❌ AIStudios 모듈을 찾을 수 없습니다.
    echo    modules/aistudios/ 디렉토리가 있는지 확인해주세요.
    pause
    exit /b 1
)

REM 디렉토리 생성
echo 📁 필요한 디렉토리 생성 중...
if not exist "aistudios_cache" mkdir aistudios_cache
if not exist "videos" mkdir videos
if not exist "videos\interview" mkdir videos\interview
if not exist "videos\opening" mkdir videos\opening
if not exist "videos\rebuttal" mkdir videos\rebuttal
if not exist "videos\counter_rebuttal" mkdir videos\counter_rebuttal
if not exist "videos\closing" mkdir videos\closing

REM 서버 시작
echo.
echo 🚀 서버 시작 중...
echo 📍 주소: http://localhost:5000
echo 🔍 테스트: http://localhost:5000/ai/test
echo.
echo 중단하려면 Ctrl+C를 누르세요.
echo ========================================

python main_server.py

pause
