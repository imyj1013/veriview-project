import numpy as np
import whisper  # openai-whisper 패키지는 여전히 whisper로 import
import logging
import librosa
import soundfile as sf
import os
import tempfile
# TTS 기능은 선택사항–$
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
import torch
import gc

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class RealtimeSpeechToText:
    def __init__(self, model="tiny", sample_rate=16000):
        self.model = whisper.load_model(model)
        self.sample_rate = sample_rate
        # self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # logger.info(f"Using device: {self.device}")
        
        # TTS 기능 임시 비활성화
        self.tts = None
        logger.info("TTS functionality disabled for compatibility")

    def transcribe_audio(self, audio_data):
        try:
            audio = np.frombuffer(audio_data, dtype=np.float32)
            result = self.model.transcribe(audio, language="ko")
            text = result["text"].strip()
            if text:
                logger.info(f"인식된 텍스트: {text}")
                return text
            return ""
        except Exception as e:
            logger.error(f"오디오 처리 오류: {str(e)}")
            return ""
        finally:
            if self.device == "cuda":
                torch.cuda.empty_cache()
            gc.collect()

    def transcribe_video(self, video_path):
        try:
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
                return ""
        except Exception as e:
            logger.error(f"영상 오디오 처리 오류: {str(e)}")
            return ""
        finally:
            if self.device == "cuda":
                torch.cuda.empty_cache()
            gc.collect()

    def text_to_speech(self, text, output_path, language="ko"):
        """텍스트를 음성으로 변환"""
        if not TTS_AVAILABLE:
            logger.warning("TTS 패키지가 설치되지 않았습니다.")
            return None
            
        try:
            # TTS 기본 모델 사용
            tts = TTS("tts_models/multilingual/multi-dataset/your_tts")
            # 한국어로 음성 생성
            wav = tts.tts(text=text, language=language)
            # 파일로 저장
            tts.save_wav(wav, output_path)
            logger.info(f"TTS 출력 저장됨: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"TTS 오류: {str(e)}")
            return None

    def test_transcribe_video(self, video_path):
        """테스트용 영상 음성-텍스트 변환 및 TTS"""
        logger.info(f"영상 음성-텍스트 변환 시작: {video_path}")
        text = self.transcribe_video(video_path)
        if text:
            logger.info(f"인식된 텍스트: {text}")
            output_audio = os.path.join(os.path.dirname(video_path), "test_tts_output.wav")
            self.text_to_speech(text, output_audio)
            return {"text": text, "tts_output": output_audio}
        else:
            logger.error("음성-텍스트 변환 실패")
            return {"text": "", "tts_output": None}