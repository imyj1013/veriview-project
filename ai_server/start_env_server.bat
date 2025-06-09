@echo off
REM 다양한 환경에서 VeriView AIStudios 서버를 시작하는 통합 배치 파일

echo 🚀 VeriView AIStudios 서버 - 환경별 시작
echo ==========================================
echo.

echo 환경을 선택하세요:
echo   1. 로컬 개발 환경 (.env 파일 사용)
echo   2. AWS 운영 환경 (Secrets Manager 사용)
echo   3. Docker 환경
echo   4. 수동 API 키 입력
echo   5. 설정 확인만
echo.

set /p CHOICE="선택 (1-5): "

if "%CHOICE%"=="1" goto LOCAL_DEV
if "%CHOICE%"=="2" goto AWS_PROD
if "%CHOICE%"=="3" goto DOCKER_ENV
if "%CHOICE%"=="4" goto MANUAL_KEY
if "%CHOICE%"=="5" goto CHECK_CONFIG
goto INVALID_CHOICE

:LOCAL_DEV
echo.
echo 📁 로컬 개발 환경으로 시작합니다...
echo ================================
echo.

REM .env 파일 확인
if not exist ".env" (
    echo ⚠️  .env 파일이 없습니다.
    echo.
    set /p CREATE_ENV="기본 .env 파일을 생성하시겠습니까? (y/n): "
    if /i "%CREATE_ENV%"=="y" (
        echo # VeriView AI 서버 환경 설정 > .env
        echo AISTUDIOS_API_KEY=your_actual_api_key_here >> .env
        echo ENVIRONMENT=development >> .env
        echo DEBUG=True >> .env
        echo.
        echo ✅ .env 파일이 생성되었습니다.
        echo 📝 메모장으로 .env 파일을 열어 실제 API 키를 입력하세요.
        notepad .env
    )
)

python run.py --mode test
goto END

:AWS_PROD
echo.
echo ☁️  AWS 운영 환경으로 시작합니다...
echo ===============================
echo.

REM AWS CLI 확인
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS CLI가 설치되지 않았습니다.
    echo    https://aws.amazon.com/cli/ 에서 AWS CLI를 설치하세요.
    goto END
)

REM AWS 인증 확인
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS 인증이 설정되지 않았습니다.
    echo    aws configure 명령으로 AWS 인증을 설정하세요.
    goto END
)

echo ✅ AWS 환경 확인 완료
set ENVIRONMENT=production
python run.py --mode main
goto END

:DOCKER_ENV
echo.
echo 🐳 Docker 환경으로 시작합니다...
echo =============================
echo.

REM Docker 확인
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker가 설치되지 않았습니다.
    echo    https://docker.com 에서 Docker를 설치하세요.
    goto END
)

REM docker-compose 확인
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose가 설치되지 않았습니다.
    goto END
)

echo ✅ Docker 환경 확인 완료
echo 🔄 Docker Compose로 시작합니다...

REM .env 파일이 없으면 생성
if not exist ".env" (
    echo AISTUDIOS_API_KEY=your_actual_api_key_here > .env
    echo ENVIRONMENT=docker >> .env
    echo 📝 .env 파일이 생성되었습니다. API 키를 설정해주세요.
)

docker-compose up -d
echo ✅ Docker 컨테이너가 시작되었습니다.
echo 🌐 http://localhost:5000 에서 확인하세요.
goto END

:MANUAL_KEY
echo.
echo 🔑 수동 API 키 입력
echo =================
echo.

set /p API_KEY="AIStudios API 키를 입력하세요: "

if "%API_KEY%"=="" (
    echo ❌ API 키가 입력되지 않았습니다.
    goto END
)

REM 환경 변수로 설정
set AISTUDIOS_API_KEY=%API_KEY%
echo ✅ API 키가 환경 변수로 설정되었습니다.

python run.py --mode test
goto END

:CHECK_CONFIG
echo.
echo 🔍 현재 설정 상태 확인
echo ===================
echo.

python -c "
try:
    from modules.aistudios.api_key_manager import api_key_manager
    status = api_key_manager.get_all_sources_status()
    print('📋 API 키 소스 상태:')
    for source, info in status.items():
        available = '✅' if info.get('available') else '❌'
        print(f'  {available} {source}: {info}')
    
    api_key = api_key_manager.get_aistudios_api_key()
    if api_key:
        print(f'\n🔑 현재 API 키: {api_key[:10]}***')
    else:
        print('\n❌ API 키를 찾을 수 없습니다.')
        
except Exception as e:
    print(f'❌ 설정 확인 중 오류: {e}')
"
goto END

:INVALID_CHOICE
echo.
echo ❌ 잘못된 선택입니다.
goto END

:END
echo.
echo 🏁 작업 완료
pause
