package com.veriview.backend.service;

import com.veriview.backend.repository.*;
import com.veriview.backend.entity.*;
import com.veriview.backend.model.*;

import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;

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
import java.util.Random;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class DebateService {

    private final UserRepository userRepository;
    private final DebateTopicRepository topicRepository;
    private final DebateRepository debateRepository;
    private final DebateAnswerRepository debateAnswerRepository;
    private final DebateFeedbackRepository debateFeedbackRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    public DebateStartResponse startDebate(String userId) {
        User user = userRepository.findByUserId(userId).orElseThrow(() -> new RuntimeException("User not found"));

        int randomId = new Random().nextInt(9) + 1; // 1부터 424 사이의 정수
        DebateTopic topic = topicRepository.findById(randomId).orElseThrow(() -> new RuntimeException("해당 ID의 주제가 존재하지 않습니다: " + randomId));

        Debate.Stance userStance = Math.random() < 0.5 ? Debate.Stance.PRO : Debate.Stance.CON;
        Debate.Stance aiStance = userStance == Debate.Stance.PRO ? Debate.Stance.CON : Debate.Stance.PRO;

        Debate debate = new Debate();
        debate.setUser(user);
        debate.setTopic(topic);
        debate.setStance(userStance);
        debate = debateRepository.save(debate);

        for (DebateAnswer.Phase phase : DebateAnswer.Phase.values()) {
            DebateAnswer answer = new DebateAnswer();
            answer.setDebate(debate);
            answer.setPhase(phase);
            debateAnswerRepository.save(answer);
    
            DebateFeedback feedback = new DebateFeedback();
            feedback.setDebateAnswer(answer);
            debateFeedbackRepository.save(feedback);
        }

        // Flask 요청
        String flaskUrl = "http://localhost:5000/ai/debate/" + debate.getDebateId() + "/ai-opening";
        Map<String, Object> flaskRequest = new HashMap<>();
        flaskRequest.put("topic", topic.getTopic());
        flaskRequest.put("position", aiStance.name());
        flaskRequest.put("debate_id", debate.getDebateId());

        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
            flaskUrl,
            org.springframework.http.HttpMethod.POST,
            new HttpEntity<>(flaskRequest),
            new org.springframework.core.ParameterizedTypeReference<>() {}
        );

        Map<String, Object> res = Optional.ofNullable(response.getBody()).orElseThrow(() -> new RuntimeException("Flask AI opening response is null"));

        DebateAnswer openingAnswer = debateAnswerRepository.findByDebate_DebateIdAndPhase(debate.getDebateId(), DebateAnswer.Phase.OPENING).orElseThrow(() -> new RuntimeException("Opening phase not found"));
        openingAnswer.setAiAnswer((String) res.get("ai_opening_text"));
        debateAnswerRepository.save(openingAnswer);


        String videoUrl = "http://localhost:5000/ai/debate/ai-opening-video";
        HttpHeaders videoHeaders = new HttpHeaders();
        videoHeaders.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> videoRequest = new HashMap<>();
        videoRequest.put("ai_opening_text", openingAnswer.getAiAnswer());

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
            String mp4FileName = "opening_ai_" + debate.getDebateId() + "_" + System.currentTimeMillis() + ".mp4";
            String filePath = baseDirPath + "/" + mp4FileName;

            // 영상 파일을 저장
            try (FileOutputStream fos = new FileOutputStream(filePath)) {
                fos.write(videoBytes);
            } catch (IOException e) {
                throw new RuntimeException("Failed to save video file", e);
            }

            // debateAnswer의 ai_video_path에 경로 저장
            openingAnswer.setAiVideoPath(filePath);
            debateAnswerRepository.save(openingAnswer);
        }

        return new DebateStartResponse(topic.getTopic(), userStance.name(), debate.getDebateId(), (String) res.get("ai_opening_text"));

        //return new DebateStartResponse("토론주제입니다", "PRO", 5, "ai의 입론입니다");
    }

    public DebateOpeningResponse getAIOpening(int debateId) {
        Debate debate = debateRepository.findById(debateId).orElseThrow(() -> new RuntimeException("Debate not found"));
    
        DebateAnswer opening = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.OPENING).orElseThrow(() -> new RuntimeException("Rebuttal phase not found"));
    
        return new DebateOpeningResponse(
            debate.getTopic().getTopic(),
            debate.getStance().name(),
            debate.getDebateId(),
            opening.getAiAnswer()
        );

        //return new DebateOpeningResponse("토론주제입니다","PRO",5,"ai 입론입니다");
    }

    public ResponseEntity<Resource> getAIOpeningVideo(int debateId) {
        DebateAnswer opening = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.OPENING).orElseThrow(() -> new RuntimeException("Opening phase not found"));
    
        String videoPath = opening.getAiVideoPath();
        if (videoPath == null || !new File(videoPath).exists()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "AI video file not found.");
        }

        try {
            FileSystemResource resource = new FileSystemResource(videoPath);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("video/mp4"));
            headers.setContentDisposition(ContentDisposition.inline().filename(resource.getFilename()).build());
            
            // 캐시 방지 헤더 추가
            headers.setCacheControl("no-cache, no-store, must-revalidate");
            headers.setPragma("no-cache");
            headers.setExpires(0);
            headers.set("Last-Modified", String.valueOf(System.currentTimeMillis()));
            headers.set("ETag", String.valueOf(System.currentTimeMillis()));

            return ResponseEntity.ok().headers(headers).contentLength(resource.contentLength()).body(resource);

        } catch (IOException e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to read video file.");
        }

    }

    public String saveOpeningVideo(int debateId, MultipartFile videoFile) throws IOException {
        // 1. 저장 경로 설정
        String timestamp = String.valueOf(System.currentTimeMillis());
        String fileName = "opening_" + debateId + "_" + timestamp + ".webm";
        String baseDirPath = new File(System.getProperty("user.dir"))
                .getParentFile()
                .getAbsolutePath() + "/videos";

        File baseDir = new File(baseDirPath);
        if (!baseDir.exists()) {
            baseDir.mkdirs();
        }

        String filePath = baseDirPath + "/" + fileName;
        File webmdest = new File(filePath);
        videoFile.transferTo(webmdest);

        String mp4FileName = "opening_" + debateId + "_" + timestamp + ".mp4";
        File dest = new File(baseDirPath + "/" + mp4FileName);

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

        // 2. Flask 서버로 전송
        String flaskUrl = "http://localhost:5000/ai/debate/" + debateId + "/opening-video";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new FileSystemResource(dest));

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
            flaskUrl,
            org.springframework.http.HttpMethod.POST,
            requestEntity,
            new org.springframework.core.ParameterizedTypeReference<>() {}
        );
    
        // res 변수는 위에서 정상적으로 선언되었음
        Map<String, Object> res = Optional.ofNullable(response.getBody()).orElseThrow(() -> new RuntimeException("Flask response is null"));


        // 3. DebateAnswer 저장
        DebateAnswer answer = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.OPENING).orElseThrow(() -> new RuntimeException("Opening phase not found"));
        answer.setVideoPath(baseDirPath + "/" + mp4FileName);
        answer.setTranscript((String) res.get("user_opening_text"));
        debateAnswerRepository.save(answer);

        DebateAnswer ai_answer = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.REBUTTAL).orElseThrow(() -> new RuntimeException("Rebuttal phase not found"));
        ai_answer.setAiAnswer((String) res.get("ai_rebuttal_text"));
        debateAnswerRepository.save(ai_answer);
        

        String videoUrl = "http://localhost:5000/ai/debate/ai-rebuttal-video";
        HttpHeaders videoHeaders = new HttpHeaders();
        videoHeaders.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> videoRequest = new HashMap<>();
        videoRequest.put("ai_rebuttal_text", ai_answer.getAiAnswer());

        ResponseEntity<byte[]> videoResponse = restTemplate.exchange(
            videoUrl,
            HttpMethod.POST,
            new HttpEntity<>(videoRequest, videoHeaders),
            byte[].class
        );

        byte[] videoBytes = videoResponse.getBody();
        if (videoBytes != null) {
            // 영상 파일 저장 경로 생성
            String aimp4FileName = "rebuttal_ai_" + debateId + "_" + System.currentTimeMillis() + ".mp4";
            String aifilePath = baseDirPath + "/" + aimp4FileName;

            // 영상 파일을 저장
            try (FileOutputStream fos = new FileOutputStream(aifilePath)) {
                fos.write(videoBytes);
            } catch (IOException e) {
                throw new RuntimeException("Failed to save video file", e);
            }

            // debateAnswer의 ai_video_path에 경로 저장
            ai_answer.setAiVideoPath(aifilePath);
            debateAnswerRepository.save(ai_answer);
        }

        // 4. Feedback 저장
        DebateFeedback feedback = debateFeedbackRepository.findByDebateAnswer_DebateAnswerId(answer.getDebateAnswerId()).orElseThrow(() -> new RuntimeException("feedback not found"));

        feedback.setInitiativeScore(((Number) res.get("initiative_score")).floatValue());
        feedback.setCollaborativeScore(((Number) res.get("collaborative_score")).floatValue());
        feedback.setCommunicationScore(((Number) res.get("communication_score")).floatValue());
        feedback.setLogicScore(((Number) res.get("logic_score")).floatValue());
        feedback.setProblemSolvingScore(((Number) res.get("problem_solving_score")).floatValue());
        feedback.setVoiceScore(((Number) res.get("voice_score")).floatValue());
        feedback.setActionScore(((Number) res.get("action_score")).floatValue());
        feedback.setInitiativeFeedback((String) res.get("initiative_feedback"));
        feedback.setCollaborativeFeedback((String) res.get("collaborative_feedback"));
        feedback.setCommunicationFeedback((String) res.get("communication_feedback"));
        feedback.setLogicFeedback((String) res.get("logic_feedback"));
        feedback.setProblemSolvingFeedback((String) res.get("problem_solving_feedback"));
        feedback.setFeedback((String) res.get("feedback"));
        feedback.setSampleAnswer((String) res.get("sample_answer"));
        debateFeedbackRepository.save(feedback);

        return "사용자의 입론 영상이 성공적으로 저장되었습니다.";
    }

    public DebateRebuttalResponse getAIRebuttal(int debateId) {
        Debate debate = debateRepository.findById(debateId).orElseThrow(() -> new RuntimeException("Debate not found"));
    
        DebateAnswer rebuttal = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.REBUTTAL).orElseThrow(() -> new RuntimeException("Rebuttal phase not found"));
    
        return new DebateRebuttalResponse(
            debate.getTopic().getTopic(),
            debate.getStance().name(),
            debate.getDebateId(),
            rebuttal.getAiAnswer()
        );

        //return new DebateRebuttalResponse("토론주제입니다","PRO",5,"ai 반론입니다");
    }

    
    public ResponseEntity<Resource> getAIRebuttalVideo(int debateId) {
        DebateAnswer rebuttal = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.REBUTTAL).orElseThrow(() -> new RuntimeException("Rebuttal phase not found"));
    
        String videoPath = rebuttal.getAiVideoPath();
        if (videoPath == null || !new File(videoPath).exists()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "AI video file not found.");
        }

        try {
            FileSystemResource resource = new FileSystemResource(videoPath);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("video/mp4"));
            headers.setContentDisposition(ContentDisposition.inline().filename(resource.getFilename()).build());
            
            // 캐시 방지 헤더 추가
            headers.setCacheControl("no-cache, no-store, must-revalidate");
            headers.setPragma("no-cache");
            headers.setExpires(0);
            headers.set("Last-Modified", String.valueOf(System.currentTimeMillis()));
            headers.set("ETag", String.valueOf(System.currentTimeMillis()));

            return ResponseEntity.ok().headers(headers).contentLength(resource.contentLength()).body(resource);

        } catch (IOException e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to read video file.");
        }

    }

    public String saveRebuttalVideo(int debateId, MultipartFile videoFile) throws IOException {
        // 1. 저장 경로 설정
        String timestamp = String.valueOf(System.currentTimeMillis());
        String fileName = "rebuttal_" + debateId + "_" + timestamp + ".webm";
        String baseDirPath = new File(System.getProperty("user.dir"))
                .getParentFile()
                .getAbsolutePath() + "/videos";

        File baseDir = new File(baseDirPath);
        if (!baseDir.exists()) {
            baseDir.mkdirs();
        }

        String filePath = baseDirPath + "/" + fileName;
        File webmdest = new File(filePath);
        videoFile.transferTo(webmdest);

        String mp4FileName = "rebuttal_" + debateId + "_" + timestamp + ".mp4";
        File dest = new File(baseDirPath + "/" + mp4FileName);

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

        // 2. Flask 서버로 전송
        String flaskUrl = "http://localhost:5000/ai/debate/" + debateId + "/rebuttal-video";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new FileSystemResource(dest));

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
            flaskUrl,
            org.springframework.http.HttpMethod.POST,
            requestEntity,
            new org.springframework.core.ParameterizedTypeReference<>() {}
        );
    
        Map<String, Object> res = Optional.ofNullable(response.getBody()).orElseThrow(() -> new RuntimeException("Flask response is null"));


        // 3. DebateAnswer 저장
        DebateAnswer answer = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.REBUTTAL).orElseThrow(() -> new RuntimeException("Rebuttal phase not found"));
        answer.setVideoPath(baseDirPath + "/" + mp4FileName);
        answer.setTranscript((String) res.get("user_rebuttal_text"));
        debateAnswerRepository.save(answer);

        DebateAnswer ai_answer = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.COUNTER_REBUTTAL).orElseThrow(() -> new RuntimeException("Counter-rebuttal phase not found"));
        ai_answer.setAiAnswer((String) res.get("ai_counter_rebuttal_text"));
        debateAnswerRepository.save(ai_answer);

        

        String videoUrl = "http://localhost:5000/ai/debate/ai-counter-rebuttal-video";
        HttpHeaders videoHeaders = new HttpHeaders();
        videoHeaders.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> videoRequest = new HashMap<>();
        videoRequest.put("ai_counter_rebuttal_text", ai_answer.getAiAnswer());

        ResponseEntity<byte[]> videoResponse = restTemplate.exchange(
            videoUrl,
            HttpMethod.POST,
            new HttpEntity<>(videoRequest, videoHeaders),
            byte[].class
        );

        byte[] videoBytes = videoResponse.getBody();
        if (videoBytes != null) {
            // 영상 파일 저장 경로 생성
            String aimp4FileName = "counter_rebuttal_ai_" + debateId + "_" + System.currentTimeMillis() + ".mp4";
            String aifilePath = baseDirPath + "/" + aimp4FileName;

            // 영상 파일을 저장
            try (FileOutputStream fos = new FileOutputStream(aifilePath)) {
                fos.write(videoBytes);
            } catch (IOException e) {
                throw new RuntimeException("Failed to save video file", e);
            }

            // debateAnswer의 ai_video_path에 경로 저장
            ai_answer.setAiVideoPath(aifilePath);
            debateAnswerRepository.save(ai_answer);
        }


        // 4. Feedback 저장
        DebateFeedback feedback = debateFeedbackRepository.findByDebateAnswer_DebateAnswerId(answer.getDebateAnswerId()).orElseThrow(() -> new RuntimeException("feedback not found"));

        feedback.setInitiativeScore(((Number) res.get("initiative_score")).floatValue());
        feedback.setCollaborativeScore(((Number) res.get("collaborative_score")).floatValue());
        feedback.setCommunicationScore(((Number) res.get("communication_score")).floatValue());
        feedback.setLogicScore(((Number) res.get("logic_score")).floatValue());
        feedback.setProblemSolvingScore(((Number) res.get("problem_solving_score")).floatValue());
        feedback.setVoiceScore(((Number) res.get("voice_score")).floatValue());
        feedback.setActionScore(((Number) res.get("action_score")).floatValue());
        feedback.setInitiativeFeedback((String) res.get("initiative_feedback"));
        feedback.setCollaborativeFeedback((String) res.get("collaborative_feedback"));
        feedback.setCommunicationFeedback((String) res.get("communication_feedback"));
        feedback.setLogicFeedback((String) res.get("logic_feedback"));
        feedback.setProblemSolvingFeedback((String) res.get("problem_solving_feedback"));
        feedback.setFeedback((String) res.get("feedback"));
        feedback.setSampleAnswer((String) res.get("sample_answer"));
        debateFeedbackRepository.save(feedback);

        return "사용자의 반론 영상이 성공적으로 저장되었습니다.";
    }

    public DebateCounterRebuttalResponse getAICounterRebuttal(int debateId) {
        Debate debate = debateRepository.findById(debateId).orElseThrow(() -> new RuntimeException("Debate not found"));
    
        DebateAnswer counterRebuttal = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.COUNTER_REBUTTAL).orElseThrow(() -> new RuntimeException("Counter rebuttal phase not found"));
    
        return new DebateCounterRebuttalResponse(
            debate.getTopic().getTopic(),
            debate.getStance().name(),
            debate.getDebateId(),
            counterRebuttal.getAiAnswer()
        );

        //return new DebateCounterRebuttalResponse("토론주제입니다","PRO",5,"ai 재반론입니다");
    }
    
    public ResponseEntity<Resource> getAICounterRebuttalVideo(int debateId) {
        DebateAnswer counterrebuttal = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.COUNTER_REBUTTAL).orElseThrow(() -> new RuntimeException("Counter Rebuttal phase not found"));
    
        String videoPath = counterrebuttal.getAiVideoPath();
        if (videoPath == null || !new File(videoPath).exists()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "AI video file not found.");
        }

        try {
            FileSystemResource resource = new FileSystemResource(videoPath);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("video/mp4"));
            headers.setContentDisposition(ContentDisposition.inline().filename(resource.getFilename()).build());
            
            // 캐시 방지 헤더 추가
            headers.setCacheControl("no-cache, no-store, must-revalidate");
            headers.setPragma("no-cache");
            headers.setExpires(0);
            headers.set("Last-Modified", String.valueOf(System.currentTimeMillis()));
            headers.set("ETag", String.valueOf(System.currentTimeMillis()));

            return ResponseEntity.ok().headers(headers).contentLength(resource.contentLength()).body(resource);

        } catch (IOException e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to read video file.");
        }

    }

    public String saveCounterRebuttalVideo(int debateId, MultipartFile videoFile) throws IOException {
        // 1. 저장 경로 설정
        String timestamp = String.valueOf(System.currentTimeMillis());
        String fileName = "counter_rebuttal_" + debateId + "_" + timestamp + ".webm";
        String baseDirPath = new File(System.getProperty("user.dir"))
                .getParentFile()
                .getAbsolutePath() + "/videos";

        File baseDir = new File(baseDirPath);
        if (!baseDir.exists()) {
            baseDir.mkdirs();
        }

        String filePath = baseDirPath + "/" + fileName;
        File webmdest = new File(filePath);
        videoFile.transferTo(webmdest);

        String mp4FileName = "counter_rebuttal_" + debateId + "_" + timestamp + ".mp4";
        File dest = new File(baseDirPath + "/" + mp4FileName);

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

        // 2. Flask 서버로 전송
        String flaskUrl = "http://localhost:5000/ai/debate/" + debateId + "/counter-rebuttal-video";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new FileSystemResource(dest));

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
            flaskUrl,
            org.springframework.http.HttpMethod.POST,
            requestEntity,
            new org.springframework.core.ParameterizedTypeReference<>() {}
        );
    
        Map<String, Object> res = Optional.ofNullable(response.getBody()).orElseThrow(() -> new RuntimeException("Flask response is null"));


        // 3. DebateAnswer 저장
        DebateAnswer answer = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.COUNTER_REBUTTAL).orElseThrow(() -> new RuntimeException("Counter-rebuttal phase not found"));
        answer.setVideoPath(baseDirPath + "/" + mp4FileName);
        answer.setTranscript((String) res.get("user_counter_rebuttal_text"));
        debateAnswerRepository.save(answer);

        DebateAnswer ai_answer = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.CLOSING).orElseThrow(() -> new RuntimeException("Closing phase not found"));
        ai_answer.setAiAnswer((String) res.get("ai_closing_text"));
        debateAnswerRepository.save(ai_answer);

        

        String videoUrl = "http://localhost:5000/ai/debate/ai-closing-video";
        HttpHeaders videoHeaders = new HttpHeaders();
        videoHeaders.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> videoRequest = new HashMap<>();
        videoRequest.put("ai_closing_text", ai_answer.getAiAnswer());

        ResponseEntity<byte[]> videoResponse = restTemplate.exchange(
            videoUrl,
            HttpMethod.POST,
            new HttpEntity<>(videoRequest, videoHeaders),
            byte[].class
        );

        byte[] videoBytes = videoResponse.getBody();
        if (videoBytes != null) {
            // 영상 파일 저장 경로 생성
            String aimp4FileName = "closing_ai_" + debateId + "_" + System.currentTimeMillis() + ".mp4";
            String aifilePath = baseDirPath + "/" + aimp4FileName;

            // 영상 파일을 저장
            try (FileOutputStream fos = new FileOutputStream(aifilePath)) {
                fos.write(videoBytes);
            } catch (IOException e) {
                throw new RuntimeException("Failed to save video file", e);
            }

            // debateAnswer의 ai_video_path에 경로 저장
            ai_answer.setAiVideoPath(aifilePath);
            debateAnswerRepository.save(ai_answer);
        }

        // 4. Feedback 저장
        DebateFeedback feedback = debateFeedbackRepository.findByDebateAnswer_DebateAnswerId(answer.getDebateAnswerId()).orElseThrow(() -> new RuntimeException("feedback not found"));

        feedback.setInitiativeScore(((Number) res.get("initiative_score")).floatValue());
        feedback.setCollaborativeScore(((Number) res.get("collaborative_score")).floatValue());
        feedback.setCommunicationScore(((Number) res.get("communication_score")).floatValue());
        feedback.setLogicScore(((Number) res.get("logic_score")).floatValue());
        feedback.setProblemSolvingScore(((Number) res.get("problem_solving_score")).floatValue());
        feedback.setVoiceScore(((Number) res.get("voice_score")).floatValue());
        feedback.setActionScore(((Number) res.get("action_score")).floatValue());
        feedback.setInitiativeFeedback((String) res.get("initiative_feedback"));
        feedback.setCollaborativeFeedback((String) res.get("collaborative_feedback"));
        feedback.setCommunicationFeedback((String) res.get("communication_feedback"));
        feedback.setLogicFeedback((String) res.get("logic_feedback"));
        feedback.setProblemSolvingFeedback((String) res.get("problem_solving_feedback"));
        feedback.setFeedback((String) res.get("feedback"));
        feedback.setSampleAnswer((String) res.get("sample_answer"));
        debateFeedbackRepository.save(feedback);

        return "사용자의 재반론 영상이 성공적으로 저장되었습니다.";
    }

    public DebateClosingResponse getAIClosing(int debateId) {
        Debate debate = debateRepository.findById(debateId).orElseThrow(() -> new RuntimeException("Debate not found"));
    
        DebateAnswer closing = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.CLOSING).orElseThrow(() -> new RuntimeException("Closing phase not found"));
    
        return new DebateClosingResponse(
            debate.getTopic().getTopic(),
            debate.getStance().name(),
            debate.getDebateId(),
            closing.getAiAnswer()
        );

        //return new DebateClosingResponse("토론주제입니다","PRO",5,"ai 최종변론입니다");
    }

    public ResponseEntity<Resource> getAIClosingVideo(int debateId) {
        DebateAnswer closing = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.CLOSING).orElseThrow(() -> new RuntimeException("Closing phase not found"));
    
        String videoPath = closing.getAiVideoPath();
        if (videoPath == null || !new File(videoPath).exists()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "AI video file not found.");
        }

        try {
            FileSystemResource resource = new FileSystemResource(videoPath);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("video/mp4"));
            headers.setContentDisposition(ContentDisposition.inline().filename(resource.getFilename()).build());
            
            // 캐시 방지 헤더 추가
            headers.setCacheControl("no-cache, no-store, must-revalidate");
            headers.setPragma("no-cache");
            headers.setExpires(0);
            headers.set("Last-Modified", String.valueOf(System.currentTimeMillis()));
            headers.set("ETag", String.valueOf(System.currentTimeMillis()));

            return ResponseEntity.ok().headers(headers).contentLength(resource.contentLength()).body(resource);

        } catch (IOException e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to read video file.");
        }

    }

    public String saveClosingVideo(int debateId, MultipartFile videoFile) throws IOException {
        // 1. 저장 경로 설정
        String timestamp = String.valueOf(System.currentTimeMillis());
        String fileName = "closing_" + debateId + "_" + timestamp + ".webm";
        String baseDirPath = new File(System.getProperty("user.dir"))
                .getParentFile()
                .getAbsolutePath() + "/videos";

        File baseDir = new File(baseDirPath);
        if (!baseDir.exists()) {
            baseDir.mkdirs();
        }

        String filePath = baseDirPath + "/" + fileName;
        File webmdest = new File(filePath);
        videoFile.transferTo(webmdest);

        String mp4FileName = "closing_" + debateId + "_" + timestamp + ".mp4";
        File dest = new File(baseDirPath + "/" + mp4FileName);

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

        // 2. Flask 서버로 전송
        String flaskUrl = "http://localhost:5000/ai/debate/" + debateId + "/closing-video";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new FileSystemResource(dest));

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
            flaskUrl,
            org.springframework.http.HttpMethod.POST,
            requestEntity,
            new org.springframework.core.ParameterizedTypeReference<>() {}
        );
    
        Map<String, Object> res = Optional.ofNullable(response.getBody()).orElseThrow(() -> new RuntimeException("Flask response is null"));


        // 3. DebateAnswer 저장
        DebateAnswer answer = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, DebateAnswer.Phase.CLOSING).orElseThrow(() -> new RuntimeException("Closing phase not found"));
        answer.setVideoPath(baseDirPath + "/" + mp4FileName);
        answer.setTranscript((String) res.get("user_closing_text"));
        debateAnswerRepository.save(answer);


        // 4. Feedback 저장
        DebateFeedback feedback = debateFeedbackRepository.findByDebateAnswer_DebateAnswerId(answer.getDebateAnswerId()).orElseThrow(() -> new RuntimeException("feedback not found"));

        feedback.setInitiativeScore(((Number) res.get("initiative_score")).floatValue());
        feedback.setCollaborativeScore(((Number) res.get("collaborative_score")).floatValue());
        feedback.setCommunicationScore(((Number) res.get("communication_score")).floatValue());
        feedback.setLogicScore(((Number) res.get("logic_score")).floatValue());
        feedback.setProblemSolvingScore(((Number) res.get("problem_solving_score")).floatValue());
        feedback.setVoiceScore(((Number) res.get("voice_score")).floatValue());
        feedback.setActionScore(((Number) res.get("action_score")).floatValue());
        feedback.setInitiativeFeedback((String) res.get("initiative_feedback"));
        feedback.setCollaborativeFeedback((String) res.get("collaborative_feedback"));
        feedback.setCommunicationFeedback((String) res.get("communication_feedback"));
        feedback.setLogicFeedback((String) res.get("logic_feedback"));
        feedback.setProblemSolvingFeedback((String) res.get("problem_solving_feedback"));
        feedback.setFeedback((String) res.get("feedback"));
        feedback.setSampleAnswer((String) res.get("sample_answer"));
        debateFeedbackRepository.save(feedback);

        return "사용자의 최종변론 영상이 성공적으로 저장되었습니다.";
    }

    public DebateFeedbackResponse getDebateFeedback(int debateId) {
        Debate debate = debateRepository.findById(debateId).orElseThrow(() -> new RuntimeException("Debate not found"));

        List<DebateFeedbackDto> debate_feedback = new ArrayList<>();

        for (DebateAnswer.Phase phase : DebateAnswer.Phase.values()) {
            DebateAnswer answer = debateAnswerRepository.findByDebate_DebateIdAndPhase(debateId, phase).orElseThrow(() -> new RuntimeException(phase + " phase not found"));
            DebateFeedback feedback = debateFeedbackRepository.findByDebateAnswer_DebateAnswerId(answer.getDebateAnswerId()).orElseThrow(() -> new RuntimeException("Feedback not found for " + phase));
    
            DebateFeedbackDto dto = new DebateFeedbackDto(
                answer.getTranscript(),
                feedback.getInitiativeScore(),
                feedback.getCollaborativeScore(),
                feedback.getCommunicationScore(),
                feedback.getLogicScore(),
                feedback.getProblemSolvingScore(),
    
                feedback.getInitiativeFeedback(),
                feedback.getCollaborativeFeedback(),
                feedback.getCommunicationFeedback(),
                feedback.getLogicFeedback(),
                feedback.getProblemSolvingFeedback(),
    
                feedback.getFeedback(),
                feedback.getSampleAnswer()
            );

            // DebateFeedbackDto dto = new DebateFeedbackDto(
            //     "사용자의 응답",
            //     5,
            //     3,
            //     2,
            //     4,
            //     5,
    
            //     "적극성 피드백",
            //     "협력적태도 피드백",
            //     "의사소통능력 피드백",
            //     "논리력 피드백",
            //     "문제해결능력 피드백",
    
            //     "종합 피드백",
            //     "예시답안"
            // );
    
            debate_feedback.add(dto);
        }
        
        return new DebateFeedbackResponse(
            debate.getDebateId(),
            debate_feedback
        );

        // return new DebateFeedbackResponse(
        //     5,
        //     debate_feedback
        // );
    }
}