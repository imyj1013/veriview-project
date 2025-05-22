"""
음성 특징 고급 분석 모듈
Librosa를 활용한 상세 음성 평가
"""

import numpy as np
import librosa
import logging

logger = logging.getLogger(__name__)

class AdvancedVoiceAnalyzer:
    """고급 음성 분석기"""
    
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        
    def analyze_voice_comprehensive(self, audio_path):
        """종합적인 음성 분석"""
        try:
            # 오디오 로드
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # 기본 특징
            basic_features = self._extract_basic_features(y, sr)
            
            # 고급 특징
            advanced_features = self._extract_advanced_features(y, sr)
            
            # 감정 특징
            emotion_features = self._extract_emotion_features(y, sr)
            
            # 말하기 패턴
            speech_patterns = self._analyze_speech_patterns(y, sr)
            
            return {
                **basic_features,
                **advanced_features,
                **emotion_features,
                **speech_patterns
            }
            
        except Exception as e:
            logger.error(f"음성 분석 오류: {str(e)}")
            return self._get_default_features()
    
    def _extract_basic_features(self, y, sr):
        """기본 음성 특징 추출"""
        # 피치 (F0)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        pitch_mean = np.mean(pitch_values) if pitch_values else 0
        pitch_std = np.std(pitch_values) if pitch_values else 0
        
        # 에너지 (RMS)
        rms = librosa.feature.rms(y=y)[0]
        rms_mean = np.mean(rms)
        rms_std = np.std(rms)
        
        # 템포
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        return {
            "pitch_mean": pitch_mean,
            "pitch_std": pitch_std,
            "pitch_range": max(pitch_values) - min(pitch_values) if pitch_values else 0,
            "rms_mean": rms_mean,
            "rms_std": rms_std,
            "tempo": tempo
        }
    
    def _extract_advanced_features(self, y, sr):
        """고급 음성 특징 추출"""
        # Spectral Centroid (음색의 밝기)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        # Zero Crossing Rate (음성의 부드러움)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        
        # MFCC (음성 특징)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # Spectral Rolloff
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        return {
            "spectral_centroid_mean": np.mean(spectral_centroids),
            "spectral_centroid_std": np.std(spectral_centroids),
            "zcr_mean": np.mean(zcr),
            "zcr_std": np.std(zcr),
            "mfcc_mean": np.mean(mfccs, axis=1).tolist(),
            "spectral_rolloff_mean": np.mean(rolloff)
        }
    
    def _extract_emotion_features(self, y, sr):
        """감정 관련 음성 특징 추출"""
        # 음성 진폭의 변화 (감정 강도)
        amplitude_envelope = np.abs(y)
        amplitude_variation = np.std(amplitude_envelope)
        
        # 스펙트럼 대비 (음성의 명확성)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        
        # 하모닉 성분 (음성의 안정성)
        harmonic, percussive = librosa.effects.hpss(y)
        harmonic_ratio = np.sum(np.abs(harmonic)) / (np.sum(np.abs(y)) + 1e-6)
        
        return {
            "amplitude_variation": amplitude_variation,
            "spectral_contrast_mean": np.mean(spectral_contrast),
            "harmonic_ratio": harmonic_ratio,
            "emotional_intensity": amplitude_variation * harmonic_ratio
        }
    
    def _analyze_speech_patterns(self, y, sr):
        """말하기 패턴 분석"""
        # 음성 활동 감지 (VAD)
        energy = librosa.feature.rms(y=y)[0]
        threshold = np.mean(energy) * 0.5
        speech_frames = energy > threshold
        
        # 발화 구간과 침묵 구간 분석
        speech_ratio = np.sum(speech_frames) / len(speech_frames)
        
        # 침묵 구간 길이 분석
        silence_lengths = []
        current_silence = 0
        for is_speech in speech_frames:
            if not is_speech:
                current_silence += 1
            elif current_silence > 0:
                silence_lengths.append(current_silence)
                current_silence = 0
        
        avg_silence_length = np.mean(silence_lengths) if silence_lengths else 0
        silence_variation = np.std(silence_lengths) if silence_lengths else 0
        
        # 발화 속도 변화
        hop_length = 512
        frame_duration = hop_length / sr
        speaking_rate_variation = np.std(energy[speech_frames]) if any(speech_frames) else 0
        
        return {
            "speech_ratio": speech_ratio,
            "avg_silence_length": avg_silence_length * frame_duration,
            "silence_variation": silence_variation * frame_duration,
            "speaking_rate_variation": speaking_rate_variation,
            "pause_frequency": len(silence_lengths) / (len(y) / sr)  # 초당 pause 횟수
        }
    
    def _get_default_features(self):
        """기본값 반환"""
        return {
            "pitch_mean": 150,
            "pitch_std": 30,
            "pitch_range": 100,
            "rms_mean": 0.3,
            "rms_std": 0.1,
            "tempo": 120,
            "spectral_centroid_mean": 2000,
            "spectral_centroid_std": 500,
            "zcr_mean": 0.05,
            "zcr_std": 0.02,
            "mfcc_mean": [0] * 13,
            "spectral_rolloff_mean": 3000,
            "amplitude_variation": 0.2,
            "spectral_contrast_mean": 20,
            "harmonic_ratio": 0.7,
            "emotional_intensity": 0.14,
            "speech_ratio": 0.8,
            "avg_silence_length": 0.5,
            "silence_variation": 0.2,
            "speaking_rate_variation": 0.1,
            "pause_frequency": 2
        }

