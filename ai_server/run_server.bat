@echo off
REM AI Server 실행 스크립트 (Windows)

echo AI Server 시작 준비 중...

REM 환경 변수 설정 (필요시)
REM set OPENFACE_PATH=C:\OpenFace\FeatureExtraction.exe
REM set OPENFACE_OUTPUT_DIR=C:\temp\openface_output

REM Python 가상환경 활성화 (있는 경우)
if exist venv\Scripts\activate.bat (
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

REM 의존성 확인
echo 의존성 확인 중...
pip install -r requirements.txt --quiet

REM 서버 시작
echo AI Server 시작...
python server_runner.py
