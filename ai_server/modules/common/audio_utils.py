"""
오디오 관련 유틸리티 함수
오디오 파일 처리, 변환, 분석 등의 기능 제공
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def extract_audio_from_video(video_path: str) -> Optional[str]:
    """
    비디오에서 오디오 추출
    
    Args:
        video_path: 비디오 파일 경로
        
    Returns:
        Optional[str]: 추출된 오디오 파일 경로 또는 None
    """
    try:
        import subprocess
        
        # 임시 오디오 파일 경로
        audio_path = video_path.replace('.mp4', '_audio.wav').replace('.webm', '_audio.wav')
        
        # FFmpeg를 사용한 오디오 추출
        command = [
            'ffmpeg', '-i', video_path, '-acodec', 'pcm_s16le', 
            '-ac', '1', '-ar', '16000', audio_path, '-y'
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        
        if os.path.exists(audio_path):
            return audio_path
        else:
            return None
            
    except Exception as e:
        logger.error(f"오디오 추출 오류: {str(e)}")
        return None

def process_audio_with_librosa(audio_path: str) -> Dict[str, Any]:
    """
    Librosa를 사용한 오디오 분석
    
    Args:
        audio_path: 오디오 파일 경로
        
    Returns:
        Dict[str, Any]: 분석 결과
    """
    try:
        import librosa
        
        y, sr = librosa.load(audio_path)
        
        # 기본 음성 특성 추출
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
        
        # 평균값 계산
        analysis_result = {
            "mfcc_mean": float(mfccs.mean()),
            "spectral_centroid_mean": float(spectral_centroids.mean()),
            "spectral_rolloff_mean": float(spectral_rolloff.mean()),
            "zero_crossing_rate_mean": float(zero_crossing_rate.mean()),
            "duration": float(len(y) / sr),
            "sample_rate": int(sr),
            "voice_stability": min(1.0, max(0.0, 1.0 - abs(spectral_centroids.std() / spectral_centroids.mean()))),
            "speaking_rate_wpm": estimate_speaking_rate(y, sr),
            "volume_consistency": calculate_volume_consistency(y),
            "fluency_score": calculate_fluency_score(y, sr)
        }
        
        return analysis_result
        
    except ImportError:
        logger.error("Librosa 모듈을 사용할 수 없습니다.")
        return {"error": "Librosa 모듈을 사용할 수 없습니다."}
    except Exception as e:
        logger.error(f"Librosa 오디오 분석 오류: {str(e)}")
        return {"error": f"오디오 분석 실패: {str(e)}"}

def estimate_speaking_rate(audio_data, sample_rate):
    """
    말하기 속도 추정 (단위: WPM)
    
    Args:
        audio_data: 오디오 데이터
        sample_rate: 샘플링 레이트
        
    Returns:
        float: 추정된 말하기 속도 (WPM)
    """
    try:
        import librosa
        
        # 간단한 음성 활동 감지
        frame_length = int(0.025 * sample_rate)  # 25ms
        hop_length = int(0.01 * sample_rate)     # 10ms
        
        # 에너지 기반 음성 활동 감지
        energy = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
        energy_threshold = energy.mean() * 0.3
        
        # 음성 구간 계산
        speech_frames = len(energy[energy > energy_threshold])
        speech_duration = speech_frames * hop_length / sample_rate
        
        # 대략적인 WPM 계산 (평균 한국어 음절/단어 비율 고려)
        estimated_wpm = max(60, min(200, (speech_duration / 60) * 150))
        
        return estimated_wpm
        
    except Exception:
        return 120  # 기본값

def calculate_volume_consistency(audio_data):
    """
    음량 일관성 계산
    
    Args:
        audio_data: 오디오 데이터
        
    Returns:
        float: 음량 일관성 점수 (0-1)
    """
    try:
        import librosa
        
        # RMS 에너지 계산
        frame_length = 2048
        hop_length = 512
        rms_energy = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
        
        # 표준편차 기반 일관성 점수
        consistency = 1.0 - min(1.0, rms_energy.std() / (rms_energy.mean() + 1e-8))
        return max(0.0, consistency)
        
    except Exception:
        return 0.5  # 기본값

def calculate_fluency_score(audio_data, sample_rate):
    """
    발화 유창성 점수 계산
    
    Args:
        audio_data: 오디오 데이터
        sample_rate: 샘플링 레이트
        
    Returns:
        float: 유창성 점수 (0-1)
    """
    try:
        import librosa
        
        # 무음 구간 감지
        frame_length = int(0.025 * sample_rate)
        hop_length = int(0.01 * sample_rate)
        
        energy = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
        silence_threshold = energy.mean() * 0.1
        
        # 무음 구간 비율 계산
        silence_ratio = len(energy[energy < silence_threshold]) / len(energy)
        
        # 유창성 점수 (무음이 적을수록 높은 점수)
        fluency_score = 1.0 - min(1.0, silence_ratio * 2)
        return max(0.0, fluency_score)
        
    except Exception:
        return 0.5  # 기본값

def transcribe_with_whisper(audio_path: str, language: str = "ko") -> Dict[str, Any]:
    """
    Whisper를 사용한 음성 인식
    
    Args:
        audio_path: 오디오 파일 경로
        language: 언어 코드 (기본값: "ko")
        
    Returns:
        Dict[str, Any]: 인식 결과
    """
    try:
        import whisper
        
        # Whisper 모델 로드
        model = whisper.load_model("base")
        
        # 음성 인식
        result = model.transcribe(audio_path, language=language)
        
        return {
            "text": result["text"],
            "language": result["language"],
            "segments": result["segments"][:3],  # 처음 3개 세그먼트만
            "confidence": calculate_transcription_confidence(result)
        }
        
    except ImportError:
        logger.error("Whisper 모듈을 사용할 수 없습니다.")
        return {"error": "Whisper 모듈을 사용할 수 없습니다."}
    except Exception as e:
        logger.error(f"Whisper 음성 인식 오류: {str(e)}")
        return {"error": f"음성 인식 실패: {str(e)}"}

def calculate_transcription_confidence(whisper_result):
    """
    Whisper 결과의 신뢰도 계산
    
    Args:
        whisper_result: Whisper 인식 결과
        
    Returns:
        float: 신뢰도 점수 (0-1)
    """
    try:
        if "segments" in whisper_result and whisper_result["segments"]:
            # 세그먼트별 평균 신뢰도 계산
            total_confidence = 0
            total_segments = 0
            
            for segment in whisper_result["segments"]:
                if "avg_logprob" in segment:
                    # logprob를 0-1 범위로 변환
                    confidence = max(0, min(1, (segment["avg_logprob"] + 1) / 1))
                    total_confidence += confidence
                    total_segments += 1
            
            if total_segments > 0:
                return total_confidence / total_segments
        
        return 0.75  # 기본 신뢰도
        
    except Exception:
        return 0.75
