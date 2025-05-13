from flask import Flask, request, jsonify
import threading
import queue
import requests
import json
import logging
import time
import random
import re
import cv2
import numpy as np
import os
import uuid
import tempfile
from .realtime_speech_to_text import RealtimeSpeechToText
from .realtime_facial_analysis import RealtimeFacialAnalysis
import jwt

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DebateServer:
    def __init__(self):
        self.facial_analyzer = RealtimeFacialAnalysis()
        self.speech_analyzer = RealtimeSpeechToText(model="base")
        self.sessions = {}  # debate_id: {state}
        self.video_dir = os.path.join(os.path.dirname(__file__), "..", "data", "debate_videos")
        self.jwt_secret = os.getenv("JWT_SECRET", "your_jwt_secret_key_base64_encoded")
        self.topic_file = os.path.join(os.path.dirname(__file__), "..", "resources", "debate_topic.txt")
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)
        self.topics = self.load_topics()
        self.debate_id_counter = int(time.time() * 1000)  # 초기 debate_id 기반으로 타임스탬프 사용

    def generate_debate_id(self):
        # 고유한 int 타입 debate_id 생성
        self.debate_id_counter += random.randint(1, 100)  # 충돌 방지를 위해 랜덤 값 추가
        return self.debate_id_counter

    def load_topics(self):
        try:
            if not os.path.exists(self.topic_file):
                logger.error(f"토론 주제 파일을 찾을 수 없습니다: {self.topic_file}")
                return ["인공지능은 인간의 일자리를 대체할 것인가에 대한 찬반토론"]
            with open(self.topic_file, 'r', encoding='utf-8') as f:
                topics = [line.strip() for line in f if line.strip()]
            if not topics:
                logger.warning("토론 주제 파일이 비어 있습니다. 기본 주제 사용")
                return ["인공지능은 인간의 일자리를 대체할 것인가에 대한 찬반토론"]
            logger.info(f"로드된 토론 주제: {topics}")
            return topics
        except Exception as e:
            logger.error(f"토론 주제 파일 로드 실패: {str(e)}")
            return ["인공지능은 인간의 일자리를 대체할 것인가에 대한 찬반토론"]

    def get_random_topic(self):
        return random.choice(self.topics)

    def verify_jwt(self, token):
        try:
            decoded = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return decoded["sub"]
        except jwt.InvalidTokenError as e:
            logger.error(f"JWT 검증 실패: {str(e)}")
            return None

    def call_ollama(self, prompt, model="gemma3:12b-it-q8_0", max_tokens=4096, retries=3):
        for attempt in range(retries):
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_k": 40,
                            "top_p": 0.9,
                            "max_tokens": max_tokens
                        }
                    },
                    timeout=60
                )
                response.raise_for_status()
                text = response.json()["response"].strip()
                text = " ".join(text.split())
                return text
            except Exception as e:
                logger.error(f"Ollama 호출 실패 (시도 {attempt+1}/{retries}): {str(e)}")
                if attempt == retries - 1:
                    return "AI 응답 생성 실패: 서버 오류"
                time.sleep(2)

    def clean_input_text(self, text):
        if not text:
            return ""
        cleaned_text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
        cleaned_text = cleaned_text.strip()
        return cleaned_text

    def create_personas(self, topic):
        persona_prompt = (
            f"당신은 AI 면접 시스템입니다. 주어진 토론 주제 '{topic}'에 대해 찬성 또는 반대 입장을 가진 1명의 AI 면접자를 생성하세요. "
            "면접자는 한국 이름, 성격, 직업, 토론 스타일, 그리고 주제에 대한 입장(찬성/반대)을 포함한 고유한 페르소나를 가져야 합니다. "
            "출력 형식은 반드시 다음과 같이 간단한 텍스트로만 작성하세요:\n"
            "면접자 1: [이름], [성격], [직업], [토론 스타일], [입장]\n"
            "추가 설명, 마크다운(##, ** 등), 또는 불필요한 텍스트를 넣지 마세요."
        )
        personas = self.call_ollama(persona_prompt, max_tokens=4096)
        if personas:
            persona_lines = personas.split("\n")
            if len(persona_lines) < 1 or not persona_lines[0].strip():
                logger.warning("페르소나 데이터가 부족하여 파싱 실패, 기본 페르소나 사용")
                return "면접자 1: 김민수, 논리적이고 분석적, 데이터 분석가, 근거 중심의 차분한 토론 스타일, 찬성"
            logger.info(f"생성된 페르소나: {personas}")
            return personas
        logger.warning("페르소나 생성 실패, 기본 페르소나 사용")
        return "면접자 1: 김민수, 논리적이고 분석적, 데이터 분석가, 근거 중심의 차분한 토론 스타일, 찬성"

    def evaluate_debate(self, debate_id):
        session = self.sessions.get(debate_id)
        if not session or not session["user_speeches"]:
            return {"status": "error", "message": "사용자가 발언하지 않아 평가를 진행할 수 없습니다."}

        round_titles = ["입론", "반론", "재반론", "최종 변론"]
        phase_key_map = {
            "입론": "opening",
            "반론": "rebuttal",
            "재반론": "counter_rebuttal",
            "최종 변론": "closing"
        }
        user_text_lines = []
        for i, speech in enumerate(session["user_speeches"]):
            if speech and i < len(round_titles):
                user_text_lines.append(f"[{round_titles[i]}]: {speech}")
        user_text = "\n".join(user_text_lines)
        
        emotion_text = "\n".join([f"[{round_titles[i]}]: {emotion}" for i, emotion in enumerate(session["user_emotions"])])
        
        feedback_lines = []
        for i, scores in enumerate(session["scores"]):
            if scores and i < len(round_titles):
                feedback_lines.append(f"[{round_titles[i]}]:")
                feedback_lines.append(f"적극성({scores['initiative_score']}): {scores['initiative_feedback']}")
                feedback_lines.append(f"협력적태도({scores['collaborative_score']}): {scores['collaborative_feedback']}")
                feedback_lines.append(f"의사소통능력({scores['communication_score']}): {scores['communication_feedback']}")
                feedback_lines.append(f"논리력({scores['logic_score']}): {scores['logic_feedback']}")
                feedback_lines.append(f"문제해결능력({scores['problem_solving_score']}): {scores['problem_solving_feedback']}")
                feedback_lines.append(f"목소리({scores['voice_score']}): {scores['voice_feedback']}")
                feedback_lines.append(f"행동({scores['action_score']}): {scores['action_feedback']}")
                feedback_lines.append(f"피드백: {scores['feedback']}")
                feedback_lines.append(f"모범답안: {scores['sample_answer']}")
        
        evaluation = {
            "status": "success",
            "user_text": user_text,
            "emotion_text": emotion_text,
            "evaluation": "\n".join(feedback_lines)
        }
        self.cleanup_videos(debate_id)
        return evaluation

    def process_round(self, debate_id, round_num, speaker):
        session = self.sessions[debate_id]
        round_titles = ["입론", "반론", "재반론", "최종 변론"]
        if speaker == "사용자":
            return {"status": "waiting", "round": round_titles[round_num-1], "speaker": speaker}
        else:
            name = session["ai_name"]
            style = session["ai_style"]
            stance = session["ai_stance"]
            if round_num == 1:
                prompt = (
                    f"당신은 '{name}'입니다. 토론 스타일은 '{style}'입니다. "
                    f"당신의 입장은 '{stance}'입니다. "
                    f"KILL 토론 주제는 '{session['topic']}'입니다. 현재 [입론] 단계이므로 자신을 소개한 후, 당신의 입장을 명확히 제시하세요. 2~4 문장으로 작성하세요."
                    f"줄바꿈 없이 문장을 이어서 작성하세요."
                )
            elif round_num == 2:
                prompt = (
                    f"당신은 '{name}'입니다. 토론 스타일은 '{style}'입니다. "
                    f"당신의 입장은 '{stance}'입니다. "
                    f"토론 주제는 '{session['topic']}'입니다. 현재 [반론] 단계이므로 이전 발언자 의견에 대해 논리적으로 반박하세요. 2~4 문장으로 작성하세요."
                    f"줄바꿈 없이 문장을 이어서 작성하세요."
                )
            elif round_num == 3:
                prompt = (
                    f"당신은 '{name}'입니다. 토론 스타일은 '{style}'입니다. "
                    f"당신의 입장은 '{stance}'입니다. "
                    f"토론 주제는 '{session['topic']}'입니다. 현재 [재반론] 단계이므로 이전 반박에 대해 추가 논쟁을 펼치세요. 2~4 문장으로 작성하세요."
                    f"줄바꿈 없이 문장을 이어서 작성하세요."
                )
            elif round_num == 4:
                prompt = (
                    f"당신은 '{name}'입니다. 토론 스타일은 '{style}'입니다. "
                    f"당신의 입장은 '{stance}'입니다. "
                    f"토론 주제는 '{session['topic']}'입니다. 현재 [최종 변론] 단계이므로 토론을 결론짓고 당신의 입장을 요약하세요. 2~4 문장으로 작성하세요."
                    f"줄바꿈 없이 문장을 이어서 작성하세요."
                )
            if session["last_speakers"]:
                last_speaker = session["last_speakers"][-1]
                last_speaker_name = last_speaker["name"]
                last_speaker_text = last_speaker["text"]
                prompt += (
                    f" 이전 발언자('{last_speaker_name}')의 발언: '{last_speaker_text}'을 참조하세요. "
                    f"단, 상대방의 이름을 반복적으로 호출하지 말고, 자연스럽게 발언을 이어가세요."
                )

            response = self.call_ollama(prompt)
            if response:
                session["last_speakers"].append({"name": name, "text": response})
                return {"status": "success", "round": round_titles[round_num-1], "speaker": name, "speech": response}
            else:
                response = f"{name}의 기본 입장입니다."
                session["last_speakers"].append({"name": name, "text": response})
                return {"status": "success", "round": round_titles[round_num-1], "speaker": name, "speech": response}

    def process_video(self, video_file, phase, debate_id, topic, position):
        video_path = os.path.join(self.video_dir, f"{debate_id}_{phase}.mp4")
        video_file.save(video_path)

        text = self.clean_input_text(self.speech_analyzer.transcribe_video(video_path))
        analysis_result = self.facial_analyzer.analyze_video(video_path)
        emotion = self.facial_analyzer.evaluate_emotion(analysis_result)
        scores = self.facial_analyzer.calculate_scores(analysis_result, text)

        session = self.sessions.get(debate_id)
        if session:
            session["user_speeches"].append(text)
            session["user_emotions"].append(emotion)
            session["scores"].append(scores)
            session["last_speakers"].append({"name": "사용자", "text": text})

        next_round = {"입론": 2, "반론": 3, "재반론": 4, "최종 변론": None}.get(phase)
        ai_response = None
        if next_round and session:
            session["round"] = next_round
            ai_result = self.process_round(debate_id, next_round, session["ai_name"])
            ai_response = ai_result["speech"] if ai_result["status"] == "success" else f"AI {phase} 생성 실패"

        phase_key_map = {
            "입론": "opening",
            "반론": "rebuttal",
            "재반론": "counter_rebuttal",
            "최종 변론": "closing"
        }
        return {
            "text": text,
            "facial_analysis": analysis_result,
            "emotion": emotion,
            "initiative_score": scores["initiative_score"],
            "collaborative_score": scores["collaborative_score"],
            "communication_score": scores["communication_score"],
            "logic_score": scores["logic_score"],
            "problem_solving_score": scores["problem_solving_score"],
            "voice_score": scores["voice_score"],
            "action_score": scores["action_score"],
            "initiative_feedback": f"적극성: {'적극적' if scores['initiative_score'] > 3 else '소극적'}",
            "collaborative_feedback": f"협력: {'협력적' if scores['collaborative_score'] > 3 else '개선 필요'}",
            "communication_feedback": f"의사소통: {'명확' if scores['communication_score'] > 3 else '불명확'}",
            "logic_feedback": f"논리: {'논리적' if scores['logic_score'] > 3 else '논리 부족'}",
            "problem_solving_feedback": f"문제해결: {'우수' if scores['problem_solving_score'] > 3 else '개선 필요'}",
            "voice_feedback": f"목소리: {'안정적' if scores['voice_score'] > 3 else '불안정'}",
            "action_feedback": f"행동: {'안정적' if scores['action_score'] > 3 else '시선 불안정'}",
            "feedback": scores["feedback"],
            "sample_answer": scores["sample_answer"],
            "ai_response": ai_response
        }

    def cleanup_videos(self, debate_id):
        for phase in ["opening", "rebuttal", "counter-rebuttal", "closing"]:
            video_path = os.path.join(self.video_dir, f"{debate_id}_{phase}.mp4")
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"삭제됨: {video_path}")

