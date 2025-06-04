package com.veriview.backend.controller;

import com.veriview.backend.model.*;
import com.veriview.backend.service.JobPostingService;
import com.veriview.backend.service.RecruitmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


@RestController
@RequestMapping("/api/recruitment")
@RequiredArgsConstructor
public class RecruitmentController {

    private final RecruitmentService recruitmentService;
    private final JobPostingService jobPostingService;

    @PostMapping("/start")
    public ResponseEntity<RecruitmentResponse> recruitment(@RequestBody RecruitmentRequest request) {
        jobPostingService.importCsvData();
        RecruitmentResponse res = recruitmentService.recommendation(request);
        return ResponseEntity.ok(res);
    }
}
