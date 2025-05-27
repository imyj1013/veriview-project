"""
테스트 서버에서 TTS 기능을 사용하기 위한 업데이트 가이드

1. 의존성 설치:
   - gTTS 모듈 설치: pip install gtts
   - 또는 pyttsx3 모듈 설치: pip install pyttsx3

2. 필요한 파일:
   - modules/text_to_speech/tts_module.py - TTS 모듈 구현
   - modules/text_to_speech/__init__.py - TTS 모듈 패키지 초기화

3. 사용 방법:
   - 환경 변수 SERVER_MODE=test 설정
   - python run.py 실행
   - TTS 테스트: http://localhost:5000/ai/tts-test?text=안녕하세요
   - 토론면접 TTS 스트리밍: http://localhost:5000/ai/debate/1/ai-opening?stream=true
   - 개인면접 TTS 스트리밍: http://localhost:5000/ai/interview/1/question?stream=true

4. TTS 스트리밍 응답 구현:
   - Flask Response와 stream_with_context를 사용하여 스트리밍 구현
   - 음성 데이터를 청크 단위로 스트리밍하여 웹 브라우저에서 실시간 재생 가능
"""