@app.route('/api/debate/start', methods=['POST'])
def start():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        user_id = app.config['server'].verify_jwt(token)
        if not user_id:
            return jsonify({"error": "유효하지 않은 토큰입니다."}), 401
    else:
        user_id = request.json.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id가 필요합니다."}), 400
    
    debate_id = app.config['server'].generate_debate_id()  # int 타입 debate_id 생성
    topic = request.json.get("topic") or app.config['server'].get_random_topic()
    personas = app.config['server'].create_personas(topic)
    persona_lines = personas.split("\n")
    try:
        match = re.search(r"면접자 1: (.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+)", persona_lines[0])
        if match:
            name, personality, job, style, stance = match.groups()
        else:
            raise ValueError("페르소나 파싱 실패")
    except Exception as e:
        logger.error(f"페르소나 파싱 실패: {str(e)}")
        name, style, stance = "김민수", "근거 중심의 차분한 토론 스타일", "찬성"
    
    user_position = "PRO" if stance == "반대" else "CON"
    session = {
        "user_id": user_id,
        "topic": topic,
        "user_position": user_position,
        "ai_name": name,
        "ai_style": style,
        "ai_stance": stance,
        "round": 0,
        "participants": [name, "사용자"],
        "start_order": random.choice([name, "사용자"]),
        "user_speeches": [],
        "user_emotions": [],
        "scores": [],
        "last_speakers": []
    }
    app.config['server'].sessions[debate_id] = session
    
    result = app.config['server'].process_round(debate_id, 1, name)
    ai_opening_text = result["speech"] if result["status"] == "success" else "AI 입론 생성 실패"
    
    return jsonify({
        "topic": topic,
        "position": user_position,
        "debate_id": debate_id,  # int 타입으로 반환
        "ai_opening_text": ai_opening_text
    })

