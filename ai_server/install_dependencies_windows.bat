@echo off
chcp 65001 > nul
echo ================================================
echo VeriView AI Server - Windows 의존성 설치 도구
echo ================================================
echo.

:: 관리자 권한 확인
net session > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 관리자 권한으로 실행하는 것이 좋습니다.
    echo 💡 일부 패키지 설치가 실패할 수 있습니다.
    echo.
    timeout /t 3 > nul
)

:: Python 설치 확인
echo 🔍 Python 설치 확인 중...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았거나 PATH에 등록되지 않았습니다.
    echo.
    echo 💡 해결 방법:
    echo    1. https://python.org에서 Python 3.8 이상 다운로드
    echo    2. 설치 시 'Add Python to PATH' 체크
    echo    3. 설치 후 명령 프롬프트 재실행
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% 감지됨
echo.

:: pip 업그레이드
echo 🔧 pip 업그레이드 중...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ❌ pip 업그레이드 실패
    echo 💡 인터넷 연결을 확인하거나 관리자 권한으로 실행하세요.
    pause
    exit /b 1
)
echo ✅ pip 업그레이드 완료
echo.

:: 기본 웹 프레임워크 설치
echo 📦 기본 웹 프레임워크 설치 중...
echo    - Flask (웹 서버)
echo    - Flask-CORS (CORS 처리)
echo    - python-dotenv (환경변수)
echo    - requests (HTTP 클라이언트)
python -m pip install flask flask-cors python-dotenv requests
if %errorlevel% neq 0 (
    echo ❌ 웹 프레임워크 설치 실패
    pause
    exit /b 1
)
echo ✅ 웹 프레임워크 설치 완료
echo.

:: 기본 AI/ML 라이브러리 설치
echo 🤖 기본 AI/ML 라이브러리 설치 중...
echo    - numpy (수치계산)
echo    - opencv-python (영상처리)
echo    - librosa (음성분석)
echo    - scikit-learn (머신러닝)
python -m pip install numpy opencv-python librosa scikit-learn
if %errorlevel% neq 0 (
    echo ❌ AI/ML 라이브러리 설치 실패
    pause
    exit /b 1
)
echo ✅ AI/ML 라이브러리 설치 완료
echo.

:: Whisper 음성인식 설치
echo 🎤 Whisper 음성인식 설치 중...
echo    (시간이 좀 걸릴 수 있습니다...)
python -m pip install openai-whisper
if %errorlevel% neq 0 (
    echo ❌ Whisper 설치 실패
    echo 💡 네트워크 문제이거나 용량 부족일 수 있습니다.
    pause
    exit /b 1
)
echo ✅ Whisper 설치 완료
echo.

:: 선택적 PyTorch 설치 (Windows CPU 버전)
echo 🔥 PyTorch 설치 여부를 선택하세요:
echo    PyTorch는 고급 AI 기능을 위해 필요하지만 용량이 큽니다 (약 1GB)
echo.
set /p INSTALL_TORCH="PyTorch를 설치하시겠습니까? (y/N): "

if /i "%INSTALL_TORCH%"=="y" (
    echo 🔥 PyTorch 설치 중... (시간이 많이 걸릴 수 있습니다)
    python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    if %errorlevel% neq 0 (
        echo ❌ PyTorch 설치 실패
        echo 💡 나중에 수동으로 설치하실 수 있습니다.
    ) else (
        echo ✅ PyTorch 설치 완료
    )
    echo.
) else (
    echo ⏭️ PyTorch 설치를 건너뜁니다.
    echo 💡 나중에 수동 설치: pip install torch torchvision torchaudio
    echo.
)

:: 추가 유용한 라이브러리 설치
echo 🛠️ 추가 유용한 라이브러리 설치 중...
echo    - pandas (데이터 처리)
echo    - matplotlib (그래프)
echo    - pillow (이미지 처리)
echo    - soundfile (음성 파일 처리)
python -m pip install pandas matplotlib pillow soundfile
if %errorlevel% neq 0 (
    echo ❌ 추가 라이브러리 설치 실패
    echo 💡 필수 기능에는 영향 없습니다.
) else (
    echo ✅ 추가 라이브러리 설치 완료
)
echo.

:: 설치 완료 및 확인
echo 🔍 설치된 패키지 확인 중...
python -c "
import sys
packages = [
    'flask', 'flask_cors', 'dotenv', 'requests',
    'numpy', 'cv2', 'librosa', 'sklearn',
    'whisper', 'pandas', 'matplotlib', 'PIL', 'soundfile'
]
print('✅ 설치 확인 결과:')
for pkg in packages:
    try:
        __import__(pkg)
        print(f'   ✅ {pkg}')
    except ImportError:
        print(f'   ❌ {pkg}')
        
print()
print('Python 버전:', sys.version)
"

echo.
echo ================================================
echo 🎉 VeriView AI Server 의존성 설치 완료!
echo ================================================
echo.
echo 📋 다음 단계:
echo    1. .env 파일에 D-ID API 키 설정
echo    2. start_windows.bat 실행하여 서버 시작
echo    3. http://localhost:5000/ai/test에서 테스트
echo.
echo 💡 설치된 패키지 목록: pip list
echo 💡 특정 패키지 확인: pip show 패키지명
echo.
echo 🚀 이제 VeriView AI 서버를 실행할 준비가 되었습니다!
echo.
pause
