package com.veriview.backend.controller;

import com.veriview.backend.service.DebateTopicService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/debate-topics")
public class DebateTopicController {

    @Autowired
    private DebateTopicService debateTopicService;

    @PostMapping("/import")
    public void importDebateTopics() throws Exception {
        debateTopicService.importTopics("src/main/resources/debate_topic.txt");
    }

    // // 크롤링 실행 엔드포인트
    // @PostMapping("/crawl")
    // public String crawlDebateTopics() {
    //     debateTopicService.crawlAndSaveDebateTopics();
    //     return "토론 면접 주제 크롤링 완료!";
    // }

    // // 모든 토론 주제 조회
    // @GetMapping
    // public List<DebateTopic> getAllDebateTopics() {
    //     return debateTopicService.getAllDebateTopics();
    // }
}
