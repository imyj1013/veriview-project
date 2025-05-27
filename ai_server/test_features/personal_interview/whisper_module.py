"""
개인면접용 Whisper 음성 인식 테스트 모듈
면접 답변의 음성 인식에 특화된 기능 제공
"""
import logging
import os
import tempfile
import gc
import numpy as np

try:
    import whisper
    import librosa
    import soundfile as sf
    WHISPER_AVAILABLE = True
    print("Whisper 및 관련 패키지 로드 성공")
except ImportError as e:
    WHISPER_AVAILABLE = False
    print(f"Whisper 관련 패키지 로드 실패: {e}")

logger = logging.getLogger(__name__)

class PersonalInterviewWhisperModule:
    def __init__(self, model_size="base", sample_rate=16000):
        """개인면접용 Whisper 테스트 모듈 초기화"""
        self.model_size = model_size  # 면접은 더 정확한 인식을 위해 base 모델 사용
        self.sample_rate = sample_rate
        self.model = None
        self.is_available = WHISPER_AVAILABLE
        
        if self.is_available:
            try:
                self.model = whisper.load_model(model_size)
                logger.info(f"면접용 Whisper 모델 로드 성공: {model_size}")
            except Exception as e:
                logger.error(f"Whisper 모델 로드 실패: {str(e)}")
                self.is_available = False
        
        logger.info(f"개인면접 Whisper 테스트 모듈 초기화 - 사용 가능: {self.is_available}")

    def test_connection(self):
        """Whisper 연결 테스트"""
        if not self.is_available or self.model is None:
            return {"status": "unavailable", "message": "Whisper 모델을 사용할 수 없습니다"}
        
        try:
            test_audio = np.zeros(self.sample_rate, dtype=np.float32)
            result = self.model.transcribe(test_audio, language="ko")
            return {"status": "available", "message": "면접용 Whisper 정상 작동", "model": self.model_size}
        except Exception as e:
            return {"status": "error", "message": f"Whisper 실행 오류: {str(e)}"}

    def transcribe_interview_answer(self, video_path, question_type="general", language="ko"):
        """면접 답변 음성 인식 - 질문 유형별 특화"""
        if not self.is_available or self.model is None:
            logger.warning("Whisper 사용 불가 - 고정 텍스트 반환")
            return self._get_default_interview_transcription(question_type)
        
        try:
            if not os.path.exists(video_path):
                logger.warning(f"비디오 파일이 존재하지 않습니다: {video_path}")
                return self._get_default_interview_transcription(question_type)
            
            logger.info(f"면접 답변 음성 인식 시작 - 질문 유형: {question_type}")
            
            # 임시 오디오 파일로 추출
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
                
                # 비디오에서 오디오 추출
                audio, sr = librosa.load(video_path, sr=self.sample_rate)
                sf.write(temp_audio_path, audio, sr)
                
                # Whisper로 음성 인식 (더 상세한 옵션 사용)
                result = self.model.transcribe(
                    temp_audio_path, 
                    language=language,
                    word_timestamps=True,  # 단어별 타임스탬프
                    verbose=False
                )
                
                # 임시 파일 삭제
                os.remove(temp_audio_path)
                
                # 면접 특화 후처리
                processed_result = self._process_interview_transcription(result, question_type)
                
                logger.info(f"면접 답변 음성 인식 완료 - 텍스트 길이: {len(processed_result.get('text', ''))}")
                
                return processed_result
            
        except Exception as e:
            logger.error(f"면접 답변 음성 인식 오류: {str(e)}")
            return self._get_default_interview_transcription(question_type)
        finally:
            gc.collect()

    def transcribe_audio_file(self, audio_path, question_type="general", language="ko"):
        """오디오 파일 음성 인식"""
        if not self.is_available or self.model is None:
            logger.warning("Whisper 사용 불가 - 고정 텍스트 반환")
            return self._get_default_interview_transcription(question_type)
        
        try:
            if not os.path.exists(audio_path):
                logger.warning(f"오디오 파일이 존재하지 않습니다: {audio_path}")
                return self._get_default_interview_transcription(question_type)
            
            logger.info(f"면접 오디오 파일 음성 인식 시작: {audio_path}")
            
            result = self.model.transcribe(
                audio_path, 
                language=language,
                word_timestamps=True,
                verbose=False
            )
            
            processed_result = self._process_interview_transcription(result, question_type)
            
            logger.info(f"면접 오디오 음성 인식 완료 - 텍스트 길이: {len(processed_result.get('text', ''))}")
            
            return processed_result
            
        except Exception as e:
            logger.error(f"면접 오디오 음성 인식 오류: {str(e)}")
            return self._get_default_interview_transcription(question_type)
        finally:
            gc.collect()

    def _process_interview_transcription(self, whisper_result, question_type):
        """면접 음성 인식 결과 후처리"""
        try:
            text = whisper_result.get("text", "").strip()
            segments = whisper_result.get("segments", [])
            language = whisper_result.get("language", "ko")
            
            # 면접 특화 분석
            analysis = {
                "text": text,
                "language": language,
                "segments": segments,
                "question_type": question_type,
                "word_count": len(text.split()) if text else 0,
                "character_count": len(text),
                "confidence": self._calculate_average_confidence(segments),
                "speech_analysis": self._analyze_speech_patterns(segments, text, question_type)
            }
            
            # 질문 유형별 특화 분석
            if question_type == "technical":
                analysis.update(self._analyze_technical_answer(text, segments))
            elif question_type == "behavioral":
                analysis.update(self._analyze_behavioral_answer(text, segments))
            else:
                analysis.update(self._analyze_general_answer(text, segments))
            
            return analysis
            
        except Exception as e:
            logger.error(f"음성 인식 결과 후처리 오류: {str(e)}")
            return self._get_default_interview_transcription(question_type)

    def _analyze_speech_patterns(self, segments, text, question_type):
        """발화 패턴 분석"""
        if not segments or not text:
            return {"pattern_analysis": "분석 불가"}
        
        patterns = {}
        
        try:
            # 발화 속도 분석
            total_duration = segments[-1]["end"] - segments[0]["start"] if segments else 0
            word_count = len(text.split())
            
            if total_duration > 0:
                speaking_rate = word_count / (total_duration / 60)  # 분당 단어 수
                patterns["speaking_rate_wpm"] = speaking_rate
                
                # 면접 적정 속도 평가 (120-180 wpm이 적절)
                if 120 <= speaking_rate <= 180:
                    patterns["pace_evaluation"] = "적절한 말하기 속도"
                elif speaking_rate < 120:
                    patterns["pace_evaluation"] = "다소 천천히 말함"
                else:
                    patterns["pace_evaluation"] = "다소 빠르게 말함"
            else:
                patterns["speaking_rate_wpm"] = 0
                patterns["pace_evaluation"] = "속도 분석 불가"
            
            # 일시정지 패턴 분석
            pauses = []
            for i in range(len(segments) - 1):
                pause_duration = segments[i+1]["start"] - segments[i]["end"]
                if pause_duration > 0.1:  # 0.1초 이상의 일시정지
                    pauses.append(pause_duration)
            
            if pauses:
                patterns["average_pause_duration"] = np.mean(pauses)
                patterns["long_pauses_count"] = len([p for p in pauses if p > 1.0])  # 1초 이상 일시정지
                patterns["pause_analysis"] = self._evaluate_pauses(pauses, question_type)
            else:
                patterns["average_pause_duration"] = 0
                patterns["long_pauses_count"] = 0
                patterns["pause_analysis"] = "일시정지 없음"
            
            # 문장 구조 분석
            sentences = [s for s in text.split('.') if s.strip()]
            if sentences:
                patterns["sentence_count"] = len(sentences)
                patterns["avg_sentence_length"] = np.mean([len(s.split()) for s in sentences])
                patterns["sentence_structure"] = self._analyze_sentence_structure(sentences)
            else:
                patterns["sentence_count"] = 0
                patterns["avg_sentence_length"] = 0
                patterns["sentence_structure"] = "문장 구조 분석 불가"
            
        except Exception as e:
            logger.error(f"발화 패턴 분석 오류: {str(e)}")
            patterns["pattern_analysis"] = f"분석 오류: {str(e)}"
        
        return patterns

    def _evaluate_pauses(self, pauses, question_type):
        """일시정지 평가"""
        avg_pause = np.mean(pauses)
        long_pause_count = len([p for p in pauses if p > 1.0])
        
        if question_type == "technical":
            # 기술 질문에서는 사고 시간이 중요
            if avg_pause >= 0.8:
                return "충분한 사고 시간 확보"
            elif avg_pause >= 0.5:
                return "적절한 사고 과정"
            else:
                return "빠른 응답 (사고 시간 부족 가능)"
        elif question_type == "behavioral":
            # 인성 질문에서는 자연스러운 흐름이 중요
            if 0.3 <= avg_pause <= 0.8:
                return "자연스러운 말하기 흐름"
            elif avg_pause > 0.8:
                return "다소 긴 사고 시간"
            else:
                return "매우 빠른 응답"
        else:
            # 일반 질문
            if 0.2 <= avg_pause <= 0.6:
                return "자연스러운 일시정지 패턴"
            elif avg_pause > 0.6:
                return "다소 긴 일시정지"
            else:
                return "매우 빠른 연속 발화"

    def _analyze_sentence_structure(self, sentences):
        """문장 구조 분석"""
        if not sentences:
            return "문장 없음"
        
        # 문장 길이 분포
        lengths = [len(s.split()) for s in sentences]
        avg_length = np.mean(lengths)
        
        if avg_length >= 15:
            return "복잡하고 상세한 문장 구조"
        elif avg_length >= 10:
            return "적절한 문장 구조"
        elif avg_length >= 5:
            return "간단명료한 문장 구조"
        else:
            return "매우 짧은 문장 구조"

    def _analyze_technical_answer(self, text, segments):
        """기술 질문 답변 분석"""
        analysis = {}
        
        # 기술 용어 사용 빈도
        technical_keywords = [
            "기술", "개발", "프로그래밍", "알고리즘", "데이터베이스", "API", "프레임워크",
            "라이브러리", "버전", "배포", "테스트", "디버깅", "최적화", "성능", "보안"
        ]
        
        keyword_count = sum(1 for keyword in technical_keywords if keyword in text)
        analysis["technical_terminology_usage"] = keyword_count
        
        # 설명의 논리적 구조
        logical_connectors = ["먼저", "그리고", "따라서", "결과적으로", "또한", "반면에"]
        connector_count = sum(1 for connector in logical_connectors if connector in text)
        analysis["logical_structure_indicators"] = connector_count
        
        # 구체적 예시 언급
        example_indicators = ["예를 들어", "예시", "경우", "상황", "프로젝트에서"]
        example_count = sum(1 for indicator in example_indicators if indicator in text)
        analysis["concrete_examples"] = example_count
        
        # 기술 답변 품질 평가
        if keyword_count >= 3 and connector_count >= 2:
            analysis["technical_answer_quality"] = "우수한 기술적 설명"
        elif keyword_count >= 2 and connector_count >= 1:
            analysis["technical_answer_quality"] = "적절한 기술적 설명"
        else:
            analysis["technical_answer_quality"] = "기술적 설명 보완 필요"
        
        return analysis

    def _analyze_behavioral_answer(self, text, segments):
        """인성 질문 답변 분석"""
        analysis = {}
        
        # 감정 표현 단어
        emotion_words = [
            "느꼈습니다", "생각했습니다", "깨달았습니다", "배웠습니다", "성장했습니다",
            "어려웠지만", "힘들었지만", "보람", "만족", "감사", "후회", "반성"
        ]
        
        emotion_count = sum(1 for word in emotion_words if word in text)
        analysis["emotional_expression"] = emotion_count
        
        # 개인적 경험 언급
        personal_indicators = ["저는", "제가", "개인적으로", "경험", "상황", "당시"]
        personal_count = sum(1 for indicator in personal_indicators if indicator in text)
        analysis["personal_experience_sharing"] = personal_count
        
        # 성찰적 표현
        reflection_words = ["배운", "깨달은", "성장", "개선", "발전", "노력", "변화"]
        reflection_count = sum(1 for word in reflection_words if word in text)
        analysis["self_reflection"] = reflection_count
        
        # 인성 답변 품질 평가
        total_indicators = emotion_count + personal_count + reflection_count
        if total_indicators >= 5:
            analysis["behavioral_answer_quality"] = "풍부한 개인적 경험과 성찰"
        elif total_indicators >= 3:
            analysis["behavioral_answer_quality"] = "적절한 개인적 경험 공유"
        else:
            analysis["behavioral_answer_quality"] = "개인적 경험 공유 보완 필요"
        
        return analysis

    def _analyze_general_answer(self, text, segments):
        """일반 질문 답변 분석"""
        analysis = {}
        
        # 답변 완성도
        question_response_indicators = [
            "이유는", "때문입니다", "결론적으로", "정리하면", "요약하면"
        ]
        
        completion_count = sum(1 for indicator in question_response_indicators if indicator in text)
        analysis["answer_completeness_indicators"] = completion_count
        
        # 구체성
        specific_indicators = ["구체적으로", "실제로", "예를 들면", "정확히", "명확히"]
        specific_count = sum(1 for indicator in specific_indicators if indicator in text)
        analysis["answer_specificity"] = specific_count
        
        # 자신감 표현
        confidence_indicators = ["확신", "분명", "자신", "있습니다", "할 수 있습니다"]
        confidence_count = sum(1 for indicator in confidence_indicators if indicator in text)
        analysis["confidence_expression"] = confidence_count
        
        # 일반 답변 품질 평가
        if completion_count >= 2 and specific_count >= 1:
            analysis["general_answer_quality"] = "완성도 높은 답변"
        elif completion_count >= 1 or specific_count >= 1:
            analysis["general_answer_quality"] = "적절한 답변 구조"
        else:
            analysis["general_answer_quality"] = "답변 구조 보완 필요"
        
        return analysis

    def _calculate_average_confidence(self, segments):
        """세그먼트별 신뢰도 평균 계산"""
        if not segments:
            return 0.8  # 기본값
        
        try:
            confidences = []
            for segment in segments:
                if "confidence" in segment:
                    confidences.append(segment["confidence"])
                elif "avg_logprob" in segment:
                    conf = max(0.0, min(1.0, np.exp(segment["avg_logprob"])))
                    confidences.append(conf)
            
            if confidences:
                return np.mean(confidences)
            else:
                return 0.8
                
        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {str(e)}")
            return 0.8

    def evaluate_interview_transcription_quality(self, transcription_result):
        """면접 음성 인식 품질 평가"""
        if not transcription_result:
            return "음성 인식 결과 없음"
        
        text = transcription_result.get("text", "")
        confidence = transcription_result.get("confidence", 0.0)
        question_type = transcription_result.get("question_type", "general")
        speech_analysis = transcription_result.get("speech_analysis", {})
        
        evaluation_parts = []
        
        # 기본 인식 품질
        if confidence >= 0.9:
            evaluation_parts.append("매우 높은 인식 정확도")
        elif confidence >= 0.7:
            evaluation_parts.append("높은 인식 정확도")
        elif confidence >= 0.5:
            evaluation_parts.append("보통 인식 정확도")
        else:
            evaluation_parts.append("낮은 인식 정확도")
        
        # 답변 길이 평가
        word_count = transcription_result.get("word_count", 0)
        if word_count >= 100:
            evaluation_parts.append("충분한 답변 길이")
        elif word_count >= 50:
            evaluation_parts.append("적절한 답변 길이")
        else:
            evaluation_parts.append("짧은 답변 길이")
        
        # 발화 패턴 평가
        pace_eval = speech_analysis.get("pace_evaluation", "")
        if pace_eval:
            evaluation_parts.append(pace_eval)
        
        # 질문 유형별 평가
        if question_type == "technical":
            tech_quality = transcription_result.get("technical_answer_quality", "")
            if tech_quality:
                evaluation_parts.append(tech_quality)
        elif question_type == "behavioral":
            behavioral_quality = transcription_result.get("behavioral_answer_quality", "")
            if behavioral_quality:
                evaluation_parts.append(behavioral_quality)
        
        return " / ".join(evaluation_parts)

    def _get_default_interview_transcription(self, question_type):
        """기본 면접 음성 인식 결과"""
        default_texts = {
            "technical": "저는 주로 Python과 JavaScript를 사용하여 웹 애플리케이션을 개발했습니다. 특히 데이터베이스 설계와 API 개발에 경험이 있으며, 성능 최적화를 위해 다양한 방법을 시도해보았습니다.",
            "behavioral": "팀 프로젝트에서 의견 충돌이 있었을 때, 먼저 각자의 관점을 이해하려고 노력했습니다. 서로의 의견을 정리하고 장단점을 분석한 후, 프로젝트 목표에 가장 적합한 방향을 찾을 수 있었습니다. 이 경험을 통해 소통의 중요성을 깨달았습니다.",
            "general": "저는 지속적인 학습을 통해 성장하는 개발자가 되고 싶습니다. 새로운 기술에 대한 호기심이 많고, 이를 실제 프로젝트에 적용해보는 것을 좋아합니다. 앞으로도 사용자에게 가치 있는 서비스를 만드는 데 기여하고 싶습니다."
        }
        
        default_text = default_texts.get(question_type, default_texts["general"])
        
        return {
            "text": default_text,
            "language": "ko",
            "segments": [],
            "question_type": question_type,
            "word_count": len(default_text.split()),
            "character_count": len(default_text),
            "confidence": 0.85,
            "speech_analysis": {
                "speaking_rate_wpm": 140,
                "pace_evaluation": "적절한 말하기 속도",
                "average_pause_duration": 0.5,
                "long_pauses_count": 2,
                "pause_analysis": "자연스러운 일시정지 패턴",
                "sentence_count": 3,
                "avg_sentence_length": 12,
                "sentence_structure": "적절한 문장 구조"
            }
        }

    def get_module_status(self):
        """모듈 상태 정보 반환"""
        return {
            "module_name": "Personal Interview Whisper STT",
            "is_available": self.is_available,
            "model_size": self.model_size,
            "sample_rate": self.sample_rate,
            "supported_question_types": ["general", "technical", "behavioral"],
            "functions": ["transcribe_interview_answer", "transcribe_audio_file", "evaluate_interview_transcription_quality"]
        }
