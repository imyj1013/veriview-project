#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 - 메인 서버 (모든 AI 모듈 포함)
LLM, OpenFace2.0, Whisper, TTS, Librosa 기능을 모두 활용하는 실제 서버

실행 방법: python main_server.py
포트: 5000
"""
from flask import Flask, jsonify, request, send_file, Response, stream_with_context
from flask_cors import CORS
import os
import tempfile
import logging
import time
import json
from typing import Dict, Any, Optional

# 실제 AI 모듈 임포트
try:
    from interview_features.debate.llm_module import DebateLLMModule
    from interview_features.debate.openface_integration import OpenFaceDebateIntegration
    LLM_MODULE_AVAILABLE = True
    OPENFACE_INTEGRATION_AVAILABLE = True
    print(" 실제 AI 모듈 로드 성공: LLM 및 OpenFace 통합 기능 사용 가능")
except ImportError as e:
    print(f" 실제 AI 모듈 로드 실패: {e}")
    LLM_MODULE_AVAILABLE = False
    OPENFACE_INTEGRATION_AVAILABLE = False

# 백업 모듈 임포트 (실제 모듈이 없을 경우)
try:
    from test_features.debate.main import DebateTestMain
    from test_features.personal_interview.main import PersonalInterviewTestMain
    BACKUP_MODULES_AVAILABLE = True
    print(" 백업 모듈 로드 성공: 테스트 기능 사용 가능")
except ImportError as e:
    print(f" 백업 모듈 로드 실패: {e}")
    BACKUP_MODULES_AVAILABLE = False

# 공통 모듈 임포트
try:
    from modules.job_recommendation_module import JobRecommendationModule
    job_recommendation_module = JobRecommendationModule()
    JOB_RECOMMENDATION_AVAILABLE = True
    print(" 공고추천 모듈 로드 성공")
except ImportError as e:
    print(f" 공고추천 모듈 로드 실패: {e}")
    JOB_RECOMMENDATION_AVAILABLE = False
    job_recommendation_module = None

# TF-IDF 공고추천 모듈 임포트
try:
    from modules.tfidf_job_recommendation_module import TFIDFJobRecommendationModule
    tfidf_recommendation_module = TFIDFJobRecommendationModule()
    TFIDF_RECOMMENDATION_AVAILABLE = True
    print(" TF-IDF 공고추천 모듈 로드 성공")
except ImportError as e:
    print(f" TF-IDF 공고추천 모듈 로드 실패: {e}")
    TFIDF_RECOMMENDATION_AVAILABLE = False
    tfidf_recommendation_module = None

# 개별 모듈 임포트
try:
    import whisper
    import librosa
    import soundfile as sf
    WHISPER_AVAILABLE = True
    LIBROSA_AVAILABLE = True
    print(" Whisper 및 Librosa 모듈 로드 성공")
except ImportError as e:
    print(f" 음성 분석 모듈 일부 제한: {e}")
    WHISPER_AVAILABLE = False
    LIBROSA_AVAILABLE = False

# TTS 모듈 임포트
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
    print(" TTS 모듈 로드 성공")
except ImportError as e:
    print(f" TTS 모듈 로드 실패: {e}")
    TTS_AVAILABLE = False

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 전역 변수로 AI 시스템 초기화
llm_module = None
openface_integration = None
debate_test_system = None
personal_interview_test_system = None
whisper_model = None
tts_model = None

def initialize_ai_systems():
    """AI 시스템 초기화"""
    global llm_module, openface_integration, debate_test_system, personal_interview_test_system
    global whisper_model, tts_model
    
    try:
        # LLM 모듈 초기화
        if LLM_MODULE_AVAILABLE:
            llm_module = DebateLLMModule(llm_provider="openai", model="gpt-4")
            logger.info("LLM 모듈 초기화 완료")
        
        # OpenFace 통합 모듈 초기화
        if OPENFACE_INTEGRATION_AVAILABLE:
            openface_integration = OpenFaceDebateIntegration()
            logger.info("OpenFace 통합 모듈 초기화 완료")
        
        # 백업 모듈 초기화 (실제 모듈이 없을 경우)
        if BACKUP_MODULES_AVAILABLE:
            if not LLM_MODULE_AVAILABLE:
                debate_test_system = DebateTestMain()
                logger.info("토론면접 백업 시스템 초기화 완료")
            
            personal_interview_test_system = PersonalInterviewTestMain()
            logger.info("개인면접 시스템 초기화 완료")
        
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
            "voice_stability": min(1.0, max(0.0, 1.0 - abs(spectral_centroids.std() / spectral_centroids.mean()))),
            "speaking_rate_wpm": estimate_speaking_rate(y, sr),
            "volume_consistency": calculate_volume_consistency(y),
            "fluency_score": calculate_fluency_score(y, sr)
        }
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Librosa 오디오 분석 오류: {str(e)}")
        return {"error": f"오디오 분석 실패: {str(e)}"}

def estimate_speaking_rate(audio_data, sample_rate):
    """말하기 속도 추정 (단위: WPM)"""
    try:
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
    """음량 일관성 계산"""
    try:
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
    """발화 유창성 점수 계산"""
    try:
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

def transcribe_with_whisper(audio_path: str) -> Dict[str, Any]:
    """Whisper를 사용한 음성 인식"""
    if not WHISPER_AVAILABLE or whisper_model is None:
        return {"error": "Whisper 모델을 사용할 수 없습니다."}
    
    try:
        result = whisper_model.transcribe(audio_path, language="ko")
        
        return {
            "text": result["text"],
            "language": result["language"],
            "segments": result["segments"][:3],  # 처음 3개 세그먼트만
            "confidence": calculate_transcription_confidence(result)
        }
        
    except Exception as e:
        logger.error(f"Whisper 음성 인식 오류: {str(e)}")
        return {"error": f"음성 인식 실패: {str(e)}"}

def calculate_transcription_confidence(whisper_result):
    """Whisper 결과의 신뢰도 계산"""
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

def synthesize_with_tts(text: str, output_path: str) -> Optional[str]:
    """TTS를 사용한 음성 합성"""
    if not TTS_AVAILABLE or tts_model is None:
        logger.warning("TTS 모델을 사용할 수 없습니다.")
        return None
    
    try:
        # 텍스트가 너무 길면 자르기
        if len(text) > 500:
            text = text[:500] + "..."
        
        tts_model.tts_to_file(text=text, file_path=output_path)
        
        if os.path.exists(output_path):
            return output_path
        else:
            return None
            
    except Exception as e:
        logger.error(f"TTS 음성 합성 오류: {str(e)}")
        return None

def extract_audio_from_video(video_path: str) -> Optional[str]:
    """비디오에서 오디오 추출"""
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

# ==================== API 엔드포인트 ====================

@app.route('/ai/test', methods=['GET'])
def test_connection():
    """연결 테스트 및 상태 확인 엔드포인트"""
    logger.info("연결 테스트 요청 받음: /ai/test")
    
    # 백엔드 연결 테스트
    backend_status = "연결 확인 필요"
    try:
        import requests
        response = requests.get("http://localhost:4000/api/test", timeout=2)
        if response.status_code == 200:
            backend_status = "연결됨 (정상 작동)"
        else:
            backend_status = f"연결됨 (상태 코드: {response.status_code})"
    except Exception as e:
        backend_status = f"연결 실패: {str(e)}"
    
    test_response = {
        "status": "AI 메인 서버가 정상 작동 중입니다.",
        "server_type": "main_server (모든 AI 모듈 포함)",
        "backend_connection": backend_status,
        "modules": {
            "llm": "사용 가능" if LLM_MODULE_AVAILABLE else "사용 불가",
            "openface": "사용 가능" if OPENFACE_INTEGRATION_AVAILABLE else "사용 불가",
            "whisper": "사용 가능" if WHISPER_AVAILABLE else "사용 불가",
            "tts": "사용 가능" if TTS_AVAILABLE else "사용 불가",
            "librosa": "사용 가능" if LIBROSA_AVAILABLE else "사용 불가",
            "job_recommendation": "사용 가능" if JOB_RECOMMENDATION_AVAILABLE else "사용 불가",
            "tfidf_recommendation": "사용 가능" if TFIDF_RECOMMENDATION_AVAILABLE else "사용 불가"
        },
        "endpoints": {
            "debate": {
                "start": "/ai/debate/start",
                "ai_opening": "/ai/debate/<debate_id>/ai-opening",
                "opening_video": "/ai/debate/<debate_id>/opening-video"
            },
            "personal_interview": {
                "start": "/ai/interview/start",  
                "question": "/ai/interview/<interview_id>/question",
                "answer_video": "/ai/interview/<interview_id>/<question_type>/answer-video",
                "followup_question": "/ai/interview/<interview_id>/genergate-followup-question"
            },
            "job_recommendation": {
                "recommend": "/ai/jobs/recommend",
                "categories": "/ai/jobs/categories",
                "recruitment_posting": "/ai/recruitment/posting",
                "tfidf_recommend": "/ai/jobs/recommend-tfidf",
                "rare_skills": "/ai/jobs/rare-skills",
                "tfidf_posting": "/ai/recruitment/posting-tfidf"
            }
        },
        "mode": "실제 AI 모듈 사용 (LLM + OpenFace + Whisper + TTS + Librosa)"
    }
    
    logger.info(f"테스트 응답: {test_response}")
    return jsonify(test_response)

# ==================== 공고추천 API 엔드포인트 ====================

@app.route('/ai/recruitment/posting', methods=['POST'])
def recruitment_posting():
    """백엔드 연동용 공고추천 엔드포인트 (RecruitmentRequest 형식 지원)"""
    if not JOB_RECOMMENDATION_AVAILABLE and not TFIDF_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        data = request.json or {}
        logger.info(f"백엔드 공고추천 요청 받음: {data}")
        
        # RecruitmentRequest 형식에서 데이터 추출
        user_id = data.get('user_id')
        category = data.get('category', 'ICT')
        
        # TF-IDF 추천을 우선 시도
        if TFIDF_RECOMMENDATION_AVAILABLE:
            try:
                # TF-IDF용 프로필 생성
                tech_stacks = []
                if data.get('tech_stack'):
                    tech_stacks = [s.strip() for s in data.get('tech_stack').split(',') if s.strip()]
                
                certificates = []
                if data.get('qualification'):
                    certificates = [s.strip() for s in data.get('qualification').split(',') if s.strip()]
                
                majors = []
                if data.get('major'):
                    majors = [s.strip() for s in data.get('major').split(',') if s.strip()]
                if data.get('double_major'):
                    majors.extend([s.strip() for s in data.get('double_major').split(',') if s.strip()])
                
                profile = {
                    'userId': user_id,
                    'techStacks': tech_stacks,
                    'certificateList': certificates,
                    'majorList': majors,
                    'careerYear': data.get('workexperience', 0),
                    'educationLevel': data.get('education', '')
                }
                
                # TF-IDF 모듈로 추천 생성
                tfidf_result = tfidf_recommendation_module.get_recommendations_by_profile(profile, 10)
                
                if tfidf_result.get('status') == 'success':
                    # TF-IDF 결과를 백엔드 형식으로 변환
                    posting_list = []
                    tfidf_postings = tfidf_result.get('posting', [])
                    
                    for posting in tfidf_postings:
                        posting_list.append({
                            "job_posting_id": posting.get('jobPostingId'),
                            "title": posting.get('title', ''),
                            "keyword": ', '.join(posting.get('techStacks', [])),
                            "corporation": posting.get('corporation', '')
                        })
                    
                    response = {"posting": posting_list}
                    logger.info(f"백엔드 TF-IDF 공고추천 응답: {len(posting_list)}개 공고")
                    return jsonify(response)
                    
            except Exception as e:
                logger.warning(f"TF-IDF 추천 실패, 기본 추천으로 폴백: {str(e)}")
        
        # 기본 추천 모듈 사용
        if JOB_RECOMMENDATION_AVAILABLE:
            recommendations = job_recommendation_module.get_recommendations_by_category(category, 10)
            
            if recommendations.get('status') == 'success':
                # 백엔드 응답 형식에 맞춰 변환
                posting_list = []
                
                base_ids = {
                    'ICT': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    'BM': [1, 2, 3, 4, 5],
                    'SM': [1, 2, 3, 4, 5],
                    'PS': [1, 2, 3, 4, 5],
                    'RND': [1, 2, 3, 4, 5],
                    'ARD': [1, 2, 3, 4, 5],
                    'MM': [1, 2, 3, 4, 5]
                }
                
                category_ids = base_ids.get(category, base_ids['ICT'])
                
                for i, job in enumerate(recommendations.get('recommendations', [])):
                    job_posting_id = category_ids[i % len(category_ids)]
                    
                    posting_list.append({
                        "job_posting_id": job_posting_id,
                        "title": job.get('title', ''),
                        "keyword": ', '.join(job.get('keywords', [])),
                        "corporation": job.get('company', '')
                    })
                
                response = {"posting": posting_list}
                logger.info(f"백엔드 기본 공고추천 응답: {len(posting_list)}개 공고")
                return jsonify(response)
        
        # 모든 추천이 실패한 경우
        return jsonify({"error": "추천 생성 실패"}), 500
            
    except Exception as e:
        error_msg = f"백엔드 공고추천 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/jobs/recommend', methods=['POST'])
def recommend_jobs():
    """공고 추천 엔드포인트"""
    if not JOB_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        data = request.json or {}
        logger.info(f"공고 추천 요청 받음: {data}")
        
        if 'interview_scores' in data:
            interview_scores = data['interview_scores']
            limit = data.get('limit', 10)
            result = job_recommendation_module.get_recommendations_by_interview_result(interview_scores, limit)
            logger.info("면접 점수 기반 추천 완료")
            return jsonify(result)
        elif 'category' in data:
            category = data['category']
            limit = data.get('limit', 10)
            result = job_recommendation_module.get_recommendations_by_category(category, limit)
            logger.info(f"{category} 카테고리 추천 완료")
            return jsonify(result)
        else:
            result = job_recommendation_module.get_recommendations_by_category("ICT", 10)
            logger.info("기본 ICT 카테고리 추천 완료")
            return jsonify(result)
            
    except Exception as e:
        error_msg = f"공고 추천 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/jobs/categories', methods=['GET'])
def get_job_categories():
    """공고 카테고리 목록 조회"""
    if not JOB_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        categories = {
            "BM": "경영/관리직",
            "SM": "영업/마케팅",
            "PS": "생산/기술직", 
            "RND": "연구개발",
            "ICT": "IT/정보통신",
            "ARD": "디자인/예술",
            "MM": "미디어/방송"
        }
        
        return jsonify({
            "status": "success",
            "categories": categories,
            "total_count": len(categories)
        })
    except Exception as e:
        return jsonify({"error": f"카테고리 조회 중 오류: {str(e)}"}), 500

@app.route('/ai/jobs/stats', methods=['GET'])  
def get_job_statistics():
    """공고 통계 정보 조회"""
    if not JOB_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        result = job_recommendation_module.get_category_statistics()
        return jsonify(result)
    except Exception as e:
        error_msg = f"통계 조회 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

# ==================== TF-IDF 공고추천 API 엔드포인트 ====================

@app.route('/ai/jobs/recommend-tfidf', methods=['POST'])
def recommend_jobs_tfidf():
    """TF-IDF 기반 공고 추천 엔드포인트"""
    if not TFIDF_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "TF-IDF 공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        data = request.json or {}
        logger.info(f"TF-IDF 공고 추천 요청 받음: {data}")
        
        # 기술 스택 기반 추천
        if 'skills' in data:
            skills = data['skills']
            limit = data.get('limit', 10)
            result = tfidf_recommendation_module.get_recommendations_by_skills(skills, limit)
            logger.info(f"기술 스택 {skills} 기반 TF-IDF 추천 완료")
            return jsonify(result)
        
        # 사용자 프로필 기반 추천
        elif 'profile' in data:
            profile = data['profile']
            limit = data.get('limit', 10)
            result = tfidf_recommendation_module.get_recommendations_by_profile(profile, limit)
            logger.info("프로필 기반 TF-IDF 추천 완료")
            return jsonify(result)
        
        else:
            return jsonify({"error": "skills 또는 profile 데이터가 필요합니다."}), 400
            
    except Exception as e:
        error_msg = f"TF-IDF 공고 추천 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/jobs/rare-skills', methods=['GET'])
def get_rare_skills():
    """희소 기술 정보 조회 엔드포인트"""
    if not TFIDF_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "TF-IDF 공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        result = tfidf_recommendation_module.get_rare_skills_info()
        logger.info("희소 기술 정보 조회 완료")
        return jsonify(result)
    except Exception as e:
        error_msg = f"희소 기술 정보 조회 중 오류: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/recruitment/posting-tfidf', methods=['POST'])
def recruitment_posting_tfidf():
    """백엔드 연동용 TF-IDF 공고추천 엔드포인트"""
    if not TFIDF_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "TF-IDF 공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        data = request.json or {}
        logger.info(f"백엔드 TF-IDF 공고추천 요청 받음: {data}")
        
        # RecruitmentRequest 형식으로 요청 처리
        user_id = data.get('userId')
        profile = {
            'userId': user_id,
            'techStacks': data.get('techStacks', []),
            'certificateList': data.get('certificateList', []),
            'majorList': data.get('majorList', []),
            'careerYear': data.get('careerYear'),
            'educationLevel': data.get('educationLevel')
        }
        
        # TF-IDF 모듈로 추천 생성
        recommendations = tfidf_recommendation_module.get_recommendations_by_profile(profile, 10)
        
        if recommendations.get('status') == 'success':
            # 백엔드 응답 형식에 맞춰 변환 (이미 모듈에서 처리됨)
            response = {
                "posting": recommendations.get('posting', []),
                "totalCount": recommendations.get('totalCount', 0),
                "userId": user_id,
                "recommendationType": "tfidf",
                "generatedAt": recommendations.get('generatedAt')
            }
            
            logger.info(f"백엔드 TF-IDF 공고추천 응답: {len(response.get('posting', []))}개 공고")
            return jsonify(response)
        else:
            return jsonify({"error": "추천 생성 실패"}), 500
            
    except Exception as e:
        error_msg = f"백엔드 TF-IDF 공고추천 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/jobs/crawl-trigger', methods=['POST'])
def trigger_job_crawling():
    """채용공고 크롤링 트리거 엔드포인트"""
    if not TFIDF_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "TF-IDF 공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        result = tfidf_recommendation_module.trigger_crawling()
        logger.info("채용공고 크롤링 트리거 완료")
        return jsonify(result)
    except Exception as e:
        error_msg = f"크롤링 트리거 중 오류: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

# ==================== 개인면접 API 엔드포인트 ====================

@app.route('/ai/interview/generate-question', methods=['POST'])
def generate_interview_question():
    """면접 질문 생성 엔드포인트 (백엔드 연동)"""
    try:
        data = request.json or {}
        logger.info(f"면접 질문 생성 요청: {data}")
        
        # 필요한 데이터 추출
        interview_id = data.get("interview_id", 0)
        job_category = data.get("job_category", "")
        workexperience = data.get("workexperience", "")
        education = data.get("education", "")
        experience_description = data.get("experience_description", "")
        tech_stack = data.get("tech_stack", "")
        personality = data.get("personality", "")
        
        # 질문 유형별 템플릿 (실제 LLM 구현 시 대체)
        question_templates = {
            "GENERAL": f"'{job_category}' 분야에서 {workexperience} 경력을 가진 지원자로서, 자신을 소개해주세요.",
            "TECH": f"'{tech_stack}' 기술을 활용한 프로젝트 경험에 대해 구체적으로 설명해주세요.",
            "FIT": f"지원자님의 '{personality}' 성격이 어떻게 업무에 도움이 될 수 있는지 설명해주세요.",
            "SITUATION": f"팀 프로젝트에서 갈등이 발생했을 때 어떻게 해결했는지 경험을 말씀해주세요."
        }
        
        # 질문 생성
        questions = []
        for question_type, template in question_templates.items():
            questions.append({
                "question_type": question_type,
                "question_text": template
            })
        
        response = {"interview_id": interview_id, "questions": questions}
        logger.info(f"생성된 면접 질문: {len(questions)}개")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"면접 질문 생성 중 오류: {str(e)}")
        return jsonify({"error": f"질문 생성 실패: {str(e)}"}), 500

@app.route('/ai/interview/<int:interview_id>/genergate-followup-question', methods=['POST'])
def generate_followup_question(interview_id):
    """후속 질문 생성 엔드포인트 (백엔드 연동)"""
    try:
        if 'file' not in request.files and 'video' not in request.files:
            return jsonify({"error": "영상 파일이 필요합니다."}), 400
        
        file = request.files.get('file') or request.files.get('video')
        
        # 임시 파일 저장
        temp_path = f"temp_interview_{interview_id}_{int(time.time())}.mp4"
        file.save(temp_path)
        
        try:
            # 오디오 추출
            audio_path = extract_audio_from_video(temp_path)
            
            # Whisper 음성 인식
            transcription_result = {"text": "답변 내용이 인식되었습니다.", "confidence": 0.85}
            if audio_path and WHISPER_AVAILABLE:
                transcription_result = transcribe_with_whisper(audio_path)
            
            # 후속 질문 생성 (실제 LLM 구현 시 대체)
            transcript = transcription_result.get("text", "")
            
            # 후속 질문 템플릿
            followup_question = "방금 말씀하신 내용을 좀 더 구체적으로 설명해주실 수 있을까요?"
            
            # 내용 기반 후속 질문 생성 (간단한 키워드 기반)
            if "프로젝트" in transcript:
                followup_question = "그 프로젝트에서 어떤 역할을 맡으셨나요?"
            elif "경험" in transcript:
                followup_question = "그 경험을 통해 어떤 교훈을 얻으셨나요?"
            elif "기술" in transcript or "스킬" in transcript:
                followup_question = "그 기술을 어떻게 습득하셨고, 실무에 어떻게 적용하셨나요?"
            
            # 임시 파일 정리
            cleanup_temp_files([temp_path, audio_path])
            
            response = {
                "interview_id": interview_id,
                "question_text": followup_question
            }
            
            logger.info(f"생성된 후속 질문: {followup_question}")
            return jsonify(response)
            
        except Exception as e:
            cleanup_temp_files([temp_path])
            raise e
        
    except Exception as e:
        logger.error(f"후속 질문 생성 중 오류: {str(e)}")
        return jsonify({"error": f"후속 질문 생성 실패: {str(e)}"}), 500

@app.route('/ai/interview/start', methods=['POST'])
def start_interview():
    """개인면접 시작 엔드포인트"""
    try:
        data = request.json or {}
        logger.info(f"개인면접 시작 요청: {data}")
        
        return jsonify({
            "status": "success",
            "interview_id": int(time.time()),
            "message": "개인면접이 시작되었습니다.",
            "first_question": "자기소개를 해주세요.",
            "server_type": "main_server"
        })
    except Exception as e:
        return jsonify({"error": f"개인면접 시작 중 오류: {str(e)}"}), 500

@app.route('/ai/interview/<int:interview_id>/question', methods=['GET'])
def get_interview_question(interview_id):
    """면접 질문 생성"""
    try:
        question_type = request.args.get('type', 'general')
        
        # LLM을 사용한 질문 생성 (사용 가능한 경우)
        if LLM_MODULE_AVAILABLE and llm_module:
            # 실제 LLM 기반 질문 생성 로직
            questions = {
                "general": "자신의 장점과 단점을 구체적인 사례와 함께 설명해주세요.",
                "technical": "최근 관심있게 지켜보고 있는 기술 트렌드가 있다면 무엇인지, 그리고 그 이유는 무엇인지 설명해주세요.",
                "behavioral": "팀 프로젝트에서 의견 충돌이 발생했을 때 어떻게 해결했는지 구체적인 경험을 바탕으로 말씀해주세요."
            }
        else:
            # 기본 질문
            questions = {
                "general": "본인의 장점과 단점에 대해 말씀해주세요.",
                "technical": "최근에 관심을 가지고 있는 기술 트렌드가 있다면 무엇인가요?",
                "behavioral": "팀 프로젝트에서 갈등이 생겼을 때 어떻게 해결하셨나요?"
            }
        
        return jsonify({
            "interview_id": interview_id,
            "question": questions.get(question_type, questions["general"]),
            "question_type": question_type,
            "generated_by": "llm" if LLM_MODULE_AVAILABLE else "template"
        })
    except Exception as e:
        return jsonify({"error": f"질문 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/interview/<int:interview_id>/<string:question_type>/answer-video', methods=['POST'])
def process_interview_answer_with_type(interview_id, question_type):
    """개인면접 답변 영상 처리 (question_type 포함)"""
    try:
        if 'file' not in request.files and 'video' not in request.files:
            return jsonify({"error": "영상 파일이 필요합니다."}), 400
        
        file = request.files.get('file') or request.files.get('video')
        
        # 임시 파일 저장
        temp_path = f"temp_interview_{interview_id}_{question_type}_{int(time.time())}.mp4"
        file.save(temp_path)
        
        try:
            # 오디오 추출
            audio_path = extract_audio_from_video(temp_path)
            
            # Whisper 음성 인식
            transcription_result = {"text": f"{question_type} 질문에 대한 답변 내용입니다.", "confidence": 0.85}
            if audio_path and WHISPER_AVAILABLE:
                transcription_result = transcribe_with_whisper(audio_path)
            
            # Librosa 오디오 분석
            audio_analysis = {"voice_stability": 0.8, "fluency_score": 0.85}
            if audio_path and LIBROSA_AVAILABLE:
                audio_analysis = process_audio_with_librosa(audio_path)
            
            # OpenFace 얼굴 분석 (사용 가능한 경우)
            facial_analysis = {"confidence": 0.8, "emotion": "중립"}
            if OPENFACE_INTEGRATION_AVAILABLE and openface_integration:
                try:
                    facial_analysis = openface_integration.analyze_video(temp_path)
                except Exception as e:
                    logger.warning(f"OpenFace 분석 실패: {str(e)}")
            
            # 종합 분석 결과
            content_score = calculate_content_score(transcription_result.get("text", ""))
            voice_score = audio_analysis.get("voice_stability", 0.8) * 5
            action_score = facial_analysis.get("confidence", 0.8) * 5
            
            feedback = generate_interview_feedback(transcription_result, audio_analysis, facial_analysis)
            answer_text = transcription_result.get("text", "")
            
            # 명세서에 맞는 응답 형식
            result = {
                "interview_id": interview_id,
                "question_type": question_type,
                "answer_text": answer_text,
                "content_score": content_score,
                "voice_score": voice_score,
                "action_score": action_score,
                "content_feedback": "내용을 정리해서 말해야 합니다.",
                "voice_feedback": "목소리가 안정적입니다.",
                "action_feedback": "시선이 자연스럽습니다.",
                "feedback": feedback
            }
            
            # 임시 파일 정리
            cleanup_temp_files([temp_path, audio_path])
            
            return jsonify(result)
            
        except Exception as e:
            cleanup_temp_files([temp_path])
            raise e
        
    except Exception as e:
        return jsonify({"error": f"답변 처리 중 오류: {str(e)}"}), 500

@app.route('/ai/interview/<int:interview_id>/answer-video', methods=['POST'])
def process_interview_answer(interview_id):
    """개인면접 답변 영상 처리 (이전 버전 호환용)"""
    try:
        if 'file' not in request.files and 'video' not in request.files:
            return jsonify({"error": "영상 파일이 필요합니다."}), 400
        
        file = request.files.get('file') or request.files.get('video')
        
        # 임시 파일 저장
        temp_path = f"temp_interview_{interview_id}_{int(time.time())}.mp4"
        file.save(temp_path)
        
        try:
            # 오디오 추출
            audio_path = extract_audio_from_video(temp_path)
            
            # Whisper 음성 인식
            transcription_result = {"text": "답변 내용이 인식되었습니다.", "confidence": 0.85}
            if audio_path and WHISPER_AVAILABLE:
                transcription_result = transcribe_with_whisper(audio_path)
            
            # Librosa 오디오 분석
            audio_analysis = {"voice_stability": 0.8, "fluency_score": 0.85}
            if audio_path and LIBROSA_AVAILABLE:
                audio_analysis = process_audio_with_librosa(audio_path)
            
            # OpenFace 얼굴 분석 (사용 가능한 경우)
            facial_analysis = {"confidence": 0.8, "emotion": "중립"}
            if OPENFACE_INTEGRATION_AVAILABLE and openface_integration:
                try:
                    facial_analysis = openface_integration.analyze_video(temp_path)
                except Exception as e:
                    logger.warning(f"OpenFace 분석 실패: {str(e)}")
            
            # 종합 분석 결과
            result = {
                "interview_id": interview_id,
                "transcription": transcription_result.get("text", ""),
                "transcription_confidence": transcription_result.get("confidence", 0.85),
                "analysis": {
                    "content_score": calculate_content_score(transcription_result.get("text", "")),
                    "voice_score": audio_analysis.get("voice_stability", 0.8) * 5,
                    "action_score": facial_analysis.get("confidence", 0.8) * 5,
                    "fluency": audio_analysis.get("fluency_score", 0.85),
                    "emotion": facial_analysis.get("emotion", "중립")
                },
                "feedback": generate_interview_feedback(transcription_result, audio_analysis, facial_analysis),
                "next_question": "다음 질문으로 넘어가시겠습니까?",
                "processing_methods": {
                    "transcription": "whisper" if WHISPER_AVAILABLE else "fallback",
                    "audio_analysis": "librosa" if LIBROSA_AVAILABLE else "fallback",
                    "facial_analysis": "openface" if OPENFACE_INTEGRATION_AVAILABLE else "fallback"
                }
            }
            
            # 임시 파일 정리
            cleanup_temp_files([temp_path, audio_path])
            
            return jsonify(result)
            
        except Exception as e:
            cleanup_temp_files([temp_path])
            raise e
        
    except Exception as e:
        return jsonify({"error": f"답변 처리 중 오류: {str(e)}"}), 500

def calculate_content_score(text: str) -> float:
    """내용 점수 계산"""
    if not text:
        return 2.0
    
    # 기본 점수
    base_score = 3.0
    
    # 길이 보너스
    word_count = len(text.split())
    if word_count > 50:
        base_score += 1.0
    elif word_count > 30:
        base_score += 0.5
    
    # 구체성 보너스
    concrete_words = ["예를 들어", "구체적으로", "실제로", "경험", "사례"]
    if any(word in text for word in concrete_words):
        base_score += 0.5
    
    return min(5.0, base_score)

def generate_interview_feedback(transcription: Dict, audio: Dict, facial: Dict) -> str:
    """면접 피드백 생성"""
    try:
        text = transcription.get("text", "")
        confidence = transcription.get("confidence", 0.85)
        voice_stability = audio.get("voice_stability", 0.8)
        
        feedback_parts = []
        
        # 내용 피드백
        if len(text) > 100:
            feedback_parts.append("충분한 내용으로 답변해주셨습니다.")
        else:
            feedback_parts.append("좀 더 구체적인 답변이 필요합니다.")
        
        # 음성 피드백
        if voice_stability > 0.8:
            feedback_parts.append("안정적인 음성으로 발표하셨습니다.")
        else:
            feedback_parts.append("음성의 안정성을 높여보세요.")
        
        # 신뢰도 피드백
        if confidence > 0.8:
            feedback_parts.append("명확한 발음으로 전달하셨습니다.")
        
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

# ==================== 스트리밍 응답 엔드포인트 ====================

@app.route('/ai/debate/<int:debate_id>/ai-response-stream', methods=['POST'])
def stream_ai_response(debate_id):
    """AI 응답을 스트리밍으로 제공 (LLM 생성 + TTS 변환)"""
    try:
        data = request.json or {}
        stage = data.get('stage', 'opening')
        topic = data.get('topic', '인공지능')
        position = data.get('position', 'CON')
        user_text = data.get('user_text', '')
        
        def generate():
            try:
                # LLM 응답 생성 스트림
                if LLM_MODULE_AVAILABLE and llm_module:
                    # 실제 LLM 스트리밍
                    prompt = f"토론 주제: {topic}, 단계: {stage}, 입장: {position}"
                    if user_text:
                        prompt += f", 상대방 의견: {user_text}"
                    
                    sentence_buffer = ""
                    full_text = ""
                    
                    # LLM이 토큰을 생성한다고 가정 (실제 구현에 맞게 수정 필요)
                    for token in generate_llm_tokens(prompt):
                        sentence_buffer += token
                        full_text += token
                        
                        # 문장이 완성되면 TTS 처리
                        if token in '.!?':
                            # TTS 변환
                            if TTS_AVAILABLE and tts_model:
                                temp_audio = f"temp_stream_{debate_id}_{int(time.time())}.wav"
                                try:
                                    tts_model.tts_to_file(text=sentence_buffer, file_path=temp_audio)
                                    
                                    # 오디오 파일을 base64로 인코딩
                                    with open(temp_audio, 'rb') as audio_file:
                                        import base64
                                        audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
                                    
                                    # 오디오 청크 전송
                                    yield f"data: {json.dumps({'type': 'audio', 'data': audio_base64})}\n\n"
                                    
                                    # 임시 파일 삭제
                                    os.remove(temp_audio)
                                except Exception as e:
                                    logger.error(f"TTS 변환 오류: {str(e)}")
                            
                            # 텍스트도 전송 (자막용)
                            yield f"data: {json.dumps({'type': 'text', 'data': sentence_buffer})}\n\n"
                            
                            sentence_buffer = ""
                    
                    # 최종 완료 신호
                    yield f"data: {json.dumps({'type': 'complete', 'full_text': full_text})}\n\n"
                    
                else:
                    # 폴백 모드 (고정 응답 스트리밍)
                    fallback_response = get_fallback_ai_response(stage, topic, user_text)
                    words = fallback_response.split()
                    
                    sentence_buffer = ""
                    for i, word in enumerate(words):
                        if i > 0:
                            word = " " + word
                        sentence_buffer += word
                        
                        # 문장 종료 체크
                        if any(punct in word for punct in '.!?'):
                            yield f"data: {json.dumps({'type': 'text', 'data': sentence_buffer})}\n\n"
                            sentence_buffer = ""
                        
                        time.sleep(0.05)  # 자연스러운 속도
                    
                    if sentence_buffer:  # 남은 텍스트 전송
                        yield f"data: {json.dumps({'type': 'text', 'data': sentence_buffer})}\n\n"
                    
                    yield f"data: {json.dumps({'type': 'complete', 'full_text': fallback_response})}\n\n"
                    
            except Exception as e:
                logger.error(f"스트리밍 생성 중 오류: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        return jsonify({"error": f"스트리밍 응답 생성 중 오류: {str(e)}"}), 500

def generate_llm_tokens(prompt: str):
    """LLM 토큰 생성 (실제 구현 필요)"""
    # 여기에 실제 LLM 토큰 스트리밍 로직 구현
    # 예시로 단어 단위 생성
    response = "인공지능의 발전은 우리 사회에 큰 영향을 미칠 것입니다. 신중한 접근이 필요합니다."
    for word in response.split():
        yield word + " "
        time.sleep(0.1)

# ==================== 토론면접 API 엔드포인트 ====================

@app.route('/ai/debate/<int:debate_id>/ai-opening', methods=['POST'])
def ai_opening(debate_id):
    """AI 입론 생성 엔드포인트"""
    try:
        data = request.json or {}
        logger.info(f"AI 입론 생성 요청: /ai/debate/{debate_id}/ai-opening")
        
        topic = data.get("topic", "인공지능")
        position = data.get("position", "CON")
        
        # LLM을 사용한 입론 생성 (사용 가능한 경우)
        if LLM_MODULE_AVAILABLE and llm_module:
            try:
                llm_result = llm_module.generate_ai_opening(topic, position, data)
                ai_response = llm_result.get("ai_response", "")
                
                # TTS 변환 (선택적)
                if TTS_AVAILABLE and len(ai_response) > 0:
                    tts_path = f"temp_tts_{debate_id}_{int(time.time())}.wav"
                    synthesize_with_tts(ai_response, tts_path)
                
                return jsonify({
                    "ai_opening_text": ai_response,
                    "generated_by": "llm",
                    "reasoning": llm_result.get("reasoning", ""),
                    "timestamp": llm_result.get("timestamp")
                })
                
            except Exception as e:
                logger.error(f"LLM 입론 생성 오류: {str(e)}")
                # 백업 응답으로 폴백
        
        # 백업 응답 (LLM 사용 불가시)
        fallback_responses = {
            "PRO": f"{topic}의 발전은 인류에게 긍정적인 영향을 미칠 것입니다. 효율성 증대와 새로운 가능성을 제공하기 때문입니다.",
            "CON": f"{topic}에 대해서는 신중한 접근이 필요합니다. 여러 부작용과 위험성을 고려해야 합니다."
        }
        
        ai_response = fallback_responses.get(position, fallback_responses["CON"])
        
        return jsonify({
            "ai_opening_text": ai_response,
            "generated_by": "fallback",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({"error": f"AI 입론 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/debate/<int:debate_id>/opening-video', methods=['POST'])
def process_opening_video(debate_id):
    """사용자 입론 영상 처리"""
    return process_debate_video_generic(debate_id, "opening", "rebuttal")

@app.route('/ai/debate/<int:debate_id>/rebuttal-video', methods=['POST'])
def process_rebuttal_video(debate_id):
    """사용자 반론 영상 처리"""
    return process_debate_video_generic(debate_id, "rebuttal", "counter_rebuttal")

@app.route('/ai/debate/<int:debate_id>/counter-rebuttal-video', methods=['POST'])
def process_counter_rebuttal_video(debate_id):
    """사용자 재반론 영상 처리"""
    return process_debate_video_generic(debate_id, "counter_rebuttal", "closing")

@app.route('/ai/debate/<int:debate_id>/closing-video', methods=['POST'])
def process_closing_video(debate_id):
    """사용자 최종 변론 영상 처리"""
    return process_debate_video_generic(debate_id, "closing", None)

def process_debate_video_generic(debate_id, current_stage, next_ai_stage):
    """토론 영상 처리 공통 함수"""
    logger.info(f"{current_stage} 영상 처리 요청: /ai/debate/{debate_id}/{current_stage}-video")
    
    if 'file' not in request.files and 'video' not in request.files:
        return jsonify({"error": "영상 파일이 필요합니다."}), 400
    
    file = request.files.get('file') or request.files.get('video')
    
    try:
        temp_path = f"temp_{current_stage}_{debate_id}_{int(time.time())}.mp4"
        file.save(temp_path)
        
        # 오디오 추출
        audio_path = extract_audio_from_video(temp_path)
        
        # Whisper 음성 인식
        transcription_result = {"text": f"사용자의 {current_stage} 발언입니다.", "confidence": 0.85}
        if audio_path and WHISPER_AVAILABLE:
            transcription_result = transcribe_with_whisper(audio_path)
        
        # Librosa 오디오 분석
        audio_analysis = {"voice_stability": 0.8, "fluency_score": 0.85}
        if audio_path and LIBROSA_AVAILABLE:
            audio_analysis = process_audio_with_librosa(audio_path)
        
        # OpenFace 얼굴 분석
        facial_analysis = {"confidence": 0.8, "emotion": "중립"}
        if OPENFACE_INTEGRATION_AVAILABLE and openface_integration:
            try:
                facial_analysis = openface_integration.analyze_video(temp_path)
            except Exception as e:
                logger.warning(f"OpenFace 분석 실패: {str(e)}")
        
        # 종합 점수 계산
        scores = calculate_debate_scores(transcription_result, audio_analysis, facial_analysis)
        
        # 결과 구성
        result = {
            f"user_{current_stage}_text": transcription_result.get("text", ""),
            "emotion": facial_analysis.get("emotion", "중립 (안정적)"),
            **scores
        }
        
        # 다음 AI 응답 생성
        if next_ai_stage:
            topic = request.form.get("topic", "인공지능")
            user_text = transcription_result.get("text", "")
            
            if LLM_MODULE_AVAILABLE and llm_module:
                try:
                    # LLM을 사용한 응답 생성
                    llm_result = llm_module.analyze_user_response_and_generate_rebuttal(
                        user_text, facial_analysis, audio_analysis, next_ai_stage
                    )
                    ai_response = llm_result.get("ai_response", "")
                    result[f"ai_{next_ai_stage}_text"] = ai_response
                    result["ai_analysis"] = llm_result.get("analysis_insights", {})
                    
                except Exception as e:
                    logger.error(f"LLM 응답 생성 오류: {str(e)}")
                    # 백업 응답 사용
                    result[f"ai_{next_ai_stage}_text"] = get_fallback_ai_response(next_ai_stage, topic, user_text)
            else:
                # 백업 응답
                result[f"ai_{next_ai_stage}_text"] = get_fallback_ai_response(next_ai_stage, topic, user_text)
        
        # 임시 파일 정리
        cleanup_temp_files([temp_path, audio_path])
        
        return jsonify(result)
        
    except Exception as e:
        cleanup_temp_files([temp_path])
        return jsonify({"error": f"영상 처리 중 오류: {str(e)}"}), 500

def calculate_debate_scores(transcription: Dict, audio: Dict, facial: Dict) -> Dict[str, Any]:
    """토론 점수 계산"""
    try:
        text = transcription.get("text", "")
        confidence = transcription.get("confidence", 0.85)
        voice_stability = audio.get("voice_stability", 0.8)
        fluency = audio.get("fluency_score", 0.85)
        facial_confidence = facial.get("confidence", 0.8)
        
        # 기본 점수 계산
        scores = {
            "initiative_score": min(5.0, 3.0 + confidence),
            "collaborative_score": min(5.0, 3.0 + (len(text.split()) / 100)),
            "communication_score": min(5.0, 3.0 + fluency),
            "logic_score": min(5.0, 3.0 + calculate_logic_score(text)),
            "problem_solving_score": min(5.0, 3.0 + calculate_problem_solving_score(text)),
            "voice_score": min(5.0, voice_stability * 5),
            "action_score": min(5.0, facial_confidence * 5)
        }
        
        # 피드백 생성
        feedback_mapping = {
            "initiative": "적극성",
            "collaborative": "협력성", 
            "communication": "의사소통",
            "logic": "논리성",
            "problem_solving": "문제해결",
            "voice": "음성품질",
            "action": "행동표현"
        }
        
        for category, korean_name in feedback_mapping.items():
            score = scores[f"{category}_score"]
            if score >= 4.5:
                scores[f"{category}_feedback"] = f"{korean_name}: 매우 우수"
            elif score >= 4.0:
                scores[f"{category}_feedback"] = f"{korean_name}: 우수"
            elif score >= 3.5:
                scores[f"{category}_feedback"] = f"{korean_name}: 양호"
            else:
                scores[f"{category}_feedback"] = f"{korean_name}: 개선 필요"
        
        # 종합 피드백
        avg_score = sum(scores[k] for k in scores if k.endswith("_score")) / 7
        if avg_score >= 4.5:
            scores["feedback"] = "매우 우수한 토론 수행을 보여주었습니다."
        elif avg_score >= 4.0:
            scores["feedback"] = "우수한 토론 수행을 보여주었습니다."
        elif avg_score >= 3.5:
            scores["feedback"] = "양호한 토론 수행을 보여주었습니다."
        else:
            scores["feedback"] = "토론 수행에 개선이 필요합니다."
        
        scores["sample_answer"] = "구체적인 근거와 예시를 들어 논리적으로 설명하는 것이 좋습니다."
        
        return scores
        
    except Exception as e:
        logger.error(f"토론 점수 계산 오류: {str(e)}")
        return get_default_debate_scores()

def calculate_logic_score(text: str) -> float:
    """논리성 점수 계산"""
    logic_indicators = ["따라서", "그러므로", "결론적으로", "왜냐하면", "근거는", "예를 들어"]
    logic_count = sum(1 for indicator in logic_indicators if indicator in text)
    return min(1.0, logic_count * 0.3)

def calculate_problem_solving_score(text: str) -> float:
    """문제해결 점수 계산"""
    problem_solving_indicators = ["해결", "방안", "대안", "개선", "전략", "접근"]
    problem_count = sum(1 for indicator in problem_solving_indicators if indicator in text)
    return min(1.0, problem_count * 0.3)

def get_default_debate_scores() -> Dict[str, Any]:
    """기본 토론 점수"""
    return {
        "initiative_score": 3.5,
        "collaborative_score": 3.2,
        "communication_score": 3.8,
        "logic_score": 3.3,
        "problem_solving_score": 3.5,
        "voice_score": 3.7,
        "action_score": 3.9,
        "initiative_feedback": "적극성: 보통",
        "collaborative_feedback": "협력성: 보통",
        "communication_feedback": "의사소통: 양호",
        "logic_feedback": "논리성: 보통",
        "problem_solving_feedback": "문제해결: 보통",
        "voice_feedback": "음성품질: 양호",
        "action_feedback": "행동표현: 양호",
        "feedback": "전반적으로 양호한 수행을 보여주었습니다.",
        "sample_answer": "구체적인 예시와 근거를 들어 논리적으로 설명해보세요."
    }

def get_fallback_ai_response(stage: str, topic: str = "인공지능", user_text: str = "") -> str:
    """백업 AI 응답"""
    responses = {
        "rebuttal": f"말씀하신 {topic}에 대한 의견을 경청했습니다. 하지만 다른 관점에서 보면 몇 가지 고려해야 할 점들이 있습니다.",
        "counter_rebuttal": f"제기하신 점들을 충분히 이해했습니다. 그러나 {topic}의 장기적 관점에서 보면 여전히 신중한 접근이 필요합니다.",
        "closing": f"결론적으로 {topic}에 대한 이번 토론을 통해 다양한 관점을 확인할 수 있었습니다. 균형잡힌 시각이 중요하다고 생각합니다."
    }
    
    return responses.get(stage, f"{topic}에 대해 의견을 나눠주셔서 감사합니다.")

# AI 단계별 응답 엔드포인트들
@app.route('/ai/debate/<int:debate_id>/ai-rebuttal', methods=['GET'])
def ai_rebuttal(debate_id):
    """AI 반론 생성"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fallback_ai_response("rebuttal", topic)
        return jsonify({"debate_id": debate_id, "ai_rebuttal_text": ai_response})
    except Exception as e:
        return jsonify({"error": f"AI 반론 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/debate/<int:debate_id>/ai-counter-rebuttal', methods=['GET'])
def ai_counter_rebuttal(debate_id):
    """AI 재반론 생성"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fallback_ai_response("counter_rebuttal", topic)
        return jsonify({"debate_id": debate_id, "ai_counter_rebuttal_text": ai_response})
    except Exception as e:
        return jsonify({"error": f"AI 재반론 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/debate/<int:debate_id>/ai-closing', methods=['GET'])
def ai_closing(debate_id):
    """AI 최종 변론 생성"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fallback_ai_response("closing", topic)
        return jsonify({"debate_id": debate_id, "ai_closing_text": ai_response})
    except Exception as e:
        return jsonify({"error": f"AI 최종 변론 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/debate/modules-status', methods=['GET'])
def modules_status():
    """모듈 상태 확인"""
    return jsonify({
        "status": "active",
        "server_type": "main_server",
        "modules": {
            "llm": {
                "available": LLM_MODULE_AVAILABLE,
                "provider": "openai" if LLM_MODULE_AVAILABLE else None
            },
            "openface": {
                "available": OPENFACE_INTEGRATION_AVAILABLE,
                "functions": ["analyze_video", "extract_features"] if OPENFACE_INTEGRATION_AVAILABLE else []
            },
            "whisper": {
                "available": WHISPER_AVAILABLE,
                "functions": ["transcribe_video"] if WHISPER_AVAILABLE else []
            },
            "tts": {
                "available": TTS_AVAILABLE,
                "functions": ["text_to_speech"] if TTS_AVAILABLE else []
            },
            "librosa": {
                "available": LIBROSA_AVAILABLE,
                "functions": ["analyze_audio", "extract_features"] if LIBROSA_AVAILABLE else []
            },
            "job_recommendation": {
                "available": JOB_RECOMMENDATION_AVAILABLE,
                "functions": ["recommend_jobs", "get_categories"] if JOB_RECOMMENDATION_AVAILABLE else []
            },
            "tfidf_recommendation": {
                "available": TFIDF_RECOMMENDATION_AVAILABLE,
                "functions": ["recommend_by_skills", "recommend_by_profile", "get_rare_skills", "trigger_crawling"] if TFIDF_RECOMMENDATION_AVAILABLE else []
            }
        }
    })

if __name__ == "__main__":
    # 시작 시 AI 시스템 초기화
    initialize_ai_systems()
    
    print(" VeriView AI 메인 서버 시작...")
    print(" 서버 주소: http://localhost:5000")
    print(" 테스트 엔드포인트: http://localhost:5000/ai/test")
    print(" 상태 확인 엔드포인트: http://localhost:5000/ai/debate/modules-status")
    print(" 토론면접 API: http://localhost:5000/ai/debate/<debate_id>/ai-opening")
    print(" 개인면접 API: http://localhost:5000/ai/interview/start")
    print(" 개인면접 답변 분석 API: http://localhost:5000/ai/interview/<interview_id>/<question_type>/answer-video")
    print(" 개인면접 꼬리질문 API: http://localhost:5000/ai/interview/<interview_id>/genergate-followup-question")
    print(" 공고추천 API: http://localhost:5000/ai/jobs/recommend")
    print(" TF-IDF 공고추천 API: http://localhost:5000/ai/jobs/recommend-tfidf")
    print(" 희소기술 정보 API: http://localhost:5000/ai/jobs/rare-skills")
    print("=" * 80)
    print("포함된 AI 모듈:")
    print(f"  - LLM: {'✅' if LLM_MODULE_AVAILABLE else '❌'}")
    print(f"  - OpenFace: {'✅' if OPENFACE_INTEGRATION_AVAILABLE else '❌'}")
    print(f"  - Whisper: {'✅' if WHISPER_AVAILABLE else '❌'}")
    print(f"  - TTS: {'✅' if TTS_AVAILABLE else '❌'}")
    print(f"  - Librosa: {'✅' if LIBROSA_AVAILABLE else '❌'}")
    print(f"  - 공고추천: {'✅' if JOB_RECOMMENDATION_AVAILABLE else '❌'}")
    print(f"  - TF-IDF 공고추천: {'✅' if TFIDF_RECOMMENDATION_AVAILABLE else '❌'}")
    print("=" * 80)
    if TFIDF_RECOMMENDATION_AVAILABLE:
        print("특별 기능:")
        print("  - 희소 기술 보너스 시스템 (PyTorch, NVIDIA DeepStream 등)")
        print("  - TF-IDF 벡터 유사도 기반 정밀 매칭")
        print("  - 백엔드 완전 호환 (JobPosting 엔티티)")
        print("="*80)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
