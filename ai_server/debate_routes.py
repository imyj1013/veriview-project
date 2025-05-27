# ==================== 토론면접 API 엔드포인트 ====================

@app.route('/ai/debate/<int:debate_id>/ai-opening', methods=['POST'])
def ai_opening(debate_id):
    """AI 입론 생성 엔드포인트"""
    try:
        data = request.json or {}
        logger.info(f"AI 입론 생성 요청: /ai/debate/{debate_id}/ai-opening")
        
        topic = data.get("topic", "인공지능")
        position = data.get("position", "CON")
        
        # 고정 AI 응답 생성
        ai_response = get_fixed_ai_response("opening", topic)
        
        # TTS 스트리밍 요청인 경우
        if request.args.get('stream') == 'true' and TTS_MODULE_AVAILABLE and tts_module:
            return stream_tts_response(ai_response)
        
        # 일반 JSON 응답
        return jsonify({
            "debate_id": debate_id,
            "ai_opening_text": ai_response,
            "generated_by": "fixed_template",
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
        
        temp_files = [temp_path]
        
        # 오디오 추출
        audio_path = extract_audio_from_video(temp_path)
        if audio_path:
            temp_files.append(audio_path)
        
        # Whisper 음성 인식
        transcription_result = transcribe_with_whisper(audio_path) if audio_path else get_default_transcription()
        
        # Librosa 오디오 분석
        audio_analysis = process_audio_with_librosa(audio_path) if audio_path else get_default_audio_analysis()
        
        # OpenFace 얼굴 분석
        facial_analysis = analyze_with_openface(temp_path)
        
        # 종합 점수 계산
        scores = calculate_debate_scores_detailed(transcription_result, audio_analysis, facial_analysis)
        
        # 결과 구성
        result = {
            f"user_{current_stage}_text": transcription_result.get("text", ""),
            "emotion": facial_analysis.get("emotion", "중립 (안정적)"),
            **scores,
            "processing_methods": {
                "transcription": "whisper" if WHISPER_AVAILABLE else "default",
                "audio_analysis": "librosa" if LIBROSA_AVAILABLE else "default", 
                "facial_analysis": "openface" if OPENFACE_AVAILABLE else "default"
            },
            "server_type": "test_server"
        }
        
        # 다음 AI 응답 생성 (고정 응답)
        if next_ai_stage:
            topic = request.form.get("topic", "인공지능")
            user_text = transcription_result.get("text", "")
            ai_response = get_fixed_ai_response(next_ai_stage, topic, user_text)
            result[f"ai_{next_ai_stage}_text"] = ai_response
            
            # TTS 스트리밍 응답을 요청한 경우
            if request.args.get('stream') == 'true' and TTS_MODULE_AVAILABLE and tts_module:
                # 임시 파일 정리
                cleanup_temp_files(temp_files)
                # TTS 스트리밍 응답 반환
                return stream_tts_response(ai_response)
        
        # 임시 파일 정리
        cleanup_temp_files(temp_files)
        
        return jsonify(result)
        
    except Exception as e:
        cleanup_temp_files([temp_path])
        return jsonify({"error": f"영상 처리 중 오류: {str(e)}"}), 500

def calculate_debate_scores_detailed(transcription: Dict, audio: Dict, facial: Dict) -> Dict[str, Any]:
    """상세한 토론 점수 계산"""
    try:
        text = transcription.get("text", "")
        confidence = transcription.get("confidence", 0.85)
        voice_stability = audio.get("voice_stability", 0.8)
        fluency = audio.get("fluency_score", 0.85)
        speaking_rate = audio.get("speaking_rate_wpm", 120)
        facial_confidence = facial.get("confidence", 0.8)
        
        # 기본 점수 계산
        scores = {
            "initiative_score": min(5.0, 3.0 + confidence * 2),
            "collaborative_score": min(5.0, 3.0 + min(1.0, len(text.split()) / 80)),
            "communication_score": min(5.0, 3.0 + fluency * 2),
            "logic_score": min(5.0, 3.0 + calculate_logic_score_detailed(text)),
            "problem_solving_score": min(5.0, 3.0 + calculate_problem_solving_score_detailed(text)),
            "voice_score": min(5.0, voice_stability * 5),
            "action_score": min(5.0, facial_confidence * 5)
        }
        
        # 말하기 속도 보정
        if 80 <= speaking_rate <= 160:  # 적절한 속도
            scores["communication_score"] = min(5.0, scores["communication_score"] + 0.3)
        
        # 피드백 생성
        feedback_categories = {
            "initiative": "적극성",
            "collaborative": "협력성",
            "communication": "의사소통",
            "logic": "논리성",
            "problem_solving": "문제해결",
            "voice": "음성품질",
            "action": "행동표현"
        }
        
        for category, korean_name in feedback_categories.items():
            score = scores[f"{category}_score"]
            if score >= 4.5:
                scores[f"{category}_feedback"] = f"{korean_name}: 매우 우수함"
            elif score >= 4.0:
                scores[f"{category}_feedback"] = f"{korean_name}: 우수함"
            elif score >= 3.5:
                scores[f"{category}_feedback"] = f"{korean_name}: 양호함"
            elif score >= 3.0:
                scores[f"{category}_feedback"] = f"{korean_name}: 보통"
            else:
                scores[f"{category}_feedback"] = f"{korean_name}: 개선 필요"
        
        # 종합 피드백
        avg_score = sum(scores[k] for k in scores if k.endswith("_score")) / 7
        if avg_score >= 4.5:
            scores["feedback"] = "매우 우수한 토론 수행을 보여주었습니다. 논리적 구성과 표현력이 뛰어납니다."
        elif avg_score >= 4.0:
            scores["feedback"] = "우수한 토론 수행을 보여주었습니다. 전반적으로 안정적인 발표였습니다."
        elif avg_score >= 3.5:
            scores["feedback"] = "양호한 토론 수행을 보여주었습니다. 몇 가지 부분에서 더 발전시킬 여지가 있습니다."
        elif avg_score >= 3.0:
            scores["feedback"] = "기본적인 토론 수행은 양호합니다. 좀 더 적극적인 자세와 명확한 표현이 필요합니다."
        else:
            scores["feedback"] = "토론 수행에 전반적인 개선이 필요합니다. 충분한 준비와 연습을 통해 발전시켜 보세요."
        
        scores["sample_answer"] = generate_sample_answer(text, avg_score)
        
        return scores
        
    except Exception as e:
        logger.error(f"토론 점수 계산 오류: {str(e)}")
        return get_default_debate_scores()

def calculate_logic_score_detailed(text: str) -> float:
    """상세한 논리성 점수 계산"""
    logic_indicators = ["따라서", "그러므로", "결론적으로", "왜냐하면", "근거는", "예를 들어", "첫째", "둘째", "셋째"]
    logic_count = sum(1 for indicator in logic_indicators if indicator in text)
    
    # 텍스트 길이 고려
    text_length_bonus = min(0.3, len(text) / 200)
    
    return min(2.0, logic_count * 0.3 + text_length_bonus)

def calculate_problem_solving_score_detailed(text: str) -> float:
    """상세한 문제해결 점수 계산"""
    problem_solving_indicators = ["해결", "방안", "대안", "개선", "전략", "접근", "해결책", "방법"]
    problem_count = sum(1 for indicator in problem_solving_indicators if indicator in text)
    
    # 구체성 보너스
    concrete_indicators = ["구체적으로", "실제로", "실천", "구현", "적용"]
    concrete_count = sum(1 for indicator in concrete_indicators if indicator in text)
    
    return min(2.0, problem_count * 0.3 + concrete_count * 0.2)

def generate_sample_answer(user_text: str, avg_score: float) -> str:
    """샘플 답변 생성"""
    if avg_score >= 4.0:
        return "논리적 구성과 구체적 예시가 잘 어우러진 답변이었습니다. 이런 수준을 유지하세요."
    elif avg_score >= 3.5:
        return "기본적인 구성은 좋았습니다. 더 구체적인 근거와 예시를 추가하면 더욱 설득력있는 답변이 될 것입니다."
    else:
        return "논리적 구조를 갖추고 구체적 예시를 들어 설명하는 연습이 필요합니다. '첫째, 둘째, 셋째' 같은 표현을 활용해보세요."

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

# AI 단계별 응답 엔드포인트들 (고정 응답)
@app.route('/ai/debate/<int:debate_id>/ai-rebuttal', methods=['GET'])
def ai_rebuttal(debate_id):
    """AI 반론 생성"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("rebuttal", topic)
        
        # TTS 스트리밍 요청인 경우
        if request.args.get('stream') == 'true' and TTS_MODULE_AVAILABLE and tts_module:
            return stream_tts_response(ai_response)
        
        return jsonify({
            "debate_id": debate_id, 
            "ai_rebuttal_text": ai_response, 
            "generated_by": "fixed_template"
        })
    except Exception as e:
        return jsonify({"error": f"AI 반론 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/debate/<int:debate_id>/ai-counter-rebuttal', methods=['GET'])
def ai_counter_rebuttal(debate_id):
    """AI 재반론 생성"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("counter_rebuttal", topic)
        
        # TTS 스트리밍 요청인 경우
        if request.args.get('stream') == 'true' and TTS_MODULE_AVAILABLE and tts_module:
            return stream_tts_response(ai_response)
        
        return jsonify({
            "debate_id": debate_id, 
            "ai_counter_rebuttal_text": ai_response, 
            "generated_by": "fixed_template"
        })
    except Exception as e:
        return jsonify({"error": f"AI 재반론 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/debate/<int:debate_id>/ai-closing', methods=['GET'])
def ai_closing(debate_id):
    """AI 최종 변론 생성"""
    try:
        topic = request.args.get("topic", "인공지능")
        ai_response = get_fixed_ai_response("closing", topic)
        
        # TTS 스트리밍 요청인 경우
        if request.args.get('stream') == 'true' and TTS_MODULE_AVAILABLE and tts_module:
            return stream_tts_response(ai_response)
        
        return jsonify({
            "debate_id": debate_id, 
            "ai_closing_text": ai_response, 
            "generated_by": "fixed_template"
        })
    except Exception as e:
        return jsonify({"error": f"AI 최종 변론 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/debate/modules-status', methods=['GET'])
def modules_status():
    """모듈 상태 확인"""
    return jsonify({
        "status": "active",
        "server_type": "test_server",
        "note": "LLM 모듈 제외, 나머지 AI 모듈 사용 + 고정 응답",
        "modules": {
            "llm": {
                "available": False,
                "note": "LLM 대신 고정 응답 사용"
            },
            "openface": {
                "available": OPENFACE_AVAILABLE,
                "functions": ["analyze_video", "extract_features"] if OPENFACE_AVAILABLE else []
            },
            "whisper": {
                "available": WHISPER_AVAILABLE,
                "functions": ["transcribe_video"] if WHISPER_AVAILABLE else []
            },
            "tts": {
                "available": TTS_MODULE_AVAILABLE,
                "functions": ["text_to_speech"] if TTS_MODULE_AVAILABLE else []
            },
            "librosa": {
                "available": LIBROSA_AVAILABLE,
                "functions": ["analyze_audio", "extract_features"] if LIBROSA_AVAILABLE else []
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
