@echo off
REM AWS에 AIStudios API 키를 Secrets Manager에 저장하는 Windows 배치 파일

echo 🔐 AWS Secrets Manager에 AIStudios API 키 설정
echo ================================================
echo.

REM API 키 입력 받기
set /p API_KEY="AIStudios API 키를 입력하세요: "

if "%API_KEY%"=="" (
    echo ❌ API 키가 입력되지 않았습니다.
    pause
    exit /b 1
)

REM AWS 리전 설정 (기본값: ap-northeast-2)
if "%AWS_DEFAULT_REGION%"=="" (
    set AWS_REGION=ap-northeast-2
) else (
    set AWS_REGION=%AWS_DEFAULT_REGION%
)

echo 📍 AWS 리전: %AWS_REGION%
echo.

REM 시크릿 데이터 파일 생성
echo { > temp_secret.json
echo   "AISTUDIOS_API_KEY": "%API_KEY%", >> temp_secret.json
echo   "created_at": "%date% %time%", >> temp_secret.json
echo   "environment": "production" >> temp_secret.json
echo } >> temp_secret.json

echo 🔄 Secrets Manager에 시크릿 생성 중...

REM 시크릿 이름 설정
set SECRET_NAME=veriview/aistudios

REM 기존 시크릿 확인 후 생성/업데이트
aws secretsmanager describe-secret --secret-id "%SECRET_NAME%" --region "%AWS_REGION%" >nul 2>&1
if %errorlevel% equ 0 (
    echo 📝 기존 시크릿 업데이트 중...
    aws secretsmanager update-secret --secret-id "%SECRET_NAME%" --secret-string file://temp_secret.json --region "%AWS_REGION%"
) else (
    echo 🆕 새 시크릿 생성 중...
    aws secretsmanager create-secret --name "%SECRET_NAME%" --description "VeriView AIStudios API Keys for Production" --secret-string file://temp_secret.json --region "%AWS_REGION%"
)

if %errorlevel% equ 0 (
    echo ✅ 시크릿 설정 완료: %SECRET_NAME%
) else (
    echo ❌ 시크릿 설정 실패
    del temp_secret.json
    pause
    exit /b 1
)

REM 추가 시크릿 생성
set ADDITIONAL_SECRET_NAME=ai-server/api-keys

echo 🔄 추가 시크릿 생성 중: %ADDITIONAL_SECRET_NAME%

aws secretsmanager describe-secret --secret-id "%ADDITIONAL_SECRET_NAME%" --region "%AWS_REGION%" >nul 2>&1
if %errorlevel% equ 0 (
    aws secretsmanager update-secret --secret-id "%ADDITIONAL_SECRET_NAME%" --secret-string file://temp_secret.json --region "%AWS_REGION%"
) else (
    aws secretsmanager create-secret --name "%ADDITIONAL_SECRET_NAME%" --description "VeriView AI Server API Keys" --secret-string file://temp_secret.json --region "%AWS_REGION%"
)

REM 임시 파일 정리
del temp_secret.json

echo.
echo ✅ 모든 시크릿 설정 완료!
echo.
echo 📋 생성된 시크릿들:
echo   - %SECRET_NAME%
echo   - %ADDITIONAL_SECRET_NAME%
echo.
echo 🚀 이제 AWS에서 VeriView AI 서버를 시작할 수 있습니다:
echo   python run.py --mode main
echo.
echo 🔍 시크릿 확인:
echo   aws secretsmanager get-secret-value --secret-id %SECRET_NAME% --region %AWS_REGION%
echo.

pause
