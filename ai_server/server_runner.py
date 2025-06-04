from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
import os
import tempfile
import logging
import json
import time
import base64

# AIStudios 모듈 임포트
from modules.aistudios.client import AIStudiosClient
from modules.aistudios.video_manager import VideoManager
from modules.aistudios.routes import setup_aistudios_routes
from modules.aistudios.interview_routes import setup_interview_routes

# 모듈 임포트
try:
    from app.modules.realtime_facial_analysis import RealtimeFacialAnalysis
    from app.modules.realtime_speech_to_text import RealtimeSpeechToText
    print("모듈 로드 성공: OpenFace, Whisper, TTS, Librosa 기능 사용 가능")
except ImportError as e:
    print(f"모듈 로드 실패: {e}")
    print("일부 기능이 제한될 수 있습니다.")

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 전역 변수로 분석기 초기화
facial_analyzer = None
speech_analyzer = None
# speech_analyzer = None

# AIStudios 관련 전역 변수
aistudios_client = None
video_manager = None

# AI 면접관 관련 엔드포인트

@app.route('/ai/interview/generate-question', methods=['POST'])
def generate_interview_question():
    """면접 질문 생성 엔드포인트"""
    try:
        data = request.json or {}
        job_position = data.get('job_position', '개발자')
        question_type = data.get('question_type', 'general')
        previous_questions = data.get('previous_questions', [])
        
        # 고정된 면접 질문 예시
        questions = {
            'general': [
                f"{job_position} 직문에 지원하게 된 동기는 무엇인가요?",
                f"본인의 강점과 약점에 대해 설명해 주세요.",
                f"팀 프로젝트에서 가장 중요하게 생각하는 가치는 무엇인가요?"
            ],
            'technical': [
                f"{job_position} 경력이 있으시다면, 가장 도전적이었던 프로젝트와 해결 과정을 설명해주세요.",
                f"본인이 가진 기술적 역량 중 가장 자신 있는 부분을 설명해주세요.",
                f"최근 관심있는 기술이나 프레임워크는 무엇인가요?"
            ],
            'scenario': [
                f"팀원과 의견 충돌이 있을 때 어떻게 해결했는지 사례를 들어 설명해주세요.",
                f"많은 업무량을 어떻게 관리하시나요?",
                f"실패한 경험과 그로부터 배운 것이 있다면 말씀해주세요."
            ]
        }
        
        # 질문 타입에 따른 질문 선택
        available_questions = questions.get(question_type, questions['general'])
        
        # 이전 질문에 없는 질문 선택
        filtered_questions = [q for q in available_questions if q not in previous_questions]
        if not filtered_questions:
            filtered_questions = available_questions  # 모든 질문을 사용했다면 다시 사용
        
        # 질문 선택 (매번 처음 질문 선택)
        import random
        selected_question = filtered_questions[0] if filtered_questions else available_questions[0]
        
        # 응답 구성
        response_data = {
            "question": selected_question,
            "question_type": question_type,
            "timestamp": int(time.time())
        }
        
        return jsonify(response_data)
    except Exception as e:
        error_msg = f"면접 질문 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/interview/<int:interview_id>/<question_type>/answer-video', methods=['POST'])
def process_interview_answer(interview_id, question_type):
    """면접 답변 영상 처리 엔드포인트"""
    initialize_analyzers()
    initialize_aistudios()  # AIStudios 초기화
    logger.info(f"면접 답변 영상 처리 요청 받음: /ai/interview/{interview_id}/{question_type}/answer-video")
    
    if 'file' not in request.files and 'video' not in request.files:
        return jsonify({"error": "영상 파일이 필요합니다."}), 400
    
    file = request.files.get('file') or request.files.get('video')
    try:
        temp_path = f"temp_interview_{interview_id}_{question_type}.mp4"
        file.save(temp_path)
        
        user_text = "저는 지속적인 학습과 새로운 기술 활용을 좋아합니다. 팀 환경에서 소통하며 협업하는 것을 중요하게 생각합니다."
        
        # 음성 인식
        if speech_analyzer:
            user_text = speech_analyzer.transcribe_video(temp_path)
        
        # 얼굴 분석
        facial_result = {"confidence": 0.9, "gaze_angle_x": 0.1, "gaze_angle_y": 0.1, "AU01_r": 1.2, "AU02_r": 0.8}
        if facial_analyzer:
            facial_result = facial_analyzer.analyze_video(temp_path)
        
        # 음성 분석
        audio_result = {"pitch_std": 30.0, "rms_mean": 0.2, "tempo": 120.0}
        if facial_analyzer:
            try:
                audio_result = facial_analyzer.analyze_audio(temp_path)
            except:
                pass
        
        # 감정 평가
        emotion = "중립 (안정적)"
        if facial_analyzer:
            emotion = facial_analyzer.evaluate_emotion(facial_result)
        
        # 사용자 영상 저장 (AIStudios 영상 관리자 사용)
        user_video_path = None
        if video_manager:
            try:
                user_video_path = video_manager.save_video(
                    source_path=temp_path,
                    interview_id=interview_id,
                    question_type=question_type,
                    is_ai=False
                )
                logger.info(f"면접 답변 영상 저장 완료: {user_video_path}")
            except Exception as e:
                logger.error(f"사용자 영상 저장 실패: {str(e)}")
        
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # 점수 계산
        content_score = min(5.0, 3.0 + len(user_text.split()) / 50)
        voice_score = 3.7
        action_score = 3.9
        
        # 피드백 생성
        feedback = "전반적으로 양호한 답변이었습니다."
        if content_score >= 4.0:
            feedback = "충분한 내용으로 답변하셨습니다. "
        if voice_score >= 4.0:
            feedback += "안정적인 음성으로 전달하셨습니다."
        
        # 다음 질문 생성
        next_question = "다음 질문은 가장 자신 있는 기술에 대해 설명해 주세요."
        
        # 응답 구성
        response = {
            "user_answer": user_text,
            "content_score": content_score,
            "voice_score": voice_score,
            "action_score": action_score,
            "emotion": emotion,
            "feedback": feedback,
            "next_question": next_question
        }
        
        # 비디오 경로 추가 (있는 경우)
        if user_video_path:
            response["user_video_path"] = user_video_path
        
        return jsonify(response)
    except Exception as e:
        error_msg = f"면접 답변 처리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/interview/next-question-video', methods=['POST'])
