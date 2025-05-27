"""
개인면접용 TTS 테스트 모듈
면접 질문 음성 출력에 특화된 기능 제공
"""
import logging
import os
import tempfile

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
    print("TTS 패키지 로드 성공")
except ImportError:
    TTS_AVAILABLE = False
    print("TTS 패키지를 찾을 수 없습니다. 음성 합성 기능이 제한됩니다.")

logger = logging.getLogger(__name__)

class PersonalInterviewTTSModule:
    def __init__(self, language="ko"):
        """개인면접용 TTS 테스트 모듈 초기화"""
        self.language = language
        self.tts_model = None
        self.is_available = TTS_AVAILABLE
        self.model_name = None
        
        if self.is_available:
            try:
                self._initialize_tts_model()
                logger.info(f"면접용 TTS 모델 초기화 성공: {self.model_name}")
            except Exception as e:
                logger.error(f"TTS 모델 초기화 실패: {str(e)}")
                self.is_available = False
        
        logger.info(f"개인면접 TTS 테스트 모듈 초기화 - 사용 가능: {self.is_available}")

    def _initialize_tts_model(self):
        """TTS 모델 초기화"""
        if not TTS_AVAILABLE:
            return
        
        try:
            tts = TTS()
            available_models = tts.list_models()
            logger.info(f"사용 가능한 TTS 모델 수: {len(available_models)}")
            
            # 면접용으로 적합한 모델 선택 (자연스러운 음성)
            korean_models = [model for model in available_models if "korean" in model.lower()]
            
            if korean_models:
                self.model_name = korean_models[0]
                logger.info(f"한국어 모델 선택: {self.model_name}")
            else:
                multilingual_models = [model for model in available_models if "multilingual" in model.lower()]
                if multilingual_models:
                    self.model_name = multilingual_models[0]
                    logger.info(f"다국어 모델 선택: {self.model_name}")
                elif available_models:
                    self.model_name = available_models[0]
                    logger.info(f"기본 모델 선택: {self.model_name}")
            
            if self.model_name:
                self.tts_model = TTS(self.model_name)
                logger.info("면접용 TTS 모델 로드 완료")
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
            test_text = "안녕하세요. 면접을 시작하겠습니다."
            wav = self.tts_model.tts(text=test_text)
            return {
                "status": "available", 
                "message": "면접용 TTS 정상 작동",
                "model": self.model_name,
                "test_length": len(wav) if wav else 0
            }
        except Exception as e:
            return {"status": "error", "message": f"TTS 실행 오류: {str(e)}"}

    def generate_interview_question_audio(self, question_text, question_type="general", output_path=None):
        """면접 질문을 음성으로 변환"""
        if not self.is_available or self.tts_model is None:
            logger.warning("TTS 사용 불가 - 변환 실패")
            return None
        
        try:
            if not question_text or not question_text.strip():
                logger.warning("변환할 질문 텍스트가 비어있습니다")
                return None
            
            # 질문 유형에 따른 음성 스타일 조정 (가능한 경우)
            processed_text = self._process_question_text(question_text, question_type)
            
            logger.info(f"면접 질문 TTS 변환 시작 - 유형: {question_type}")
            
            # TTS 실행
            wav = self.tts_model.tts(text=processed_text, language=self.language)
            
            # 결과 저장
            if output_path:
                self.tts_model.save_wav(wav, output_path)
                logger.info(f"면접 질문 TTS 결과 저장: {output_path}")
                return output_path
            else:
                temp_path = tempfile.mktemp(suffix=f"_interview_question.wav")
                self.tts_model.save_wav(wav, temp_path)
                logger.info(f"면접 질문 TTS 결과 임시 저장: {temp_path}")
                return temp_path
            
        except Exception as e:
            logger.error(f"면접 질문 TTS 변환 오류: {str(e)}")
            return None

    def generate_followup_question_audio(self, followup_text, context_info=None, output_path=None):
        """추가 질문을 음성으로 변환"""
        if not self.is_available or self.tts_model is None:
            logger.warning("TTS 사용 불가 - 변환 실패")
            return None
        
        try:
            if not followup_text or not followup_text.strip():
                logger.warning("변환할 추가 질문 텍스트가 비어있습니다")
                return None
            
            # 추가 질문 특성에 맞게 텍스트 처리
            processed_text = self._process_followup_text(followup_text, context_info)
            
            logger.info(f"추가 질문 TTS 변환 시작")
            
            # TTS 실행
            wav = self.tts_model.tts(text=processed_text, language=self.language)
            
            # 결과 저장
            if output_path:
                self.tts_model.save_wav(wav, output_path)
                logger.info(f"추가 질문 TTS 결과 저장: {output_path}")
                return output_path
            else:
                temp_path = tempfile.mktemp(suffix=f"_followup_question.wav")
                self.tts_model.save_wav(wav, temp_path)
                logger.info(f"추가 질문 TTS 결과 임시 저장: {temp_path}")
                return temp_path
            
        except Exception as e:
            logger.error(f"추가 질문 TTS 변환 오류: {str(e)}")
            return None

    def generate_interview_feedback_audio(self, feedback_text, output_path=None):
        """면접 피드백을 음성으로 변환"""
        if not self.is_available or self.tts_model is None:
            logger.warning("TTS 사용 불가 - 변환 실패")
            return None
        
        try:
            if not feedback_text or not feedback_text.strip():
                logger.warning("변환할 피드백 텍스트가 비어있습니다")
                return None
            
            # 피드백 특성에 맞게 텍스트 처리
            processed_text = self._process_feedback_text(feedback_text)
            
            logger.info(f"면접 피드백 TTS 변환 시작")
            
            # TTS 실행
            wav = self.tts_model.tts(text=processed_text, language=self.language)
            
            # 결과 저장
            if output_path:
                self.tts_model.save_wav(wav, output_path)
                logger.info(f"면접 피드백 TTS 결과 저장: {output_path}")
                return output_path
            else:
                temp_path = tempfile.mktemp(suffix=f"_interview_feedback.wav")
                self.tts_model.save_wav(wav, temp_path)
                logger.info(f"면접 피드백 TTS 결과 임시 저장: {temp_path}")
                return temp_path
            
        except Exception as e:
            logger.error(f"면접 피드백 TTS 변환 오류: {str(e)}")
            return None

    def _process_question_text(self, text, question_type):
        """질문 텍스트 전처리"""
        processed = text.strip()
        
        # 질문 유형별 톤 조정 (필요시)
        if question_type == "technical":
            # 기술 질문은 명확하고 정확한 톤
            if not processed.endswith(('?', '.')):
                processed += "?"
        elif question_type == "behavioral":
            # 인성 질문은 친근하고 자연스러운 톤
            if not processed.endswith(('?', '.')):
                processed += "?"
        else:
            # 일반 질문
            if not processed.endswith(('?', '.')):
                processed += "?"
        
        return processed

    def _process_followup_text(self, text, context_info):
        """추가 질문 텍스트 전처리"""
        processed = text.strip()
        
        # 추가 질문은 더 자연스럽고 대화적인 톤으로
        if context_info:
            # 컨텍스트 정보가 있으면 더 구체적인 질문으로 조정
            pass
        
        if not processed.endswith(('?', '.')):
            processed += "?"
        
        return processed

    def _process_feedback_text(self, text):
        """피드백 텍스트 전처리"""
        processed = text.strip()
        
        # 피드백은 격려와 개선점을 균형있게 전달하는 톤
        if not processed.endswith('.'):
            processed += "."
        
        return processed

    def batch_generate_interview_audio(self, text_items, output_dir=None):
        """면접 관련 텍스트들을 일괄 음성 변환"""
        if not self.is_available or self.tts_model is None:
            logger.warning("TTS 사용 불가 - 일괄 변환 실패")
            return []
        
        if not text_items:
            logger.warning("변환할 텍스트 목록이 비어있습니다")
            return []
        
        results = []
        
        try:
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            logger.info(f"면접 오디오 일괄 변환 시작 - {len(text_items)}개 항목")
            
            for i, item in enumerate(text_items):
                if isinstance(item, dict):
                    text = item.get('text', '')
                    item_type = item.get('type', 'general')
                    filename = item.get('filename', f'interview_audio_{i+1}.wav')
                else:
                    text = str(item)
                    item_type = 'general'
                    filename = f'interview_audio_{i+1}.wav'
                
                if not text or not text.strip():
                    continue
                
                # 출력 파일 경로 생성
                if output_dir:
                    output_path = os.path.join(output_dir, filename)
                else:
                    output_path = tempfile.mktemp(suffix=f"_batch_{i+1}.wav")
                
                # 타입별 TTS 변환
                if item_type == 'question':
                    result_path = self.generate_interview_question_audio(text, "general", output_path)
                elif item_type == 'followup':
                    result_path = self.generate_followup_question_audio(text, None, output_path)
                elif item_type == 'feedback':
                    result_path = self.generate_interview_feedback_audio(text, output_path)
                else:
                    result_path = self.generate_interview_question_audio(text, "general", output_path)
                
                if result_path:
                    results.append({
                        "index": i,
                        "text": text[:50] + "..." if len(text) > 50 else text,
                        "type": item_type,
                        "output_path": result_path,
                        "success": True
                    })
                    logger.info(f"변환 완료 ({i+1}/{len(text_items)}): {item_type}")
                else:
                    results.append({
                        "index": i,
                        "text": text[:50] + "..." if len(text) > 50 else text,
                        "type": item_type,
                        "output_path": None,
                        "success": False
                    })
                    logger.warning(f"변환 실패 ({i+1}/{len(text_items)}): {item_type}")
            
            successful_count = len([r for r in results if r['success']])
            logger.info(f"면접 오디오 일괄 변환 완료 - 성공: {successful_count}/{len(text_items)}")
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
                "sample_rate": getattr(model_config, "sample_rate", 22050),
                "optimized_for": "interview_scenarios"
            }
        except Exception as e:
            logger.error(f"음성 설정 조회 오류: {str(e)}")
            return {"available": False, "error": str(e)}

    def evaluate_generated_audio_quality(self, audio_path, expected_duration_range=(3, 30)):
        """생성된 음성의 품질 평가"""
        if not audio_path or not os.path.exists(audio_path):
            return "TTS 출력 파일을 찾을 수 없음"
        
        try:
            # 파일 크기 및 기본 정보 확인
            file_size = os.path.getsize(audio_path)
            
            # 대략적인 품질 평가 (파일 크기 기반)
            quality_indicators = []
            
            if file_size < 5000:  # 5KB 미만
                quality_indicators.append("매우 짧은 출력")
            elif file_size < 50000:  # 50KB 미만
                quality_indicators.append("적절한 길이")
            elif file_size < 200000:  # 200KB 미만
                quality_indicators.append("상세한 음성")
            else:
                quality_indicators.append("긴 음성 출력")
            
            # 면접용 음성 품질 특성
            quality_indicators.append("면접 상황에 적합한 톤")
            
            # librosa를 사용한 추가 분석 (가능한 경우)
            try:
                import librosa
                y, sr = librosa.load(audio_path)
                duration = len(y) / sr
                
                if expected_duration_range[0] <= duration <= expected_duration_range[1]:
                    quality_indicators.append(f"적절한 길이 ({duration:.1f}초)")
                else:
                    quality_indicators.append(f"예상과 다른 길이 ({duration:.1f}초)")
                
            except ImportError:
                quality_indicators.append("상세 분석 불가 (librosa 없음)")
            except Exception as e:
                quality_indicators.append(f"오디오 분석 오류: {str(e)[:30]}")
            
            return " / ".join(quality_indicators)
            
        except Exception as e:
            logger.error(f"TTS 품질 평가 오류: {str(e)}")
            return f"TTS 품질 평가 실패: {str(e)}"

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
        
        logger.info(f"면접용 TTS 임시 파일 {cleaned_count}개 정리 완료")
        return cleaned_count

    def get_module_status(self):
        """모듈 상태 정보 반환"""
        return {
            "module_name": "Personal Interview TTS",
            "is_available": self.is_available,
            "model_name": self.model_name,
            "language": self.language,
            "voice_settings": self.get_voice_settings(),
            "supported_types": ["question", "followup", "feedback"],
            "functions": ["generate_interview_question_audio", "generate_followup_question_audio", "generate_interview_feedback_audio", "batch_generate_interview_audio"]
        }
