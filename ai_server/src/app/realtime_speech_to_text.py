import numpy as np
import whisper
import logging
import time
import librosa
import soundfile as sf
import os
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeSpeechToText:
    def __init__(self, model="base", sample_rate=16000):
        self.model = whisper.load_model(model)
        self.sample_rate = sample_rate

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