def generate_interview_question_video():
    """면접관 다음 질문 영상 생성 엔드포인트"""
    initialize_aistudios()  # AIStudios 초기화
    logger.info(f"면접관 다음 질문 영상 생성 요청 받음")
    
    try:
        data = request.json or {}
        question_text = data.get('question', '다음 질문은 어떤 것이 있을까요?')
        interview_id = data.get('interview_id', int(time.time()))
        question_type = data.get('question_type', 'general')
        
        # 캐시 확인
        ai_video_path = None
        if video_manager:
            cached_video = video_manager.get_video_if_exists(
                interview_id=interview_id, 
                question_type=question_type, 
                is_ai=True
            )
            if cached_video:
                ai_video_path = cached_video
                logger.info(f"캐시된 면접관 질문 영상 사용: {ai_video_path}")
        
        # 새 영상 생성
        if not ai_video_path and aistudios_client and video_manager:
            try:
                generated_video = aistudios_client.generate_avatar_video(question_text)
                ai_video_path = video_manager.save_video(
                    source_path=generated_video,
                    interview_id=interview_id,
                    question_type=question_type,
                    is_ai=True
                )
                logger.info(f"AIStudios로 면접관 질문 영상 생성 완료: {ai_video_path}")
            except Exception as e:
                logger.error(f"면접관 질문 영상 생성 실패: {str(e)}")
        
        # 응답 구성
        response = {
            "question": question_text,
            "question_type": question_type,
            "interview_id": interview_id
        }
        
        if ai_video_path:
            response["video_path"] = ai_video_path
        
        return jsonify(response)
    except Exception as e:
        error_msg = f"면접관 질문 영상 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/interview/feedback-video', methods=['POST'])
def generate_interview_feedback_video():
    """면접 피드백 영상 생성 엔드포인트"""
    initialize_aistudios()  # AIStudios 초기화
    logger.info(f"면접 피드백 영상 생성 요청 받음")
    
    try:
        data = request.json or {}
        feedback_text = data.get('feedback', '답변을 잘 해주셨습니다. 전반적으로 우수한 수행입니다.')
        interview_id = data.get('interview_id', int(time.time()))
        question_type = data.get('question_type', 'feedback')
        
        # 캐시 확인
        ai_video_path = None
        if video_manager:
            cached_video = video_manager.get_video_if_exists(
                interview_id=interview_id, 
                question_type='feedback', 
                is_ai=True
            )
            if cached_video:
                ai_video_path = cached_video
                logger.info(f"캐시된 면접 피드백 영상 사용: {ai_video_path}")
        
        # 새 영상 생성
        if not ai_video_path and aistudios_client and video_manager:
            try:
                generated_video = aistudios_client.generate_avatar_video(feedback_text)
                ai_video_path = video_manager.save_video(
                    source_path=generated_video,
                    interview_id=interview_id,
                    question_type='feedback',
                    is_ai=True
                )
                logger.info(f"AIStudios로 면접 피드백 영상 생성 완료: {ai_video_path}")
            except Exception as e:
                logger.error(f"면접 피드백 영상 생성 실패: {str(e)}")
        
        # 응답 구성
        response = {
            "feedback": feedback_text,
            "interview_id": interview_id
        }
        
        if ai_video_path:
            response["video_path"] = ai_video_path
        
        return jsonify(response)
    except Exception as e:
        error_msg = f"면접 피드백 영상 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500
    


def initialize_analyzers():
    """분석기 초기화 함수"""
    global facial_analyzer, speech_analyzer
    try:
        if facial_analyzer is None:
            facial_analyzer = RealtimeFacialAnalysis()
            logger.info("얼굴 분석기 초기화 완료 (OpenFace, Librosa)")
        if speech_analyzer is None:
            speech_analyzer = RealtimeSpeechToText(model="tiny")
            logger.info("음성 분석기 초기화 완료 (Whisper, TTS)")
    except Exception as e:
        logger.error(f"분석기 초기화 실패: {str(e)}")

