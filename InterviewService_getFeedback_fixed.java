// InterviewService.java의 getFeedback 메서드 수정본
// 기존 코드를 다음과 같이 수정

public InterviewFeedbackResponse getFeedback(int interviewId) {
    List<InterviewFeedbackDto> interview_feedback = new ArrayList<>();

    for (InterviewQuestion.QuestionType questionType : InterviewQuestion.QuestionType.values()) {
        try {
            InterviewQuestion question = questionRepository
                .findByInterview_InterviewIdAndQuestionType(interviewId, questionType)
                .orElse(null);
                
            if (question == null || question.getQuestionText() == null) {
                // 질문이 없거나 질문 텍스트가 null인 경우 기본 피드백 생성
                InterviewFeedbackDto feedbackDto = new InterviewFeedbackDto();
                feedbackDto.setQuestion_type(questionType.name());
                feedbackDto.setQuestion_text("질문을 불러올 수 없습니다.");
                feedbackDto.setAnswer_text("답변이 제공되지 않았습니다.");
                feedbackDto.setContent_score(0.0f);
                feedbackDto.setVoice_score(0.0f);
                feedbackDto.setAction_score(0.0f);
                feedbackDto.setContent_feedback("질문을 확인해주세요.");
                feedbackDto.setVoice_feedback("답변을 확인해주세요.");
                feedbackDto.setAction_feedback("영상을 확인해주세요.");
                feedbackDto.setFeedback("데이터를 확인해주세요.");
                interview_feedback.add(feedbackDto);
                continue;
            }

            InterviewAnswer answer = answerRepository
                .findByInterviewQuestion_InterviewQuestionId(question.getInterviewQuestionId())
                .orElse(null);

            if (answer == null || answer.getVideoPath() == null) {
                // 답변이 없는 경우 기본 피드백 생성
                InterviewFeedbackDto feedbackDto = new InterviewFeedbackDto();
                feedbackDto.setQuestion_type(questionType.name());
                feedbackDto.setQuestion_text(question.getQuestionText());
                feedbackDto.setAnswer_text("답변이 제공되지 않았습니다.");
                feedbackDto.setContent_score(0.0f);
                feedbackDto.setVoice_score(0.0f);
                feedbackDto.setAction_score(0.0f);
                feedbackDto.setContent_feedback("답변을 녹화해주세요.");
                feedbackDto.setVoice_feedback("답변을 녹화해주세요.");
                feedbackDto.setAction_feedback("답변을 녹화해주세요.");
                feedbackDto.setFeedback("이 질문에 대한 답변을 녹화해주세요.");
                interview_feedback.add(feedbackDto);
                continue;
            }

            File videoFile = new File(answer.getVideoPath());
            if (!videoFile.exists()) {
                // 영상 파일이 없는 경우 기본 피드백 생성
                InterviewFeedbackDto feedbackDto = new InterviewFeedbackDto();
                feedbackDto.setQuestion_type(questionType.name());
                feedbackDto.setQuestion_text(question.getQuestionText());
                feedbackDto.setAnswer_text("영상 파일을 찾을 수 없습니다.");
                feedbackDto.setContent_score(0.0f);
                feedbackDto.setVoice_score(0.0f);
                feedbackDto.setAction_score(0.0f);
                feedbackDto.setContent_feedback("영상을 다시 업로드해주세요.");
                feedbackDto.setVoice_feedback("영상을 다시 업로드해주세요.");
                feedbackDto.setAction_feedback("영상을 다시 업로드해주세요.");
                feedbackDto.setFeedback("영상 파일이 손상되었거나 경로를 찾을 수 없습니다.");
                interview_feedback.add(feedbackDto);
                continue;
            }

            // Flask 서버로 전송하여 분석
            try {
                String flaskUrl = "http://localhost:5000/ai/interview/" + interviewId + "/" + questionType.name() + "/answer-video";

                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.MULTIPART_FORM_DATA);

                MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
                body.add("file", new FileSystemResource(videoFile));

                HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
                ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    flaskUrl,
                    HttpMethod.POST,
                    requestEntity,
                    new ParameterizedTypeReference<>() {}
                );

                Map<String, Object> res = Optional.ofNullable(response.getBody())
                    .orElseThrow(() -> new RuntimeException("Flask response is null"));

                // 답변 업데이트
                answer.setTranscript((String) res.get("answer_text"));
                answerRepository.save(answer);

                // 피드백 업데이트
                InterviewFeedback feedback = feedbackRepository
                    .findByInterviewAnswer_InterviewAnswerId(answer.getInterviewAnswerId())
                    .orElseThrow(() -> new RuntimeException("Feedback not found"));

                // Flask에서 받은 점수를 Float로 변환 (Double일 수도 있음)
                Object contentScoreObj = res.get("content_score");
                Object voiceScoreObj = res.get("voice_score");
                Object actionScoreObj = res.get("action_score");

                feedback.setContentScore(contentScoreObj instanceof Number ? 
                    ((Number) contentScoreObj).floatValue() : 0.0f);
                feedback.setVoiceScore(voiceScoreObj instanceof Number ? 
                    ((Number) voiceScoreObj).floatValue() : 0.0f);
                feedback.setActionScore(actionScoreObj instanceof Number ? 
                    ((Number) actionScoreObj).floatValue() : 0.0f);
                feedback.setContentFeedback((String) res.get("content_feedback"));
                feedback.setVoiceFeedback((String) res.get("voice_feedback"));
                feedback.setActionFeedback((String) res.get("action_feedback"));
                feedback.setFeedback((String) res.get("feedback"));
                feedbackRepository.save(feedback);

                // DTO 생성
                InterviewFeedbackDto feedbackDto = new InterviewFeedbackDto();
                feedbackDto.setQuestion_type(questionType.name());
                feedbackDto.setQuestion_text(question.getQuestionText());
                feedbackDto.setAnswer_text((String) res.get("answer_text"));
                feedbackDto.setContent_score(feedback.getContentScore());
                feedbackDto.setVoice_score(feedback.getVoiceScore());
                feedbackDto.setAction_score(feedback.getActionScore());
                feedbackDto.setContent_feedback((String) res.get("content_feedback"));
                feedbackDto.setVoice_feedback((String) res.get("voice_feedback"));
                feedbackDto.setAction_feedback((String) res.get("action_feedback"));
                feedbackDto.setFeedback((String) res.get("feedback"));

                interview_feedback.add(feedbackDto);

            } catch (Exception e) {
                // Flask 서버 연결 실패 시 기본 피드백
                System.err.println("Flask 서버 연결 실패: " + e.getMessage());
                
                InterviewFeedbackDto feedbackDto = new InterviewFeedbackDto();
                feedbackDto.setQuestion_type(questionType.name());
                feedbackDto.setQuestion_text(question.getQuestionText());
                feedbackDto.setAnswer_text("분석 중 오류가 발생했습니다.");
                feedbackDto.setContent_score(2.5f);
                feedbackDto.setVoice_score(2.5f);
                feedbackDto.setAction_score(2.5f);
                feedbackDto.setContent_feedback("AI 서버 연결 실패");
                feedbackDto.setVoice_feedback("AI 서버 연결 실패");
                feedbackDto.setAction_feedback("AI 서버 연결 실패");
                feedbackDto.setFeedback("AI 분석 서버에 연결할 수 없습니다.");
                interview_feedback.add(feedbackDto);
            }

        } catch (Exception e) {
            System.err.println("피드백 처리 중 오류: " + questionType + " - " + e.getMessage());
            // 예외 발생 시에도 기본 피드백 추가하여 전체 프로세스가 중단되지 않도록 함
            InterviewFeedbackDto feedbackDto = new InterviewFeedbackDto();
            feedbackDto.setQuestion_type(questionType.name());
            feedbackDto.setQuestion_text("오류 발생");
            feedbackDto.setAnswer_text("처리 중 오류 발생");
            feedbackDto.setContent_score(0.0f);
            feedbackDto.setVoice_score(0.0f);
            feedbackDto.setAction_score(0.0f);
            feedbackDto.setContent_feedback("시스템 오류");
            feedbackDto.setVoice_feedback("시스템 오류");
            feedbackDto.setAction_feedback("시스템 오류");
            feedbackDto.setFeedback("시스템 오류가 발생했습니다: " + e.getMessage());
            interview_feedback.add(feedbackDto);
        }
    }

    return new InterviewFeedbackResponse(interviewId, interview_feedback);
}
