"""
TTS (Text-to-Speech) 테스트 모듈
LLM 미사용 환경에서 TTS 기능의 정상 작동을 테스트
"""
import logging
import os
import tempfile

# TTS 라이브러리 임포트 시도
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
    print("TTS 패키지 로드 성공")
except ImportError:
    TTS_AVAILABLE = False
    print("TTS 패키지를 찾을 수 없습니다. 음성 합성 기능이 제한됩니다.")

logger = logging.getLogger(__name__)

class TTSTestModule:
    def __init__(self, language="ko"):
        """TTS 테스트 모듈 초기화"""
        self.language = language
        self.tts_model = None
        self.is_available = TTS_AVAILABLE
        self.model_name = None
        
        if self.is_available:
            try:
                self._initialize_tts_model()
                logger.info(f"TTS 모델 초기화 성공: {self.model_name}")
            except Exception as e:
                logger.error(f"TTS 모델 초기화 실패: {str(e)}")
                self.is_available = False
        
        logger.info(f"TTS 테스트 모듈 초기화 - 사용 가능: {self.is_available}")

    def _initialize_tts_model(self):
        """TTS 모델 초기화"""
        if not TTS_AVAILABLE:
            return
        
        try:
            # 사용 가능한 모델 목록 확인
            tts = TTS()
            available_models = tts.list_models()
            logger.info(f"사용 가능한 TTS 모델 수: {len(available_models)}")
            
            # 한국어 지원 모델 우선 선택
            korean_models = [model for model in available_models if "korean" in model.lower()]
            
            if korean_models:
                self.model_name = korean_models[0]
                logger.info(f"한국어 모델 선택: {self.model_name}")
            else:
                # 다국어 모델 선택
                multilingual_models = [model for model in available_models if "multilingual" in model.lower()]
                if multilingual_models:
                    self.model_name = multilingual_models[0]
                    logger.info(f"다국어 모델 선택: {self.model_name}")
                else:
                    # 기본 영어 모델 사용
                    english_models = [model for model in available_models if "english" in model.lower()]
                    if english_models:
                        self.model_name = english_models[0]
                        logger.info(f"영어 모델 선택: {self.model_name}")
                    elif available_models:
                        self.model_name = available_models[0]
                        logger.info(f"기본 모델 선택: {self.model_name}")
            
            # 선택된 모델로 TTS 객체 생성
            if self.model_name:
                self.tts_model = TTS(self.model_name)
                logger.info("TTS 모델 로드 완료")
            else:
                logger.error("사용 가능한 TTS 모델이 없습니다")
                
        except Exception as e:
            logger.error(f"TTS 모델 초기화 중 오류: {str(e)}")
            raise

    def test_connection(self):
        """TTS 연결 테스트"""
        if not self.is_available or self.tts_model is None:
            return {"status": "unavailable", "message": "TTS 모델을 사용할 수 없습니다"}
        
        try:
            # 간단한 테스트 문장으로 TTS 동작 확인
            test_text = "안녕하세요. TTS 테스트입니다."
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
                wav = self.tts_model.tts(text=test_text)
                return {
                    "status": "available", 
                    "message": "TTS 정상 작동",
                    "model": self.model_name,
                    "test_length": len(wav) if wav else 0
                }
        except Exception as e:
            return {"status": "error", "message": f"TTS 실행 오류: {str(e)}"}

    def text_to_speech(self, text, output_path=None, language=None):
        """텍스트를 음성으로 변환"""
        if not self.is_available or self.tts_model is None:
            logger.warning("TTS 사용 불가 - 변환 실패")
            return None
        
        try:
            if not text or not text.strip():
                logger.warning("변환할 텍스트가 비어있습니다")
                return None
            
            # 언어 설정
            target_language = language or self.language
            
            logger.info(f"TTS 변환 시작 - 텍스트 길이: {len(text)}, 언어: {target_language}")
            
            # 모델 설정 확인
            model_config = self.tts_model.synthesizer.tts_config
            supported_languages = getattr(model_config, "languages", ["en"])
            is_multilingual = getattr(model_config, "multilingual", False)
            
            # TTS 실행
            if target_language in supported_languages or is_multilingual:
                logger.info(f"언어 지원 확인됨: {target_language}")
                wav = self.tts_model.tts(text=text, language=target_language)
            else:
                logger.info("언어 파라미터 없이 TTS 실행")
                wav = self.tts_model.tts(text=text)
            
            # 결과 저장
            if output_path:
                self.tts_model.save_wav(wav, output_path)
                logger.info(f"TTS 결과 저장: {output_path}")
                return output_path
            else:
                # 임시 파일로 저장
                temp_path = tempfile.mktemp(suffix=".wav")
                self.tts_model.save_wav(wav, temp_path)
                logger.info(f"TTS 결과 임시 저장: {temp_path}")
                return temp_path
            
        except Exception as e:
            logger.error(f"TTS 변환 오류: {str(e)}")
            return None

    def batch_text_to_speech(self, text_list, output_dir=None):
        """여러 텍스트를 일괄 음성 변환"""
        if not self.is_available or self.tts_model is None:
            logger.warning("TTS 사용 불가 - 일괄 변환 실패")
            return []
        
        if not text_list:
            logger.warning("변환할 텍스트 목록이 비어있습니다")
            return []
        
        results = []
        
        try:
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            logger.info(f"일괄 TTS 변환 시작 - {len(text_list)}개 텍스트")
            
            for i, text in enumerate(text_list):
                if not text or not text.strip():
                    continue
                
                # 출력 파일 경로 생성
                if output_dir:
                    output_path = os.path.join(output_dir, f"tts_output_{i+1}.wav")
                else:
                    output_path = tempfile.mktemp(suffix=f"_batch_{i+1}.wav")
                
                # TTS 변환
                result_path = self.text_to_speech(text, output_path)
                if result_path:
                    results.append({
                        "index": i,
                        "text": text[:50] + "..." if len(text) > 50 else text,
                        "output_path": result_path,
                        "success": True
                    })
                    logger.info(f"변환 완료 ({i+1}/{len(text_list)}): {text[:30]}...")
                else:
                    results.append({
                        "index": i,
                        "text": text[:50] + "..." if len(text) > 50 else text,
                        "output_path": None,
                        "success": False
                    })
                    logger.warning(f"변환 실패 ({i+1}/{len(text_list)}): {text[:30]}...")
            
            logger.info(f"일괄 TTS 변환 완료 - 성공: {len([r for r in results if r['success']])}/{len(text_list)}")
            return results
            
        except Exception as e:
            logger.error(f"일괄 TTS 변환 오류: {str(e)}")
            return results

    def get_voice_settings(self):
        """현재 음성 설정 정보 반환"""
        if not self.is_available or self.tts_model is None:
            return {"available": False}
        
        try:
            model_config = self.tts_model.synthesizer.tts_config
            
            return {
                "available": True,
                "model_name": self.model_name,
                "language": self.language,
                "supported_languages": getattr(model_config, "languages", ["en"]),
                "is_multilingual": getattr(model_config, "multilingual", False),
                "sample_rate": getattr(model_config, "sample_rate", 22050)
            }
        except Exception as e:
            logger.error(f"음성 설정 조회 오류: {str(e)}")
            return {"available": False, "error": str(e)}

    def evaluate_tts_quality(self, output_path):
        """생성된 TTS 음성의 품질 평가"""
        if not output_path or not os.path.exists(output_path):
            return "TTS 출력 파일을 찾을 수 없음"
        
        try:
            # 파일 크기 확인
            file_size = os.path.getsize(output_path)
            
            if file_size < 1000:  # 1KB 미만
                return "TTS 품질: 매우 짧은 출력 (품질 확인 필요)"
            elif file_size < 10000:  # 10KB 미만
                return "TTS 품질: 짧은 출력 (적절한 길이)"
            elif file_size < 100000:  # 100KB 미만
                return "TTS 품질: 보통 길이 (양호한 품질 예상)"
            else:
                return "TTS 품질: 긴 출력 (상세한 음성 생성)"
            
        except Exception as e:
            logger.error(f"TTS 품질 평가 오류: {str(e)}")
            return "TTS 품질 평가 실패"

    def cleanup_temp_files(self, file_paths):
        """임시 TTS 파일들 정리"""
        cleaned_count = 0
        
        for file_path in file_paths:
            try:
                if file_path and os.path.exists(file_path) and file_path.startswith(tempfile.gettempdir()):
                    os.remove(file_path)
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"임시 파일 삭제 실패 {file_path}: {str(e)}")
        
        logger.info(f"임시 TTS 파일 {cleaned_count}개 정리 완료")
        return cleaned_count

    def get_module_status(self):
        """모듈 상태 정보 반환"""
        return {
            "module_name": "TTS (Text-to-Speech)",
            "is_available": self.is_available,
            "model_name": self.model_name,
            "language": self.language,
            "voice_settings": self.get_voice_settings(),
            "functions": ["text_to_speech", "batch_text_to_speech", "evaluate_tts_quality"]
        }
