from flask import jsonify, request
import os
import time
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

def setup_interview_routes(app, facial_analyzer, speech_analyzer, aistudios_client, video_manager):
    """AI 면접관 관련 라우트 설정"""
    
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
        logger.info(f"면접 피드백 영상 생성 요청 받음")
        
        try:
            data = request.json or {}
            feedback_text = data.get('feedback', '답변을 잘 해주셨습니다. 전반적으로 우수한 수행입니다.')
            interview_id = data.get('interview_id', int(time.time()))
            
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

    return app
