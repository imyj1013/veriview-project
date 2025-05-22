# AI 서버 설치 및 실행 가이드

## 🚀 빠른 설치

### 방법 1: 자동 설치 스크립트 사용 (권장)

**Windows:**
```bash
cd ai_server
install_dependencies.bat
```

**Linux/Mac:**
```bash
cd ai_server
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### 방법 2: 수동 설치
```bash
cd ai_server

# pip 업그레이드
python -m pip install --upgrade pip

# 모든 의존성 설치
pip install -r requirements.txt
```

---

## 📦 주요 패키지

- **Flask**: 웹 서버 프레임워크
- **Whisper**: OpenAI 음성 인식 모델
- **TTS**: Coqui 텍스트-투-스피치 
- **OpenCV**: 얼굴 분석 (OpenFace 연동)
- **Librosa**: 오디오 신호 처리
- **PyTorch**: 딥러닝 프레임워크

---

## 🧪 테스트 및 실행

### 1. TTS 기능 테스트
```bash
python test_tts.py
```

### 2. AI 서버 실행
```bash
python server_runner.py
```

서버가 성공적으로 실행되면:
- **서버 주소**: http://localhost:5000
- **테스트 엔드포인트**: http://localhost:5000/ai/test
- **상태 확인**: http://localhost:5000/ai/debate/modules-status

---

## 🔧 문제 해결

### TTS 관련 오류
```bash
# TTS 재설치
pip uninstall TTS
pip install TTS --upgrade

# 또는 Git 버전 설치
pip install git+https://github.com/coqui-ai/TTS.git
```

### PyTorch 관련 오류
```bash
# CPU 버전 설치
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# CUDA 버전 설치 (GPU 지원)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Visual Studio Build Tools 오류 (Windows)
Microsoft Visual Studio Build Tools 설치 필요:
- [다운로드 링크](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)

---

## 📋 시스템 요구사항

- **Python**: 3.8 이상
- **메모리**: 4GB RAM 이상 (TTS 모델 로드용)
- **디스크**: 2GB 이상 여유 공간 (모델 캐시용)
- **OS**: Windows 10+, macOS 10.15+, Linux

---

## 🎯 기능 확인

서버 실행 후 로그에서 다음 메시지 확인:
```
✓ TTS 모델 로드 성공: [모델명]
✓ 얼굴 분석기 초기화 완료 (OpenFace, Librosa)
✓ 음성 분석기 초기화 완료 (Whisper, TTS)
✓ AI 서버 Flask 애플리케이션 시작...
```

모든 기능이 정상 작동하면 VeriView 토론 시스템에서 다음 기능을 사용할 수 있습니다:
- 🎤 음성 인식 (Whisper)
- 🎭 얼굴 감정 분석 (OpenFace)
- 🔊 AI 응답 음성 변환 (TTS)
- 📊 실시간 토론 분석 및 점수화