def evaluate_voice_performance(voice_features):
    """음성 특징으로부터 평가 점수 계산"""
    scores = {}
    
    # 1. 음성 안정성 (pitch 변화가 적고 일정)
    pitch_stability = max(0, 1 - (voice_features["pitch_std"] / 100))
    scores["stability"] = pitch_stability
    
    # 2. 명확성 (적절한 spectral centroid, 높은 harmonic ratio)
    clarity = min(1, voice_features["spectral_centroid_mean"] / 3000) * voice_features["harmonic_ratio"]
    scores["clarity"] = clarity
    
    # 3. 에너지/열정 (적절한 RMS, 감정 강도)
    energy_score = min(1, voice_features["rms_mean"] / 0.4) * (1 + voice_features["emotional_intensity"])
    scores["energy"] = min(1, energy_score)
    
    # 4. 속도 적절성 (템포 100-140 BPM이 이상적)
    tempo = voice_features["tempo"]
    if 100 <= tempo <= 140:
        pace_score = 1.0
    elif 90 <= tempo <= 150:
        pace_score = 0.7
    else:
        pace_score = 0.4
    scores["pace"] = pace_score
    
    # 5. 유창성 (발화 비율 높고, 침묵 변화 적음)
    fluency = voice_features["speech_ratio"] * (1 - min(1, voice_features["silence_variation"]))
    scores["fluency"] = fluency
    
    return scores

def generate_voice_feedback(voice_features, voice_scores):
    """음성 분석 기반 상세 피드백 생성"""
    feedback = []
    
    # 안정성 피드백
    if voice_scores["stability"] > 0.7:
        feedback.append("목소리가 매우 안정적입니다. 신뢰감을 주는 톤입니다.")
    elif voice_scores["stability"] > 0.5:
        feedback.append("목소리가 대체로 안정적이나, 조금 더 일정한 톤을 유지해보세요.")
    else:
        feedback.append("목소리의 떨림이 감지됩니다. 심호흡을 하고 편안하게 말해보세요.")
    
    # 명확성 피드백
    if voice_scores["clarity"] > 0.7:
        feedback.append("발음이 명확하고 전달력이 좋습니다.")
    else:
        feedback.append("발음을 더 또렷하게 하면 전달력이 향상될 것입니다.")
    
    # 에너지 피드백
    if voice_scores["energy"] > 0.8:
        feedback.append("열정적이고 활기찬 목소리입니다.")
    elif voice_scores["energy"] > 0.5:
        feedback.append("적절한 에너지 레벨입니다.")
    else:
        feedback.append("조금 더 활기차게 말해보세요. 목소리에 힘을 실어보세요.")
    
    # 속도 피드백
    if voice_scores["pace"] > 0.9:
        feedback.append("말하는 속도가 적절합니다.")
    elif voice_scores["pace"] > 0.6:
        feedback.append("말하는 속도가 약간 빠르거나 느립니다. 조절해보세요.")
    else:
        feedback.append("말하는 속도가 너무 빠르거나 느립니다. 적절한 속도를 유지하세요.")
    
    # 유창성 피드백
    if voice_features["pause_frequency"] > 5:
        feedback.append("말을 자주 멈추는 편입니다. 더 유창하게 이어서 말해보세요.")
    elif voice_features["avg_silence_length"] > 1:
        feedback.append("침묵 구간이 깁니다. 생각을 정리하되 너무 오래 멈추지 마세요.")
    
    return feedback