def initialize_aistudios():
    """
AIStudios 관련 모듈 초기화 함수

생성형 AI 아바타 영상 생성을 위한 클라이언트와 비디오 관리자를 초기화합니다.
    """
    global aistudios_client, video_manager
    try:
        # 환경 변수에서 API 키 가져오기
        api_key = os.environ.get('AISTUDIOS_API_KEY', 'YOUR_API_KEY')
        
        # AIStudios 클라이언트 초기화
        if aistudios_client is None:
            aistudios_client = AIStudiosClient(api_key=api_key)
            logger.info("AIStudios 클라이언트 초기화 완료")
        
        # 영상 관리자 초기화
        if video_manager is None:
            videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
            video_manager = VideoManager(base_dir=videos_dir)
            logger.info(f"AIStudios 영상 관리자 초기화 완료: {videos_dir}")
        
        return True
    except Exception as e:
        logger.error(f"AIStudios 모듈 초기화 실패: {str(e)}")
        return False

# 고정된 AI 응답을 제공하는 함수 (LLM 대신 사용)
def get_fixed_ai_response(phase, topic=None, user_text=None, debate_id=None):
    """토론 단계별 고정된 AI 응답 반환"""
    responses = {
        "opening": "인공지능은 인간의 일자리를 대체하는 위험을 내포하고 있습니다. 기술의 발전으로 반복적이고 예측 가능한 일자리부터 자동화되어 사라질 것입니다.",
        "rebuttal": "인공지능이 일부 일자리를 대체할 수 있다는 점은 인정합니다만, 동시에 새로운 일자리도 창출합니다. 기술 발전으로 인한 일자리 변화는 역사적으로 항상 있어왔습니다.",
        "counter_rebuttal": "새로운 일자리 창출 가능성은 인정하지만, 그 속도와 규모가 일자리 손실을 따라가지 못합니다. 인공지능이 점점 더 복잡한 업무를 수행할 수 있게 되어 직업 전반에 영향을 미칠 것입니다.",
        "closing": "결론적으로, 인공지능은 일자리를 대체할 위험이 크며 이에 대한 사회적 대비가 필요합니다. 재교육과 새로운 경제 체제에 대한 논의가 시급합니다."
    }
    
    return responses.get(phase, "AI 응답을 생성할 수 없습니다.")

# LLM 통합 후
def get_dynamic_ai_response(phase, topic=None, user_text=None, debate_id=None):
    """LLM을 사용한 동적 AI 응답 생성"""
    if not llm_client:
        return get_fixed_ai_response(phase, topic, user_text, debate_id)
    
    prompt = generate_prompt(phase, topic, user_text)
    ai_response = llm_client.generate_response(prompt)
    
    # AIStudios로 아바타 영상 생성
    if aistudios_client:
        video_path = aistudios_client.generate_avatar_video(ai_response)
        # 영상 경로도 함께 반환
        return ai_response, video_path
    
    return ai_response, None

# ==================== 스트리밍 응답 엔드포인트 ====================

@app.route('/ai/debate/<int:debate_id>/ai-response-stream', methods=['POST'])
def stream_ai_response(debate_id):
    """AI 응답을 스트리밍으로 제공 (텍스트 생성 + TTS 변환)"""
    try:
        data = request.json or {}
        stage = data.get('stage', 'opening')
        topic = data.get('topic', '인공지능')
        position = data.get('position', 'CON')
        user_text = data.get('user_text', '')
        
        def generate():
            try:
                # 고정 응답 가져오기
                if stage == "opening":
                    ai_response = get_fixed_ai_response(stage, topic)
                else:
                    ai_response = get_fixed_ai_response(stage, topic, user_text, debate_id)
                
                # 단어 단위로 스트리밍
                words = ai_response.split()
                sentence_buffer = ""
                full_text = ""
                
                for i, word in enumerate(words):
                    if i > 0:
                        word = " " + word
                    sentence_buffer += word
                    full_text += word
                    
                    # 문장 완성 체크
                    if any(punct in word for punct in '.!?'):
                        # TTS 처리 (사용 가능한 경우)
                        if speech_analyzer and hasattr(speech_analyzer, 'tts') and speech_analyzer.tts:
                            try:
                                temp_audio = f"temp_stream_{debate_id}_{int(time.time())}.wav"
                                speech_analyzer.text_to_speech(sentence_buffer, temp_audio)
                                
                                # 오디오 파일을 base64로 인코딩
                                with open(temp_audio, 'rb') as audio_file:
                                    audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
                                
                                # 오디오 청크 전송
                                yield f"data: {json.dumps({'type': 'audio', 'data': audio_base64})}\n\n"
                                
                                # 임시 파일 삭제
                                if os.path.exists(temp_audio):
                                    os.remove(temp_audio)
                            except Exception as e:
                                logger.error(f"TTS 변환 오류: {str(e)}")
                        
                        # 텍스트 전송 (자막용)
                        yield f"data: {json.dumps({'type': 'text', 'data': sentence_buffer})}\n\n"
                        sentence_buffer = ""
                    
                    time.sleep(0.05)  # 자연스러운 속도
                
                # 남은 텍스트 처리
                if sentence_buffer:
                    yield f"data: {json.dumps({'type': 'text', 'data': sentence_buffer})}\n\n"
                
                # 완료 신호
                yield f"data: {json.dumps({'type': 'complete', 'full_text': full_text})}\n\n"
                
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

