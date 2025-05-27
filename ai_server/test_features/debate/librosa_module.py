"""
Librosa 음성 분석 테스트 모듈
LLM 미사용 환경에서 Librosa 기능의 정상 작동을 테스트
"""
import logging
import os
import numpy as np

# Librosa 임포트 시도
try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
    print("Librosa 패키지 로드 성공")
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Librosa 패키지를 찾을 수 없습니다. 음성 분석 기능이 제한됩니다.")

logger = logging.getLogger(__name__)

class LibrosaTestModule:
    def __init__(self, sample_rate=16000):
        """Librosa 테스트 모듈 초기화"""
        self.sample_rate = sample_rate
        self.is_available = LIBROSA_AVAILABLE
        logger.info(f"Librosa 테스트 모듈 초기화 - 사용 가능: {self.is_available}")

    def test_connection(self):
        """Librosa 연결 테스트"""
        if not self.is_available:
            return {"status": "unavailable", "message": "Librosa 패키지를 찾을 수 없습니다"}
        
        try:
            # 간단한 테스트 신호 생성 및 분석
            test_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, self.sample_rate))
            _ = librosa.feature.rms(y=test_signal)
            return {"status": "available", "message": "Librosa 정상 작동"}
        except Exception as e:
            return {"status": "error", "message": f"Librosa 실행 오류: {str(e)}"}

    def analyze_audio(self, audio_path):
        """오디오 파일 분석"""
        if not self.is_available:
            logger.warning("Librosa 사용 불가 - 고정값 반환")
            return self._get_default_result()
        
        try:
            if not os.path.exists(audio_path):
                logger.warning(f"오디오 파일이 존재하지 않습니다: {audio_path}")
                return self._get_default_result()
            
            # 오디오 로드
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            logger.info(f"오디오 로드 완료 - 길이: {len(y)}, 샘플레이트: {sr}")
            
            # 다양한 음성 특징 분석
            analysis_result = self._extract_audio_features(y, sr)
            logger.info("오디오 분석 완료")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"오디오 분석 오류: {str(e)}")
            return self._get_default_result()

    def analyze_video_audio(self, video_path):
        """비디오에서 오디오 추출 후 분석"""
        if not self.is_available:
            logger.warning("Librosa 사용 불가 - 고정값 반환")
            return self._get_default_result()
        
        try:
            if not os.path.exists(video_path):
                logger.warning(f"비디오 파일이 존재하지 않습니다: {video_path}")
                return self._get_default_result()
            
            # 비디오에서 오디오 추출
            y, sr = librosa.load(video_path, sr=self.sample_rate)
            logger.info(f"비디오에서 오디오 추출 완료 - 길이: {len(y)}, 샘플레이트: {sr}")
            
            # 오디오 분석
            analysis_result = self._extract_audio_features(y, sr)
            logger.info("비디오 오디오 분석 완료")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"비디오 오디오 분석 오류: {str(e)}")
            return self._get_default_result()

    def _extract_audio_features(self, y, sr):
        """오디오 특징 추출"""
        try:
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
                features["pitch_min"] = np.min(pitch_values)
                features["pitch_max"] = np.max(pitch_values)
            else:
                features["pitch_mean"] = 0.0
                features["pitch_std"] = 0.0
                features["pitch_min"] = 0.0
                features["pitch_max"] = 0.0
            
            # RMS 에너지
            rms = librosa.feature.rms(y=y)
            features["rms_mean"] = np.mean(rms)
            features["rms_std"] = np.std(rms)
            
            # 스펙트럴 중심
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            features["spectral_centroid_mean"] = np.mean(spectral_centroids)
            
            # 템포
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            features["tempo"] = tempo
            
            # 제로 크로싱 레이트 (음성의 안정성 지표)
            zcr = librosa.feature.zero_crossing_rate(y)
            features["zcr_mean"] = np.mean(zcr)
            
            # MFCC (음성 인식에 주로 사용되는 특징)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(mfccs.shape[0]):
                features[f"mfcc_{i+1}_mean"] = np.mean(mfccs[i])
            
            logger.info(f"추출된 특징 수: {len(features)}")
            return features
            
        except Exception as e:
            logger.error(f"특징 추출 오류: {str(e)}")
            return self._get_default_result()

    def evaluate_voice_quality(self, analysis_result):
        """음성 품질 평가"""
        if not analysis_result:
            return "분석 결과 없음"
        
        # 피치 안정성 평가
        pitch_std = analysis_result.get("pitch_std", 50)
        rms_mean = analysis_result.get("rms_mean", 0.3)
        zcr_mean = analysis_result.get("zcr_mean", 0.1)
        
        quality_score = 0
        quality_comments = []
        
        # 피치 안정성 (낮을수록 좋음)
        if pitch_std < 20:
            quality_score += 2
            quality_comments.append("피치가 매우 안정적")
        elif pitch_std < 40:
            quality_score += 1
            quality_comments.append("피치가 안정적")
        else:
            quality_comments.append("피치가 불안정")
        
        # 음성 에너지 (적절한 범위)
        if 0.1 < rms_mean < 0.5:
            quality_score += 2
            quality_comments.append("적절한 음성 크기")
        elif 0.05 < rms_mean <= 0.1 or 0.5 <= rms_mean < 0.8:
            quality_score += 1
            quality_comments.append("음성 크기 양호")
        else:
            quality_comments.append("음성 크기 조절 필요")
        
        # 제로 크로싱 레이트 (음성의 명료성)
        if zcr_mean < 0.1:
            quality_score += 1
            quality_comments.append("명료한 발음")
        
        # 종합 평가
        if quality_score >= 4:
            overall = "우수한 음성 품질"
        elif quality_score >= 2:
            overall = "양호한 음성 품질"
        else:
            overall = "음성 품질 개선 필요"
        
        return f"{overall} ({', '.join(quality_comments)})"

    def calculate_voice_scores(self, analysis_result):
        """음성 관련 점수 계산"""
        if not analysis_result:
            return {
                "voice_score": 1.0,
                "voice_feedback": "음성 분석 불가"
            }
        
        pitch_std = analysis_result.get("pitch_std", 50)
        rms_mean = analysis_result.get("rms_mean", 0.3)
        tempo = analysis_result.get("tempo", 120)
        
        # 기본 점수 3.0에서 시작
        voice_score = 3.0
        
        # 피치 안정성 반영 (낮을수록 좋음)
        if pitch_std < 30:
            voice_score += 1.0
        elif pitch_std < 50:
            voice_score += 0.5
        
        # 음성 에너지 반영
        if 0.1 < rms_mean < 0.5:
            voice_score += 0.5
        
        # 템포 반영 (적절한 범위)
        if 100 < tempo < 140:
            voice_score += 0.5
        
        # 최대 5.0으로 제한
        voice_score = min(5.0, voice_score)
        
        # 피드백 생성
        if voice_score >= 4.0:
            feedback = "목소리: 매우 안정적이고 명확함"
        elif voice_score >= 3.5:
            feedback = "목소리: 안정적"
        elif voice_score >= 3.0:
            feedback = "목소리: 보통"
        else:
            feedback = "목소리: 개선 필요"
        
        return {
            "voice_score": voice_score,
            "voice_feedback": feedback
        }

    def _get_default_result(self):
        """테스트용 기본 결과값"""
        return {
            "pitch_mean": 150.0,
            "pitch_std": 30.0,
            "pitch_min": 100.0,
            "pitch_max": 200.0,
            "rms_mean": 0.2,
            "rms_std": 0.05,
            "spectral_centroid_mean": 2000.0,
            "tempo": 120.0,
            "zcr_mean": 0.08
        }

    def get_module_status(self):
        """모듈 상태 정보 반환"""
        return {
            "module_name": "Librosa",
            "is_available": self.is_available,
            "sample_rate": self.sample_rate,
            "functions": ["analyze_audio", "analyze_video_audio", "evaluate_voice_quality", "calculate_voice_scores"]
        }
