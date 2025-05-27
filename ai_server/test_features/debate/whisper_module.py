"""
Whisper 음성 인식 테스트 모듈
LLM 미사용 환경에서 Whisper STT 기능의 정상 작동을 테스트
"""
import logging
import os
import tempfile
import gc
import numpy as np

# Whisper 및 관련 라이브러리 임포트 시도
try:
    import whisper
    import librosa
    import soundfile as sf
    WHISPER_AVAILABLE = True
    print("Whisper 및 관련 패키지 로드 성공")
except ImportError as e:
    WHISPER_AVAILABLE = False
    print(f"Whisper 관련 패키지 로드 실패: {e}")
    print("음성 인식 기능이 제한됩니다.")

logger = logging.getLogger(__name__)

class WhisperTestModule:
    def __init__(self, model_size="tiny", sample_rate=16000):
        """Whisper 테스트 모듈 초기화"""
        self.model_size = model_size
        self.sample_rate = sample_rate
        self.model = None
        self.is_available = WHISPER_AVAILABLE
        
        if self.is_available:
            try:
                self.model = whisper.load_model(model_size)
                logger.info(f"Whisper 모델 로드 성공: {model_size}")
            except Exception as e:
                logger.error(f"Whisper 모델 로드 실패: {str(e)}")
                self.is_available = False
        
        logger.info(f"Whisper 테스트 모듈 초기화 - 사용 가능: {self.is_available}")

    def test_connection(self):
        """Whisper 연결 테스트"""
        if not self.is_available or self.model is None:
            return {"status": "unavailable", "message": "Whisper 모델을 사용할 수 없습니다"}
        
        try:
            # 간단한 테스트 오디오로 모델 동작 확인
            test_audio = np.zeros(self.sample_rate, dtype=np.float32)  # 1초 무음
            result = self.model.transcribe(test_audio, language="ko")
            return {"status": "available", "message": "Whisper 정상 작동", "test_result": result.get("text", "")}
        except Exception as e:
            return {"status": "error", "message": f"Whisper 실행 오류: {str(e)}"}

    def transcribe_audio_file(self, audio_path, language="ko"):
        """오디오 파일 음성 인식"""
        if not self.is_available or self.model is None:
            logger.warning("Whisper 사용 불가 - 고정 텍스트 반환")
            return self._get_default_transcription("audio")
        
        try:
            if not os.path.exists(audio_path):
                logger.warning(f"오디오 파일이 존재하지 않습니다: {audio_path}")
                return self._get_default_transcription("audio")
            
            logger.info(f"오디오 파일 음성 인식 시작: {audio_path}")
            
            # Whisper로 음성 인식
            result = self.model.transcribe(audio_path, language=language)
            text = result["text"].strip()
            
            logger.info(f"음성 인식 완료 - 텍스트 길이: {len(text)}")
            
            return {
                "text": text,
                "language": result.get("language", language),
                "segments": result.get("segments", []),
                "confidence": self._calculate_average_confidence(result.get("segments", []))
            }
            
        except Exception as e:
            logger.error(f"오디오 음성 인식 오류: {str(e)}")
            return self._get_default_transcription("audio")
        finally:
            gc.collect()  # 메모리 정리

    def transcribe_video_file(self, video_path, language="ko"):
        """비디오 파일에서 오디오 추출 후 음성 인식"""
        if not self.is_available or self.model is None:
            logger.warning("Whisper 사용 불가 - 고정 텍스트 반환")
            return self._get_default_transcription("video")
        
        try:
            if not os.path.exists(video_path):
                logger.warning(f"비디오 파일이 존재하지 않습니다: {video_path}")
                return self._get_default_transcription("video")
            
            logger.info(f"비디오 파일 음성 인식 시작: {video_path}")
            
            # 임시 오디오 파일로 추출
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
                
                # librosa로 비디오에서 오디오 추출
                audio, sr = librosa.load(video_path, sr=self.sample_rate)
                sf.write(temp_audio_path, audio, sr)
                
                logger.info("비디오에서 오디오 추출 완료")
                
                # Whisper로 음성 인식
                result = self.model.transcribe(temp_audio_path, language=language)
                text = result["text"].strip()
                
                # 임시 파일 삭제
                os.remove(temp_audio_path)
                
                logger.info(f"비디오 음성 인식 완료 - 텍스트 길이: {len(text)}")
                
                return {
                    "text": text,
                    "language": result.get("language", language),
                    "segments": result.get("segments", []),
                    "confidence": self._calculate_average_confidence(result.get("segments", []))
                }
            
        except Exception as e:
            logger.error(f"비디오 음성 인식 오류: {str(e)}")
            return self._get_default_transcription("video")
        finally:
            gc.collect()  # 메모리 정리

    def transcribe_audio_data(self, audio_data, language="ko"):
        """메모리 상의 오디오 데이터 음성 인식"""
        if not self.is_available or self.model is None:
            logger.warning("Whisper 사용 불가 - 고정 텍스트 반환")
            return self._get_default_transcription("data")
        
        try:
            logger.info("오디오 데이터 음성 인식 시작")
            
            # numpy 배열로 변환
            if isinstance(audio_data, bytes):
                audio_array = np.frombuffer(audio_data, dtype=np.float32)
            else:
                audio_array = np.array(audio_data, dtype=np.float32)
            
            # Whisper로 음성 인식
            result = self.model.transcribe(audio_array, language=language)
            text = result["text"].strip()
            
            logger.info(f"오디오 데이터 음성 인식 완료 - 텍스트 길이: {len(text)}")
            
            return {
                "text": text,
                "language": result.get("language", language),
                "segments": result.get("segments", []),
                "confidence": self._calculate_average_confidence(result.get("segments", []))
            }
            
        except Exception as e:
            logger.error(f"오디오 데이터 음성 인식 오류: {str(e)}")
            return self._get_default_transcription("data")
        finally:
            gc.collect()  # 메모리 정리

    def get_supported_languages(self):
        """지원하는 언어 목록 반환"""
        if not self.is_available or self.model is None:
            return ["ko"]  # 기본값
        
        try:
            # Whisper가 지원하는 언어들
            languages = [
                "ko", "en", "ja", "zh", "es", "fr", "de", "it", "pt", "ru",
                "ar", "hi", "th", "vi", "id", "ms", "tl", "nl", "sv", "da"
            ]
            return languages
        except Exception as e:
            logger.error(f"지원 언어 조회 오류: {str(e)}")
            return ["ko", "en"]

    def _calculate_average_confidence(self, segments):
        """세그먼트별 신뢰도 평균 계산"""
        if not segments:
            return 0.0
        
        try:
            # 일부 Whisper 버전에서는 confidence 정보가 없을 수 있음
            confidences = []
            for segment in segments:
                if "confidence" in segment:
                    confidences.append(segment["confidence"])
                elif "avg_logprob" in segment:
                    # avg_logprob을 confidence로 변환 (근사치)
                    conf = max(0.0, min(1.0, np.exp(segment["avg_logprob"])))
                    confidences.append(conf)
            
            if confidences:
                return np.mean(confidences)
            else:
                return 0.8  # 기본값
                
        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {str(e)}")
            return 0.8

    def _get_default_transcription(self, source_type):
        """테스트용 기본 음성 인식 결과"""
        default_texts = {
            "audio": "테스트 오디오 파일입니다. 인공지능 기술의 발전으로 우리의 일상생활이 많이 변화하고 있습니다.",
            "video": "테스트 비디오 파일입니다. 토론에서 중요한 것은 논리적인 근거와 명확한 의사전달입니다.",
            "data": "테스트 오디오 데이터입니다. 면접에서는 자신감과 진정성을 보여주는 것이 중요합니다."
        }
        
        return {
            "text": default_texts.get(source_type, "테스트 음성 인식 결과입니다."),
            "language": "ko",
            "segments": [],
            "confidence": 0.85
        }

    def evaluate_transcription_quality(self, transcription_result):
        """음성 인식 품질 평가"""
        if not transcription_result:
            return "음성 인식 결과 없음"
        
        text = transcription_result.get("text", "")
        confidence = transcription_result.get("confidence", 0.0)
        
        # 텍스트 길이 평가
        text_length = len(text.strip())
        
        # 품질 점수 계산
        quality_score = 0
        comments = []
        
        # 신뢰도 평가
        if confidence >= 0.9:
            quality_score += 3
            comments.append("매우 높은 인식 신뢰도")
        elif confidence >= 0.7:
            quality_score += 2
            comments.append("높은 인식 신뢰도")
        elif confidence >= 0.5:
            quality_score += 1
            comments.append("보통 인식 신뢰도")
        else:
            comments.append("낮은 인식 신뢰도")
        
        # 텍스트 길이 평가
        if text_length >= 50:
            quality_score += 2
            comments.append("충분한 발화량")
        elif text_length >= 20:
            quality_score += 1
            comments.append("적절한 발화량")
        else:
            comments.append("짧은 발화량")
        
        # 언어 일관성 (한국어 인식 시)
        if transcription_result.get("language") == "ko":
            quality_score += 1
            comments.append("한국어 인식 성공")
        
        # 종합 평가
        if quality_score >= 5:
            overall = "우수한 음성 인식 품질"
        elif quality_score >= 3:
            overall = "양호한 음성 인식 품질"
        else:
            overall = "음성 인식 품질 개선 필요"
        
        return f"{overall} ({', '.join(comments)})"

    def get_module_status(self):
        """모듈 상태 정보 반환"""
        return {
            "module_name": "Whisper STT",
            "is_available": self.is_available,
            "model_size": self.model_size,
            "sample_rate": self.sample_rate,
            "supported_languages": self.get_supported_languages(),
            "functions": ["transcribe_audio_file", "transcribe_video_file", "transcribe_audio_data"]
        }
