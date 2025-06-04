package com.veriview.backend.service;

import lombok.RequiredArgsConstructor;

import com.veriview.backend.repository.*;
import com.veriview.backend.entity.*;
import com.veriview.backend.model.*;

import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.core.io.Resource;

import java.util.Map;
import java.util.List;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.util.Optional;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
@RequiredArgsConstructor
public class InterviewService {

    private static final Logger logger = LoggerFactory.getLogger(InterviewService.class);

    private final UserRepository userRepository;
    private final InterviewRepository interviewRepository;
    private final InterviewQuestionRepository questionRepository;
    private final InterviewAnswerRepository answerRepository;
    private final InterviewFeedbackRepository feedbackRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    public int savePortfolioAndGenerateQuestions(InterviewPortfolioRequest dto) {
        switch (dto.getJob_category()) {
            case "경영/사무": dto.setJob_category("BM"); break;
            case "영업/판매": dto.setJob_category("SM"); break;
            case "공공/서비스": dto.setJob_category("PS"); break;
            case "ICT": dto.setJob_category("ICT"); break;
            case "R&D": dto.setJob_category("RND"); break;
            case "생산/정비": dto.setJob_category("MM"); break;
            case "예술/디자인": dto.setJob_category("ARD"); break;
        }

        User user = userRepository.findByUserId(dto.getUser_id()).orElseThrow(() -> new RuntimeException("User not found"));
        // 1. Interview 저장
        Interview interview = new Interview();
        interview.setUser(user);
        interview.setJobCategory(dto.getJob_category());
        interview.setWorkexperience(dto.getWorkexperience());
        interview.setEducation(dto.getEducation());
        interview.setExperienceDescription(dto.getExperience_description());
        interview.setTechStack(dto.getTech_stack());
        interview.setPersonality(dto.getPersonality());

        Interview savedInterview = interviewRepository.save(interview);

        for (InterviewQuestion.QuestionType q : InterviewQuestion.QuestionType.values()) {
            // 1. 질문 생성
            InterviewQuestion question = new InterviewQuestion();
            question.setInterview(savedInterview);
            question.setQuestionType(q);
            InterviewQuestion savedQuestion = questionRepository.save(question);

            // 2. 빈 답변 생성
            InterviewAnswer answer = new InterviewAnswer();
            answer.setInterviewQuestion(savedQuestion);
            InterviewAnswer savedAnswer = answerRepository.save(answer);

            // 3. 빈 피드백 생성
            InterviewFeedback feedback = new InterviewFeedback();
            feedback.setInterviewAnswer(savedAnswer);
            feedbackRepository.save(feedback);
        }

        // 2. Flask에 질문 생성 요청
        String flaskUrl = "http://localhost:5000/ai/interview/generate-question";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, Object> request = new HashMap<>();
        request.put("interview_id", savedInterview.getInterviewId());
        request.put("job_category", dto.getJob_category());
        request.put("workexperience", dto.getWorkexperience());
        request.put("education", dto.getEducation());
        request.put("experience_description", dto.getExperience_description());
        request.put("tech_stack", dto.getTech_stack());
        request.put("personality", dto.getPersonality());

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);

        // ResponseEntity<Map> response = restTemplate.exchange(flaskUrl, HttpMethod.POST, entity, Map.class);

