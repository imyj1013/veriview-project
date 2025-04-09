package com.veriview.backend.controller;

import com.veriview.backend.service.JobPostingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/job-postings")
public class JobPostingController {

    @Autowired
    private JobPostingService service;

    @PostMapping("/crawl")
    public String crawlJobPostings() {
        service.crawlAndSaveAll();
        return "채용 공고 크롤링 완료!";
    }
}