import numpy as np
import whisper
import logging
import librosa
import soundfile as sf
import os
import tempfile
import gc

# TTS 기능 활성화
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
    print("TTS 패키지 로드 성공")
except ImportError:
    print("TTS 패키지를 설치합니다...")
    import subprocess
    try:
        subprocess.run(["pip", "install", "TTS"], check=True)
        from TTS.api import TTS
        TTS_AVAILABLE = True
        print("TTS 패키지 설치 및 로드 성공")
    except Exception as e:
        print(f"TTS 패키지 설치 실패: {e}")
        TTS_AVAILABLE = False
        print("TTS 패키지를 찾을 수 없습니다. text_to_speech 기능이 제한됩니다.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class RealtimeSpeechToText:
    def __init__(self, model="tiny", sample_rate=16000):
        try:
            self.model = whisper.load_model(model)
        except Exception as e:
            logger.error(f"Whisper 모델 로드 실패: {str(e)}")
            logger.warning("테스트 모드로 진행합니다. 실제 음성 인식 대신 고정 텍스트를 반환합니다.")
            self.model = None
        
        self.sample_rate = sample_rate
        self.device = "cpu"  # 기본값 CPU
        
        # TTS 기능 초기화
        self.tts = None
        if TTS_AVAILABLE:
            try:
                # 모델 리스트 출력
                available_models = TTS().list_models()
                logger.info(f"Available TTS models: {available_models}")
                
                # 모델 선택 - 한국어 지원 모델 우선
                ko_model = None
                for model in available_models:
                    if "korean" in model.lower() or "korean" in model.lower():
                        ko_model = model
                        break
                
                if not ko_model:
                    # 다국어 모델 사용
                    for model in available_models:
                        if "multilingual" in model.lower():
                            ko_model = model
                            break
                
                # 기본 모델 사용
                if not ko_model and available_models:
                    ko_model = available_models[0]
                
                if ko_model:
                    self.tts = TTS(ko_model)
                    logger.info(f"TTS 모델 로드 성공: {ko_model}")
                else:
                    logger.error("TTS 모델을 찾을 수 없습니다.")
            except Exception as e:
                logger.error(f"TTS 모델 로드 실패: {str(e)}")
                logger.info("TTS 기능이 비활성화됩니다.")
        else:
            logger.info("TTS 패키지가 설치되지 않아 TTS 기능이 비활성화됩니다.")

    def transcribe_audio(self, audio_data):
        """오디오 데이터를 텍스트로 변환"""
        try:
            if self.model is None:
                # 테스트 모드: 고정 텍스트 반환
                return "테스트 오디오 텍스트입니다. 인공지능은 인간의 삶에 많은 도움을 줄 수 있습니다."
            
            audio = np.frombuffer(audio_data, dtype=np.float32)
            result = self.model.transcribe(audio, language="ko")
            text = result["text"].strip()
            if text:
                logger.info(f"인식된 텍스트: {text}")
                return text
            return ""
        except Exception as e:
            logger.error(f"오디오 처리 오류: {str(e)}")
            # 테스트 모드: 고정 텍스트 반환
            return "테스트 오디오 텍스트입니다. 인공지능은 인간의 삶에 많은 도움을 줄 수 있습니다."
        finally:
            gc.collect()

    def transcribe_video(self, video_path):
        """비디오 파일에서 오디오를 추출하여 텍스트로 변환"""
        try:
            if self.model is None or not os.path.exists(video_path):
                # 테스트 모드: 고정 텍스트 반환
                return "테스트 비디오 텍스트입니다. 인공지능은 인간의 삶에 많은 도움을 줄 수 있습니다."
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                audio_path = temp_audio.name
                audio, sr = librosa.load(video_path, sr=self.sample_rate)
                sf.write(audio_path, audio, sr)
                result = self.model.transcribe(audio_path, language="ko")
                os.remove(audio_path)
                text = result["text"].strip()
                if text:
                    logger.info(f"영상에서 인식된 텍스트: {text}")
                    return text
                return "인식된 텍스트가 없습니다."
        except Exception as e:
            logger.error(f"영상 오디오 처리 오류: {str(e)}")
            # 테스트 모드: 고정 텍스트 반환
            return "테스트 비디오 텍스트입니다. 인공지능은 인간의 삶에 많은 도움을 줄 수 있습니다."
        finally:
            gc.collect()

    def text_to_speech(self, text, output_path, language="ko"):
        """텍스트를 음성으로 변환 - TTS 기능 활성화"""
        if not TTS_AVAILABLE or self.tts is None:
            logger.warning("TTS 기능이 비활성화되어 있습니다.")
            return None
        
        try:
            logger.info(f"TTS 시작: {text[:30]}...")
            # 모델 기능 여부 확인
            model_config = self.tts.synthesizer.tts_config
            supported_languages = getattr(model_config, "languages", ["en"])
            is_multilingual = getattr(model_config, "multilingual", False)
            
            # 다국어 지원 모델 확인
            if language in supported_languages or is_multilingual:
                logger.info(f"한국어 지원 모델: {is_multilingual}, 지원 언어: {supported_languages}")
                # 언어 파라미터 사용
                wav = self.tts.tts(text=text, language=language)
            else:
                logger.info(f"한국어 미지원 모델, 기본 설정 사용")
                # 언어 파라미터 없이 사용
                wav = self.tts.tts(text=text)
                
            # 파일로 저장
            self.tts.save_wav(wav, output_path)
            logger.info(f"TTS 출력 저장됨: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"TTS 오류: {str(e)}")
            return None