        // List<Map<String, String>> questions = (List<Map<String, String>>) response.getBody().get("questions");
        // for (Map<String, String> q : questions) {
        //     InterviewQuestion question = questionRepository.findByInterview_InterviewIdAndQuestionType(savedInterview.getInterviewId(), InterviewQuestion.QuestionType.valueOf(q.get("question_type"))).orElseThrow(() -> new RuntimeException("Question not found"));
        //     question.setInterview(savedInterview);
        //     question.setQuestionText(q.get("question_text"));
        //     questionRepository.save(question);
        // }

        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
            flaskUrl,
            HttpMethod.POST,
            entity,
            new ParameterizedTypeReference<>() {}
        );

        Map<String, Object> body = response.getBody();
        if (body != null) {
            Object questionsObj = body.get("questions");
            if (questionsObj instanceof List<?>) {
                List<?> questionsList = (List<?>) questionsObj;
                if (!questionsList.isEmpty()) {
                    List<Map<String, String>> questions = new ArrayList<>();
                    for (Object item : questionsList) {
                        if (item instanceof Map<?, ?>) {
                            Map<?, ?> map = (Map<?, ?>) item;
                            Map<String, String> questionMap = new HashMap<>();
                            for (Map.Entry<?, ?> entry : map.entrySet()) {
                                if (entry.getKey() instanceof String && entry.getValue() instanceof String) {
                                    questionMap.put((String) entry.getKey(), (String) entry.getValue());
                                }
                            }
                            questions.add(questionMap);
                        }
                    }
                    
                    if (!questions.isEmpty()) {
                        for (Map<String, String> q : questions) {
                            try {
                                String questionType = q.get("question_type");
                                if (questionType != null) {
                                    InterviewQuestion question = questionRepository
                                        .findByInterview_InterviewIdAndQuestionType(
                                            savedInterview.getInterviewId(),
                                            InterviewQuestion.QuestionType.valueOf(questionType)
                                        ).orElseThrow(() -> new RuntimeException("Question not found"));
                                    question.setInterview(savedInterview);
                                    
                                    String questionText = q.get("question_text");
                                    if (questionText != null) {
                                        question.setQuestionText(questionText);
                                        questionRepository.save(question);

                                        // AI 비디오 생성 및 저장 로직

                                        String videoUrl = "http://localhost:5000/ai/interview/ai-video";
                                        HttpHeaders videoHeaders = new HttpHeaders();
                                        videoHeaders.setContentType(MediaType.APPLICATION_JSON);

                                        Map<String, String> videoRequest = new HashMap<>();
                                        videoRequest.put("question_text", questionText);

                                        try {
                                            ResponseEntity<byte[]> videoResponse = restTemplate.exchange(
                                                videoUrl,
                                                HttpMethod.POST,
                                                new HttpEntity<>(videoRequest, videoHeaders),
                                                byte[].class
                                            );

                                            byte[] videoBytes = videoResponse.getBody();
                                            if (videoBytes != null) {
                                                // 영상 파일 저장 경로 생성
                                                String baseDirPath = new File(System.getProperty("user.dir")).getParentFile().getAbsolutePath() + "/videos";
                                                File baseDir = new File(baseDirPath);
                                                if (!baseDir.exists()) {
                                                    baseDir.mkdirs();
                                                }
                                                String mp4FileName = "interview_ai_" + savedInterview.getInterviewId() + "_" + questionType + "_" + System.currentTimeMillis() + ".mp4";
                                                String filePath = baseDirPath + "/" + mp4FileName;

                                                // 영상 파일을 저장
                                                try (FileOutputStream fos = new FileOutputStream(filePath)) {
                                                    fos.write(videoBytes);
                                                } catch (IOException e) {
                                                    logger.error("Failed to save video file: " + e.getMessage());
                                                }

                                                // InterviewQuestion의 ai_video_path에 경로 저장
                                                question.setAiVideoPath(filePath);
                                                questionRepository.save(question);
                                            }
                                        } catch (Exception e) {
                                            logger.error("Error generating AI video: " + e.getMessage());
                                        }
                                    }
                                }
                            } catch (Exception e) {
                                logger.error("Error processing question: " + e.getMessage());
                            }
                        }
                    }
                }
            }
        }

        return savedInterview.getInterviewId();

        //return 1;
    }
    

    public InterviewQuestionResponse getInterviewQuestions(int interviewId) {
        List<InterviewQuestion> questions = questionRepository.findByInterview_InterviewId(interviewId);

        List<InterviewQuestionDto> questionDtoList = questions.stream().filter(q -> !q.getQuestionType().name().equals("FOLLOWUP"))
            .map(q -> new InterviewQuestionDto(
                q.getInterviewQuestionId(),
                q.getQuestionType().name(),
                q.getQuestionText()))
            .collect(Collectors.toList());

        return new InterviewQuestionResponse(interviewId, questionDtoList);

        // List<InterviewQuestion> questions = questionRepository.findByInterview_InterviewId(interviewId);

        // List<InterviewQuestionDto> questionDtoList = questions.stream().filter(q -> !q.getQuestionType().name().equals("FOLLOWUP"))
        //     .map(q -> new InterviewQuestionDto(
        //         q.getInterviewQuestionId(),
        //         q.getQuestionType().name(),
        //         "면접질문입니다"))
        //     .collect(Collectors.toList());

        // return new InterviewQuestionResponse(interviewId, questionDtoList);
    }

    public ResponseEntity<Resource> getAIVideo(int interviewId, String questionTypeStr) {
        InterviewQuestion.QuestionType questionType;
        try {
            questionType = InterviewQuestion.QuestionType.valueOf(questionTypeStr.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Invalid question type.");
        }

        InterviewQuestion question = questionRepository.findByInterview_InterviewIdAndQuestionType(interviewId, questionType)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Interview question not found."));

        String videoPath = question.getAiVideoPath();
        if (videoPath == null || !new File(videoPath).exists()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "AI video file not found.");
        }

        try {
            FileSystemResource resource = new FileSystemResource(videoPath);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("video/mp4"));
            headers.setContentDisposition(ContentDisposition.inline().filename(resource.getFilename()).build());

            return ResponseEntity.ok().headers(headers).contentLength(resource.contentLength()).body(resource);

        } catch (IOException e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to read video file.");
        }

    }

    public String uploadAnswerVideo(int interviewId, String questionType, MultipartFile videoFile) throws IOException {
        // 1. 저장 경로 설정
        String timestamp = String.valueOf(System.currentTimeMillis());
        String fileName = "interview_" + interviewId + "_" + questionType + "_" + timestamp + ".webm";
        String baseDirPath = new File(System.getProperty("user.dir"))
                .getParentFile()
                .getAbsolutePath() + "/videos";

        File baseDir = new File(baseDirPath);
        if (!baseDir.exists()) {
            baseDir.mkdirs();
        }

        File webmdest = new File(baseDirPath + "/" + fileName);
        videoFile.transferTo(webmdest);

        String mp4FileName = "interview_" + interviewId + "_" + questionType + "_" + timestamp + ".mp4";
        String filePath = baseDirPath + "/" + mp4FileName;
        File dest = new File(filePath);

        // FFmpeg로 webm -> mp4 변환
        String command = String.format("ffmpeg -i %s -c:v libx264 -preset fast -crf 23 %s",
                webmdest.getAbsolutePath(), dest.getAbsolutePath());

        ProcessBuilder pb = new ProcessBuilder(command.split(" "));
        pb.redirectErrorStream(true);
        Process process = pb.start();

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line); // 로그 출력
            }
        }

        try {
            int exitCode = process.waitFor();
            if (exitCode != 0) {
                throw new RuntimeException("FFmpeg 변환 실패 (exitCode=" + exitCode + ")");
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Process was interrupted", e);
        }
        InterviewQuestion question = questionRepository.findByInterview_InterviewIdAndQuestionType(interviewId, InterviewQuestion.QuestionType.valueOf(questionType)).orElseThrow(() -> new RuntimeException("Question not found"));
        InterviewAnswer answer = answerRepository.findByInterviewQuestion_InterviewQuestionId(question.getInterviewQuestionId()).orElseThrow(() -> new RuntimeException("Answer not found"));

        answer.setVideoPath(filePath);
        answerRepository.save(answer);

        return "답변영상저장성공";
    }

    public InterviewFollowupResponse getFollowupQuestion(int interviewId) {
        InterviewQuestion question = questionRepository.findByInterview_InterviewIdAndQuestionType(interviewId, InterviewQuestion.QuestionType.valueOf("TECH")).orElseThrow(() -> new RuntimeException("Question not found"));
        InterviewAnswer answer = answerRepository.findByInterviewQuestion_InterviewQuestionId(question.getInterviewQuestionId()).orElseThrow(() -> new RuntimeException("Answer not found"));

        File videoFile = new File(answer.getVideoPath());

        if (!videoFile.exists()) {
            throw new RuntimeException("Video file not found: " + answer.getVideoPath());
        }

        // Flask 서버로 전송
        String flaskUrl = "http://localhost:5000/ai/interview/" + interviewId + "/genergate-followup-question";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new FileSystemResource(videoFile));

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
            flaskUrl,
            org.springframework.http.HttpMethod.POST,
            requestEntity,
            new org.springframework.core.ParameterizedTypeReference<>() {}
        );
    
        Map<String, Object> res = Optional.ofNullable(response.getBody()).orElseThrow(() -> new RuntimeException("Flask response is null"));

        InterviewQuestion followupquestion = questionRepository.findByInterview_InterviewIdAndQuestionType(interviewId, InterviewQuestion.QuestionType.valueOf("FOLLOWUP")).orElseThrow(() -> new RuntimeException("Question not found"));
        followupquestion.setQuestionText((String) res.get("question_text"));
        questionRepository.save(followupquestion);


        return new InterviewFollowupResponse(interviewId, followupquestion.getInterviewQuestionId(), "FOLLOWUP", followupquestion.getQuestionText());

        //return new InterviewFollowupResponse(interviewId, 5, "FOLLOWUP", "꼬리질문입니다.");
    }

    public InterviewFeedbackResponse getFeedback(int interviewId) {

        List<InterviewFeedbackDto> interview_feedback = new ArrayList<>();

        for (InterviewQuestion.QuestionType questionType : InterviewQuestion.QuestionType.values()) {
            InterviewQuestion question = questionRepository.findByInterview_InterviewIdAndQuestionType(interviewId, questionType).orElseThrow(() -> new RuntimeException("Question not found"));
            InterviewAnswer answer = answerRepository.findByInterviewQuestion_InterviewQuestionId(question.getInterviewQuestionId()).orElseThrow(() -> new RuntimeException("Answer not found"));

            File videoFile = new File(answer.getVideoPath());

            if (!videoFile.exists()) {
                throw new RuntimeException("Video file not found: " + answer.getVideoPath());
            }

            // Flask 서버로 전송
            String flaskUrl = "http://localhost:5000/ai/interview/" + interviewId + "/" + questionType.name() + "/answer-video";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", new FileSystemResource(videoFile));

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                flaskUrl,
                org.springframework.http.HttpMethod.POST,
                requestEntity,
                new org.springframework.core.ParameterizedTypeReference<>() {}
            );
        
            Map<String, Object> res = Optional.ofNullable(response.getBody()).orElseThrow(() -> new RuntimeException("Flask response is null"));

            answer.setTranscript((String) res.get("answer_text"));
            answerRepository.save(answer);

            InterviewFeedback feedback = feedbackRepository.findByInterviewAnswer_InterviewAnswerId(answer.getInterviewAnswerId()).orElseThrow(() -> new RuntimeException("Question not found"));
            feedback.setContentScore((Float) res.get("content_score"));
            feedback.setVoiceScore((Float) res.get("voice_score"));
            feedback.setActionScore((Float) res.get("action_score"));
            feedback.setContentFeedback((String) res.get("content_feedback"));
            feedback.setVoiceFeedback((String) res.get("voice_feedback"));
            feedback.setActionFeedback((String) res.get("action_feedback"));
            feedback.setFeedback((String) res.get("feedback"));
            feedbackRepository.save(feedback);

            InterviewFeedbackDto feedbackDto = new InterviewFeedbackDto();
            feedbackDto.setQuestion_type((String) questionType.name());
            feedbackDto.setQuestion_text((String) question.getQuestionText());
            feedbackDto.setAnswer_text((String) res.get("answer_text"));
            feedbackDto.setContent_score((Float) res.get("content_score"));
            feedbackDto.setVoice_score((Float) res.get("voice_score"));
            feedbackDto.setAction_score((Float) res.get("action_score"));
            feedbackDto.setContent_feedback((String) res.get("content_feedback"));
            feedbackDto.setVoice_feedback((String) res.get("voice_feedback"));
            feedbackDto.setAction_feedback((String) res.get("action_feedback"));
            feedbackDto.setFeedback((String) res.get("feedback"));

            interview_feedback.add(feedbackDto);

        }

        // for (InterviewQuestion.QuestionType questionType : InterviewQuestion.QuestionType.values()) {
        //     InterviewQuestion question = questionRepository.findByInterview_InterviewIdAndQuestionType(interviewId, questionType).orElseThrow(() -> new RuntimeException("Question not found"));
        //     InterviewAnswer answer = answerRepository.findByInterviewQuestion_InterviewQuestionId(question.getInterviewQuestionId()).orElseThrow(() -> new RuntimeException("Answer not found"));

        //     File videoFile = new File(answer.getVideoPath());

        //     if (!videoFile.exists()) {
        //         throw new RuntimeException("Video file not found: " + answer.getVideoPath());
        //     }

        //     // Flask 서버로 전송
        //     String flaskUrl = "http://localhost:5000/ai/interview/" + interviewId + "/" + questionType.name() + "/answer-video";

        //     HttpHeaders headers = new HttpHeaders();
        //     headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        //     MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        //     body.add("file", new FileSystemResource(videoFile));

        //     HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        //     ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
        //         flaskUrl,
        //         org.springframework.http.HttpMethod.POST,
        //         requestEntity,
        //         new org.springframework.core.ParameterizedTypeReference<>() {}
        //     );
        
        //     Map<String, Object> res = Optional.ofNullable(response.getBody()).orElseThrow(() -> new RuntimeException("Flask response is null"));

        //     answer.setTranscript((String) "answer_text");
        //     answerRepository.save(answer);

        //     InterviewFeedback feedback = feedbackRepository.findByInterviewAnswer_InterviewAnswerId(answer.getInterviewAnswerId()).orElseThrow(() -> new RuntimeException("Question not found"));
        //     feedback.setContentScore((float) 5);
        //     feedback.setVoiceScore((float) 4);
        //     feedback.setActionScore((float) 3);
        //     feedback.setContentFeedback("content_feedback");
        //     feedback.setVoiceFeedback("voice_feedback");
        //     feedback.setActionFeedback("action_feedback");
        //     feedback.setFeedback("feedback");
        //     feedbackRepository.save(feedback);

        //     InterviewFeedbackDto feedbackDto = new InterviewFeedbackDto();
        //     feedbackDto.setQuestion_type((String) questionType.name());
        //     feedbackDto.setQuestion_text("question");
        //     feedbackDto.setAnswer_text("answer_text");
        //     feedbackDto.setContent_score((float) 5);
        //     feedbackDto.setVoice_score((float) 4);
        //     feedbackDto.setAction_score((float) 3);
        //     feedbackDto.setContent_feedback("content_feedback");
        //     feedbackDto.setVoice_feedback("voice_feedback");
        //     feedbackDto.setAction_feedback("action_feedback");
        //     feedbackDto.setFeedback("feedback");

        //     interview_feedback.add(feedbackDto);

        // }

        return new InterviewFeedbackResponse(interviewId, interview_feedback);

    }
}