@app.route('/ai/interview/<int:interview_id>/answer-stream', methods=['POST'])
def stream_interview_feedback(interview_id):
    """면접 답변에 대한 실시간 피드백 스트리밍"""
    try:
        if 'file' not in request.files and 'video' not in request.files:
            return jsonify({"error": "영상 파일이 필요합니다."}), 400
        
        file = request.files.get('file') or request.files.get('video')
        
        def generate():
            try:
                # 1. 처리 시작 알림
                yield f"data: {json.dumps({'type': 'status', 'message': '영상 분석을 시작합니다...'})}\n\n"
                
                # 2. 영상 저장
                temp_path = f"temp_interview_{interview_id}_{int(time.time())}.mp4"
                file.save(temp_path)
                
                # 3. 음성 인식
                user_text = "면접 답변 내용입니다."
                if speech_analyzer:
                    user_text = speech_analyzer.transcribe_video(temp_path)
                    yield f"data: {json.dumps({'type': 'transcription', 'data': user_text})}\n\n"
                
                # 4. 얼굴 분석
                emotion = "중립"
                if facial_analyzer:
                    facial_result = facial_analyzer.analyze_video(temp_path)
                    emotion = facial_analyzer.evaluate_emotion(facial_result)
                    yield f"data: {json.dumps({'type': 'emotion', 'data': emotion})}\n\n"
                
                # 5. 음성 분석
                audio_result = {"pitch_std": 30.0, "rms_mean": 0.2, "tempo": 120.0}
                if facial_analyzer:
                    try:
                        audio_result = facial_analyzer.analyze_audio(temp_path)
                        yield f"data: {json.dumps({'type': 'audio_analysis', 'data': audio_result})}\n\n"
                    except:
                        pass
                
                # 6. 점수 계산
                scores = {
                    "content_score": min(5.0, 3.0 + len(user_text.split()) / 50),
                    "voice_score": 3.7,
                    "action_score": 3.9
                }
                yield f"data: {json.dumps({'type': 'scores', 'data': scores})}\n\n"
                
                # 7. 피드백 생성
                feedback = "전반적으로 양호한 답변이었습니다."
                if scores["content_score"] >= 4.0:
                    feedback = "충분한 내용으로 답변하셨습니다. "
                if scores["voice_score"] >= 4.0:
                    feedback += "안정적인 음성으로 전달하셨습니다."
                
                yield f"data: {json.dumps({'type': 'feedback', 'data': feedback})}\n\n"
                
                # 8. 완료
                yield f"data: {json.dumps({'type': 'complete'})}\n\n"
                
                # 임시 파일 삭제
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
            except Exception as e:
                logger.error(f"면접 스트리밍 처리 오류: {str(e)}")
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
        return jsonify({"error": f"스트리밍 처리 중 오류: {str(e)}"}), 500

@app.route('/ai/test', methods=['GET'])
def test_connection():
    """연결 테스트 엔드포인트"""
    # 분석기 초기화 시도
    initialize_analyzers()
    logger.info("연결 테스트 요청 받음: /ai/test")
    
    # 분석기 상태 확인
    facial_status = "사용 가능" if facial_analyzer else "사용 불가"
    speech_status = "사용 가능" if speech_analyzer else "사용 불가"
    
    # 백엔드 연결 테스트
    backend_status = "연결 확인 필요"
    try:
        import requests
        response = requests.get("http://localhost:8080/api/health", timeout=2)
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
            "OpenFace/Librosa": facial_status,
            "Whisper/TTS": speech_status
        },
        "endpoints": {
            "ai_opening": "/ai/debate/<debate_id>/ai-opening",
            "opening_video": "/ai/debate/<debate_id>/opening-video",
            "ai_rebuttal": "/ai/debate/<debate_id>/ai-rebuttal",
            "rebuttal_video": "/ai/debate/<debate_id>/rebuttal-video",
            "ai_counter_rebuttal": "/ai/debate/<debate_id>/ai-counter-rebuttal",
            "counter_rebuttal_video": "/ai/debate/<debate_id>/counter-rebuttal-video",
            "ai_closing": "/ai/debate/<debate_id>/ai-closing",
            "closing_video": "/ai/debate/<debate_id>/closing-video",
            "modules_status": "/ai/debate/modules-status"
        },
        "mode": "고정된 텍스트 응답 모드 (LLM 미사용)"
    }
    
    logger.info(f"테스트 응답: {test_response}")
    return jsonify(test_response)

@app.route('/ai/debate/<int:debate_id>/ai-opening', methods=['POST'])
def ai_opening(debate_id):
    """AI 입론 생성 엔드포인트"""
    try:
        # 요청 데이터 로깅
        data = request.json or {}
        logger.info(f"요청 받음: /ai/debate/{debate_id}/ai-opening")
        logger.info(f"요청 데이터: {data}")
        
        # 주제 추출
        topic = data.get("topic", "인공지능")
        position = data.get("position", "PRO")
        
        # 고정된 AI 입론 응답
        ai_response = get_fixed_ai_response("opening", topic, None, debate_id)
        
        response_data = {
            "ai_opening_text": ai_response
        }
        logger.info(f"응답 데이터: {response_data}")
        
        return jsonify(response_data)
    except Exception as e:
        error_msg = f"AI 입론 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/debate/<int:debate_id>/opening-video', methods=['POST'])
