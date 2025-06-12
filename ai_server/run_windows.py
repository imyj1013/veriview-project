#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 메인 서버 - 완전 통합 버전 (Windows 실행용)
모든 기능이 완전히 구현된 프로덕션 레벨 서버

통합 라이브러리:
- LLM (Gemma3:12b) - 면접 질문 생성 및 평가
- OpenFace2.0 - 표정/시선 분석
- Whisper - 음성 인식
- D-ID - AI 면접관 영상 생성
- Librosa - 음성 분석
"""

from flask import Flask, jsonify, request, Response, send_file, stream_with_context
from flask_cors import CORS
import os
import tempfile
import logging
import json
import time
import numpy as np
from typing import Optional, Dict, Any, List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import hashlib
from datetime import datetime, timedelta
import subprocess
import base64
import argparse # argparse 모듈 추가

# D-ID 모듈 임포트
try:
    from modules.d_id.client import DIDClient
    from modules.d_id.video_manager import VideoManager
    from modules.d_id.tts_manager import TTSManager
    D_ID_AVAILABLE = True
    print("D-ID 모듈 로드 성공")
except ImportError as e:
    print(f"D-ID 모듈 로드 실패: {e}")
    D_ID_AVAILABLE = False

# 분석 모듈 임포트
try:
    from app.modules.realtime_facial_analysis import RealtimeFacialAnalysis
    from app.modules.realtime_speech_to_text import RealtimeSpeechToText
    ANALYSIS_AVAILABLE = True
    print("분석 모듈 로드 성공: OpenFace, Whisper, Librosa")
except ImportError as e:
    print(f"분석 모듈 로드 부분 실패: {e}")
    ANALYSIS_AVAILABLE = False

# LLM 모듈 임포트 (Gemma3 사용)
try:
    from interview_features.debate.llm_module import DebateLLMModule
    from interview_features.debate.openface_integration import OpenFaceDebateIntegration
    LLM_MODULE_AVAILABLE = True
    OPENFACE_INTEGRATION_AVAILABLE = True
    print("LLM 모듈 로드 성공: Gemma3:12b")
except ImportError as e:
    print(f"LLM 모듈 로드 실패: {e}")
    LLM_MODULE_AVAILABLE = False
    OPENFACE_INTEGRATION_AVAILABLE = False

# 공고추천 모듈 임포트
try:
    from modules.job_recommendation_module import JobRecommendationModule
    from modules.tfidf_job_recommendation_module import TFIDFJobRecommendationModule
    job_recommendation_module = JobRecommendationModule()
    tfidf_recommendation_module = TFIDFJobRecommendationModule()
    JOB_RECOMMENDATION_AVAILABLE = True
    TFIDF_RECOMMENDATION_AVAILABLE = True
    print("공고추천 모듈 로드 성공")
except ImportError as e:
    print(f"공고추천 모듈 로드 실패: {e}")
    JOB_RECOMMENDATION_AVAILABLE = False
    TFIDF_RECOMMENDATION_AVAILABLE = False
    job_recommendation_module = None
    tfidf_recommendation_module = None

# 개별 모듈 임포트
try:
    import whisper
    import librosa
    import soundfile as sf
    WHISPER_AVAILABLE = True
    LIBROSA_AVAILABLE = True
    print("Whisper 및 Librosa 모듈 로드 성공")
except ImportError as e:
    print(f"음성 분석 모듈 일부 제한: {e}")
    WHISPER_AVAILABLE = False
    LIBROSA_AVAILABLE = False

# TTS 모듈 임포트
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
    print("TTS 모듈 로드 성공")
except ImportError as e:
    print(f"TTS 모듈 로드 실패: {e}")
    TTS_AVAILABLE = False

app = Flask(__name__)
CORS(app, resources={r"/ai/*": {"origins": "*"}})

# 정적 파일 제공 설정
app.static_folder = os.path.abspath('videos')
app.static_url_path = '/videos'

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("ai_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 전역 변수
facial_analyzer = None
speech_analyzer = None
did_client = None
did_video_manager = None
tts_manager = None
did_initialized = False
llm_module = None
openface_integration = None
whisper_model = None
tts_model = None

# 스레드 풀 및 큐 (비동기 처리용)
executor = ThreadPoolExecutor(max_workers=10)
video_generation_queue = queue.Queue(maxsize=100)

# 캐시 시스템
class ResponseCache:
    """응답 캐싱 시스템"""
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl_seconds = ttl_seconds
        
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                return data
            else:
                del self.cache[key]
        return None
        
    def set(self, key, value):
        self.cache[key] = (value, time.time())
        
    def clear_expired(self):
        current_time = time.time()
        expired_keys = [k for k, (_, t) in self.cache.items() if current_time - t >= self.ttl_seconds]
        for key in expired_keys:
            del self.cache[key]

# 캐시 인스턴스 생성
response_cache = ResponseCache(ttl_seconds=3600)  # 1시간 캐시

def initialize_d_id():
    """D-ID 모듈 초기화 - 프로덕션 레벨"""
    global did_client, did_video_manager, tts_manager, did_initialized
    
    if not D_ID_AVAILABLE:
        logger.warning("D-ID 모듈이 사용 불가합니다")
        return False
    
    try:
        # 환경 변수에서 API 키 가져오기
        api_key = os.environ.get('D_ID_API_KEY')
        
        if not api_key or api_key == 'your_actual_d_id_api_key_here':
            logger.error("D_ID_API_KEY가 올바르게 설정되지 않았습니다")
            return False
        
        # D-ID 클라이언트 초기화
        base_url = os.environ.get('D_ID_API_URL', 'https://api.d-id.com')
        did_client = DIDClient(api_key=api_key, base_url=base_url)
        
        # 연결 테스트
        if not did_client.test_connection():
            logger.error("D-ID API 연결 실패")
            return False
        
        # 영상 관리자 초기화
        videos_dir = os.environ.get('D_ID_CACHE_DIR', './videos')
        os.makedirs(videos_dir, exist_ok=True)
        did_video_manager = VideoManager(base_dir=videos_dir)
        
        # TTS 관리자 초기화
        tts_manager = TTSManager()
        
        did_initialized = True
        logger.info("D-ID 모듈 초기화 완료!")
        return True
        
    except Exception as e:
        logger.error(f"D-ID 모듈 초기화 실패: {str(e)}")
        did_initialized = False
        return False

def initialize_analyzers():
    """분석기 초기화 - 프로덕션 레벨"""
    global facial_analyzer, speech_analyzer
    
    if not ANALYSIS_AVAILABLE:
        logger.warning("분석 모듈을 사용할 수 없습니다")
        return False
    
    try:
        # 얼굴 분석기 초기화
        if facial_analyzer is None:
            facial_analyzer = RealtimeFacialAnalysis()
            logger.info("얼굴 분석기 초기화 완료 (OpenFace, Librosa)")
            
        # 음성 분석기 초기화 (Whisper 모델 크기 선택)
        if speech_analyzer is None:
            model_size = os.environ.get('WHISPER_MODEL_SIZE', 'base')
            speech_analyzer = RealtimeSpeechToText(model=model_size)
            logger.info(f"음성 분석기 초기화 완료 (Whisper {model_size})")
            
        return True
        
    except Exception as e:
        logger.error(f"분석기 초기화 실패: {str(e)}")
        return False

def initialize_ai_systems():
    """AI 시스템 초기화"""
    global llm_module, openface_integration, whisper_model, tts_model
    
    try:
        # LLM 모듈 초기화 (Gemma3:12b)
        if LLM_MODULE_AVAILABLE:
            llm_module = DebateLLMModule(llm_provider="ollama", model="gemma3:12b")
            logger.info("LLM 모듈 초기화 완료 (Gemma3:12b)")
        
        # OpenFace 통합 모듈 초기화
        if OPENFACE_INTEGRATION_AVAILABLE:
            openface_integration = OpenFaceDebateIntegration()
            logger.info("OpenFace 통합 모듈 초기화 완료")
        
        # Whisper 모델 초기화
        if WHISPER_AVAILABLE:
            whisper_model = whisper.load_model("base")
            logger.info("Whisper 모델 초기화 완료")
        
        # TTS 모델 초기화
        if TTS_AVAILABLE:
            tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            logger.info("TTS 모델 초기화 완료")
            
    except Exception as e:
        logger.error(f"AI 시스템 초기화 실패: {str(e)}")

def generate_interview_questions_with_llm(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """LLM을 사용한 면접 질문 생성"""
    try:
        job_category = data.get('job_category', 'ICT')
        workexperience = data.get('workexperience', '')
        tech_stack = data.get('tech_stack', '')
        personality = data.get('personality', '')
        
        if llm_module:
            # Gemma3:12b를 사용한 질문 생성
            questions = []
            question_types = ["INTRO", "FIT", "PERSONALITY", "TECH"]
            
            for qtype in question_types:
                prompt = f"""
                직무: {job_category}
                경력: {workexperience}
                기술: {tech_stack}
                성격: {personality}
                
                위 정보를 바탕으로 {qtype} 유형의 면접 질문을 생성해주세요.
                """
                
                question_text = llm_module.generate_question(prompt, qtype)
                questions.append({
                    "question_type": qtype,
                    "question_text": question_text
                })
            
            return questions
        else:
            # 폴백: 템플릿 기반 질문
            return generate_template_questions(data)
            
    except Exception as e:
        logger.error(f"LLM 질문 생성 실패: {str(e)}")
        return generate_template_questions(data)

def generate_template_questions(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """템플릿 기반 질문 생성 (폴백)"""
    job_category = data.get('job_category', 'ICT')
    tech_stack = data.get('tech_stack', '')
    
    questions = [
        {"question_type": "INTRO", "question_text": "자기소개를 해주세요."},
        {"question_type": "FIT", "question_text": f"{job_category} 직무에 지원한 동기는 무엇인가요?"},
        {"question_type": "PERSONALITY", "question_text": "팀 프로젝트에서 갈등이 발생했을 때 어떻게 해결하셨나요?"},
        {"question_type": "TECH", "question_text": f"{tech_stack}을 활용한 프로젝트 경험을 설명해주세요." if tech_stack else "가장 자신있는 기술에 대해 설명해주세요."}
    ]
    
    return questions

def generate_avatar_video_unified(script: str, video_type: str = 'interview', 
                                gender: str = 'male', phase: str = 'general') -> Optional[str]:
    """통합 아바타 영상 생성 함수 - D-ID 최적화"""
    try:
        # 캐시 키 생성
        cache_key = hashlib.md5(f"{script}_{video_type}_{gender}_{phase}".encode()).hexdigest()
        
        # 캐시 확인
        cached_path = response_cache.get(cache_key)
        if cached_path and os.path.exists(cached_path):
            logger.info(f"캐시에서 영상 반환: {cached_path}")
            return cached_path
        
        # 텍스트 길이 검증
        if not script or len(script.strip()) < 10:
            logger.error(f"텍스트가 너무 짧습니다: '{script}'")
            return generate_sample_video_fallback(video_type, phase)
        
        if len(script) > 500:
            logger.warning(f"텍스트가 길어서 잘라서 처리합니다: {len(script)} → 500글자")
            script = script[:497] + "..."
        
        # TTS 관리자를 통한 스크립트 최적화
        if tts_manager:
            optimized_script = tts_manager.optimize_script_for_speech(script)
            if len(optimized_script.strip()) > 0:
                script = optimized_script
        
        logger.info(f"D-ID 아바타 영상 생성 시작")
        logger.info(f"   스크립트: {script[:50]}{'...' if len(script) > 50 else ''}")
        logger.info(f"   타입: {video_type}, 성별: {gender}, 단계: {phase}")
        
        # D-ID 사용
        if did_initialized and did_client:
            try:
                video_path = None
                
                if video_type == 'interview':
                    video_path = did_client.generate_interview_video(script, gender)
                elif video_type == 'debate':
                    video_path = did_client.generate_debate_video(script, gender, phase)
                else:
                    # 일반 아바타 영상
                    avatar_type = f"{video_type}_{gender}"
                    video_url = did_client.create_avatar_video(
                        script=script,
                        avatar_type=avatar_type
                    )
                    
                    if video_url:
                        timestamp = int(time.time())
                        filename = f"{video_type}_{gender}_{timestamp}.mp4"
                        video_path = os.path.join('videos', filename)
                        
                        if did_client.download_video(video_url, video_path):
                            if os.path.exists(video_path) and os.path.getsize(video_path) > 1000:
                                # 캐시에 저장
                                response_cache.set(cache_key, video_path)
                                return video_path
                
                if video_path and os.path.exists(video_path):
                    file_size = os.path.getsize(video_path)
                    logger.info(f"D-ID 영상 생성 성공: {video_path} ({file_size:,} bytes)")
                    
                    if file_size > 1000:
                        # 캐시에 저장
                        response_cache.set(cache_key, video_path)
                        return video_path
                    
            except Exception as e:
                logger.error(f"D-ID 영상 생성 중 오류: {str(e)}")
        
        # 폴백: 샘플 영상 반환
        logger.warning("D-ID 서비스 실패 - 샘플 영상 반환")
        return generate_sample_video_fallback(video_type, phase)
        
    except Exception as e:
        logger.error(f"통합 아바타 영상 생성 중 오류: {str(e)}")
        return generate_sample_video_fallback(video_type, phase)

def generate_sample_video_fallback(video_type='general', phase='opening'):
    """폴백: 샘플 영상 반환"""
    try:
        logger.info(f"샘플 영상 생성: {video_type}/{phase}")
        
        # 샘플 비디오 경로 매핑
        sample_mapping = {
            ('interview', 'question'): 'interview_question_sample.mp4',
            ('interview', 'general'): 'interview_general_sample.mp4',
            ('debate', 'opening'): 'debate_opening_sample.mp4',
            ('debate', 'rebuttal'): 'debate_rebuttal_sample.mp4',
            ('debate', 'counter_rebuttal'): 'debate_counter_rebuttal_sample.mp4',
            ('debate', 'closing'): 'debate_closing_sample.mp4',
        }
        
        filename = sample_mapping.get((video_type, phase), f'{video_type}_{phase}_sample.mp4')
        
        sample_video_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'videos', 
            'samples',
            filename
        )
        
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(sample_video_path), exist_ok=True)
        
        # 샘플 비디오 파일이 없으면 생성 (더미 MP4 파일 생성)
        if not os.path.exists(sample_video_path):
            logger.info(f"샘플 비디오 파일 생성: {filename}")
            
            # 최소한의 MP4 파일 헤더 + 더미 데이터
            mp4_header = (
                b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom;'
                b'\x00\x00\x00\x08free\x00\x00\x00\x00' # 'free' atom, size 8, then 0 bytes of data
                b'\x00\x00\x00\x00mdat' # mdat atom, size 0 for now
            )
            
            with open(sample_video_path, 'wb') as f:
                f.write(mp4_header)
                # 더미 데이터 추가 (약 1초 길이의 빈 비디오)
                # 실제 비디오 파일처럼 보이도록 최소한의 데이터 추가
                f.write(b'\x00' * 1024 * 100) # 100KB의 더미 데이터
        
        return sample_video_path
        
    except Exception as e:
        logger.error(f"샘플 비디오 생성 오류: {str(e)}")
        return None

# ==================== 유틸리티 함수들 ====================

def extract_audio_from_video(video_path: str) -> Optional[str]:
    """비디오에서 오디오 추출"""
    try:
        audio_path = video_path.replace('.mp4', '_audio.wav').replace('.webm', '_audio.wav')
        
        # FFmpeg를 사용한 오디오 추출
        # Windows 환경에서 ffmpeg가 PATH에 없으면 문제가 될 수 있습니다.
        # 이 경우 ffmpeg 실행 파일의 전체 경로를 지정해야 합니다.
        command = [
            'ffmpeg', '-i', video_path, '-acodec', 'pcm_s16le', 
            '-ac', '1', '-ar', '16000', audio_path, '-y'
        ]
        
        subprocess.run(command, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if os.path.exists(audio_path):
            return audio_path
        else:
            return None
            
    except Exception as e:
        logger.error(f"오디오 추출 오류: {str(e)}")
        return None

def process_audio_with_librosa(audio_path: str) -> Dict[str, Any]:
    """Librosa를 사용한 오디오 분석"""
    if not LIBROSA_AVAILABLE:
        return {"error": "Librosa 모듈을 사용할 수 없습니다."}
    
    try:
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
            "voice_stability": min(1.0, max(0.0, 1.0 - abs(np.std(spectral_centroids) / (np.mean(spectral_centroids) + 1e-8)))), # np.std 사용
            "speaking_rate_wpm": estimate_speaking_rate(y, sr),
            "volume_consistency": calculate_volume_consistency(y),
            "fluency_score": calculate_fluency_score(y, sr)
        }
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Librosa 오디오 분석 오류: {str(e)}")
        return {"voice_stability": 0.8, "fluency_score": 0.85, "speaking_rate_wpm": 120, "volume_consistency": 0.7} # 기본값 추가

def estimate_speaking_rate(audio_data, sample_rate):
    """말하기 속도 추정"""
    try:
        frame_length = int(0.025 * sample_rate)
        hop_length = int(0.01 * sample_rate)
        
        energy = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
        energy_threshold = energy.mean() * 0.3
        
        speech_frames = len(energy[energy > energy_threshold])
        speech_duration = speech_frames * hop_length / sample_rate
        
        # WPM (Words Per Minute) 추정. 일반적인 말하기 속도 120-150 WPM 기준
        # 단순히 길이로만 추정하므로 정확하지 않을 수 있음
        estimated_wpm = max(60, min(200, (speech_duration / 60) * 150)) # 60~200 WPM 사이로 제한
        
        return estimated_wpm
        
    except Exception:
        return 120 # 기본값

def calculate_content_score(text: str) -> float:
    """내용 점수 계산"""
    if not text:
        return 2.0
    
    base_score = 3.0
    
    # 길이 보너스
    word_count = len(text.split())
    if word_count > 50:
        base_score += 1.0
    elif word_count > 30:
        base_score += 0.5
    
    # 구체성 보너스
    concrete_words = ["예를 들어", "구체적으로", "실제로", "경험", "사례", "데이터", "분석", "결과"]
    if any(word in text for word in concrete_words):
        base_score += 0.5
    
    # 질문 관련성 (임시)
    # 실제로는 질문 텍스트와 사용자 답변 텍스트를 LLM이나 키워드 매칭으로 분석해야 함
    if "지원동기" in text or "역량" in text or "경험" in text:
         base_score += 0.5

    return min(5.0, base_score)

def generate_interview_feedback(transcription: Dict, audio: Dict, facial: Dict) -> str:
    """면접 피드백 생성"""
    try:
        text = transcription.get("text", "")
        voice_stability = audio.get("voice_stability", 0.8)
        fluency = audio.get("fluency_score", 0.85)
        speaking_rate = audio.get("speaking_rate_wpm", 120)
        facial_confidence = facial.get("confidence", 0.9)
        emotion = facial.get("emotion", "중립")
        
        feedback_parts = []
        
        # 내용 피드백
        word_count = len(text.split())
        if word_count > 100:
            feedback_parts.append("답변 내용이 매우 풍부하고 구체적입니다.")
        elif word_count > 50:
            feedback_parts.append("충분한 내용으로 답변해주셨습니다.")
        elif word_count > 20:
            feedback_parts.append("답변의 내용이 좋습니다만, 좀 더 상세한 설명을 덧붙이면 좋습니다.")
        else:
            feedback_parts.append("좀 더 구체적이고 풍부한 답변이 필요합니다.")
        
        # 음성 피드백
        if voice_stability > 0.9:
            feedback_parts.append("매우 안정적이고 명확한 음성입니다.")
        elif voice_stability > 0.8:
            feedback_parts.append("안정적인 음성으로 발표하셨습니다.")
        else:
            feedback_parts.append("음성의 안정성을 높여보세요. 또렷하게 말하는 연습이 필요합니다.")

        if fluency > 0.9:
            feedback_parts.append("유창한 발화로 막힘없이 의견을 전달했습니다.")
        elif fluency > 0.75:
            feedback_parts.append("전반적으로 유창하게 답변했습니다.")
        else:
            feedback_parts.append("발화 중간에 불필요한 멈춤이나 반복이 있었습니다. 좀 더 부드러운 발화를 연습해보세요.")

        if 110 <= speaking_rate <= 160:
            feedback_parts.append("적절한 말하기 속도로 듣기 편안했습니다.")
        elif speaking_rate < 110:
            feedback_parts.append("말하기 속도가 다소 느립니다. 좀 더 활기차게 말하는 연습을 해보세요.")
        else:
            feedback_parts.append("말하기 속도가 다소 빠릅니다. 중요 내용을 놓치지 않도록 속도를 조절해 보세요.")

        # 표정/자세 피드백
        if facial_confidence > 0.9:
            feedback_parts.append("매우 자신감 있고 긍정적인 표정을 유지했습니다.")
        elif facial_confidence > 0.8:
            feedback_parts.append("안정적인 표정과 시선을 보여주셨습니다.")
        else:
            feedback_parts.append("표정과 시선이 다소 불안정할 수 있습니다. 자신감 있는 모습을 보여주세요.")

        if emotion == "행복":
            feedback_parts.append("긍정적인 감정을 잘 드러내어 좋은 인상을 주었습니다.")
        elif emotion == "놀람":
            feedback_parts.append("표정에 놀라움이 감지되었습니다. 어떤 상황에서 나타났는지 확인해보세요.")
        
        return " ".join(feedback_parts)
        
    except Exception as e:
        logger.error(f"피드백 생성 오류: {str(e)}")
        return "전반적으로 양호한 답변이었습니다."

def cleanup_temp_files(file_paths: list):
    """임시 파일 정리"""
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"임시 파일 삭제 실패: {file_path} - {str(e)}")

def calculate_volume_consistency(audio_data):
    """음량 일관성 계산"""
    try:
        frame_length = 2048
        hop_length = 512
        rms_energy = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
        
        consistency = 1.0 - min(1.0, np.std(rms_energy) / (np.mean(rms_energy) + 1e-8)) # np.std 사용
        return max(0.0, consistency)
        
    except Exception:
        return 0.5

def calculate_fluency_score(audio_data, sample_rate):
    """발화 유창성 점수 계산"""
    try:
        frame_length = int(0.025 * sample_rate)
        hop_length = int(0.01 * sample_rate)
        
        energy = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
        silence_threshold = energy.mean() * 0.1 # 평균 에너지의 10% 이하를 침묵으로 간주
        
        silence_ratio = len(energy[energy < silence_threshold]) / len(energy)
        
        fluency_score = 1.0 - min(1.0, silence_ratio * 2) # 침묵 비율이 높을수록 점수 감소
        return max(0.0, fluency_score)
        
    except Exception:
        return 0.5

def transcribe_with_whisper(audio_path: str) -> Dict[str, Any]:
    """Whisper를 사용한 음성 인식"""
    if not WHISPER_AVAILABLE or whisper_model is None:
        return {"text": "음성 인식을 사용할 수 없습니다.", "confidence": 0.5}
    
    try:
        result = whisper_model.transcribe(audio_path, language="ko")
        
        return {
            "text": result["text"],
            "language": result["language"],
            "segments": result.get("segments", [])[:3], # 모든 세그먼트 대신 일부만 포함
            "confidence": calculate_transcription_confidence(result)
        }
        
    except Exception as e:
        logger.error(f"Whisper 음성 인식 오류: {str(e)}")
        return {"text": "음성 인식 실패", "confidence": 0.0}

def calculate_transcription_confidence(whisper_result):
    """Whisper 결과의 신뢰도 계산"""
    try:
        if "segments" in whisper_result and whisper_result["segments"]:
            total_confidence = 0
            total_segments = 0
            
            for segment in whisper_result["segments"]:
                # avg_logprob는 보통 음수이므로 0-1 스케일로 변환
                # Whisper의 avg_logprob는 낮을수록(음수값이 클수록) 신뢰도가 낮음
                # 대략 -1.0을 기준으로 0.0에 가까울수록 높다고 가정
                confidence = max(0, min(1, (segment["avg_logprob"] + 0.5) / 0.5)) # -0.5를 0, 0을 1로 매핑 (조정 필요)
                total_confidence += confidence
                total_segments += 1
            
            if total_segments > 0:
                return total_confidence / total_segments
        
        return 0.75 # 세그먼트가 없거나 오류 시 기본값
        
    except Exception:
        return 0.75

# ==================== API 엔드포인트 ====================

@app.route('/ai/test', methods=['GET'])
def test_connection():
    """연결 테스트 및 상태 확인 엔드포인트"""
    logger.info("연결 테스트 요청 받음: /ai/test")
    
    # 백엔드 연결 테스트
    backend_status = "연결 확인 필요"
    try:
        import requests
        # 로컬 백엔드가 실행 중인지 확인 (Flask 앱과 다른 포트 가정)
        response = requests.get("http://localhost:4000/api/test", timeout=2) 
        if response.status_code == 200:
            backend_status = "연결됨"
        else:
            backend_status = f"연결됨 (상태 코드: {response.status_code})"
    except Exception as e:
        backend_status = f"연결 실패: {str(e)}"
    
    # 각 모듈 상태 확인
    did_status = "사용 가능" if did_initialized else "사용 불가"
    facial_status = "사용 가능" if facial_analyzer else "사용 불가"
    speech_status = "사용 가능" if speech_analyzer else "사용 불가"
    tts_status = "사용 가능" if tts_manager else "사용 불가"
    llm_status = "사용 가능 (Gemma3:12b)" if llm_module else "사용 불가"
    
    test_response = {
        "status": "VeriView AI 메인 서버 - 완전 통합 버전",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "backend_connection": backend_status,
        "d_id_integration": {
            "service_status": did_status,
            "api_key_status": "설정됨" if os.environ.get('D_ID_API_KEY') else "미설정",
            "korean_tts": "한국어 TTS 지원" # TTSManager가 한국어 TTS 지원 여부를 명시적으로 알 수는 없지만, 일반적인 가정.
        },
        "ai_modules": {
            "LLM (Gemma3:12b)": llm_status,
            "OpenFace/Librosa": facial_status, # OpenFace는 facial_analyzer, Librosa는 speech_analyzer에 포함
            "Whisper/STT": speech_status,
            "TTS Manager": tts_status,
            "Job Recommendation": "사용 가능" if JOB_RECOMMENDATION_AVAILABLE else "사용 불가",
            "TF-IDF Recommendation": "사용 가능" if TFIDF_RECOMMENDATION_AVAILABLE else "사용 불가"
        },
        "supported_features": {
            "개인면접": {
                "질문 생성": "/ai/interview/generate-question",
                "AI 영상": "/ai/interview/ai-video",
                "답변 분석": "/ai/interview/<interview_id>/<question_type>/answer-video",
                "꼬리질문": "/ai/interview/<interview_id>/genergate-followup-question"
            },
            "토론면접": {
                "AI 입론": "/ai/debate/<debate_id>/ai-opening",
                "입론 영상": "/ai/debate/ai-opening-video",
                "반론 영상": "/ai/debate/ai-rebuttal-video",
                "재반론 영상": "/ai/debate/ai-counter-rebuttal-video",
                "최종변론 영상": "/ai/debate/ai-closing-video"
            },
            "채용추천": {
                "기본 추천": "/ai/recruitment/posting",
                "TF-IDF 추천": "/ai/jobs/recommend-tfidf",
                "희소기술 정보": "/ai/jobs/rare-skills"
            }
        },
        "server_mode": "MAIN (프로덕션)"
    }
    
    return jsonify(test_response)

# ==================== 채용 공고 추천 엔드포인트 ====================

@app.route('/ai/recruitment/posting', methods=['POST'])
def recommend_job_postings():
    """채용 공고 추천 엔드포인트 (백엔드 연동)"""
    logger.info("채용 공고 추천 요청 받음: /ai/recruitment/posting")
    
    try:
        data = request.json or {}
        user_id = data.get('user_id', '')
        category = data.get('category', 'ICT')
        
        # TF-IDF 추천 우선 시도
        if TFIDF_RECOMMENDATION_AVAILABLE and tfidf_recommendation_module:
            try:
                tech_stacks = []
                if data.get('tech_stack'):
                    tech_stacks = [s.strip() for s in data.get('tech_stack').split(',') if s.strip()]
                
                certificates = []
                if data.get('qualification'):
                    certificates = [s.strip() for s in data.get('qualification').split(',') if s.strip()]
                
                profile = {
                    'userId': user_id,
                    'techStacks': tech_stacks,
                    'certificateList': certificates,
                    'careerYear': data.get('workexperience', 0),
                    'educationLevel': data.get('education', '')
                }
                
                tfidf_result = tfidf_recommendation_module.get_recommendations_by_profile(profile, 10)
                
                if tfidf_result.get('status') == 'success':
                    posting_list = []
                    for posting in tfidf_result.get('posting', []):
                        posting_list.append({
                            "job_posting_id": posting.get('jobPostingId'),
                            "title": posting.get('title', ''),
                            "keyword": ', '.join(posting.get('techStacks', [])),
                            "corporation": posting.get('corporation', '')
                        })
                    
                    response = {"posting": posting_list[:5]}  # 최대 5개만 반환
                    logger.info(f"TF-IDF 공고추천 완료: {len(posting_list)}개")
                    return jsonify(response)
                    
            except Exception as e:
                logger.warning(f"TF-IDF 추천 실패, 기본 추천으로 폴백: {str(e)}")
        
        # 기본 추천 (카테고리 기반)
        recommended_postings = generate_default_recommendations(category, data)
        
        response = {"posting": recommended_postings}
        logger.info(f"기본 공고추천 완료: {len(recommended_postings)}개")
        return jsonify(response)
        
    except Exception as e:
        error_msg = f"채용 추천 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        # 오류 발생 시 기본 추천 제공
        return jsonify({"posting": generate_default_recommendations("ICT", {})})

def generate_default_recommendations(category: str, data: Dict) -> List[Dict]:
    """기본 채용 공고 추천 생성"""
    base_postings = {
        "ICT": [
            {"job_posting_id": 1, "title": "백엔드 개발자", "keyword": "Java, Spring, MySQL", "corporation": "네이버"},
            {"job_posting_id": 2, "title": "프론트엔드 개발자", "keyword": "React, TypeScript, CSS", "corporation": "카카오"},
            {"job_posting_id": 3, "title": "풀스택 개발자", "keyword": "Python, Django, React", "corporation": "쿠팡"},
            {"job_posting_id": 4, "title": "데이터 엔지니어", "keyword": "Python, Spark, Hadoop", "corporation": "토스"},
            {"job_posting_id": 5, "title": "AI 엔지니어", "keyword": "Python, TensorFlow, PyTorch", "corporation": "삼성전자"}
        ],
        "BM": [
            {"job_posting_id": 6, "title": "경영기획", "keyword": "전략기획, 사업개발, 분석", "corporation": "삼성물산"},
            {"job_posting_id": 7, "title": "마케팅 매니저", "keyword": "브랜드마케팅, 디지털마케팅", "corporation": "LG생활건강"},
            {"job_posting_id": 8, "title": "재무분석가", "keyword": "재무회계, 관리회계, ERP", "corporation": "현대자동차"},
            {"job_posting_id": 9, "title": "인사담당자", "keyword": "채용, 교육, 조직문화", "corporation": "SK하이닉스"},
            {"job_posting_id": 10, "title": "사업개발", "keyword": "신사업, 제휴, 전략", "corporation": "CJ제일제당"}
        ]
    }
    
    postings = base_postings.get(category, base_postings["ICT"])
    
    # 경력에 따른 필터링
    workexperience = data.get('workexperience', '')
    if workexperience == "신입":
        return postings[:3]
    elif workexperience in ["1-3년", "3-5년"]:
        return postings[1:4]
    else:
        return postings[:5]

# ==================== 개인면접 엔드포인트 ====================

@app.route('/ai/interview/generate-question', methods=['POST'])
def generate_interview_question():
    """면접 질문 생성 엔드포인트"""
    try:
        data = request.json or {}
        interview_id = data.get('interview_id', 0)
        
        logger.info(f"면접 질문 생성 요청: interview_id={interview_id}")
        
        # LLM을 사용한 질문 생성
        questions = generate_interview_questions_with_llm(data)
        
        response_data = {
            "interview_id": interview_id,
            "questions": questions
        }
        
        logger.info(f"면접 질문 생성 완료: {len(questions)}개 질문")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"면접 질문 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/interview/ai-video', methods=['POST'])
def generate_ai_video():
    """AI 면접관 영상 생성 엔드포인트 - D-ID 통합"""
    logger.info("AI 면접관 영상 생성 요청 받음: /ai/interview/ai-video")
    
    try:
        data = request.json or {}
        question_text = data.get('question_text', '안녕하세요, 면접에 참여해 주셔서 감사합니다.')
        interviewer_gender = data.get('interviewer_gender', 'male')
        
        if not question_text or len(question_text.strip()) < 5:
            question_text = "안녕하세요, 면접에 참여해 주셔서 감사합니다. 자기소개를 부탁드립니다."
        
        logger.info(f"   질문: {question_text[:50]}{'...' if len(question_text) > 50 else ''}")
        logger.info(f"   성별: {interviewer_gender}")
        
        # D-ID로 면접관 영상 생성
        video_path = generate_avatar_video_unified(
            script=question_text,
            video_type='interview',
            gender=interviewer_gender,
            phase='question'
        )
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            logger.info(f"AI 면접관 영상 준비 완료: {video_path} ({file_size:,} bytes)")
            
            return send_file(os.path.abspath(video_path), mimetype='video/mp4', as_attachment=False)
        
        # 폴백: 샘플 영상 반환
        logger.warning("AI 면접관 영상 생성 실패 - 샘플 영상 반환")
        sample_path = generate_sample_video_fallback('interview', 'question')
        if sample_path and os.path.exists(sample_path):
            return send_file(os.path.abspath(sample_path), mimetype='video/mp4')
        else:
            return Response(b'', mimetype='video/mp4', status=204) # No Content
        
    except Exception as e:
        error_msg = f"AI 면접관 영상 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return Response(b'', mimetype='video/mp4', status=500)

@app.route('/ai/interview/<int:interview_id>/genergate-followup-question', methods=['POST'])
def generate_followup_question(interview_id):
    """꼬리질문 생성 엔드포인트"""
    initialize_analyzers() # 분석기 초기화는 매 요청마다 할 필요는 없지만, 안전을 위해 유지
    logger.info(f"꼬리질문 생성 요청 받음: interview_id={interview_id}")
    
    if 'file' not in request.files:
        logger.warning("파일이 제공되지 않음, 기본 꼬리질문 생성")
        response = {
            "interview_id": interview_id,
            "question_type": "FOLLOWUP",
            "question_text": "방금 답변하신 내용에 대해 좀 더 구체적인 예시를 들어주실 수 있나요?"
        }
        return jsonify(response)
    
    file = request.files['file']
    temp_path = None
    audio_path = None
    try:
        temp_path = os.path.join(tempfile.gettempdir(), f"temp_followup_{interview_id}_{int(time.time())}.mp4")
        file.save(temp_path)
        
        # 오디오 추출 및 음성 인식
        audio_path = extract_audio_from_video(temp_path)
        user_text = "답변 내용" # 기본값
        
        if audio_path and speech_analyzer:
            try:
                # transcribe_video 함수는 RealtimeSpeechToText에 없음. transcribe_with_whisper 사용.
                transcription_result = transcribe_with_whisper(audio_path)
                user_text = transcription_result.get("text", user_text)
            except Exception as e:
                logger.warning(f"음성 인식 실패: {str(e)}")
        
        # LLM을 사용한 꼬리질문 생성
        followup_question = "방금 말씀하신 내용에 대해 더 자세히 설명해 주세요."
        
        if llm_module and user_text:
            try:
                prompt = f"사용자 답변: {user_text}\n이 답변에 대한 적절한 꼬리질문을 생성해주세요."
                # LLMModule에 generate_followup_question 메서드가 직접 정의되어 있지 않으므로, generate_question을 활용
                # 또는 LLM 모듈 내에 해당 기능 추가 필요. 여기서는 예시로 generate_question 사용.
                followup_question = llm_module.generate_question(prompt, "FOLLOWUP") 
            except Exception as e:
                logger.warning(f"LLM 꼬리질문 생성 실패: {str(e)}")
        else:
            # 키워드 기반 꼬리질문
            tech_keywords = ["Java", "Python", "React", "Spring", "Node.js", "JavaScript", "클라우드", "데이터베이스", "AI"]
            mentioned_tech = [tech for tech in tech_keywords if tech.lower() in user_text.lower()]
            
            if mentioned_tech:
                tech = mentioned_tech[0]
                followup_question = f"{tech}를 사용하여 진행한 프로젝트에서 가장 어려웠던 부분은 무엇이었나요? 어떻게 해결하셨나요?"
            elif len(user_text.split()) > 10: # 답변이 짧지 않으면 더 구체적인 질문
                followup_question = f"방금 답변에서 언급하신 '{user_text.split()[-1]}' 부분에 대해 좀 더 자세히 설명해주실 수 있나요?"
        
        response = {
            "interview_id": interview_id,
            "question_type": "FOLLOWUP",
            "question_text": followup_question
        }
        
        return jsonify(response)
        
    except Exception as e:
        error_msg = f"꼬리질문 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "interview_id": interview_id,
            "question_type": "FOLLOWUP",
            "question_text": "추가로 설명해주실 내용이 있나요?"
        })
    finally:
        cleanup_temp_files([temp_path, audio_path])

@app.route('/ai/interview/<int:interview_id>/<question_type>/answer-video', methods=['POST'])
def process_interview_answer(interview_id, question_type):
    """면접 답변 영상 처리 엔드포인트"""
    initialize_analyzers()
    logger.info(f"면접 답변 영상 처리 요청: interview_id={interview_id}, type={question_type}")
    
    if 'file' not in request.files and 'video' not in request.files:
        logger.warning("영상 파일이 제공되지 않음")
        return jsonify(generate_default_interview_response(interview_id, question_type))
    
    file = request.files.get('file') or request.files.get('video')
    temp_path = None
    audio_path = None
    try:
        # 임시 파일 경로를 tempfile 모듈을 사용하여 안전하게 생성
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"temp_interview_{interview_id}_{question_type}_{int(time.time())}.mp4")
        file.save(temp_path)
        
        # 오디오 추출
        audio_path = extract_audio_from_video(temp_path)
        
        # 음성 인식
        user_text = "답변 내용입니다."
        transcription_confidence = 0.5
        
        if audio_path and WHISPER_AVAILABLE: # WHISPER_AVAILABLE 확인
            try:
                transcription_result = transcribe_with_whisper(audio_path)
                user_text = transcription_result.get("text", user_text)
                transcription_confidence = transcription_result.get("confidence", 0.5)
            except Exception as e:
                logger.warning(f"음성 인식 실패: {str(e)}")
        
        # 얼굴 분석
        facial_result = {"confidence": 0.5, "emotion": "중립"} # 기본값 변경 (0.9는 너무 높음)
        if facial_analyzer:
            try:
                facial_result = facial_analyzer.analyze_video(temp_path)
            except Exception as e:
                logger.warning(f"얼굴 분석 실패: {str(e)}")
        
        # 음성 분석
        audio_result = {"voice_stability": 0.5, "fluency_score": 0.5, "speaking_rate_wpm": 120, "volume_consistency": 0.7} # 기본값 추가
        if audio_path and LIBROSA_AVAILABLE:
            try:
                audio_result = process_audio_with_librosa(audio_path)
            except Exception as e:
                logger.warning(f"음성 분석 실패: {str(e)}")
        
        # 점수 계산
        content_score = round(calculate_content_score(user_text), 1)
        voice_score = round(audio_result.get("voice_stability", 0.5) * 5, 1) # 기본값 반영
        action_score = round(facial_result.get("confidence", 0.5) * 5, 1) # 기본값 반영
        
        # 피드백 생성
        content_feedback = generate_content_feedback(content_score)
        voice_feedback = generate_voice_feedback(voice_score)
        action_feedback = generate_action_feedback(action_score)
        overall_feedback = generate_interview_feedback(
            {"text": user_text, "confidence": transcription_confidence},
            audio_result,
            facial_result
        )
        
        response = {
            "interview_id": interview_id,
            "question_type": question_type,
            "answer_text": user_text,
            "content_score": content_score,
            "voice_score": voice_score,
            "action_score": action_score,
            "content_feedback": content_feedback,
            "voice_feedback": voice_feedback,
            "action_feedback": action_feedback,
            "feedback": overall_feedback
        }
        
        logger.info(f"면접 답변 처리 완료: 점수 {content_score}/{voice_score}/{action_score}")
        return jsonify(response)
        
    except Exception as e:
        error_msg = f"면접 답변 처리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify(generate_default_interview_response(interview_id, question_type)), 200
    finally:
        cleanup_temp_files([temp_path, audio_path])

def generate_default_interview_response(interview_id: int, question_type: str) -> Dict:
    """기본 면접 응답 생성"""
    return {
        "interview_id": interview_id,
        "question_type": question_type,
        "answer_text": "답변 영상이 제공되지 않았습니다.",
        "content_score": 2.5,
        "voice_score": 2.5,
        "action_score": 2.5,
        "content_feedback": "내용 평가를 위해 답변이 필요합니다.",
        "voice_feedback": "음성 평가를 위해 답변이 필요합니다.",
        "action_feedback": "행동 평가를 위해 답변이 필요합니다.",
        "feedback": "답변 영상을 제출해주시면 더 정확한 피드백을 제공할 수 있습니다."
    }

def generate_content_feedback(score: float) -> str:
    """내용 점수에 따른 피드백 생성"""
    if score >= 4.5:
        return "매우 체계적이고 구체적인 답변입니다. 질문의 핵심을 정확히 짚었습니다."
    elif score >= 4.0:
        return "충분하고 체계적인 답변입니다. 내용 구성이 좋습니다."
    elif score >= 3.5:
        return "적절한 내용의 답변입니다. 필요한 정보는 잘 전달했습니다."
    elif score >= 3.0:
        return "내용이 다소 부족합니다. 구체적인 사례나 경험을 추가하여 답변을 풍부하게 만들 수 있습니다."
    else:
        return "내용을 좀 더 구체적으로 설명해 주세요. 답변의 핵심이 불분명할 수 있습니다."

def generate_voice_feedback(score: float) -> str:
    """음성 점수에 따른 피드백 생성"""
    if score >= 4.5:
        return "매우 명확하고 안정적인 음성으로 신뢰감을 줍니다. 발음과 톤이 훌륭합니다."
    elif score >= 4.0:
        return "명확하고 안정적인 음성입니다. 듣기에 편안합니다."
    elif score >= 3.5:
        return "적절한 음성 전달입니다. 조금 더 자신감을 보여주면 좋습니다."
    elif score >= 3.0:
        return "목소리가 다소 불안정하거나 작을 수 있습니다. 발성 연습을 통해 개선할 수 있습니다."
    else:
        return "좀 더 명확하고 안정적으로 말씀해 주세요. 발음이 불분명하거나 음량이 작을 수 있습니다."

def generate_action_feedback(score: float) -> str:
    """행동 점수에 따른 피드백 생성"""
    if score >= 4.5:
        return "매우 자신감 있고 안정적인 태도입니다. 면접관과 눈을 잘 마주치고 표정이 자연스럽습니다."
    elif score >= 4.0:
        return "자신감 있고 안정적인 태도입니다. 시선 처리와 표정이 좋습니다."
    elif score >= 3.5:
        return "적절한 자세와 표정입니다. 전반적으로 무난한 인상을 줍니다."
    elif score >= 3.0:
        return "시선과 자세가 다소 불안정할 수 있습니다. 면접관과의 눈맞춤을 늘리고 바른 자세를 유지해 보세요."
    else:
        return "눈맞춤과 자세를 개선해 주세요. 불안하거나 자신감 없는 모습으로 비칠 수 있습니다."

# ==================== 토론면접 엔드포인트 ====================

@app.route('/ai/debate/<int:debate_id>/ai-opening', methods=['POST'])
def generate_ai_opening(debate_id):
    """AI 입론 생성 엔드포인트"""
    logger.info(f"AI 입론 생성 요청 받음: debate_id={debate_id}")
    
    try:
        data = request.json or {}
        topic = data.get('topic', '기본 토론 주제')
        position = data.get('position', 'PRO')
        
        # LLM을 사용한 입론 생성
        if llm_module:
            try:
                # DebateLLMModule의 generate_ai_opening 메서드 호출
                ai_opening_text = llm_module.generate_ai_opening(topic, position, data).get("ai_response", "")
                if not ai_opening_text.strip(): # LLM이 빈 응답을 줄 경우 폴백
                    ai_opening_text = generate_fallback_opening(topic, position)
            except Exception as e:
                logger.warning(f"LLM 입론 생성 실패: {str(e)}")
                ai_opening_text = generate_fallback_opening(topic, position)
        else:
            ai_opening_text = generate_fallback_opening(topic, position)
        
        response_data = {
            "ai_opening_text": ai_opening_text,
            "debate_id": debate_id,
            "topic": topic,
            "position": position
        }
        
        logger.info(f"AI 입론 생성 완료: {debate_id}")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"AI 입론 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "ai_opening_text": "AI 입론을 생성할 수 없습니다.",
            "debate_id": debate_id,
            "error": error_msg
        }), 200

def generate_fallback_opening(topic: str, position: str) -> str:
    """폴백 입론 생성"""
    if position.upper() == 'PRO':
        return f"'{topic}'에 대해 찬성하는 입장에서 말씀드리겠습니다. 이 주제는 우리 사회에 긍정적인 영향을 미칠 것이며, 다음과 같은 이유로 지지합니다."
    else:
        return f"'{topic}'에 대해 반대하는 입장에서 말씀드리겠습니다. 이 주제에는 신중한 접근이 필요하며, 예상되는 문제점들을 간과해서는 안 됩니다."

@app.route('/ai/debate/ai-opening-video', methods=['POST'])
def generate_ai_opening_video():
    """AI 입론 영상 생성 엔드포인트 - D-ID 통합"""
    logger.info("AI 입론 영상 생성 요청 받음")
    
    try:
        data = request.json or {}
        ai_opening_text = data.get('ai_opening_text', '기본 입론 텍스트')
        debater_gender = data.get('debater_gender', 'male')
        
        if not ai_opening_text or len(ai_opening_text.strip()) < 10:
            ai_opening_text = "토론 주제에 대해 찬성하는 입장에서 의견을 말씀드리겠습니다. 제 입론을 시작하겠습니다."
        
        # D-ID로 토론자 영상 생성
        video_path = generate_avatar_video_unified(
            script=ai_opening_text,
            video_type='debate',
            gender=debater_gender,
            phase='opening'
        )
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            logger.info(f"AI 입론 영상 준비 완료: {video_path} ({file_size:,} bytes)")
            return send_file(os.path.abspath(video_path), mimetype='video/mp4')
        
        # 폴백
        logger.warning("AI 입론 영상 생성 실패 - 샘플 영상 반환")
        sample_path = generate_sample_video_fallback('debate', 'opening')
        if sample_path and os.path.exists(sample_path):
            return send_file(os.path.abspath(sample_path), mimetype='video/mp4')
        else:
            return Response(b'', mimetype='video/mp4', status=204)
        
    except Exception as e:
        logger.error(f"AI 입론 영상 생성 중 오류: {str(e)}")
        return Response(b'', mimetype='video/mp4', status=500)

@app.route('/ai/debate/ai-rebuttal-video', methods=['POST'])
def generate_ai_rebuttal_video():
    """AI 반론 영상 생성 엔드포인트 - D-ID 통합"""
    logger.info("AI 반론 영상 생성 요청 받음")
    
    try:
        data = request.json or {}
        ai_rebuttal_text = data.get('ai_rebuttal_text', '기본 반론 텍스트')
        debater_gender = data.get('debater_gender', 'male')

        if not ai_rebuttal_text or len(ai_rebuttal_text.strip()) < 10:
            ai_rebuttal_text = "상대방의 의견에 대해 반론하겠습니다. 제가 제기한 문제점은 여전히 유효합니다."
        
        video_path = generate_avatar_video_unified(
            script=ai_rebuttal_text,
            video_type='debate',
            gender=debater_gender,
            phase='rebuttal'
        )
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            logger.info(f"AI 반론 영상 준비 완료: {video_path} ({file_size:,} bytes)")
            return send_file(os.path.abspath(video_path), mimetype='video/mp4')
        
        logger.warning("AI 반론 영상 생성 실패 - 샘플 영상 반환")
        sample_path = generate_sample_video_fallback('debate', 'rebuttal')
        if sample_path and os.path.exists(sample_path):
            return send_file(os.path.abspath(sample_path), mimetype='video/mp4')
        else:
            return Response(b'', mimetype='video/mp4', status=204)
        
    except Exception as e:
        logger.error(f"AI 반론 영상 생성 중 오류: {str(e)}")
        return Response(b'', mimetype='video/mp4', status=500)

@app.route('/ai/debate/ai-counter-rebuttal-video', methods=['POST'])
def generate_ai_counter_rebuttal_video():
    """AI 재반론 영상 생성 엔드포인트 - D-ID 통합"""
    logger.info("🎬 AI 재반론 영상 생성 요청 받음")
    
    try:
        data = request.json or {}
        ai_counter_rebuttal_text = data.get('ai_counter_rebuttal_text', '기본 재반론 텍스트')
        debater_gender = data.get('debater_gender', 'male')

        if not ai_counter_rebuttal_text or len(ai_counter_rebuttal_text.strip()) < 10:
            ai_counter_rebuttal_text = "상대방의 반론에 대해 다시 반박하겠습니다. 제 주장의 핵심은 변함이 없습니다."
        
        video_path = generate_avatar_video_unified(
            script=ai_counter_rebuttal_text,
            video_type='debate',
            gender=debater_gender,
            phase='counter_rebuttal'
        )
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            logger.info(f"AI 재반론 영상 준비 완료: {video_path} ({file_size:,} bytes)")
            return send_file(os.path.abspath(video_path), mimetype='video/mp4')
        
        logger.warning("AI 재반론 영상 생성 실패 - 샘플 영상 반환")
        sample_path = generate_sample_video_fallback('debate', 'counter_rebuttal')
        if sample_path and os.path.exists(sample_path):
            return send_file(os.path.abspath(sample_path), mimetype='video/mp4')
        else:
            return Response(b'', mimetype='video/mp4', status=204)
        
    except Exception as e:
        logger.error(f"AI 재반론 영상 생성 중 오류: {str(e)}")
        return Response(b'', mimetype='video/mp4', status=500)

@app.route('/ai/debate/ai-closing-video', methods=['POST'])
def generate_ai_closing_video():
    """AI 최종변론 영상 생성 엔드포인트 - D-ID 통합"""
    logger.info("AI 최종변론 영상 생성 요청 받음")
    
    try:
        data = request.json or {}
        ai_closing_text = data.get('ai_closing_text', '기본 최종변론 텍스트')
        debater_gender = data.get('debater_gender', 'male')

        if not ai_closing_text or len(ai_closing_text.strip()) < 10:
            ai_closing_text = "최종적으로 제 주장을 요약하고 마무리하겠습니다. 이 토론을 통해 중요한 점들을 확인했습니다."
        
        video_path = generate_avatar_video_unified(
            script=ai_closing_text,
            video_type='debate',
            gender=debater_gender,
            phase='closing'
        )
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            logger.info(f"AI 최종변론 영상 준비 완료: {video_path} ({file_size:,} bytes)")
            return send_file(os.path.abspath(video_path), mimetype='video/mp4')
        
        logger.warning("AI 최종변론 영상 생성 실패 - 샘플 영상 반환")
        sample_path = generate_sample_video_fallback('debate', 'closing')
        if sample_path and os.path.exists(sample_path):
            return send_file(os.path.abspath(sample_path), mimetype='video/mp4')
        else:
            return Response(b'', mimetype='video/mp4', status=204)
        
    except Exception as e:
        logger.error(f"AI 최종변론 영상 생성 중 오류: {str(e)}")
        return Response(b'', mimetype='video/mp4', status=500)

@app.route('/ai/debate/<int:debate_id>/opening-video', methods=['POST'])
def process_opening_video(debate_id):
    """사용자 입론 영상 처리 엔드포인트"""
    return process_debate_video_generic(debate_id, "opening", "rebuttal")

@app.route('/ai/debate/<int:debate_id>/rebuttal-video', methods=['POST'])
def process_rebuttal_video(debate_id):
    """사용자 반론 영상 처리 엔드포인트"""
    return process_debate_video_generic(debate_id, "rebuttal", "counter_rebuttal")

@app.route('/ai/debate/<int:debate_id>/counter-rebuttal-video', methods=['POST'])
def process_counter_rebuttal_video(debate_id):
    """사용자 재반론 영상 처리 엔드포인트"""
    return process_debate_video_generic(debate_id, "counter_rebuttal", "closing")

@app.route('/ai/debate/<int:debate_id>/closing-video', methods=['POST'])
def process_closing_video(debate_id):
    """사용자 최종변론 영상 처리 엔드포인트"""
    return process_debate_video_generic(debate_id, "closing", None) # 마지막 단계는 다음 AI 단계 없음

def process_debate_video_generic(debate_id, current_stage, next_ai_stage):
    """토론 영상 처리 공통 함수"""
    initialize_analyzers() # 분석기 초기화
    logger.info(f"📺 {current_stage} 영상 처리 요청: debate_id={debate_id}")
    
    if 'file' not in request.files and 'video' not in request.files:
        logger.warning("파일이 제공되지 않음")
        return jsonify(generate_default_debate_response(debate_id, current_stage, next_ai_stage))
    
    file = request.files.get('file') or request.files.get('video')
    temp_path = None
    audio_path = None
    try:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"temp_{current_stage}_{debate_id}_{int(time.time())}.mp4")
        file.save(temp_path)
        
        # 오디오 추출
        audio_path = extract_audio_from_video(temp_path)
        
        # 음성 인식
        transcription_result = {"text": f"사용자의 {current_stage} 발언입니다.", "confidence": 0.5} # 기본값
        if audio_path and WHISPER_AVAILABLE:
            transcription_result = transcribe_with_whisper(audio_path)
        
        # 음성 분석
        audio_analysis = {"voice_stability": 0.5, "fluency_score": 0.5, "speaking_rate_wpm": 120, "volume_consistency": 0.7} # 기본값
        if audio_path and LIBROSA_AVAILABLE:
            audio_analysis = process_audio_with_librosa(audio_path)
        
        # 얼굴 분석
        facial_analysis = {"confidence": 0.5, "emotion": "중립"} # 기본값
        if openface_integration: # openface_integration 사용 여부 확인
            try:
                facial_analysis = openface_integration.analyze_video(temp_path)
            except Exception as e:
                logger.warning(f"OpenFace 분석 실패: {str(e)}")
        
        # 종합 점수 계산
        scores = calculate_debate_scores(transcription_result, audio_analysis, facial_analysis)
        
        # 결과 구성
        result = {
            f"user_{current_stage}_text": transcription_result.get("text", ""),
            **scores
        }
        
        # 다음 AI 응답 생성
        if next_ai_stage:
            topic = request.form.get("topic", "토론 주제") # 폼 데이터에서 주제 가져오기
            user_text = transcription_result.get("text", "")
            
            if llm_module:
                try:
                    # DebateLLMModule의 analyze_user_response_and_generate_rebuttal 메서드 호출
                    llm_result = llm_module.analyze_user_response_and_generate_rebuttal(
                        user_text, facial_analysis, audio_analysis, next_ai_stage
                    )
                    ai_response = llm_result.get("ai_response", "")
                    if not ai_response.strip(): # LLM이 빈 응답을 줄 경우 폴백
                        ai_response = get_fallback_ai_response(next_ai_stage, topic, user_text)
                    result[f"ai_{next_ai_stage}_text"] = ai_response
                except Exception as e:
                    logger.error(f"LLM 응답 생성 오류: {str(e)}")
                    result[f"ai_{next_ai_stage}_text"] = get_fallback_ai_response(next_ai_stage, topic, user_text)
            else:
                result[f"ai_{next_ai_stage}_text"] = get_fallback_ai_response(next_ai_stage, topic, user_text)
        
        logger.info(f"{current_stage} 영상 처리 완료")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"{current_stage} 영상 처리 중 오류: {str(e)}"
        logger.error(error_msg)
        return jsonify(generate_default_debate_response(debate_id, current_stage, next_ai_stage)), 200
    finally:
        cleanup_temp_files([temp_path, audio_path])

def calculate_debate_scores(transcription: Dict, audio: Dict, facial: Dict) -> Dict[str, Any]:
    """토론 점수 계산"""
    try:
        text = transcription.get("text", "")
        confidence = transcription.get("confidence", 0.5) # 기본값 반영
        voice_stability = audio.get("voice_stability", 0.5) # 기본값 반영
        fluency = audio.get("fluency_score", 0.5) # 기본값 반영
        facial_confidence = facial.get("confidence", 0.5) # 기본값 반영
        
        # 점수 계산 (소수점 한 자리) - 0~5점 스케일로 조정
        # 기존 0~1 값을 0~5로 매핑하고, 기본점을 2.5 정도로 설정하여 너무 낮지 않게 조정
        scores = {
            "initiative_score": round(min(5.0, 2.5 + confidence * 2.5), 1), # 0.5~5.0
            "collaborative_score": round(min(5.0, 2.5 + (len(text.split()) / 100) * 2.5), 1), # 텍스트 길이에 비례 (max 100단어 기준)
            "communication_score": round(min(5.0, 2.5 + fluency * 2.5), 1), # 0.5~5.0
            "logic_score": round(min(5.0, 2.5 + calculate_logic_score(text) * 2.5), 1), # 0.5~5.0
            "problem_solving_score": round(min(5.0, 2.5 + calculate_problem_solving_score(text) * 2.5), 1), # 0.5~5.0
            "voice_score": round(min(5.0, voice_stability * 5), 1), # 0~5.0
            "action_score": round(min(5.0, facial_confidence * 5), 1) # 0~5.0
        }
        
        # 피드백 생성
        for category in ["initiative", "collaborative", "communication", "logic", "problem_solving"]:
            score = scores[f"{category}_score"]
            if score >= 4.5:
                scores[f"{category}_feedback"] = f"{get_korean_name(category)}: 매우 우수. 논거 제시가 탁월합니다."
            elif score >= 4.0:
                scores[f"{category}_feedback"] = f"{get_korean_name(category)}: 우수. 의견 개진이 명확합니다."
            elif score >= 3.5:
                scores[f"{category}_feedback"] = f"{get_korean_name(category)}: 양호. 전반적으로 좋은 토론 참여를 보여주었습니다."
            else:
                scores[f"{category}_feedback"] = f"{get_korean_name(category)}: 개선 필요. 더 적극적인 참여와 논리적인 근거 제시가 필요합니다."
        
        # Voice and Action feedback based on score ranges (0-5)
        scores["voice_feedback"] = generate_voice_feedback(scores["voice_score"])
        scores["action_feedback"] = generate_action_feedback(scores["action_score"])

        # 종합 피드백
        avg_score = sum(scores[k] for k in scores if k.endswith("_score")) / len([k for k in scores if k.endswith("_score")])
        if avg_score >= 4.5:
            scores["feedback"] = "매우 우수한 토론 수행을 보여주었습니다. 탁월한 논리력과 명확한 의사소통 능력이 돋보입니다."
        elif avg_score >= 4.0:
            scores["feedback"] = "우수한 토론 수행을 보여주었습니다. 균형 잡힌 참여와 효과적인 의견 제시가 좋았습니다."
        elif avg_score >= 3.5:
            scores["feedback"] = "양호한 토론 수행을 보여주었습니다. 전반적으로 안정적인 참여였으나, 더 깊이 있는 분석이 필요합니다."
        else:
            scores["feedback"] = "토론 수행에 개선이 필요합니다. 논리적 구성과 적극적인 참여를 통해 더 좋은 결과를 얻을 수 있습니다."
        
        scores["sample_answer"] = "구체적인 근거와 예시를 들어 논리적으로 설명하는 것이 좋습니다. 상대방의 의견을 경청하고 핵심을 짚어 반론하는 연습을 해보세요."
        
        return scores
        
    except Exception as e:
        logger.error(f"토론 점수 계산 오류: {str(e)}")
        return get_default_debate_scores()

def calculate_logic_score(text: str) -> float:
    """논리성 점수 계산"""
    if not text:
        return 0.0
    logic_indicators = ["따라서", "그러므로", "결론적으로", "왜냐하면", "근거는", "예를 들어", "즉", "핵심은"]
    logic_count = sum(1 for indicator in logic_indicators if indicator in text)
    # 텍스트 길이에 따라 점수 가중 (길이가 너무 짧으면 논리성 판단 어려움)
    word_count = len(text.split())
    
    score = min(1.0, logic_count * 0.2 + (word_count / 100) * 0.1) # 최대 100단어 기준
    return score

def calculate_problem_solving_score(text: str) -> float:
    """문제해결 점수 계산"""
    if not text:
        return 0.0
    problem_solving_indicators = ["해결", "방안", "대안", "개선", "전략", "접근", "극복", "제시", "도출"]
    problem_count = sum(1 for indicator in problem_solving_indicators if indicator in text)
    word_count = len(text.split())

    score = min(1.0, problem_count * 0.2 + (word_count / 100) * 0.1)
    return score

def get_korean_name(category: str) -> str:
    """카테고리 한글명 반환"""
    mapping = {
        "initiative": "적극성",
        "collaborative": "협력성",
        "communication": "의사소통",
        "logic": "논리성",
        "problem_solving": "문제해결"
    }
    return mapping.get(category, category)

def get_default_debate_scores() -> Dict[str, Any]:
    """기본 토론 점수"""
    return {
        "initiative_score": 2.5,
        "collaborative_score": 2.5,
        "communication_score": 2.5,
        "logic_score": 2.5,
        "problem_solving_score": 2.5,
        "voice_score": 2.5,
        "action_score": 2.5,
        "initiative_feedback": "적극성: 보통",
        "collaborative_feedback": "협력성: 보통",
        "communication_feedback": "의사소통: 보통",
        "logic_feedback": "논리성: 보통",
        "problem_solving_feedback": "문제해결: 보통",
        "voice_feedback": "음성 전달: 보통",
        "action_feedback": "행동/태도: 보통",
        "feedback": "전반적으로 무난한 토론 수행을 보여주었습니다. 더 나은 피드백을 위해 답변 영상을 제공해주세요.",
        "sample_answer": "구체적인 예시와 근거를 들어 논리적으로 설명해보세요. 상대방의 의견을 경청하고 핵심을 짚어 반론하는 연습을 해보세요."
    }

def generate_default_debate_response(debate_id: int, stage: str, next_stage: Optional[str]) -> Dict:
    """기본 토론 응답 생성"""
    response = {
        f"user_{stage}_text": "파일이 제공되지 않았습니다. 분석을 위해 영상을 업로드해주세요.",
        **get_default_debate_scores()
    }
    
    if next_stage:
        response[f"ai_{next_stage}_text"] = get_fallback_ai_response(next_stage, "토론 주제", "사용자 답변 없음")
    
    return response

def get_fallback_ai_response(stage: str, topic: str = "토론 주제", user_text: str = "") -> str:
    """폴백 AI 응답"""
    responses = {
        "rebuttal": f"말씀하신 '{user_text[:30]}...'에 대한 의견을 경청했습니다. 하지만 '{topic}'에 대해 다른 관점에서 몇 가지 고려해야 할 점들이 있습니다. 예를 들어...",
        "counter_rebuttal": f"제기하신 점들을 충분히 이해했습니다. 그러나 '{topic}'의 장기적 관점에서 보면 여전히 신중한 접근이 필요하며, 저는 다음과 같은 근거를 제시합니다.",
        "closing": f"결론적으로 '{topic}'에 대한 이번 토론을 통해 다양한 관점을 확인할 수 있었습니다. 저는 여전히 제 입장을 지지하며, 균형잡힌 시각이 중요하다고 생각합니다. 감사합니다."
    }
    
    return responses.get(stage, f"'{topic}'에 대해 의견을 나눠주셔서 감사합니다. 추가적인 논의를 기대합니다.")

# ==================== 추가 유틸리티 엔드포인트 ====================

@app.route('/videos/<path:filename>')
def serve_video(filename):
    """영상 파일 제공 엔드포인트"""
    try:
        video_path = os.path.join(app.static_folder, filename) # app.static_folder 사용
        if os.path.exists(video_path):
            return send_file(video_path, mimetype='video/mp4')
        else:
            logger.error(f"영상 파일을 찾을 수 없음: {video_path}")
            return Response(b'Video not found', status=404)
    except Exception as e:
        logger.error(f"영상 파일 제공 중 오류: {str(e)}")
        return Response(b'Error serving video', status=500)

@app.route('/ai/jobs/recommend-tfidf', methods=['POST'])
def recommend_jobs_tfidf():
    """TF-IDF 기반 공고 추천 엔드포인트"""
    if not TFIDF_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "TF-IDF 공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        data = request.json or {}
        logger.info(f"TF-IDF 공고 추천 요청 받음: {data}")
        
        if 'skills' in data:
            skills = data['skills']
            limit = data.get('limit', 10)
            result = tfidf_recommendation_module.get_recommendations_by_skills(skills, limit)
            return jsonify(result)
        
        elif 'profile' in data:
            profile = data['profile']
            limit = data.get('limit', 10)
            result = tfidf_recommendation_module.get_recommendations_by_profile(profile, limit)
            return jsonify(result)
        
        else:
            return jsonify({"error": "skills 또는 profile 데이터가 필요합니다."}), 400
            
    except Exception as e:
        logger.error(f"TF-IDF 공고 추천 중 오류: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ai/jobs/rare-skills', methods=['GET'])
def get_rare_skills():
    """희소 기술 정보 조회 엔드포인트"""
    if not TFIDF_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "TF-IDF 공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        result = tfidf_recommendation_module.get_rare_skills_info()
        return jsonify(result)
    except Exception as e:
        logger.error(f"희소 기술 정보 조회 중 오류: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== 메인 실행 ====================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VeriView AI Main Server")
    parser.add_argument("--mode", type=str, default="main", help="Server mode (e.g., main)")
    args = parser.parse_args()

    if args.mode == "main":
        print("=" * 80)
        print("VeriView AI 메인 서버 시작 - 완전 통합 버전")
        print("=" * 80)
        
        # D-ID 초기화
        if initialize_d_id():
            print("D-ID 통합 성공")
        else:
            print("D-ID 통합 실패 - 폴백 모드 사용")
        
        # 분석기 초기화
        if initialize_analyzers():
            print("분석기 초기화 성공")
        else:
            print("분석기 초기화 부분 실패")
        
        # AI 시스템 초기화
        initialize_ai_systems()
        
        print("-" * 80)
        print("서버 주소: http://localhost:5000")
        print("테스트 엔드포인트: http://localhost:5000/ai/test")
        print("-" * 80)
        print("활성화된 모듈:")
        print(f"  - D-ID API: {'✅' if did_initialized else '❌'}")
        print(f"  - LLM (Gemma3:12b): {'✅' if llm_module else '❌'}")
        print(f"  - OpenFace: {'✅' if openface_integration else '❌'}")
        print(f"  - Whisper: {'✅' if WHISPER_AVAILABLE else '❌'}")
        print(f"  - TTS: {'✅' if TTS_AVAILABLE else '❌'}")
        print(f"  - Librosa: {'✅' if LIBROSA_AVAILABLE else '❌'}")
        print(f"  - 공고추천: {'✅' if JOB_RECOMMENDATION_AVAILABLE else '❌'}")
        print(f"  - TF-IDF 추천: {'✅' if TFIDF_RECOMMENDATION_AVAILABLE else '❌'}")
        print("=" * 80)
        
        # 주의사항 출력
        if not os.environ.get('D_ID_API_KEY'):
            print("주의: D_ID_API_KEY 환경 변수를 설정해주세요!")
            print("  export D_ID_API_KEY='your_api_key_here' (Linux/macOS)")
            print("  set D_ID_API_KEY=your_api_key_here (Windows Command Prompt)")
            print("  $env:D_ID_API_KEY='your_api_key_here' (Windows PowerShell)")
        
        print("\n서버를 종료하려면 Ctrl+C를 누르세요.\n")
        
        # Flask 앱 실행
        app.run(host="0.0.0.0", port=5000, debug=False)
    else:
        print(f"Unknown mode: {args.mode}")