@echo off
echo ===== Veriview AI Server 종속성 설치 =====

:: Python 가상환경 생성 및 활성화
echo 가상환경 생성 중...
python -m venv venv
call venv\Scripts\activate

:: pip 업그레이드
echo pip 업그레이드 중...
python -m pip install --upgrade pip

:: 개별 패키지 설치 - 호환성 문제 있는 패키지들 단계적으로 설치
echo 기본 패키지 설치 중...
pip install Flask==2.3.2 requests==2.32.2 numpy==1.26.4 pandas==1.5.3 pyjwt==2.6.0 flask-cors==4.0.0 unidecode==1.3.8

echo 과학 계산 패키지 설치 중...
pip install scipy==1.14.1 numba>=0.56.0

echo OpenCV 설치 중...
pip install opencv-python==4.10.0.84

echo 오디오 관련 패키지 설치 중...
pip install librosa==0.10.2 soundfile==0.12.1 sounddevice==0.5.0 pydub>=0.25.1

echo PyTorch 설치 중...
pip install torch>=2.0.0 torchaudio>=2.0.0

echo Whisper 모델 설치 중...
pip install openai-whisper>=20230918

echo TTS 설치 중...
pip install TTS>=0.22.0

echo AIStudios 관련 패키지 설치 중...
pip install python-dotenv>=1.0.0 pillow>=10.0.0

echo 시스템 모니터링 패키지 설치 중...
pip install psutil>=5.9.0

echo ===== 설치 완료 =====
echo 이제 run_server.bat을 실행하여 AI 서버를 시작할 수 있습니다.

pause