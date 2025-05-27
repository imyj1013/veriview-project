#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper 모듈 - 음성 인식 및 전사
OpenAI Whisper를 사용한 고품질 음성-텍스트 변환
"""
import logging
import time
import os
import tempfile
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger(__name__)

class WhisperModule:
    def __init__(self, model_size: str = "base", language: str = "ko"):
        """
        Whisper 모듈 초기화
        
        Args:
            model_size: 모델 크기 (tiny, base, small, medium, large)
            language: 주 언어 (ko, en, auto 등)
        """
        self.model_size = model_size
        self.language = language
        self.model = None
        self.available = False
        
        try:
            self._initialize_whisper()
            self.available = True
            logger.info(f"Whisper 모듈 초기화 성공: {model_size} 모델, 언어: {language}")
        except Exception as e:
            logger.error(f"Whisper 모듈 초기화 실패: {str(e)}")
            self.available = False
    
    def _initialize_whisper(self):
        """Whisper 모델 초기화"""
        try:
            import whisper
            self.whisper = whisper
            
            # 모델 로드
            self.model = whisper.load_model(self.model_size)
            logger.info(f"Whisper {self.model_size} 모델 로드 완료")
            
        except ImportError:
            raise ImportError("Whisper 라이브러리가 설치되지 않았습니다. 'pip install openai-whisper' 실행해주세요.")
        except Exception as e:
            raise RuntimeError(f"Whisper 모델 로드 실패: {str(e)}")
    
    def is_available(self) -> bool:
        """Whisper 모듈 사용 가능 여부 확인"""
        return self.available and self.model is not None
    
    def transcribe_audio(self, audio_path: str, language: str = None, 
                        with_timestamps: bool = True) -> Dict[str, Any]:
        """
        오디오 파일을 텍스트로 변환
        
        Args:
            audio_path: 오디오 파일 경로
            language: 언어 코드 (None이면 기본값 사용)
            with_timestamps: 타임스탬프 포함 여부
            
        Returns:
            Dict containing transcription results
        """
        if not self.available:
            return {"error": "Whisper 모듈을 사용할 수 없습니다."}
        
        if not os.path.exists(audio_path):
            return {"error": f"오디오 파일이 존재하지 않습니다: {audio_path}"}
        
        try:
            # 언어 설정
            target_language = language or self.language
            if target_language == "auto":
                target_language = None  # Whisper가 자동 감지
            
            # Whisper 실행
            start_time = time.time()
            
            result = self.model.transcribe(
                audio_path,
                language=target_language,
                verbose=False,
                word_timestamps=with_timestamps
            )
            
            processing_time = time.time() - start_time
            
            # 결과 분석 및 구조화
            transcription_result = {
                "success": True,
                "text": result["text"].strip(),
                "language": result["language"],
                "processing_time": round(processing_time, 2),
                "confidence": self._calculate_confidence(result),
                "word_count": len(result["text"].split()),
                "duration": self._get_audio_duration(result),
                "segments": self._process_segments(result.get("segments", [])),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "quality_metrics": self._analyze_transcription_quality(result)
            }
            
            # 추가 분석
            if with_timestamps and result.get("segments"):
                transcription_result["speaking_analysis"] = self._analyze_speaking_pattern(result["segments"])
            
            return transcription_result
            
        except Exception as e:
            logger.error(f"음성 인식 오류: {str(e)}")
            return {
                "success": False,
                "error": f"음성 인식 실패: {str(e)}",
                "audio_path": audio_path
            }
    
    def transcribe_video(self, video_path: str, extract_audio: bool = True, 
                        language: str = None) -> Dict[str, Any]:
        """
        비디오 파일에서 오디오를 추출하여 텍스트로 변환
        
        Args:
            video_path: 비디오 파일 경로
            extract_audio: 오디오 추출 여부
            language: 언어 코드
            
        Returns:
            Dict containing transcription results
        """
        if not self.available:
            return {"error": "Whisper 모듈을 사용할 수 없습니다."}
        
        if not os.path.exists(video_path):
            return {"error": f"비디오 파일이 존재하지 않습니다: {video_path}"}
        
        try:
            # 비디오에서 오디오 추출 (필요한 경우)
            if extract_audio:
                audio_path = self._extract_audio_from_video(video_path)
                if not audio_path:
                    return {"error": "비디오에서 오디오 추출 실패"}
            else:
                audio_path = video_path
            
            # 오디오 전사
            result = self.transcribe_audio(audio_path, language, with_timestamps=True)
            
            # 추가 정보
            if result.get("success"):
                result["source_type"] = "video"
                result["video_path"] = video_path
                if extract_audio and audio_path != video_path:
                    result["extracted_audio_path"] = audio_path
            
            # 임시 오디오 파일 정리
            if extract_audio and audio_path != video_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception as e:
                    logger.warning(f"임시 오디오 파일 삭제 실패: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"비디오 음성 인식 오류: {str(e)}")
            return {
                "success": False,
                "error": f"비디오 음성 인식 실패: {str(e)}",
                "video_path": video_path
            }
    
    def batch_transcribe(self, file_paths: List[str], language: str = None) -> List[Dict[str, Any]]:
        """
        여러 파일을 일괄 전사
        
        Args:
            file_paths: 파일 경로 리스트
            language: 언어 코드
            
        Returns:
            List of transcription results
        """
        if not self.available:
            return [{"error": "Whisper 모듈을 사용할 수 없습니다."}] * len(file_paths)
        
        results = []
        
        for i, file_path in enumerate(file_paths):
            logger.info(f"배치 처리 진행: {i+1}/{len(file_paths)} - {file_path}")
            
            try:
                if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                    result = self.transcribe_video(file_path, language=language)
                else:
                    result = self.transcribe_audio(file_path, language=language)
                
                result["batch_index"] = i
                results.append(result)
                
            except Exception as e:
                logger.error(f"배치 처리 오류 - {file_path}: {str(e)}")
                results.append({
                    "success": False,
                    "error": f"처리 실패: {str(e)}",
                    "file_path": file_path,
                    "batch_index": i
                })
        
        return results
    
    def _extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """비디오에서 오디오 추출"""
        try:
            import subprocess
            
            # 임시 오디오 파일 경로
            temp_audio = tempfile.mktemp(suffix=".wav")
            
            # FFmpeg를 사용한 오디오 추출
            command = [
                'ffmpeg', '-i', video_path, 
                '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000',
                '-y', temp_audio
            ]
            
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5분 타임아웃
            )
            
            if result.returncode == 0 and os.path.exists(temp_audio):
                return temp_audio
            else:
                logger.error(f"FFmpeg 오디오 추출 실패: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("오디오 추출 시간 초과")
            return None
        except Exception as e:
            logger.error(f"오디오 추출 오류: {str(e)}")
            return None
    
    def _calculate_confidence(self, whisper_result: Dict) -> float:
        """Whisper 결과의 신뢰도 계산"""
        try:
            segments = whisper_result.get("segments", [])
            if not segments:
                return 0.75  # 기본 신뢰도
            
            # 세그먼트별 평균 log 확률을 신뢰도로 변환
            total_logprob = 0
            total_tokens = 0
            
            for segment in segments:
                if "avg_logprob" in segment:
                    segment_tokens = len(segment.get("tokens", []))
                    total_logprob += segment["avg_logprob"] * segment_tokens
                    total_tokens += segment_tokens
            
            if total_tokens > 0:
                avg_logprob = total_logprob / total_tokens
                # log prob를 0-1 범위의 신뢰도로 변환
                confidence = max(0.0, min(1.0, (avg_logprob + 1) / 1))
                return round(confidence, 3)
            
            return 0.75
            
        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {str(e)}")
            return 0.75
    
    def _get_audio_duration(self, whisper_result: Dict) -> float:
        """오디오 지속 시간 계산"""
        try:
            segments = whisper_result.get("segments", [])
            if segments:
                last_segment = segments[-1]
                return round(last_segment.get("end", 0.0), 2)
            return 0.0
        except Exception:
            return 0.0
    
    def _process_segments(self, segments: List[Dict]) -> List[Dict[str, Any]]:
        """세그먼트 데이터 처리 및 정리"""
        processed_segments = []
        
        try:
            for i, segment in enumerate(segments[:10]):  # 처음 10개만 포함
                processed_segment = {
                    "id": segment.get("id", i),
                    "start": round(segment.get("start", 0.0), 2),
                    "end": round(segment.get("end", 0.0), 2),
                    "text": segment.get("text", "").strip(),
                    "avg_logprob": round(segment.get("avg_logprob", -1.0), 3),
                    "no_speech_prob": round(segment.get("no_speech_prob", 0.0), 3)
                }
                
                # 단어별 타임스탬프 (있는 경우)
                if "words" in segment:
                    processed_segment["words"] = [
                        {
                            "start": round(word.get("start", 0.0), 2),
                            "end": round(word.get("end", 0.0), 2),
                            "word": word.get("word", ""),
                            "probability": round(word.get("probability", 0.0), 3)
                        }
                        for word in segment["words"][:20]  # 최대 20개 단어
                    ]
                
                processed_segments.append(processed_segment)
                
        except Exception as e:
            logger.error(f"세그먼트 처리 오류: {str(e)}")
        
        return processed_segments
    
    def _analyze_transcription_quality(self, whisper_result: Dict) -> Dict[str, Any]:
        """전사 품질 분석"""
        try:
            segments = whisper_result.get("segments", [])
            
            if not segments:
                return {"overall_quality": "보통", "analysis": "세그먼트 데이터 없음"}
            
            # 품질 지표 계산
            avg_logprob_values = [s.get("avg_logprob", -1.0) for s in segments]
            no_speech_prob_values = [s.get("no_speech_prob", 0.0) for s in segments]
            
            avg_logprob = np.mean(avg_logprob_values)
            avg_no_speech_prob = np.mean(no_speech_prob_values)
            
            # 품질 등급 결정
            if avg_logprob > -0.5 and avg_no_speech_prob < 0.3:
                quality = "우수"
            elif avg_logprob > -1.0 and avg_no_speech_prob < 0.5:
                quality = "양호"
            elif avg_logprob > -1.5 and avg_no_speech_prob < 0.7:
                quality = "보통"
            else:
                quality = "개선필요"
            
            return {
                "overall_quality": quality,
                "avg_logprob": round(avg_logprob, 3),
                "avg_no_speech_prob": round(avg_no_speech_prob, 3),
                "segment_count": len(segments),
                "analysis": self._generate_quality_analysis(quality, avg_logprob, avg_no_speech_prob)
            }
            
        except Exception as e:
            logger.error(f"품질 분석 오류: {str(e)}")
            return {"overall_quality": "알 수 없음", "analysis": "품질 분석 실패"}
    
    def _generate_quality_analysis(self, quality: str, avg_logprob: float, no_speech_prob: float) -> str:
        """품질 분석 텍스트 생성"""
        analysis_parts = []
        
        if quality == "우수":
            analysis_parts.append("음성 인식 품질이 매우 우수합니다")
        elif quality == "양호":
            analysis_parts.append("음성 인식 품질이 양호합니다")
        elif quality == "보통":
            analysis_parts.append("음성 인식 품질이 보통입니다")
        else:
            analysis_parts.append("음성 품질 개선이 필요합니다")
        
        if no_speech_prob > 0.5:
            analysis_parts.append("무음 구간이 다소 많습니다")
        elif no_speech_prob < 0.2:
            analysis_parts.append("연속적인 발화로 인식되었습니다")
        
        if avg_logprob < -1.5:
            analysis_parts.append("일부 구간에서 인식 정확도가 낮을 수 있습니다")
        
        return ". ".join(analysis_parts) + "."
    
    def _analyze_speaking_pattern(self, segments: List[Dict]) -> Dict[str, Any]:
        """발화 패턴 분석"""
        try:
            if not segments:
                return {"analysis": "분석할 세그먼트가 없습니다"}
            
            # 발화 속도 계산 (단어/분)
            total_duration = 0
            total_words = 0
            pause_count = 0
            long_pauses = 0
            
            for i, segment in enumerate(segments):
                duration = segment.get("end", 0) - segment.get("start", 0)
                words = len(segment.get("text", "").split())
                
                total_duration += duration
                total_words += words
                
                # 다음 세그먼트와의 간격 계산 (무음 구간)
                if i < len(segments) - 1:
                    next_segment = segments[i + 1]
                    gap = next_segment.get("start", 0) - segment.get("end", 0)
                    
                    if gap > 0.5:  # 0.5초 이상 무음
                        pause_count += 1
                        if gap > 2.0:  # 2초 이상 긴 무음
                            long_pauses += 1
            
            # 발화 속도 (WPM: Words Per Minute)
            speaking_rate = (total_words / (total_duration / 60)) if total_duration > 0 else 0
            
            # 무음 비율
            pause_ratio = pause_count / len(segments) if segments else 0
            
            # 패턴 분석
            pattern_analysis = {
                "speaking_rate_wpm": round(speaking_rate, 1),
                "total_duration": round(total_duration, 2),
                "total_words": total_words,
                "pause_count": pause_count,
                "long_pause_count": long_pauses,
                "pause_ratio": round(pause_ratio, 3),
                "fluency_assessment": self._assess_fluency(speaking_rate, pause_ratio, long_pauses)
            }
            
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"발화 패턴 분석 오류: {str(e)}")
            return {"analysis": "발화 패턴 분석 실패"}
    
    def _assess_fluency(self, speaking_rate: float, pause_ratio: float, long_pauses: int) -> str:
        """유창성 평가"""
        try:
            # 한국어 기준 적정 발화 속도: 120-180 WPM
            if 120 <= speaking_rate <= 180 and pause_ratio < 0.3 and long_pauses <= 2:
                return "유창함"
            elif 90 <= speaking_rate <= 220 and pause_ratio < 0.5 and long_pauses <= 4:
                return "보통"
            elif speaking_rate < 60 or pause_ratio > 0.6 or long_pauses > 5:
                return "느림/끊김"
            elif speaking_rate > 250:
                return "매우 빠름"
            else:
                return "개선 필요"
                
        except Exception:
            return "평가 불가"
    
    def get_supported_languages(self) -> List[str]:
        """지원되는 언어 목록 반환"""
        if not self.available:
            return []
        
        try:
            # Whisper에서 지원하는 주요 언어들
            return [
                "ko",  # 한국어
                "en",  # 영어
                "ja",  # 일본어
                "zh",  # 중국어
                "es",  # 스페인어
                "fr",  # 프랑스어
                "de",  # 독일어
                "it",  # 이탈리아어
                "pt",  # 포르투갈어
                "ru",  # 러시아어
                "ar",  # 아랍어
                "hi",  # 힌디어
                "th",  # 태국어
                "vi"   # 베트남어
            ]
        except Exception:
            return ["ko", "en"]
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        return {
            "model_size": self.model_size,
            "default_language": self.language,
            "available": self.available,
            "supported_languages": self.get_supported_languages(),
            "model_parameters": self._get_model_parameters()
        }
    
    def _get_model_parameters(self) -> Dict[str, Any]:
        """모델 파라미터 정보"""
        model_specs = {
            "tiny": {"parameters": "39M", "speed": "매우 빠름", "accuracy": "낮음"},
            "base": {"parameters": "74M", "speed": "빠름", "accuracy": "보통"},
            "small": {"parameters": "244M", "speed": "보통", "accuracy": "양호"},
            "medium": {"parameters": "769M", "speed": "느림", "accuracy": "좋음"},
            "large": {"parameters": "1550M", "speed": "매우 느림", "accuracy": "매우 좋음"}
        }
        
        return model_specs.get(self.model_size, {"parameters": "알 수 없음", "speed": "알 수 없음", "accuracy": "알 수 없음"})

# 편의를 위한 함수들
def create_whisper_module(model_size: str = "base", language: str = "ko") -> WhisperModule:
    """Whisper 모듈 생성 팩토리 함수"""
    return WhisperModule(model_size, language)

def is_whisper_available() -> bool:
    """Whisper 모듈 사용 가능 여부 확인"""
    try:
        test_module = WhisperModule()
        return test_module.is_available()
    except Exception:
        return False

def transcribe_file(file_path: str, model_size: str = "base", language: str = "ko") -> Dict[str, Any]:
    """단일 파일 전사 편의 함수"""
    try:
        whisper_module = create_whisper_module(model_size, language)
        
        if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            return whisper_module.transcribe_video(file_path)
        else:
            return whisper_module.transcribe_audio(file_path)
            
    except Exception as e:
        return {"success": False, "error": f"파일 전사 실패: {str(e)}"}