@app.route('/ai/debate/<int:debate_id>/ai-opening', methods=['POST'])
def ai_opening(debate_id):
    server = app.config['server']
    if debate_id not in server.sessions:
        data = request.json or {}
        user_id = data.get("user_id", "default_user")
        topic = data.get("topic") or server.get_random_topic()
        position = data.get("position", "PRO")
        personas = server.create_personas(topic)
        persona_lines = personas.split("\n")
        try:
            match = re.search(r"면접자 1: (.+?),\s*(.+?),\s*(.+?),\s*(.+?),\s*(.+)", persona_lines[0])
            if match:
                name, personality, job, style, stance = match.groups()
            else:
                raise ValueError("페르소나 파싱 실패")
        except Exception as e:
            logger.error(f"페르소나 파싱 실패: {str(e)}")
            name, style, stance = "김민수", "근거 중심의 차분한 토론 스타일", "찬성"
        
        user_position = "PRO" if stance == "반대" else "CON"
        server.sessions[debate_id] = {
            "user_id": user_id,
            "topic": topic,
            "user_position": user_position,
            "ai_name": name,
            "ai_style": style,
            "ai_stance": stance,
            "round": 0,
            "participants": [name, "사용자"],
            "start_order": random.choice([name, "사용자"]),
            "user_speeches": [],
            "user_emotions": [],
            "scores": [],
            "last_speakers": []
        }
        logger.info(f"세션 자동 생성: debate_id={debate_id}, topic={topic}, user_position={user_position}")

    session = server.sessions[debate_id]
    session["ai_stance"] = request.json.get("position", session["ai_stance"])
    result = server.process_round(debate_id, 1, session["ai_name"])
    if result["status"] == "success":
        return jsonify({
            "debate_id": debate_id,  # int 타입으로 반환
            "ai_opening_text": result["speech"]
        })
    return jsonify({"error": "AI 입론 생성 실패"}), 500