def process_opening_video(debate_id):
    """사용자 입론 영상 처리 엔드포인트"""
    initialize_analyzers()
    logger.info(f"입론 영상 처리 요청 받음: /ai/debate/{debate_id}/opening-video")
    
    # 사용자 비디오 경로 초기화 - AIStudios 모듈 없어도 오류 방지
    user_video_path = None
    ai_video_path = None
    
    if 'file' not in request.files and 'video' not in request.files:
        return jsonify({"error": "영상 파일이 필요합니다."}), 400
    
    file = request.files.get('file') or request.files.get('video')
    if file.filename == '':
        return jsonify({"error": "파일명이 비어있습니다."}), 400
    
    try:
        # 임시 파일 저장
        temp_path = f"temp_video_{debate_id}.mp4"
        file.save(temp_path)
        logger.info(f"영상 파일 저장됨: {temp_path}")
        
        # 영상 분석
        user_text = "인공지능의 발전은 인류에게 도움이 될 것입니다. 다양한 영역에서 인간의 능력을 확장시켜 줄 것입니다."
        facial_result = {"confidence": 0.9, "gaze_angle_x": 0.1, "gaze_angle_y": 0.1, "AU01_r": 1.2, "AU02_r": 0.8}
        audio_result = {"pitch_std": 30.0, "rms_mean": 0.2, "tempo": 120.0}
        
        if speech_analyzer:
            user_text = speech_analyzer.transcribe_video(temp_path)
            logger.info(f"Whisper 음성 인식 결과: {user_text}")
        else:
            logger.warning("Whisper 분석기 사용 불가, 기본 텍스트 사용")
        
        if facial_analyzer:
            facial_result = facial_analyzer.analyze_video(temp_path)
            logger.info(f"OpenFace 얼굴 분석 결과: {facial_result}")
            
            try:
                audio_result = facial_analyzer.analyze_audio(temp_path)
                logger.info(f"Librosa 음성 분석 결과: {audio_result}")
            except Exception as e:
                logger.error(f"Librosa 분석 오류: {str(e)}")
        else:
            logger.warning("OpenFace/Librosa 분석기 사용 불가, 기본 값 사용")
        
        # 감정 평가
        emotion = "중립 (안정적)"
        if facial_analyzer:
            emotion = facial_analyzer.evaluate_emotion(facial_result)
            logger.info(f"감정 분석 결과: {emotion}")
        
        # 점수 계산
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
        
        scores = default_scores
        if facial_analyzer:
            scores = facial_analyzer.calculate_scores(facial_result, user_text, audio_result)
            logger.info("점수 계산 완료")
        
        # AI 반론 생성 (고정 텍스트)
        topic = request.form.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("rebuttal", topic, user_text, debate_id)
        
        # 필요하면 TTS 기능 테스트
        tts_path = None
        if speech_analyzer and hasattr(speech_analyzer, 'tts') and speech_analyzer.tts:
            try:
                tts_path = f"ai_response_{debate_id}.wav"
                speech_analyzer.text_to_speech(ai_response, tts_path)
                logger.info(f"TTS 변환 완료: {tts_path}")
            except Exception as e:
                logger.error(f"TTS 변환 실패: {str(e)}")
        
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"임시 파일 삭제됨: {temp_path}")
        
        # 응답 데이터 구성
        response_data = {
            "user_counter_rebuttal_text": user_text,
            "ai_closing_text": ai_response,
            "emotion": emotion,
            "initiative_score": scores["initiative_score"],
            "collaborative_score": scores["collaborative_score"],
            "communication_score": scores["communication_score"],
            "logic_score": scores["logic_score"],
            "problem_solving_score": scores["problem_solving_score"],
            "voice_score": scores["voice_score"],
            "action_score": scores["action_score"],
            "initiative_feedback": scores["initiative_feedback"],
            "collaborative_feedback": scores["collaborative_feedback"],
            "communication_feedback": scores["communication_feedback"],
            "logic_feedback": scores["logic_feedback"],
            "problem_solving_feedback": scores["problem_solving_feedback"],
            "voice_feedback": scores["voice_feedback"],
            "action_feedback": scores["action_feedback"],
            "feedback": scores["feedback"],
            "sample_answer": scores["sample_answer"]
        }
        
        # 비디오 경로 추가 (있는 경우)
        if user_video_path:
            response_data["user_video_path"] = user_video_path
        if ai_video_path:
            response_data["ai_video_path"] = ai_video_path
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"영상 처리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500 

