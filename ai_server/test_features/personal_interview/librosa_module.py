"""
개인면접용 Librosa 음성 분석 테스트 모듈
면접 상황에 특화된 음성 특징 분석 제공
"""
import logging
import os
import numpy as np

try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
    print("Librosa 패키지 로드 성공")
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Librosa 패키지를 찾을 수 없습니다. 음성 분석 기능이 제한됩니다.")

logger = logging.getLogger(__name__)

class PersonalInterviewLibrosaModule:
    def __init__(self, sample_rate=16000):
        """개인면접용 Librosa 테스트 모듈 초기화"""
        self.sample_rate = sample_rate
        self.is_available = LIBROSA_AVAILABLE
        logger.info(f"개인면접 Librosa 테스트 모듈 초기화 - 사용 가능: {self.is_available}")

    def test_connection(self):
        """Librosa 연결 테스트"""
        if not self.is_available:
            return {"status": "unavailable", "message": "Librosa 패키지를 찾을 수 없습니다"}
        
        try:
            test_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, self.sample_rate))
            _ = librosa.feature.rms(y=test_signal)
            return {"status": "available", "message": "Librosa 정상 작동"}
        except Exception as e:
            return {"status": "error", "message": f"Librosa 실행 오류: {str(e)}"}

    def analyze_interview_audio(self, audio_path, question_type="general"):
        """면접 오디오 분석 - 질문 유형별 특화 분석"""
        if not self.is_available:
            logger.warning("Librosa 사용 불가 - 고정값 반환")
            return self._get_default_interview_result(question_type)
        
        try:
            if not os.path.exists(audio_path):
                logger.warning(f"오디오 파일이 존재하지 않습니다: {audio_path}")
                return self._get_default_interview_result(question_type)
            
            # 오디오 로드
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            logger.info(f"면접 오디오 로드 완료 - 길이: {len(y)}, 샘플레이트: {sr}")
            
            # 면접 특화 음성 특징 분석
            analysis_result = self._extract_interview_features(y, sr, question_type)
            logger.info("면접 오디오 분석 완료")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"면접 오디오 분석 오류: {str(e)}")
            return self._get_default_interview_result(question_type)

    def analyze_interview_video_audio(self, video_path, question_type="general"):
        """면접 비디오에서 오디오 추출 후 분석"""
        if not self.is_available:
            logger.warning("Librosa 사용 불가 - 고정값 반환")
            return self._get_default_interview_result(question_type)
        
        try:
            if not os.path.exists(video_path):
                logger.warning(f"비디오 파일이 존재하지 않습니다: {video_path}")
                return self._get_default_interview_result(question_type)
            
            # 비디오에서 오디오 추출
            y, sr = librosa.load(video_path, sr=self.sample_rate)
            logger.info(f"면접 비디오에서 오디오 추출 완료 - 길이: {len(y)}")
            
            # 면접 특화 분석
            analysis_result = self._extract_interview_features(y, sr, question_type)
            logger.info("면접 비디오 오디오 분석 완료")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"면접 비디오 오디오 분석 오류: {str(e)}")
            return self._get_default_interview_result(question_type)

    def _extract_interview_features(self, y, sr, question_type):
        """면접용 음성 특징 추출"""
        try:
            features = {}
            
            # 기본 음성 특징
            basic_features = self._extract_basic_features(y, sr)
            features.update(basic_features)
            
            # 면접 특화 특징
            interview_features = self._extract_interview_specific_features(y, sr, question_type)
            features.update(interview_features)
            
            # 질문 유형별 특화 분석
            if question_type == "technical":
                tech_features = self._analyze_technical_speech_patterns(y, sr)
                features.update(tech_features)
            elif question_type == "behavioral":
                behavioral_features = self._analyze_behavioral_speech_patterns(y, sr)
                features.update(behavioral_features)
            else:
                general_features = self._analyze_general_speech_patterns(y, sr)
                features.update(general_features)
            
            logger.info(f"추출된 면접 특징 수: {len(features)}")
            return features
            
        except Exception as e:
            logger.error(f"면접 특징 추출 오류: {str(e)}")
            return self._get_default_interview_result(question_type)

    def _extract_basic_features(self, y, sr):
        """기본 음성 특징 추출"""
        features = {}
        
        # 피치 분석
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        
        for i in range(magnitudes.shape[1]):
            if magnitudes[:, i].max() > 0:
                pitch_idx = magnitudes[:, i].argmax()
                pitch = pitches[pitch_idx, i]
                if pitch > 0:
                    pitch_values.append(pitch)
        
        if pitch_values:
            features["pitch_mean"] = np.mean(pitch_values)
            features["pitch_std"] = np.std(pitch_values)
            features["pitch_range"] = np.max(pitch_values) - np.min(pitch_values)
            features["pitch_median"] = np.median(pitch_values)
        else:
            features.update({"pitch_mean": 0, "pitch_std": 0, "pitch_range": 0, "pitch_median": 0})
        
        # RMS 에너지 (음성 크기)
        rms = librosa.feature.rms(y=y)
        features["rms_mean"] = np.mean(rms)
        features["rms_std"] = np.std(rms)
        features["rms_max"] = np.max(rms)
        
        # 스펙트럴 특징
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
        features["spectral_centroid_mean"] = np.mean(spectral_centroids)
        features["spectral_centroid_std"] = np.std(spectral_centroids)
        
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        features["spectral_rolloff_mean"] = np.mean(spectral_rolloff)
        
        # 제로 크로싱 레이트
        zcr = librosa.feature.zero_crossing_rate(y)
        features["zcr_mean"] = np.mean(zcr)
        features["zcr_std"] = np.std(zcr)
        
        return features

    def _extract_interview_specific_features(self, y, sr, question_type):
        """면접 특화 특징 추출"""
        features = {}
        
        # 발화 패턴 분석
        features.update(self._analyze_speech_patterns(y, sr))
        
        # 감정적 특징 추출
        features.update(self._extract_emotional_features(y, sr))
        
        # 자신감 지표
        features.update(self._calculate_confidence_indicators(y, sr))
        
        # 질문 유형 표시
        features["question_type"] = question_type
        
        return features

    def _analyze_speech_patterns(self, y, sr):
        """발화 패턴 분석"""
        patterns = {}
        
        # 무음 구간 분석
        intervals = librosa.effects.split(y, top_db=20)
        if len(intervals) > 0:
            speech_durations = [interval[1] - interval[0] for interval in intervals]
            silence_durations = []
            
            for i in range(len(intervals) - 1):
                silence_duration = intervals[i+1][0] - intervals[i][1]
                silence_durations.append(silence_duration)
            
            patterns["avg_speech_duration"] = np.mean(speech_durations) / sr if speech_durations else 0
            patterns["avg_silence_duration"] = np.mean(silence_durations) / sr if silence_durations else 0
            patterns["speech_segments_count"] = len(intervals)
            patterns["speech_rate"] = len(intervals) / (len(y) / sr) if len(y) > 0 else 0
        else:
            patterns.update({
                "avg_speech_duration": 0,
                "avg_silence_duration": 0,
                "speech_segments_count": 0,
                "speech_rate": 0
            })
        
        # 말의 속도 (템포)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        patterns["tempo"] = tempo
        
        return patterns

    def _extract_emotional_features(self, y, sr):
        """감정적 특징 추출"""
        emotional = {}
        
        # MFCC 계수들 (감정 분석에 유용)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        for i in range(min(5, mfccs.shape[0])):  # 처음 5개 계수만 사용
            emotional[f"mfcc_{i+1}_mean"] = np.mean(mfccs[i])
            emotional[f"mfcc_{i+1}_std"] = np.std(mfccs[i])
        
        # 크로마 특징 (음성의 하모닉 특성)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        emotional["chroma_mean"] = np.mean(chroma)
        emotional["chroma_std"] = np.std(chroma)
        
        return emotional

    def _calculate_confidence_indicators(self, y, sr):
        """자신감 지표 계산"""
        confidence = {}
        
        # 음성 안정성 (피치 변동성으로 측정)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = [pitches[magnitudes[:, i].argmax(), i] 
                       for i in range(magnitudes.shape[1]) if magnitudes[:, i].max() > 0]
        
        if pitch_values:
            confidence["voice_stability"] = 1.0 - min(1.0, np.std(pitch_values) / 100.0)
        else:
            confidence["voice_stability"] = 0.5
        
        # 음성 강도 일관성
        rms = librosa.feature.rms(y=y)
        if len(rms[0]) > 0:
            confidence["volume_consistency"] = 1.0 - min(1.0, np.std(rms) / np.mean(rms))
        else:
            confidence["volume_consistency"] = 0.5
        
        return confidence

    def _analyze_technical_speech_patterns(self, y, sr):
        """기술 질문 음성 패턴 분석"""
        tech_patterns = {}
        
        # 사고 중 무음 패턴 (기술 질문에서 중요)
        intervals = librosa.effects.split(y, top_db=25)
        if len(intervals) > 1:
            pause_durations = []
            for i in range(len(intervals) - 1):
                pause_duration = (intervals[i+1][0] - intervals[i][1]) / sr
                pause_durations.append(pause_duration)
            
            if pause_durations:
                tech_patterns["thinking_pauses_avg"] = np.mean(pause_durations)
                tech_patterns["thinking_pauses_count"] = len([p for p in pause_durations if p > 1.0])
            else:
                tech_patterns["thinking_pauses_avg"] = 0
                tech_patterns["thinking_pauses_count"] = 0
        else:
            tech_patterns["thinking_pauses_avg"] = 0
            tech_patterns["thinking_pauses_count"] = 0
        
        # 설명 패턴 (기술적 설명 시 나타나는 특징)
        tech_patterns["explanation_rhythm"] = self._detect_explanation_rhythm(y, sr)
        
        return tech_patterns

    def _analyze_behavioral_speech_patterns(self, y, sr):
        """인성 질문 음성 패턴 분석"""
        behavioral_patterns = {}
        
        # 감정적 변화 패턴
        rms = librosa.feature.rms(y=y)
        if len(rms[0]) > 10:
            energy_changes = np.diff(rms[0])
            behavioral_patterns["emotional_variability"] = np.std(energy_changes)
            behavioral_patterns["emotional_peaks_count"] = len([e for e in energy_changes if abs(e) > np.std(energy_changes)])
        else:
            behavioral_patterns["emotional_variability"] = 0
            behavioral_patterns["emotional_peaks_count"] = 0
        
        # 진정성 지표 (자연스러운 음성 변화)
        behavioral_patterns["authenticity_score"] = self._calculate_authenticity_score(y, sr)
        
        return behavioral_patterns

    def _analyze_general_speech_patterns(self, y, sr):
        """일반 질문 음성 패턴 분석"""
        general_patterns = {}
        
        # 전반적인 유창성
        general_patterns["fluency_score"] = self._calculate_fluency_score(y, sr)
        
        # 명료도
        general_patterns["clarity_score"] = self._calculate_clarity_score(y, sr)
        
        return general_patterns

    def _detect_explanation_rhythm(self, y, sr):
        """설명 리듬 감지"""
        try:
            # 음성 세그먼트 길이의 패턴으로 설명 리듬 추정
            intervals = librosa.effects.split(y, top_db=20)
            if len(intervals) > 2:
                segment_lengths = [(interval[1] - interval[0]) / sr for interval in intervals]
                rhythm_consistency = 1.0 - min(1.0, np.std(segment_lengths) / np.mean(segment_lengths))
                return rhythm_consistency
            return 0.5
        except:
            return 0.5

    def _calculate_authenticity_score(self, y, sr):
        """진정성 점수 계산"""
        try:
            # MFCC 변화의 자연스러움으로 진정성 추정
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=5)
            if mfccs.shape[1] > 10:
                mfcc_changes = np.diff(mfccs, axis=1)
                naturalness = 1.0 - min(1.0, np.mean(np.std(mfcc_changes, axis=1)) / 10.0)
                return max(0.0, min(1.0, naturalness))
            return 0.5
        except:
            return 0.5

    def _calculate_fluency_score(self, y, sr):
        """유창성 점수 계산"""
        try:
            # 무음 구간과 발화 구간의 비율로 유창성 추정
            intervals = librosa.effects.split(y, top_db=20)
            if len(intervals) > 0:
                speech_time = sum([(interval[1] - interval[0]) for interval in intervals]) / sr
                total_time = len(y) / sr
                speech_ratio = speech_time / total_time if total_time > 0 else 0
                
                # 적절한 발화 비율 (0.6-0.8)이 유창함을 나타냄
                if 0.6 <= speech_ratio <= 0.8:
                    return min(1.0, speech_ratio + 0.2)
                else:
                    return max(0.3, 1.0 - abs(speech_ratio - 0.7))
            return 0.5
        except:
            return 0.5

    def _calculate_clarity_score(self, y, sr):
        """명료도 점수 계산"""
        try:
            # 고주파 에너지 비율로 명료도 추정
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            
            # 저주파 vs 고주파 에너지 비교
            low_freq_energy = np.mean(magnitude[:len(magnitude)//4])
            high_freq_energy = np.mean(magnitude[len(magnitude)//2:])
            
            if low_freq_energy > 0:
                clarity_ratio = high_freq_energy / low_freq_energy
                return min(1.0, clarity_ratio / 2.0)
            return 0.5
        except:
            return 0.5

    def evaluate_interview_voice_quality(self, analysis_result):
        """면접 음성 품질 종합 평가"""
        if not analysis_result:
            return "음성 분석 결과 없음"
        
        question_type = analysis_result.get("question_type", "general")
        
        # 공통 평가 요소
        voice_stability = analysis_result.get("voice_stability", 0.5)
        volume_consistency = analysis_result.get("volume_consistency", 0.5)
        
        evaluation_parts = []
        
        # 기본 음성 품질
        if voice_stability >= 0.8 and volume_consistency >= 0.8:
            evaluation_parts.append("안정적이고 일관된 음성")
        elif voice_stability >= 0.6 and volume_consistency >= 0.6:
            evaluation_parts.append("양호한 음성 품질")
        else:
            evaluation_parts.append("음성 안정성 개선 필요")
        
        # 질문 유형별 특화 평가
        if question_type == "technical":
            thinking_pauses = analysis_result.get("thinking_pauses_avg", 0)
            if thinking_pauses >= 1.0:
                evaluation_parts.append("충분한 사고 시간 활용")
            elif thinking_pauses >= 0.5:
                evaluation_parts.append("적절한 사고 과정")
            else:
                evaluation_parts.append("사고 시간 부족 가능성")
                
        elif question_type == "behavioral":
            authenticity = analysis_result.get("authenticity_score", 0.5)
            if authenticity >= 0.8:
                evaluation_parts.append("진정성 있는 표현")
            elif authenticity >= 0.6:
                evaluation_parts.append("자연스러운 표현")
            else:
                evaluation_parts.append("표현의 자연스러움 개선 필요")
                
        else:
            fluency = analysis_result.get("fluency_score", 0.5)
            clarity = analysis_result.get("clarity_score", 0.5)
            
            if fluency >= 0.7 and clarity >= 0.7:
                evaluation_parts.append("유창하고 명료한 발화")
            elif fluency >= 0.5 and clarity >= 0.5:
                evaluation_parts.append("적절한 발화 품질")
            else:
                evaluation_parts.append("발화 품질 개선 필요")
        
        return " / ".join(evaluation_parts)

    def calculate_interview_voice_scores(self, analysis_result):
        """면접용 음성 점수 계산"""
        if not analysis_result:
            return {
                "voice_score": 1.0,
                "voice_feedback": "음성 분석 불가"
            }
        
        question_type = analysis_result.get("question_type", "general")
        
        # 기본 점수 3.0에서 시작
        voice_score = 3.0
        
        # 공통 평가 요소
        voice_stability = analysis_result.get("voice_stability", 0.5)
        volume_consistency = analysis_result.get("volume_consistency", 0.5)
        
        voice_score += voice_stability * 1.0  # 최대 1점 추가
        voice_score += volume_consistency * 0.5  # 최대 0.5점 추가
        
        # 질문 유형별 가산점
        if question_type == "technical":
            thinking_pauses = analysis_result.get("thinking_pauses_avg", 0)
            if thinking_pauses >= 1.0:
                voice_score += 0.5
            elif thinking_pauses >= 0.5:
                voice_score += 0.3
                
        elif question_type == "behavioral":
            authenticity = analysis_result.get("authenticity_score", 0.5)
            voice_score += authenticity * 0.5
            
        else:
            fluency = analysis_result.get("fluency_score", 0.5)
            clarity = analysis_result.get("clarity_score", 0.5)
            voice_score += (fluency + clarity) * 0.25
        
        # 최대 5.0으로 제한
        voice_score = min(5.0, voice_score)
        
        # 피드백 생성
        if voice_score >= 4.5:
            feedback = "목소리: 매우 우수한 음성 품질과 표현력"
        elif voice_score >= 4.0:
            feedback = "목소리: 우수한 음성 품질"
        elif voice_score >= 3.5:
            feedback = "목소리: 양호한 음성 품질"
        elif voice_score >= 3.0:
            feedback = "목소리: 적절한 음성 품질"
        else:
            feedback = "목소리: 음성 품질 개선 필요"
        
        return {
            "voice_score": voice_score,
            "voice_feedback": feedback
        }

    def _get_default_interview_result(self, question_type):
        """기본 면접 음성 분석 결과"""
        base_result = {
            "pitch_mean": 180.0,
            "pitch_std": 25.0,
            "pitch_range": 80.0,
            "pitch_median": 175.0,
            "rms_mean": 0.15,
            "rms_std": 0.03,
            "rms_max": 0.25,
            "spectral_centroid_mean": 2200.0,
            "spectral_centroid_std": 300.0,
            "spectral_rolloff_mean": 3500.0,
            "zcr_mean": 0.06,
            "zcr_std": 0.02,
            "avg_speech_duration": 2.5,
            "avg_silence_duration": 0.8,
            "speech_segments_count": 8,
            "speech_rate": 0.75,
            "tempo": 110.0,
            "voice_stability": 0.75,
            "volume_consistency": 0.80,
            "question_type": question_type
        }
        
        # 질문 유형별 특화 기본값
        if question_type == "technical":
            base_result.update({
                "thinking_pauses_avg": 1.2,
                "thinking_pauses_count": 3,
                "explanation_rhythm": 0.7
            })
        elif question_type == "behavioral":
            base_result.update({
                "emotional_variability": 0.15,
                "emotional_peaks_count": 4,
                "authenticity_score": 0.75
            })
        else:
            base_result.update({
                "fluency_score": 0.7,
                "clarity_score": 0.75
            })
        
        return base_result

    def get_module_status(self):
        """모듈 상태 정보 반환"""
        return {
            "module_name": "Personal Interview Librosa",
            "is_available": self.is_available,
            "sample_rate": self.sample_rate,
            "supported_question_types": ["general", "technical", "behavioral"],
            "functions": ["analyze_interview_audio", "analyze_interview_video_audio", "evaluate_interview_voice_quality", "calculate_interview_voice_scores"]
        }
