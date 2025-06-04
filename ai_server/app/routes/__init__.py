from flask import Blueprint, request, jsonify
import sys
import os

# 직접 작성한 모듈 로드
try:
    from app.modules.realtime_facial_analysis import RealtimeFacialAnalysis
    from app.modules.realtime_speech_to_text import RealtimeSpeechToText
    print("사용자 정의 모듈에서 분석기 로드됨")
except ImportError as e:
    print(f"모듈 로드 실패: {e}")
    sys.exit(1)  # 중요: 모듈이 로드되지 않으면 종료

debate_bp = Blueprint('debate', __name__)

# 전역 객체 초기화
facial_analyzer = None
speech_analyzer = None

def initialize_analyzers():
    global facial_analyzer, speech_analyzer
    if facial_analyzer is None:
        facial_analyzer = RealtimeFacialAnalysis()
    if speech_analyzer is None:
        speech_analyzer = RealtimeSpeechToText(model="tiny")

@debate_bp.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"status": "AI 서버가 정상 작동 중입니다."})

@debate_bp.route('/debate/<int:debate_id>/opening-video', methods=['POST'])
def process_opening_video(debate_id):
    initialize_analyzers()
    
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "파일명이 없습니다."}), 400
    
    try:
        # 임시 파일 저장
        temp_path = f"temp_video_{debate_id}.mp4"
        file.save(temp_path)
        
        # 음성-텍스트 변환
        user_text = speech_analyzer.transcribe_video(temp_path)
        
        # 얼굴 분석
        facial_result = facial_analyzer.analyze_video(temp_path)
        
        # 음성 분석 (영상에서 오디오 추출 필요)
        try:
            audio_result = facial_analyzer.analyze_audio(temp_path)
        except:
            # 오디오 분석 실패 시 기본값 사용
            audio_result = {"pitch_std": 0, "rms_mean": 0, "tempo": 0}
        
        # 감정 평가
        emotion = facial_analyzer.evaluate_emotion(facial_result)
        
        # 점수 계산
        scores = facial_analyzer.calculate_scores(facial_result, user_text, audio_result)
        
        # AI 응답 생성 (고정값)
        ai_response = "인공지능은 인간의 일자리를 대체하는 위험을 내포하고 있습니다."
        
        # 임시 파일 삭제 시도
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            logger.warning(f"임시 파일 삭제 실패: {str(e)}")
        
        return jsonify({
            "user_opening_text": user_text,
            "ai_rebuttal_text": ai_response,
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
        })
        
    except Exception as e:
        return jsonify({"error": f"처리 중 오류 발생: {str(e)}"}), 500

@debate_bp.route('/debate/<int:debate_id>/rebuttal-video', methods=['POST'])
def process_rebuttal_video(debate_id):
    # opening-video와 유사한 로직, AI 응답만 다름
    initialize_analyzers()
    
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400
    
    file = request.files['file']
    try:
        temp_path = f"temp_video_{debate_id}.mp4"
        file.save(temp_path)
        
        user_text = speech_analyzer.transcribe_video(temp_path)
        facial_result = facial_analyzer.analyze_video(temp_path)
        try:
            audio_result = facial_analyzer.analyze_audio(temp_path)
        except:
            audio_result = {"pitch_std": 0, "rms_mean": 0, "tempo": 0}
        emotion = facial_analyzer.evaluate_emotion(facial_result)
        scores = facial_analyzer.calculate_scores(facial_result, user_text, audio_result)
        
        ai_response = "AI는 발전하면서도 위험을 내포하고 있으며, 통제 방안을 논의해야 합니다."
        
        # 임시 파일 삭제 시도
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            logger.warning(f"임시 파일 삭제 실패: {str(e)}")
        
        return jsonify({
            "user_rebuttal_text": user_text,
            "ai_counter_rebuttal_text": ai_response,
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
        })
        
    except Exception as e:
        return jsonify({"error": f"처리 중 오류 발생: {str(e)}"}), 500

@debate_bp.route('/debate/<int:debate_id>/counter-rebuttal-video', methods=['POST'])
def process_counter_rebuttal_video(debate_id):
    initialize_analyzers()
    
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400
    
    file = request.files['file']
    try:
        temp_path = f"temp_video_{debate_id}.mp4"
        file.save(temp_path)
        
        user_text = speech_analyzer.transcribe_video(temp_path)
        facial_result = facial_analyzer.analyze_video(temp_path)
        try:
            audio_result = facial_analyzer.analyze_audio(temp_path)
        except:
            audio_result = {"pitch_std": 0, "rms_mean": 0, "tempo": 0}
        emotion = facial_analyzer.evaluate_emotion(facial_result)
        scores = facial_analyzer.calculate_scores(facial_result, user_text, audio_result)
        
        ai_response = "AI는 자율성을 지나치게 부여받는 것이 위험하며, 인간의 제어를 유지해야 합니다."
        
        # 임시 파일 삭제 시도
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            logger.warning(f"임시 파일 삭제 실패: {str(e)}")
        
        return jsonify({
            "user_counter_rebuttal_text": user_text,
            "ai_closing_text": ai_response,
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
        })
        
    except Exception as e:
        return jsonify({"error": f"처리 중 오류 발생: {str(e)}"}), 500

@debate_bp.route('/debate/<int:debate_id>/closing-video', methods=['POST'])
def process_closing_video(debate_id):
    initialize_analyzers()
    
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400
    
    file = request.files['file']
    try:
        temp_path = f"temp_video_{debate_id}.mp4"
        file.save(temp_path)
        
        user_text = speech_analyzer.transcribe_video(temp_path)
        facial_result = facial_analyzer.analyze_video(temp_path)
        try:
            audio_result = facial_analyzer.analyze_audio(temp_path)
        except:
            audio_result = {"pitch_std": 0, "rms_mean": 0, "tempo": 0}
        emotion = facial_analyzer.evaluate_emotion(facial_result)
        scores = facial_analyzer.calculate_scores(facial_result, user_text, audio_result)
        
        # 임시 파일 삭제 시도
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            logger.warning(f"임시 파일 삭제 실패: {str(e)}")
        
        return jsonify({
            "user_closing_text": user_text,
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
        })
        
    except Exception as e:
        return jsonify({"error": f"처리 중 오류 발생: {str(e)}"}), 500

@debate_bp.route('/debate/<int:debate_id>/ai-opening', methods=['POST'])
def generate_ai_opening(debate_id):
    try:
        data = request.json
        topic = data.get('topic')
        position = data.get('position')
        
        # 고정 AI 입론 응답
        ai_response = "인공지능은 인간의 일자리를 대체하는 위험을 내포하고 있습니다."
        
        return jsonify({
            "ai_opening_text": ai_response
        })
        
    except Exception as e:
        return jsonify({"error": f"AI 입론 생성 중 오류 발생: {str(e)}"}), 500