@app.route('/ai/debate/<int:debate_id>/rebuttal-video', methods=['POST'])
def process_rebuttal_video(debate_id):
    """사용자 반론 영상 처리 엔드포인트"""
    # opening-video와 유사한 로직, 다른 단계만 사용
    initialize_analyzers()
    initialize_aistudios()  # AIStudios 초기화
    logger.info(f"반론 영상 처리 요청 받음: /ai/debate/{debate_id}/rebuttal-video")
    
    # 비디오 경로 초기화
    user_video_path = None
    ai_video_path = None
    
    if 'file' not in request.files and 'video' not in request.files:
        return jsonify({"error": "영상 파일이 필요합니다."}), 400
    
    file = request.files.get('file') or request.files.get('video')
    try:
        temp_path = f"temp_video_{debate_id}.mp4"
        file.save(temp_path)
        logger.info(f"영상 파일 저장됨: {temp_path}")
        
        user_text = "인공지능이 일자리를 대체한다는 주장은 과장되었습니다. 오히려 새로운 직업이 생겨날 것입니다."
        facial_result = {"confidence": 0.9, "gaze_angle_x": 0.1, "gaze_angle_y": 0.1, "AU01_r": 1.2, "AU02_r": 0.8}
        audio_result = {"pitch_std": 30.0, "rms_mean": 0.2, "tempo": 120.0}
        
        if speech_analyzer:
            user_text = speech_analyzer.transcribe_video(temp_path)
            logger.info(f"Whisper 음성 인식 결과: {user_text}")
        
        if facial_analyzer:
            facial_result = facial_analyzer.analyze_video(temp_path)
            logger.info(f"OpenFace 얼굴 분석 결과: {facial_result}")
            try:
                audio_result = facial_analyzer.analyze_audio(temp_path)
                logger.info(f"Librosa 음성 분석 결과: {audio_result}")
            except Exception as e:
                logger.error(f"Librosa 분석 오류: {str(e)}")
        
        emotion = "중립 (안정적)"
        if facial_analyzer:
            emotion = facial_analyzer.evaluate_emotion(facial_result)
            logger.info(f"감정 분석 결과: {emotion}")
        
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
        
        scores = default_scores
        if facial_analyzer:
            scores = facial_analyzer.calculate_scores(facial_result, user_text, audio_result)
            logger.info("점수 계산 완료")
        
        topic = request.form.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("counter_rebuttal", topic, user_text, debate_id)
        
        # 사용자 영상 저장 (AIStudios 영상 관리자 사용)
        user_video_path = None
        if video_manager:
            try:
                user_video_path = video_manager.save_video(
                    source_path=temp_path,
                    debate_id=debate_id,
                    phase='rebuttal',
                    is_ai=False
                )
                logger.info(f"사용자 반론 영상 저장 완료: {user_video_path}")
            except Exception as e:
                logger.error(f"사용자 영상 저장 실패: {str(e)}")
        
        # AI 영상 생성 (AIStudios 사용)
        ai_video_path = None
        if aistudios_client and video_manager:
            try:
                # 캐시 확인
                cached_video = video_manager.get_video_if_exists(debate_id=debate_id, phase='counter_rebuttal', is_ai=True)
                if cached_video:
                    ai_video_path = cached_video
                    logger.info(f"캐시된 AI 재반론 영상 사용: {ai_video_path}")
                else:
                    # 새 영상 생성
                    generated_video = aistudios_client.generate_avatar_video(ai_response)
                    ai_video_path = video_manager.save_video(
                        source_path=generated_video,
                        debate_id=debate_id,
                        phase='counter_rebuttal',
                        is_ai=True
                    )
                    logger.info(f"AIStudios로 AI 재반론 영상 생성 완료: {ai_video_path}")
            except Exception as e:
                logger.error(f"AI 재반론 영상 생성 실패: {str(e)}")
        
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"임시 파일 삭제됨: {temp_path}")
        
        # 응답 구성
        response_data = {
            "user_rebuttal_text": user_text,
            "ai_counter_rebuttal_text": ai_response,
            "emotion": emotion,
            "initiative_score": scores["initiative_score"],
            "collaborative_score": scores["collaborative_score"],
            "communication_score": scores["communication_score"],
            "logic_score": scores["logic_score"],
            "problem_solving_score": scores["problem_solving_score"],
            "voice_score": scores["voice_score"],
            "action_score": scores["action_score"],
            "initiative_feedback": scores["initiative_feedback"],
            "collaborative_feedback": scores["collaborative_feedback"],
            "communication_feedback": scores["communication_feedback"],
            "logic_feedback": scores["logic_feedback"],
            "problem_solving_feedback": scores["problem_solving_feedback"],
            "voice_feedback": scores["voice_feedback"],
            "action_feedback": scores["action_feedback"],
            "feedback": scores["feedback"],
            "sample_answer": scores["sample_answer"]
        }
        
        # 비디오 경로 추가 (있는 경우)
        if user_video_path:
            response_data["user_video_path"] = user_video_path
        if ai_video_path:
            response_data["ai_video_path"] = ai_video_path
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"영상 처리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/debate/<int:debate_id>/counter-rebuttal-video', methods=['POST'])
def process_counter_rebuttal_video(debate_id):
    """사용자 재반론 영상 처리 엔드포인트"""
    initialize_analyzers()
    initialize_aistudios()  # AIStudios 초기화
    logger.info(f"재반론 영상 처리 요청 받음: /ai/debate/{debate_id}/counter-rebuttal-video")
    
    # 비디오 경로 초기화
    user_video_path = None
    ai_video_path = None
    
    if 'file' not in request.files and 'video' not in request.files:
        return jsonify({"error": "영상 파일이 필요합니다."}), 400
    
    file = request.files.get('file') or request.files.get('video')
    try:
        temp_path = f"temp_video_{debate_id}.mp4"
        file.save(temp_path)
        
        user_text = "자동화로 일부 직업이 사라질 수 있지만, 기술 발전은 항상 새로운 기회를 만들어왔습니다."
        facial_result = {"confidence": 0.9, "gaze_angle_x": 0.1, "gaze_angle_y": 0.1, "AU01_r": 1.2, "AU02_r": 0.8}
        audio_result = {"pitch_std": 30.0, "rms_mean": 0.2, "tempo": 120.0}
        
        if speech_analyzer:
            user_text = speech_analyzer.transcribe_video(temp_path)
        
        if facial_analyzer:
            facial_result = facial_analyzer.analyze_video(temp_path)
            try:
                audio_result = facial_analyzer.analyze_audio(temp_path)
            except:
                pass
        
        emotion = "중립 (안정적)"
        if facial_analyzer:
            emotion = facial_analyzer.evaluate_emotion(facial_result)
        
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
        
        scores = default_scores
        if facial_analyzer:
            scores = facial_analyzer.calculate_scores(facial_result, user_text, audio_result)
        
        topic = request.form.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("closing", topic, user_text)
        
        # 사용자 영상 저장 (AIStudios 영상 관리자 사용)
        user_video_path = None
        if video_manager:
            try:
                user_video_path = video_manager.save_video(
                    source_path=temp_path,
                    debate_id=debate_id,
                    phase='counter_rebuttal',
                    is_ai=False
                )
                logger.info(f"사용자 재반론 영상 저장 완료: {user_video_path}")
            except Exception as e:
                logger.error(f"사용자 영상 저장 실패: {str(e)}")
        
        # AI 영상 생성 (AIStudios 사용)
        ai_video_path = None
        if aistudios_client and video_manager:
            try:
                # 캐시 확인
                cached_video = video_manager.get_video_if_exists(debate_id=debate_id, phase='closing', is_ai=True)
                if cached_video:
                    ai_video_path = cached_video
                    logger.info(f"캐시된 AI 최종변론 영상 사용: {ai_video_path}")
                else:
                    # 새 영상 생성
                    generated_video = aistudios_client.generate_avatar_video(ai_response)
                    ai_video_path = video_manager.save_video(
                        source_path=generated_video,
                        debate_id=debate_id,
                        phase='closing',
                        is_ai=True
                    )
                    logger.info(f"AIStudios로 AI 최종변론 영상 생성 완료: {ai_video_path}")
            except Exception as e:
                logger.error(f"AI 최종변론 영상 생성 실패: {str(e)}")
        
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        response_data = {
            "user_counter_rebuttal_text": user_text,
            "ai_closing_text": ai_response,
            "emotion": emotion,
            "initiative_score": scores["initiative_score"],
            "collaborative_score": scores["collaborative_score"],
            "communication_score": scores["communication_score"],
            "logic_score": scores["logic_score"],
            "problem_solving_score": scores["problem_solving_score"],
            "voice_score": scores["voice_score"],
            "action_score": scores["action_score"],
            "initiative_feedback": scores["initiative_feedback"],
            "collaborative_feedback": scores["collaborative_feedback"],
            "communication_feedback": scores["communication_feedback"],
            "logic_feedback": scores["logic_feedback"],
            "problem_solving_feedback": scores["problem_solving_feedback"],
            "voice_feedback": scores["voice_feedback"],
            "action_feedback": scores["action_feedback"],
            "feedback": scores["feedback"],
            "sample_answer": scores["sample_answer"]
        }
        
        # 비디오 경로 추가 (있는 경우)
        if user_video_path:
            response_data["user_video_path"] = user_video_path
        if ai_video_path:
            response_data["ai_video_path"] = ai_video_path
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"영상 처리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/debate/<int:debate_id>/closing-video', methods=['POST'])
def process_closing_video(debate_id):
    """사용자 최종 변론 영상 처리 엔드포인트"""
    initialize_analyzers()
    initialize_aistudios()  # AIStudios 초기화
    logger.info(f"최종 변론 영상 처리 요청 받음: /ai/debate/{debate_id}/closing-video")
    
    # 비디오 경로 초기화
    user_video_path = None
    ai_video_path = None
    
    if 'file' not in request.files and 'video' not in request.files:
        return jsonify({"error": "영상 파일이 필요합니다."}), 400
    
    file = request.files.get('file') or request.files.get('video')
    try:
        temp_path = f"temp_video_{debate_id}.mp4"
        file.save(temp_path)
        
        user_text = "결론적으로, 인공지능은 우리의 삶을 개선하는 도구이며, 미래를 위한 준비가 중요합니다."
        facial_result = {"confidence": 0.9, "gaze_angle_x": 0.1, "gaze_angle_y": 0.1, "AU01_r": 1.2, "AU02_r": 0.8}
        audio_result = {"pitch_std": 30.0, "rms_mean": 0.2, "tempo": 120.0}
        
        if speech_analyzer:
            user_text = speech_analyzer.transcribe_video(temp_path)
        
        if facial_analyzer:
            facial_result = facial_analyzer.analyze_video(temp_path)
            try:
                audio_result = facial_analyzer.analyze_audio(temp_path)
            except:
                pass
        
        emotion = "중립 (안정적)"
        if facial_analyzer:
            emotion = facial_analyzer.evaluate_emotion(facial_result)
        
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
        
        scores = default_scores
        if facial_analyzer:
            scores = facial_analyzer.calculate_scores(facial_result, user_text, audio_result)
        
        # 사용자 영상 저장 (AIStudios 영상 관리자 사용)
        user_video_path = None
        if video_manager:
            try:
                user_video_path = video_manager.save_video(
                    source_path=temp_path,
                    debate_id=debate_id,
                    phase='closing',
                    is_ai=False
                )
                logger.info(f"사용자 최종변론 영상 저장 완료: {user_video_path}")
            except Exception as e:
                logger.error(f"사용자 영상 저장 실패: {str(e)}")
        
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"임시 파일 삭제됨: {temp_path}")
        
        # 응답 데이터 구성
        response_data = {
            "user_closing_text": user_text,
            "emotion": emotion,
            "initiative_score": scores["initiative_score"],
            "collaborative_score": scores["collaborative_score"],
            "communication_score": scores["communication_score"],
            "logic_score": scores["logic_score"],
            "problem_solving_score": scores["problem_solving_score"],
            "voice_score": scores["voice_score"],
            "action_score": scores["action_score"],
            "initiative_feedback": scores["initiative_feedback"],
            "collaborative_feedback": scores["collaborative_feedback"],
            "communication_feedback": scores["communication_feedback"],
            "logic_feedback": scores["logic_feedback"],
            "problem_solving_feedback": scores["problem_solving_feedback"],
            "voice_feedback": scores["voice_feedback"],
            "action_feedback": scores["action_feedback"],
            "feedback": scores["feedback"],
            "sample_answer": scores["sample_answer"]
        }
        
        # 비디오 경로 추가 (있는 경우)
        if user_video_path:
            response_data["user_video_path"] = user_video_path
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"영상 처리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/debate/<int:debate_id>/ai-rebuttal', methods=['GET'])
def ai_rebuttal(debate_id):
    """AI 반론 생성 엔드포인트"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("rebuttal", topic, None, debate_id)
        
        return jsonify({
            "debate_id": debate_id,
            "ai_rebuttal_text": ai_response
        })
    except Exception as e:
        return jsonify({"error": f"AI 반론 생성 중 오류 발생: {str(e)}"}), 500

@app.route('/ai/debate/<int:debate_id>/ai-counter-rebuttal', methods=['GET'])
def ai_counter_rebuttal(debate_id):
    """AI 재반론 생성 엔드포인트"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("counter_rebuttal", topic, None, debate_id)
        
        return jsonify({
            "debate_id": debate_id,
            "ai_counter_rebuttal_text": ai_response
        })
    except Exception as e:
        return jsonify({"error": f"AI 재반론 생성 중 오류 발생: {str(e)}"}), 500

