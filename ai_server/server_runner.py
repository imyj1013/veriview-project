from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import tempfile
import logging
import time
from typing import Dict, Any, Optional

# LLM 미사용 테스트 모듈 임포트
try:
    from test_features.debate.main import DebateTestMain
    from test_features.personal_interview.main import PersonalInterviewTestMain
    DEBATE_MODULE_AVAILABLE = True
    PERSONAL_INTERVIEW_MODULE_AVAILABLE = True
    print("✅ 테스트 모듈 로드 성공: 토론면접 및 개인면접 기능 사용 가능")
except ImportError as e:
    print(f"❌ 테스트 모듈 로드 실패: {e}")
    DEBATE_MODULE_AVAILABLE = False
    PERSONAL_INTERVIEW_MODULE_AVAILABLE = False

# 실시간 분석 모듈 임포트 (선택적)
try:
    from app.modules.realtime_facial_analysis import RealtimeFacialAnalysis
    from app.modules.realtime_speech_to_text import RealtimeSpeechToText
    REALTIME_MODULES_AVAILABLE = True
    print("✅ 실시간 분석 모듈 로드 성공")
except ImportError as e:
    print(f"⚠️ 실시간 분석 모듈 일부 제한: {e}")
    REALTIME_MODULES_AVAILABLE = False

# 공고추천 모듈 임포트 및 초기화
try:
    from job_recommendation_module import JobRecommendationModule
    job_recommendation_module = JobRecommendationModule()
    JOB_RECOMMENDATION_AVAILABLE = True
    print("✅ 공고추천 모듈 로드 성공")
except ImportError as e:
    print(f"❌ 공고추천 모듈 로드 실패: {e}")
    JOB_RECOMMENDATION_AVAILABLE = False
    job_recommendation_module = None

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 전역 변수로 테스트 시스템 초기화
debate_test_system = None
personal_interview_test_system = None
realtime_facial_analyzer = None
realtime_speech_analyzer = None

def initialize_systems():
    """테스트 시스템 및 실시간 분석기 초기화"""
    global debate_test_system, personal_interview_test_system
    global realtime_facial_analyzer, realtime_speech_analyzer
    
    try:
        # 토론면접 테스트 시스템 초기화
        if DEBATE_MODULE_AVAILABLE and debate_test_system is None:
            debate_test_system = DebateTestMain()
            logger.info("토론면접 테스트 시스템 초기화 완료")
        
        # 개인면접 테스트 시스템 초기화
        if PERSONAL_INTERVIEW_MODULE_AVAILABLE and personal_interview_test_system is None:
            personal_interview_test_system = PersonalInterviewTestMain()
            logger.info("개인면접 테스트 시스템 초기화 완료")
        
        # 실시간 분석기 초기화 (선택적)
        if REALTIME_MODULES_AVAILABLE:
            if realtime_facial_analyzer is None:
                realtime_facial_analyzer = RealtimeFacialAnalysis()
                logger.info("실시간 얼굴 분석기 초기화 완료")
            if realtime_speech_analyzer is None:
                realtime_speech_analyzer = RealtimeSpeechToText(model="tiny")
                logger.info("실시간 음성 분석기 초기화 완료")
                
    except Exception as e:
        logger.error(f"시스템 초기화 실패: {str(e)}")

# 고정 응답을 위한 도우미 함수
def get_fixed_ai_response(stage, topic="인공지능", user_text=None, debate_id=None):
    """토론 단계별 고정 AI 응답 생성"""
    responses = {
        "opening": f"{topic}의 발전은 인류에게 긍정적인 영향을 미칠 것입니다. 효율성 증대와 새로운 가능성을 제공하기 때문입니다.",
        "rebuttal": f"말씀하신 우려사항도 있지만, {topic}의 장점이 더 크다고 생각합니다. 적절한 규제와 함께 발전시켜 나가면 될 것입니다.",
        "counter_rebuttal": f"규제만으로는 한계가 있을 수 있지만, {topic} 기술 자체의 발전을 통해 문제를 해결할 수 있습니다.",
        "closing": f"결론적으로 {topic}은 인류의 미래를 위한 필수적인 기술입니다. 신중한 접근과 함께 적극적으로 활용해야 합니다."
    }
    return responses.get(stage, f"{topic}에 대한 의견을 말씀드리겠습니다.")

# 분석기 초기화 함수
def initialize_analyzers():
    """실시간 분석기 별칭"""
    initialize_systems()

