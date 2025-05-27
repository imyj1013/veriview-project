                "question_type": "TECH",
                "question_text": "최근에 관심을 가지고 있는 기술 트렌드가 있다면 설명해주세요."
            }
        ]
        
        # ICT 직무인 경우 기술 관련 질문 추가
        if job_category == 'ICT':
            questions[3]["question_text"] = "본인이 가장 자신있는 프로그래밍 언어는 무엇이며, 그 이유는 무엇인가요?"
        
        return jsonify({
            "interview_id": interview_id,
            "questions": questions
        })
    except Exception as e:
        return jsonify({"error": f"질문 생성 중 오류: {str(e)}"}), 500

@app.route('/ai/interview/<int:interview_id>/question', methods=['GET'])
def get_interview_question(interview_id):
    """면접 질문 조회"""
    try:
        question_type = request.args.get('type', 'general')
        
        # 고정 질문
        questions = {
            "general": "본인의 장점과 단점에 대해 말씀해주세요.",
            "technical": "최근에 관심을 가지고 있는 기술 트렌드가 있다면 무엇인가요?",
            "behavioral": "팀 프로젝트에서 갈등이 생겼을 때 어떻게 해결하셨나요?"
        }
        
        question = get_fixed_interview_question(question_type)
        
        # 응답에 TTS 스트리밍 URL 추가
        response = {
            "interview_id": interview_id,
            "question": question,
            "question_type": question_type,
            "generated_by": "fixed_template"
        }
        
        # 스트리밍 요청인 경우
        if request.args.get('stream') == 'true':
            return stream_tts_response(question)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"질문 조회 중 오류: {str(e)}"}), 500

@app.route('/ai/interview/<int:interview_id>/<question_type>/answer-video', methods=['POST'])
def process_interview_answer(interview_id, question_type):
    """개인면접 답변 영상 처리"""
    if not PERSONAL_INTERVIEW_MODULE_AVAILABLE:
        return jsonify({"error": "개인면접 모듈을 사용할 수 없습니다."}), 500
    
    try:
        if 'file' not in request.files and 'video' not in request.files:
            return jsonify({"error": "영상 파일이 필요합니다."}), 400
        
        file = request.files.get('file') or request.files.get('video')
        
        # 임시 파일 저장
        temp_path = f"temp_interview_{interview_id}.mp4"
        file.save(temp_path)
        
        temp_files = [temp_path]
        
        try:
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
            content_score = min(5.0, 3.0 + 0.5 * len(transcription_result.get("text", "").split()) / 20)
            voice_score = min(5.0, audio_analysis.get("voice_stability", 0.8) * 5)
            action_score = min(5.0, facial_analysis.get("confidence", 0.8) * 5)
            
            # 피드백 생성
            feedback = generate_interview_feedback(question_type, transcription_result.get("text", ""))
            
            # 결과 구성
            result = {
                "interview_id": interview_id,
                "question_type": question_type,
                "answer_text": transcription_result.get("text", ""),
                "content_score": content_score,
                "voice_score": voice_score,
                "action_score": action_score,
                "content_feedback": "내용을 더 구체적으로 설명하면 좋겠습니다.",
                "voice_feedback": "발음이 명확하고 목소리 톤이 안정적입니다.",
                "action_feedback": "시선 처리와 표정 관리가 필요합니다.",
                "feedback": feedback
            }
            
            # 임시 파일 정리
            cleanup_temp_files(temp_files)
            
            return jsonify(result)
            
        except Exception as e:
            cleanup_temp_files(temp_files)
            raise e
        
    except Exception as e:
        return jsonify({"error": f"답변 처리 중 오류: {str(e)}"}), 500

def generate_interview_feedback(question_type, answer_text):
    """면접 질문 유형별 피드백 생성"""
    if not answer_text or len(answer_text) < 10:
        return "답변이 너무 짧습니다. 좀 더 구체적으로 설명해주세요."
    
    # 질문 유형별 피드백
    feedback_templates = {
        "INTRO": "자기소개는 간결하면서도 본인의 특징을 잘 드러내는 것이 중요합니다.",
        "FIT": "직무 적합성을 설명할 때는 구체적인 경험과 역량을 연결지어 설명하는 것이 좋습니다.",
        "PERSONALITY": "성격적 강점을 구체적인 사례와 함께 설명하면 더 설득력이 있습니다.",
        "TECH": "기술적 역량을 설명할 때는 실제 프로젝트 경험과 연결지어 설명하는 것이 효과적입니다.",
        "FOLLOWUP": "추가 질문에 대해 더 구체적인 사례와 결과를 중심으로 답변하면 좋겠습니다."
    }
    
    # 답변 길이에 따른 피드백
    length_feedback = ""
    word_count = len(answer_text.split())
    if word_count < 20:
        length_feedback = "답변이 다소 짧습니다. 좀 더 구체적인 설명이 필요합니다."
    elif word_count > 100:
        length_feedback = "답변이 다소 길어 핵심이 흐려질 수 있습니다. 좀 더 간결하게 정리해보세요."
    else:
        length_feedback = "답변 길이는 적절합니다."
    
    # 최종 피드백 생성
    base_feedback = feedback_templates.get(question_type, feedback_templates["INTRO"])
    return f"{base_feedback} {length_feedback}"

@app.route('/ai/interview/<int:interview_id>/followup-question', methods=['GET'])
def get_followup_question(interview_id):
    """꼬리질문 조회"""
    try:
        # 고정 꼬리질문
        question = "방금 답변해주신 내용에 대해 좀 더 구체적인 사례나 경험을 말씀해주실 수 있을까요?"
        
        # 응답 생성
        response = {
            "interview_id": interview_id,
            "interview_question_id": int(time.time()),
            "question_type": "FOLLOWUP",
            "question_text": question
        }
        
        # 스트리밍 요청인 경우
        if request.args.get('stream') == 'true':
            return stream_tts_response(question)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"꼬리질문 조회 중 오류: {str(e)}"}), 500

@app.route('/ai/interview/<int:interview_id>/generate-followup-question', methods=['POST'])
def generate_followup_question(interview_id):
    """꼬리질문 생성 엔드포인트"""
    try:
        if 'file' not in request.files and 'video' not in request.files:
            return jsonify({"error": "영상 파일이 필요합니다."}), 400
        
        file = request.files.get('file') or request.files.get('video')
        
        # 임시 파일 저장
        temp_path = f"temp_followup_{interview_id}.mp4"
        file.save(temp_path)
        
        # 답변 분석 후 꼬리질문 생성
        audio_path = extract_audio_from_video(temp_path)
        transcription_result = transcribe_with_whisper(audio_path) if audio_path else get_default_transcription()
        answer_text = transcription_result.get("text", "")
        
        # 고정 꼬리질문
        if "프로젝트" in answer_text.lower():
            question = "그 프로젝트에서 가장 어려웠던 점과 어떻게 해결했는지 설명해주실 수 있을까요?"
        elif "경험" in answer_text.lower():
            question = "그 경험을 통해 어떤 것을 배우셨나요?"
        else:
            question = "방금 답변해주신 내용에 대해 좀 더 구체적인 사례나 경험을 말씀해주실 수 있을까요?"
        
        # 임시 파일 정리
        cleanup_temp_files([temp_path, audio_path] if audio_path else [temp_path])
        
        # 응답 생성
        response = {
            "interview_id": interview_id,
            "question_type": "FOLLOWUP",
            "question_text": question
        }
        
        # 스트리밍 요청인 경우
        if request.args.get('stream') == 'true':
            return stream_tts_response(question)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"꼬리질문 생성 중 오류: {str(e)}"}), 500