@app.route('/ai/debate/<int:debate_id>/ai-closing', methods=['GET'])
def ai_closing(debate_id):
    """AI 최종 변론 생성 엔드포인트"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("closing", topic, None, debate_id)
        
        return jsonify({
            "debate_id": debate_id,
            "ai_closing_text": ai_response
        })
    except Exception as e:
        return jsonify({"error": f"AI 최종 변론 생성 중 오류 발생: {str(e)}"}), 500

@app.route('/ai/debate/modules-status', methods=['GET'])
def modules_status():
    """모듈 상태 확인 엔드포인트"""
    initialize_analyzers()
    logger.info("모듈 상태 확인 요청 받음")
    
    facial_status = {
        "available": facial_analyzer is not None,
        "openface_path": getattr(facial_analyzer, 'openface_path', 'N/A') if facial_analyzer else 'N/A',
        "functions": ["analyze_video", "analyze_audio", "evaluate_emotion", "calculate_scores"] if facial_analyzer else []
    }
    
    speech_status = {
        "available": speech_analyzer is not None,
        "whisper_model": getattr(speech_analyzer, 'model', 'N/A') if speech_analyzer else 'N/A',
        "tts_available": hasattr(speech_analyzer, 'tts') and speech_analyzer.tts is not None if speech_analyzer else False,
        "functions": ["transcribe_audio", "transcribe_video", "text_to_speech"] if speech_analyzer else []
    }
    
    return jsonify({
        "status": "active",
        "modules": {
            "facial_analyzer": facial_status,
            "speech_analyzer": speech_status
        },
        "fixed_responses": {
            "opening": get_fixed_ai_response("opening"),
            "rebuttal": get_fixed_ai_response("rebuttal"),
            "counter_rebuttal": get_fixed_ai_response("counter_rebuttal"),
            "closing": get_fixed_ai_response("closing")
        }
    })

if __name__ == "__main__":
    # 시작 시 분석기 초기화 시도
    initialize_analyzers()
    initialize_aistudios()
    
    # AIStudios 라우트 설정
    setup_aistudios_routes(app)
    
    # 면접관 라우트 추가 설정
    setup_interview_routes(app, facial_analyzer, speech_analyzer, aistudios_client, video_manager)
    
    print("AI 서버 Flask 애플리케이션 시작...")
    print("서버 주소: http://localhost:5000")
    print("테스트 엔드포인트: http://localhost:5000/ai/test")
    print("상태 확인 엔드포인트: http://localhost:5000/ai/debate/modules-status")
    print("    - 스트리밍 AI 응답: http://localhost:5000/ai/debate/<debate_id>/ai-response-stream")
    print("    - 면접 실시간 피드백: http://localhost:5000/ai/interview/<interview_id>/answer-stream")
    print("    - 개인면접 질문 생성: http://localhost:5000/ai/interview/generate-question")
    print("    - 개인면접 답변 분석: http://localhost:5000/ai/interview/<interview_id>/<question_type>/answer-video")
    print("    - 공고추천: http://localhost:5000/ai/recruitment/posting")
    print("-" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