# 고정 분석기 참조
facial_analyzer = realtime_facial_analyzer
speech_analyzer = realtime_speech_analyzer

@app.route('/ai/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "services": {
            "debate": DEBATE_MODULE_AVAILABLE,
            "personal_interview": PERSONAL_INTERVIEW_MODULE_AVAILABLE,
            "realtime_analysis": REALTIME_MODULES_AVAILABLE,
            "job_recommendation": JOB_RECOMMENDATION_AVAILABLE
        }
    })

@app.route('/ai/test', methods=['GET'])
def test_connection():
    """연결 테스트 및 상태 확인 엔드포인트"""
    initialize_systems()
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
        "status": "AI 서버가 정상 작동 중입니다.",
        "backend_connection": backend_status,
        "modules": {
            "debate_test": "사용 가능" if DEBATE_MODULE_AVAILABLE else "사용 불가",
            "personal_interview_test": "사용 가능" if PERSONAL_INTERVIEW_MODULE_AVAILABLE else "사용 불가",
            "realtime_analysis": "사용 가능" if REALTIME_MODULES_AVAILABLE else "사용 불가",
            "job_recommendation": "사용 가능" if JOB_RECOMMENDATION_AVAILABLE else "사용 불가"
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
                "answer_video": "/ai/interview/<interview_id>/answer-video"
            },
            "job_recommendation": {
                "recommend": "/ai/jobs/recommend",
                "categories": "/ai/jobs/categories",
                "stats": "/ai/jobs/stats"
            }
        },
        "mode": "테스트 모드 (LLM 미사용, 고정 응답)"
    }
    
    logger.info(f"테스트 응답: {test_response}")
    return jsonify(test_response)

@app.route('/ai/recruitment/posting', methods=['POST'])
def recruitment_posting():
    """백엔드 연동용 공고추천 엔드포인트"""
    if not JOB_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        data = request.json or {}
        logger.info(f"백엔드 공고추천 요청 받음: {data}")
        
        # 백엔드에서 전달되는 데이터 형식
        category = data.get('category', 'ICT')
        user_id = data.get('user_id')
        workexperience = data.get('workexperience')
        education = data.get('education')
        major = data.get('major')
        location = data.get('location')
        
        # 공고추천 모듈로 추천 생성
        recommendations = job_recommendation_module.get_recommendations_by_category(category, 10)
        
        if recommendations.get('status') == 'success':
            # 백엔드 응답 형식에 맞춰 변환
            posting_list = []
            
            # CSV 파일의 실제 job_posting_id를 사용하도록 매핑
            base_ids = {
                'ICT': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # ICT 카테고리의 실제 ID
                'BM': [1, 2, 3, 4, 5],  # 경영/관리직 예시
                'SM': [1, 2, 3, 4, 5]   # 영업/마케팅 예시
            }
            
            category_ids = base_ids.get(category, base_ids['ICT'])
            
            for i, job in enumerate(recommendations.get('recommendations', [])):
                # 실제 CSV 데이터의 job_posting_id 사용
                job_posting_id = category_ids[i % len(category_ids)]
                
                posting_list.append({
                    "job_posting_id": job_posting_id,
                    "title": job.get('title', ''),
                    "keyword": ', '.join(job.get('keywords', [])),
                    "corporation": job.get('company', '')
                })
            
            response = {
                "posting": posting_list
            }
            
            logger.info(f"백엔드 공고추천 응답: {len(posting_list)}개 공고")
            return jsonify(response)
        else:
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
        
        # 면접 점수 기반 추천
        if 'interview_scores' in data:
            interview_scores = data['interview_scores']
            limit = data.get('limit', 10)
            
            result = job_recommendation_module.get_recommendations_by_interview_result(
                interview_scores, limit
            )
            logger.info("면접 점수 기반 추천 완료")
            return jsonify(result)
        
        # 카테고리 기반 추천
        elif 'category' in data:
            category = data['category']
            limit = data.get('limit', 10)
            
            result = job_recommendation_module.get_recommendations_by_category(
                category, limit
            )
            logger.info(f"{category} 카테고리 추천 완료")
            return jsonify(result)
        
        # 기본 ICT 카테고리 추천
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

@app.route('/ai/jobs/crawl', methods=['POST'])
def trigger_job_crawling():
    """채용공고 크롤링 트리거"""
    if not JOB_RECOMMENDATION_AVAILABLE:
        return jsonify({"error": "공고추천 모듈을 사용할 수 없습니다."}), 500
    
    try:
        result = job_recommendation_module.trigger_crawling()
        return jsonify(result)
    except Exception as e:
        error_msg = f"크롤링 트리거 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

