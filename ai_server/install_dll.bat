@echo off
setlocal enabledelayedexpansion

echo 베리뷰 프로젝트 DLL 설치 도구
echo ============================
echo.

REM 관리자 권한 확인
NET SESSION >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 이 스크립트는 관리자 권한이 필요합니다.
    echo 오른쪽 클릭 후 "관리자 권한으로 실행"을 선택하세요.
    pause
    exit /b 1
)

REM 현재 디렉토리와 목표 디렉토리 설정
set "CURRENT_DIR=%~dp0"
set "TOOLS_DIR=%CURRENT_DIR%tools"
set "SYSTEM32_DIR=%SystemRoot%\System32"

echo DLL 파일 확인 중...

REM tools 디렉토리 내의 DLL 파일 확인
if not exist "%TOOLS_DIR%\openblas.dll" (
    echo openblas.dll 파일을 찾을 수 없습니다.
    echo 도구 디렉토리에 해당 파일이 있는지 확인하세요: %TOOLS_DIR%
    set "ERROR=1"
) else (
    echo openblas.dll 발견: %TOOLS_DIR%\openblas.dll
)

if not exist "%TOOLS_DIR%\opencv_world410.dll" (
    echo opencv_world410.dll 파일을 찾을 수 없습니다.
    echo 도구 디렉토리에 해당 파일이 있는지 확인하세요: %TOOLS_DIR%
    set "ERROR=1"
) else (
    echo opencv_world410.dll 발견: %TOOLS_DIR%\opencv_world410.dll
)

if defined ERROR (
    echo.
    echo 오류: 필요한 DLL 파일이 없습니다.
    pause
    exit /b 1
)

echo.
echo DLL 파일을 System32 디렉토리에 복사하시겠습니까? (Y/N)
set /p CONFIRM=선택: 

if /i "%CONFIRM%"=="Y" (
    echo.
    echo DLL 파일을 %SYSTEM32_DIR%에 복사 중...
    
    copy /Y "%TOOLS_DIR%\openblas.dll" "%SYSTEM32_DIR%"
    if %ERRORLEVEL% neq 0 (
        echo openblas.dll 복사 실패!
    ) else (
        echo openblas.dll 복사 성공!
    )
    
    copy /Y "%TOOLS_DIR%\opencv_world410.dll" "%SYSTEM32_DIR%"
    if %ERRORLEVEL% neq 0 (
        echo opencv_world410.dll 복사 실패!
    ) else (
        echo opencv_world410.dll 복사 성공!
    )
    
    echo.
    echo 작업 완료! 서버를 다시 시작하세요.
) else (
    echo.
    echo 작업이 취소되었습니다.
)

pause
