package com.veriview.backend.controller;

import com.veriview.backend.service.InterviewService;
import com.veriview.backend.model.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/interview")
@RequiredArgsConstructor
public class InterviewController {

    private final InterviewService interviewService;

    @PostMapping("/portfolio")
    public ResponseEntity<Map<String, Object>> postPortfolio(@RequestBody InterviewPortfolioRequest dto) {
        int interviewId = interviewService.savePortfolioAndGenerateQuestions(dto);

        Map<String, Object> response = new HashMap<>();
        response.put("message", "포트폴리오저장성공");
        response.put("interview_id", interviewId);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/{interviewId}/question")
    public ResponseEntity<InterviewQuestionResponse> getInterviewQuestions(@PathVariable int interviewId) {
        InterviewQuestionResponse response = interviewService.getInterviewQuestions(interviewId);
        return ResponseEntity.ok(response);
    }

    @PostMapping("{interviewId}/{questionType}/answer-video")
    public ResponseEntity<Map<String, String>> uploadAnswerVideo(@PathVariable int interviewId, @PathVariable String questionType, @RequestParam("file") MultipartFile videoFile) {
        try {
            String message = interviewService.uploadAnswerVideo(interviewId, questionType, videoFile);
            return ResponseEntity.ok(Map.of("message", message));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "영상 저장 실패: " + e.getMessage()));
        }
    }

    @GetMapping("/{interviewId}/followup-question")
    public ResponseEntity<InterviewFollowupResponse> getFollowupQuestion(@PathVariable int interviewId) {
        InterviewFollowupResponse response = interviewService.getFollowupQuestion(interviewId);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{interviewId}/feedback")
    public ResponseEntity<InterviewFeedbackResponse> getFeedback(@PathVariable int interviewId) {
        InterviewFeedbackResponse response = interviewService.getFeedback(interviewId);
        return ResponseEntity.ok(response);
    }
    
}