@app.route('/api/debate/<int:debate_id>/opening-video', methods=['POST'])
@app.route('/api/debate/<int:debate_id>/rebuttal-video', methods=['POST'])
@app.route('/api/debate/<int:debate_id>/counter-rebuttal-video', methods=['POST'])
@app.route('/api/debate/<int:debate_id>/closing-video', methods=['POST'])
def save_video(debate_id):
    if debate_id not in app.config['server'].sessions:
        return jsonify({"error": "유효하지 않은 debate_id입니다."}), 404
    if 'video' not in request.files and 'file' not in request.files:
        return jsonify({"error": "영상 파일이 필요합니다."}), 400
    
    video = request.files.get('video') or request.files.get('file')
    phase = request.path.split('/')[-1].split('-')[0]
    phase_map = {
        "opening": "입론",
        "rebuttal": "반론",
        "counter-rebuttal": "재반론",
        "closing": "최종 변론"
    }
    phase_kr = phase_map.get(phase, phase)
    
    video_path = os.path.join(app.config['server'].video_dir, f"{debate_id}_{phase}.mp4")
    video.save(video_path)
    
    return jsonify({"message": f"사용자의 {phase_kr} 영상이 성공적으로 저장되었습니다."})

@app.route('/ai/debate/<int:debate_id>/opening-video', methods=['POST'])
@app.route('/ai/debate/<int:debate_id>/rebuttal-video', methods=['POST'])
@app.route('/ai/debate/<int:debate_id>/counter-rebuttal-video', methods=['POST'])
@app.route('/ai/debate/<int:debate_id>/closing-video', methods=['POST'])
def analyze_video(debate_id):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        user_id = app.config['server'].verify_jwt(token)
        if not user_id:
            return jsonify({"error": "유효하지 않은 토큰입니다."}), 401

    if debate_id not in app.config['server'].sessions:
        return jsonify({"error": "유효하지 않은 debate_id입니다."}), 404
    if 'video' not in request.files and 'file' not in request.files:
        return jsonify({"error": "영상 파일이 필요합니다."}), 400
    
    session = app.config['server'].sessions[debate_id]
    phase = request.path.split('/')[-1].split('-')[0]
    phase_map = {
        "opening": "입론",
        "rebuttal": "반론",
        "counter-rebuttal": "재반론",
        "closing": "최종 변론"
    }
    phase_kr = phase_map.get(phase, phase)
    
    video = request.files.get('video') or request.files.get('file')
    video_path = os.path.join(app.config['server'].video_dir, f"{debate_id}_{phase}.mp4")
    video.save(video_path)
    
    text = app.config['server'].clean_input_text(app.config['server'].speech_analyzer.transcribe_video(video_path))
    if text:
        session["user_speeches"].append(text)
        session["last_speakers"].append({"name": "사용자", "text": text})
    
    analysis_result = app.config['server'].facial_analyzer.analyze_video(video_path)
    emotion = app.config['server'].facial_analyzer.evaluate_emotion(analysis_result)
    session["user_emotions"].append(emotion)
    
    scores = app.config['server'].facial_analyzer.calculate_scores(analysis_result, text)
    scores["sample_answer"] = "AI는 인간의 삶의 질을 향상시켜주고 활용도가 높습니다."
    session["scores"].append(scores)
    
    next_round = {"입론": 2, "반론": 3, "재반론": 4, "최종 변론": None}.get(phase_kr)
    ai_response_key = None
    ai_response = None
    if next_round:
        session["round"] = next_round
        ai_result = app.config['server'].process_round(debate_id, next_round, session["ai_name"])
        ai_response = ai_result["speech"] if ai_result["status"] == "success" else f"AI {phase_kr} 생성 실패"
        ai_response_key = f"ai_{'rebuttal' if phase_kr == '입론' else 'counter_rebuttal' if phase_kr == '반론' else 'closing'}_text"
    
    phase_key_map = {
        "입론": "opening",
        "반론": "rebuttal",
        "재반론": "counter_rebuttal",
        "최종 변론": "closing"
    }
    response = {
        "debate_id": debate_id,  # int 타입으로 반환
        f"user_{phase_key_map[phase_kr]}_text": text,
        "initiative_score": scores["initiative_score"],
        "collaborative_score": scores["collaborative_score"],
        "communication_score": scores["communication_score"],
        "logic_score": scores["logic_score"],
        "problem_solving_score": scores["problem_solving_score"],
        "voice_score": scores["voice_score"],
        "action_score": scores["action_score"],
        "initiative_feedback": f"적극성: {'적극적' if scores['initiative_score'] > 3 else '소극적'}",
        "collaborative_feedback": f"협력: {'협력적' if scores['collaborative_score'] > 3 else '개선 필요'}",
        "communication_feedback": f"의사소통: {'명확' if scores['communication_score'] > 3 else '불명확'}",
        "logic_feedback": f"논리: {'논리적' if scores['logic_score'] > 3 else '논리 부족'}",
        "problem_solving_feedback": f"문제해결: {'우수' if scores['problem_solving_score'] > 3 else '개선 필요'}",
        "voice_feedback": f"목소리: {'안정적' if scores['voice_score'] > 3 else '불안정'}",
        "action_feedback": f"행동: {'안정적' if scores['action_score'] > 3 else '시선 불안정'}",
        "feedback": scores["feedback"],
        "sample_answer": scores["sample_answer"]
    }
    if ai_response and ai_response_key:
        response[ai_response_key] = ai_response
    
    return jsonify(response)

