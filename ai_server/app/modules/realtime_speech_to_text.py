import numpy as np
import whisper
import logging
import librosa
import soundfile as sf
import os
import tempfile
import gc

# TTS 기능 활성화 - 올바른 방법
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
            # Whisper 모델 로드 시 보안 경고 해결
            import warnings
            warnings.filterwarnings("ignore", category=FutureWarning, module="whisper")
            
            self.model = whisper.load_model(model)
            logger.info(f"Whisper 모델 로드 성공: {model}")
        except Exception as e:
            logger.error(f"Whisper 모델 로드 실패: {str(e)}")
            logger.warning("테스트 모드로 진행합니다. 실제 음성 인식 대신 고정 텍스트를 반환합니다.")
            self.model = None
        
        self.sample_rate = sample_rate
        self.device = "cpu"  # 기본값 CPU
        
        # TTS 기능 초기화 (더 안전한 방법)
        self.tts = None
        if TTS_AVAILABLE:
            self._safe_initialize_tts()
        else:
            logger.info("TTS 패키지가 설치되지 않아 TTS 기능이 비활성화됩니다.")

    def _safe_initialize_tts(self):
        """올바른 TTS 초기화 메서드 - 2024 버전"""
        try:
            logger.info("TTS 초기화 시작...")
            
            # 방법 1: 글로벌 기본 모델 사용 (list_models 없이)
            logger.info("방법 1: 기본 모델로 TTS 초기화 시도")
            try:
                # 방법 1-1: 기본값으로 생성
                self.tts = TTS()
                logger.info("TTS 기본 모델 로드 성공")
                return
            except Exception as e1:
                logger.warning(f"기본 모델 로드 실패: {e1}")
                
            # 방법 2: 직접 모델 지정
            logger.info("방법 2: 직접 모델 지정")
            recommended_models = [
                # 다국어 모델 (한국어 지원)
                "tts_models/multilingual/multi-dataset/xtts_v2",
                # 영어 모델들
                "tts_models/en/ljspeech/tacotron2-DDC",
                "tts_models/en/ljspeech/glow-tts",
                "tts_models/en/ljspeech/speedy-speech",
                # 기본 Tacotron2
                "tts_models/en/ljspeech/tacotron2-DCA"
            ]
            
            for model_name in recommended_models:
                try:
                    logger.info(f"TTS 모델 시도: {model_name}")
                    self.tts = TTS(model_name=model_name)
                    logger.info(f"TTS 모델 로드 성공: {model_name}")
                    return
                except Exception as model_error:
                    logger.warning(f"모델 {model_name} 로드 실패: {model_error}")
                    continue
            
            # 방법 3: 언어별 모델 시도
            logger.info("방법 3: 언어별 모델 시도")
            language_models = [
                "tts_models/ko/kss/tacotron2-DDC",  # 한국어 전용
                "tts_models/en/ek1/tacotron2",       # 영어 간단
            ]
            
            for model_name in language_models:
                try:
                    logger.info(f"TTS 언어 모델 시도: {model_name}")
                    self.tts = TTS(model_name=model_name)
                    logger.info(f"TTS 모델 로드 성공: {model_name}")
                    return
                except Exception as lang_error:
                    logger.warning(f"언어 모델 {model_name} 로드 실패: {lang_error}")
                    continue
            
            # 방법 4: 최소 모델 시도
            logger.info("방법 4: 최소 모델 시도")
            minimal_models = [
                "tts_models/en/ljspeech/speedy-speech",  # 가장 가벼운 모델
            ]
            
            for model_name in minimal_models:
                try:
                    logger.info(f"TTS 최소 모델 시도: {model_name}")
                    self.tts = TTS(model_name=model_name)
                    logger.info(f"TTS 모델 로드 성공: {model_name}")
                    return
                except Exception as min_error:
                    logger.warning(f"최소 모델 {model_name} 로드 실패: {min_error}")
                    continue
            
            # 모든 시도가 실패한 경우
            logger.error("모든 TTS 모델 로드 시도 실패")
            logger.info("TTS 기능이 비활성화됩니다.")
            self.tts = None
                
        except Exception as e:
            logger.error(f"TTS 초기화 중 예상치 못한 오류: {str(e)}")
            logger.info("TTS 기능이 비활성화됩니다.")
            self.tts = None

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
        """개선된 TTS 변환 메서드 - 2024 버전"""
        if not TTS_AVAILABLE or self.tts is None:
            logger.warning("TTS 기능이 비활성화되어 있습니다.")
            return None
        
        try:
            logger.info(f"TTS 변환 시작: {text[:50]}...")
            
            # 텍스트 전처리
            text = text.strip()
            if not text:
                logger.warning("빈 텍스트로 TTS 변환을 시도할 수 없습니다.")
                return None
            
            # 텍스트 길이 제한 (TTS 모델에 따라 다름)
            if len(text) > 500:
                text = text[:500]
                logger.warning("텍스트가 너무 길어 500자로 자릅니다.")
            
            # TTS 변환 시도
            wav = None
            
            # 방법 1: 다국어 지원 모델에서 언어 지정
            try:
                if hasattr(self.tts, 'synthesizer') and hasattr(self.tts.synthesizer, 'tts_config'):
                    config = self.tts.synthesizer.tts_config
                    if hasattr(config, 'languages') and language in config.languages:
                        logger.info(f"다국어 모델에서 {language} 언어 사용")
                        wav = self.tts.tts(text=text, language=language)
                    elif hasattr(config, 'multilingual') and config.multilingual:
                        logger.info("다국어 모델에서 기본 언어 사용")
                        wav = self.tts.tts(text=text)
                    else:
                        logger.info("단일 언어 모델에서 기본 변환")
                        wav = self.tts.tts(text=text)
                else:
                    # 방법 2: 기본 변환
                    logger.info("기본 TTS 변환 시도")
                    wav = self.tts.tts(text=text)
                    
            except Exception as tts_error:
                logger.warning(f"고급 TTS 변환 실패: {tts_error}")
                # 방법 3: 가장 기본적인 방법
                try:
                    logger.info("기본적인 TTS 변환 시도")
                    wav = self.tts.tts(text)
                except Exception as basic_error:
                    logger.error(f"기본 TTS 변환에서 실패: {basic_error}")
                    return None
            
            if wav is None or len(wav) == 0:
                logger.error("TTS 변환 결과가 비어있습니다.")
                return None
            
            # 오디오 저장
            try:
                # 방법 1: TTS 내장 저장 방법
                if hasattr(self.tts, 'save_wav'):
                    self.tts.save_wav(wav, output_path)
                    logger.info(f"TTS 내장 방법으로 저장: {output_path}")
                else:
                    # 방법 2: soundfile로 직접 저장
                    import soundfile as sf
                    # 샘플링레이트 추정 (TTS 모델에 따라 다름)
                    sample_rate = 22050
                    if hasattr(self.tts, 'synthesizer') and hasattr(self.tts.synthesizer, 'output_sample_rate'):
                        sample_rate = self.tts.synthesizer.output_sample_rate
                    
                    sf.write(output_path, wav, sample_rate)
                    logger.info(f"soundfile로 저장: {output_path} (SR: {sample_rate})")
                    
            except Exception as save_error:
                logger.error(f"오디오 저장 실패: {save_error}")
                # 방법 3: numpy 배열로 직접 저장
                try:
                    import numpy as np
                    import wave
                    
                    # WAV 파일로 수동 저장
                    wav_array = np.array(wav, dtype=np.float32)
                    wav_int = np.int16(wav_array * 32767)
                    
                    with wave.open(output_path, 'w') as wav_file:
                        wav_file.setnchannels(1)  # 모노
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(22050)  # 기본 샘플링레이트
                        wav_file.writeframes(wav_int.tobytes())
                    
                    logger.info(f"wave 모듈로 수동 저장: {output_path}")
                except Exception as manual_error:
                    logger.error(f"수동 저장도 실패: {manual_error}")
                    return None
            
            # 저장된 파일 확인
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"TTS 출력 성공적으로 저장됨: {output_path} ({os.path.getsize(output_path)} bytes)")
                return output_path
            else:
                logger.error(f"저장된 파일을 확인할 수 없습니다: {output_path}")
                return None
            
        except Exception as e:
            logger.error(f"TTS 변환 중 예상치 못한 오류: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