# ==================== 개인면접 API 엔드포인트 ====================

@app.route('/ai/interview/start', methods=['POST'])
def start_interview():
    """개인면접 시작 엔드포인트"""
    if not PERSONAL_INTERVIEW_MODULE_AVAILABLE:
        return jsonify({"error": "개인면접 모듈을 사용할 수 없습니다."}), 500
    
    try:
        data = request.json or {}
        logger.info(f"개인면접 시작 요청: {data}")
        
        # 간단한 응답 반환
        return jsonify({
            "status": "success",
            "interview_id": int(time.time()),
            "message": "개인면접이 시작되었습니다.",
            "first_question": "자기소개를 해주세요."
        })
    except Exception as e:
        return jsonify({"error": f"개인면접 시작 중 오류: {str(e)}"}), 500

@app.route('/ai/interview/<int:interview_id>/question', methods=['GET'])
def get_interview_question(interview_id):
    """면접 질문 생성"""
    if not PERSONAL_INTERVIEW_MODULE_AVAILABLE:
        return jsonify({"error": "개인면접 모듈을 사용할 수 없습니다."}), 500
    
    try:
        question_type = request.args.get('type', 'general')
        
        # 고정 질문 반환
        questions = {
            "general": "본인의 장점과 단점에 대해 말씀해주세요.",
            "technical": "최근에 관심을 가지고 있는 기술 트렌드가 있다면 무엇인가요?",
            "behavioral": "팀 프로젝트에서 갈등이 생겼을 때 어떻게 해결하셨나요?"
        }
        
        return jsonify({
            "interview_id": interview_id,
            "question": questions.get(question_type, questions["general"]),
            "question_type": question_type
        })
    except Exception as e:
        return jsonify({"error": f"질문 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/interview/<int:interview_id>/answer-video', methods=['POST'])
def process_interview_answer(interview_id):
    """개인면접 답변 영상 처리"""
    if not PERSONAL_INTERVIEW_MODULE_AVAILABLE:
        return jsonify({"error": "개인면접 모듈을 사용할 수 없습니다."}), 500
    
    try:
        if 'file' not in request.files and 'video' not in request.files:
            return jsonify({"error": "영상 파일이 필요합니다."}), 400
        
        file = request.files.get('file') or request.files.get('video')
        
        # 임시 파일 저장 및 분석
        temp_path = f"temp_interview_{interview_id}.mp4"
        file.save(temp_path)
        
        # 기본 분석 결과 반환
        result = {
            "interview_id": interview_id,
            "transcription": "면접 답변에 대한 기본 텍스트입니다.",
            "analysis": {
                "confidence": 0.85,
                "clarity": 0.8,
                "relevance": 0.9
            },
            "feedback": "전반적으로 좋은 답변이었습니다. 좀 더 구체적인 예시가 있으면 더 좋겠습니다.",
            "next_question": "다음 질문으로 넘어가시겠습니까?"
        }
        
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"답변 처리 중 오류: {str(e)}"}), 500

# ==================== 토론면접 API 엔드포인트 ====================