@app.route('/api/debate/<int:debate_id>/ai-rebuttal', methods=['GET'])
@app.route('/api/debate/<int:debate_id>/ai-counter-rebuttal', methods=['GET'])
@app.route('/api/debate/<int:debate_id>/ai-closing', methods=['GET'])
def ai_response(debate_id):
    if debate_id not in app.config['server'].sessions:
        return jsonify({"error": "유효하지 않은 debate_id입니다."}), 404
    session = app.config['server'].sessions[debate_id]
    phase = request.path.split('/')[-1].split('-')[1]
    round_num = {"rebuttal": 2, "counter-rebuttal": 3, "closing": 4}.get(phase)
    result = app.config['server'].process_round(debate_id, round_num, session["ai_name"])
    if result["status"] == "success":
        return jsonify({
            "topic": session["topic"],
            "position": session["user_position"],
            "debate_id": debate_id,  # int 타입으로 반환
            f"ai_{phase}_text": result["speech"]
        })
    return jsonify({"error": f"AI {phase} 생성 실패"}), 500

@app.route('/api/debate/<int:debate_id>/feedback', methods=['GET'])
def feedback(debate_id):
    if debate_id not in app.config['server'].sessions:
        return jsonify({"error": "유효하지 않은 debate_id입니다."}), 404
    session = app.config['server'].sessions[debate_id]
    evaluation = app.config['server'].evaluate_debate(debate_id)
    if evaluation["status"] == "success":
        debate_feedback = []
        round_titles = ["입론", "반론", "재반론", "최종 변론"]
        phase_key_map = {
            "입론": "opening",
            "반론": "rebuttal",
            "재반론": "counter_rebuttal",
            "최종 변론": "closing"
        }
        for i, (speech, scores) in enumerate(zip(session["user_speeches"], session["scores"])):
            if speech and scores:
                debate_feedback.append({
                    "user_text": speech,
                    f"user_{phase_key_map[round_titles[i]]}_text": speech,
                    "initiative_score": scores["initiative_score"],
                    "collaborative_score": scores["collaborative_score"],
                    "communication_score": scores["communication_score"],
                    "logic_score": scores["logic_score"],
                    "problem_solving_score": scores["problem_solving_score"],
                    "initiative_feedback": f"적극성: {'적극적' if scores['initiative_score'] > 3 else '소극적'}",
                    "collaborative_feedback": f"협력: {'협력적' if scores['collaborative_score'] > 3 else '개선 필요'}",
                    "communication_feedback": f"의사소통: {'명확' if scores['communication_score'] > 3 else '불명확'}",
                    "logic_feedback": f"논리: {'논리적' if scores['logic_score'] > 3 else '논리 부족'}",
                    "problem_solving_feedback": f"문제해결: {'우수' if scores['problem_solving_score'] > 3 else '개선 필요'}",
                    "voice_score": scores["voice_score"],
                    "action_score": scores["action_score"],
                    "feedback": scores["feedback"],
                    "sample_answer": scores["sample_answer"]
                })
        return jsonify({
            "debate_id": debate_id,  # int 타입으로 반환
            "debate_feedback": debate_feedback
        })
    return jsonify({"error": evaluation["message"]}), 500

