package com.veriview.backend.controller;

import com.veriview.backend.service.DebateService;
import com.veriview.backend.model.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

import org.springframework.core.io.Resource;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/debate")
@RequiredArgsConstructor
public class DebateController {

    private final DebateService debateService;

    @PostMapping("/start")
    public ResponseEntity<DebateStartResponse> startDebate(@RequestBody DebateStartRequest request) {
        DebateStartResponse response = debateService.startDebate(request.getUser_id());
        return ResponseEntity.ok(response);
    }

    
    @GetMapping("/{debateId}/ai-opening")
    public ResponseEntity<DebateOpeningResponse> getAIOpening(@PathVariable int debateId) {

        DebateOpeningResponse response = debateService.getAIOpening(debateId);
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/{debateId}/ai-opening-video")
    public ResponseEntity<Resource> getAIOpeningVideo(@PathVariable int debateId) {
        return debateService.getAIOpeningVideo(debateId);
    }

    @PostMapping("/{debateId}/opening-video")
    public ResponseEntity<Map<String, String>> uploadOpeningVideo(@PathVariable int debateId, @RequestParam("file") MultipartFile videoFile) {
        try {
            String message = debateService.saveOpeningVideo(debateId, videoFile);
            return ResponseEntity.ok(Map.of("message", message));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "입론 영상 저장 실패: " + e.getMessage()));
        }
    }

    @GetMapping("/{debateId}/ai-rebuttal")
    public ResponseEntity<DebateRebuttalResponse> getAIRebuttal(@PathVariable int debateId) {

        DebateRebuttalResponse response = debateService.getAIRebuttal(debateId);
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/{debateId}/ai-rebuttal-video")
    public ResponseEntity<Resource> getAIRebuttalVideo(@PathVariable int debateId) {
        return debateService.getAIOpeningVideo(debateId);
    }

    @PostMapping("{debateId}/rebuttal-video")
    public ResponseEntity<Map<String, String>> uploadRebuttalVideo(@PathVariable int debateId, @RequestParam("file") MultipartFile videoFile) {
        try {
            String message = debateService.saveRebuttalVideo(debateId, videoFile);
            return ResponseEntity.ok(Map.of("message", message));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "반론 영상 저장 실패: " + e.getMessage()));
        }
    }

    @GetMapping("{debateId}/ai-counter-rebuttal")
    public ResponseEntity<DebateCounterRebuttalResponse> getAICounterRebuttal(@PathVariable int debateId) {

        DebateCounterRebuttalResponse response = debateService.getAICounterRebuttal(debateId);
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/{debateId}/ai-counter-rebuttal-video")
    public ResponseEntity<Resource> getAICounterRebuttalVideo(@PathVariable int debateId) {
        return debateService.getAICounterRebuttalVideo(debateId);
    }

    @PostMapping("{debateId}/counter-rebuttal-video")
    public ResponseEntity<Map<String, String>> uploadCounterRebuttalVideo(@PathVariable int debateId, @RequestParam("file") MultipartFile videoFile) {
        try {
            String message = debateService.saveCounterRebuttalVideo(debateId, videoFile);
            return ResponseEntity.ok(Map.of("message", message));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "재반론 영상 저장 실패: " + e.getMessage()));
        }
    }

    @GetMapping("{debateId}/ai-closing")
    public ResponseEntity<DebateClosingResponse> getAIClosing(@PathVariable int debateId) {

        DebateClosingResponse response = debateService.getAIClosing(debateId);
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/{debateId}/ai-closing-video")
    public ResponseEntity<Resource> getAIClosingVideo(@PathVariable int debateId) {
        return debateService.getAIClosingVideo(debateId);
    }

    @PostMapping("{debateId}/closing-video")
    public ResponseEntity<Map<String, String>> uploadClosingVideo(@PathVariable int debateId, @RequestParam("file") MultipartFile videoFile) {
        try {
            String message = debateService.saveClosingVideo(debateId, videoFile);
            return ResponseEntity.ok(Map.of("message", message));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("message", "반론 영상 저장 실패: " + e.getMessage()));
        }
    }

    @GetMapping("{debateId}/feedback")
    public ResponseEntity<DebateFeedbackResponse> getDebateFeedback(@PathVariable int debateId) {

        DebateFeedbackResponse response = debateService.getDebateFeedback(debateId);
        return ResponseEntity.ok(response);
    }

}