@app.route('/ai/debate/<int:debate_id>/ai-opening', methods=['POST'])
def ai_opening(debate_id):
    """AI 입론 생성 엔드포인트"""
    try:
        data = request.json or {}
        logger.info(f"요청 받음: /ai/debate/{debate_id}/ai-opening")
        
        topic = data.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("opening", topic, None, debate_id)
        
        return jsonify({"ai_opening_text": ai_response})
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
    initialize_analyzers()
    logger.info(f"{current_stage} 영상 처리 요청: /ai/debate/{debate_id}/{current_stage}-video")
    
    if 'file' not in request.files and 'video' not in request.files:
        return jsonify({"error": "영상 파일이 필요합니다."}), 400
    
    file = request.files.get('file') or request.files.get('video')
    try:
        temp_path = f"temp_video_{debate_id}.mp4"
        file.save(temp_path)
        
        # 기본 텍스트 응답
        stage_texts = {
            "opening": "인공지능의 발전은 인류에게 도움이 될 것입니다. 다양한 영역에서 인간의 능력을 확장시켜 줄 것입니다.",
            "rebuttal": "인공지능이 일자리를 대체한다는 주장은 과장되었습니다. 오히려 새로운 직업이 생겨날 것입니다.",
            "counter_rebuttal": "자동화로 일부 직업이 사라질 수 있지만, 기술 발전은 항상 새로운 기회를 만들어왔습니다.",
            "closing": "결론적으로, 인공지능은 우리의 삶을 개선하는 도구이며, 미래를 위한 준비가 중요합니다."
        }
        user_text = stage_texts.get(current_stage, "토론 의견을 말씀드리겠습니다.")
        
        # 기본 점수
        default_scores = {
            "initiative_score": 3.5,
            "collaborative_score": 3.2,
            "communication_score": 3.8,
            "logic_score": 3.3,
            "problem_solving_score": 3.5,
            "voice_score": 3.7,
            "action_score": 3.9,
            "initiative_feedback": "적극성: 적극적",
            "collaborative_feedback": "협력: 협력적",
            "communication_feedback": "의사소통: 명확",
            "logic_feedback": "논리: 논리적",
            "problem_solving_feedback": "문제해결: 우수",
            "voice_feedback": "목소리: 안정적",
            "action_feedback": "행동: 안정적",
            "feedback": "전반적으로 좋은 수행을 보여주었습니다.",
            "sample_answer": "AI는 인간의 삶의 질을 향상시켜주고 활용도가 높습니다."
        }
        
        # AI 응답 생성
        topic = request.form.get("topic", "인공지능")
        response = {
            f"user_{current_stage}_text": user_text,
            "emotion": "중립 (안정적)",
            **default_scores
        }
        
        if next_ai_stage:
            ai_response = get_fixed_ai_response(next_ai_stage, topic, user_text)
            response[f"ai_{next_ai_stage}_text"] = ai_response
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"영상 처리 중 오류: {str(e)}"}), 500

# AI 단계별 응답 엔드포인트들
@app.route('/ai/debate/<int:debate_id>/ai-rebuttal', methods=['GET'])
def ai_rebuttal(debate_id):
    """AI 반론 생성"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("rebuttal", topic, None, debate_id)
        return jsonify({"debate_id": debate_id, "ai_rebuttal_text": ai_response})
    except Exception as e:
        return jsonify({"error": f"AI 반론 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/debate/<int:debate_id>/ai-counter-rebuttal', methods=['GET'])
def ai_counter_rebuttal(debate_id):
    """AI 재반론 생성"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("counter_rebuttal", topic, None, debate_id)
        return jsonify({"debate_id": debate_id, "ai_counter_rebuttal_text": ai_response})
    except Exception as e:
        return jsonify({"error": f"AI 재반론 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/debate/<int:debate_id>/ai-closing', methods=['GET'])
def ai_closing(debate_id):
    """AI 최종 변론 생성"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("closing", topic, None, debate_id)
        return jsonify({"debate_id": debate_id, "ai_closing_text": ai_response})
    except Exception as e:
        return jsonify({"error": f"AI 최종 변론 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/debate/modules-status', methods=['GET'])
def modules_status():
    """모듈 상태 확인"""
    initialize_analyzers()
    
    return jsonify({
        "status": "active",
        "modules": {
            "facial_analyzer": {
                "available": facial_analyzer is not None,
                "functions": ["analyze_video", "analyze_audio"] if facial_analyzer else []
            },
            "speech_analyzer": {
                "available": speech_analyzer is not None,
                "functions": ["transcribe_video"] if speech_analyzer else []
            },
            "job_recommendation": {
                "available": JOB_RECOMMENDATION_AVAILABLE,
                "functions": ["recommend_jobs", "get_categories"] if JOB_RECOMMENDATION_AVAILABLE else []
            }
        },
        "fixed_responses": {
            "opening": get_fixed_ai_response("opening"),
            "rebuttal": get_fixed_ai_response("rebuttal"),
            "counter_rebuttal": get_fixed_ai_response("counter_rebuttal"),
            "closing": get_fixed_ai_response("closing")
        }
    })

if __name__ == "__main__":
    # 시작 시 시스템 초기화
    initialize_systems()
    
    print("🚀 AI 서버 Flask 애플리케이션 시작...")
    print("📍 서버 주소: http://localhost:5000")
    print("🔍 테스트 엔드포인트: http://localhost:5000/ai/test")
    print("📊 상태 확인 엔드포인트: http://localhost:5000/ai/debate/modules-status")
    print("🎯 토론면접 API: http://localhost:5000/ai/debate/<debate_id>/ai-opening")
    print("💼 개인면접 API: http://localhost:5000/ai/interview/start")
    print("📋 공고추천 API: http://localhost:5000/ai/jobs/recommend")
    print("-" * 70)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