@app.route('/process', methods=['POST'])
def process_video():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        user_id = app.config['server'].verify_jwt(token)
        if not user_id:
            return jsonify({"error": "유효하지 않은 토큰입니다."}), 401
    else:
        user_id = request.form.get("user_id")

    if 'video' not in request.files and 'file' not in request.files:
        return jsonify({"error": "영상 파일이 필요합니다."}), 400
    video = request.files.get('video') or request.files.get('file')
    debate_id = int(request.form.get('debate_id'))  # int로 변환
    phase = request.form.get('phase')
    topic = request.form.get('topic') or app.config['server'].get_random_topic()
    position = request.form.get('position')

    if not all([debate_id, phase, topic, position]):
        return jsonify({"error": "debate_id, phase, topic, position이 필요합니다."}), 400

    if debate_id not in app.config['server'].sessions:
        app.config['server'].sessions[debate_id] = {
            "user_id": user_id,
            "topic": topic,
            "user_position": position,
            "ai_name": "김민수",
            "ai_style": "근거 중심의 차분한 토론 스타일",
            "ai_stance": "PRO" if position == "CON" else "CON",
            "round": 1,
            "participants": ["김민수", "사용자"],
            "start_order": "김민수",
            "user_speeches": [],
            "user_emotions": [],
            "scores": [],
            "last_speakers": []
        }

    phase_map = {
        "OPENING": "입론",
        "REBUTTAL": "반론",
        "COUNTER_REBUTTAL": "재반론",
        "CLOSING": "최종 변론"
    }
    phase_kr = phase_map.get(phase.upper(), phase)

    result = app.config['server'].process_video(video, phase_kr, debate_id, topic, position)
    phase_key_map = {
        "입론": "opening",
        "반론": "rebuttal",
        "재반론": "counter_rebuttal",
        "최종 변론": "closing"
    }
    response = {
        "debate_id": debate_id,  # int 타입으로 반환
        f"user_{phase_key_map[phase_kr]}_text": result["text"],
        "initiative_score": result["initiative_score"],
        "collaborative_score": result["collaborative_score"],
        "communication_score": result["communication_score"],
        "logic_score": result["logic_score"],
        "problem_solving_score": result["problem_solving_score"],
        "voice_score": result["voice_score"],
        "action_score": result["action_score"],
        "initiative_feedback": result["initiative_feedback"],
        "collaborative_feedback": result["collaborative_feedback"],
        "communication_feedback": result["communication_feedback"],
        "logic_feedback": result["logic_feedback"],
        "problem_solving_feedback": result["problem_solving_feedback"],
        "voice_feedback": result["voice_feedback"],
        "action_feedback": result["action_feedback"],
        "feedback": result["feedback"],
        "sample_answer": result["sample_answer"]
    }
    if result["ai_response"]:
        next_phase = {
            "입론": "rebuttal",
            "반론": "counter_rebuttal",
            "재반론": "closing",
            "최종 변론": None
        }.get(phase_kr)
        if next_phase:
            response[f"ai_{next_phase}_text"] = result["ai_response"]
    return jsonify(response)