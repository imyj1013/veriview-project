package com.veriview.backend.service;

import com.veriview.backend.entity.DebateTopic;
import com.veriview.backend.repository.DebateTopicRepository;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.util.List;

@Service
public class DebateTopicService {

    @Autowired
    private DebateTopicRepository debateTopicRepository;

    private static final String BASE_URL = "https://joberum.com/interview/zocbo/zocbo01.asp?SEARCH_FIELD=TITLE&SEARCH_VALUE=&ORDER_FIELD=WR_DATE&ORDER_METHOD=DESC&pc=1&INTERVIEW_GROUP=INTERVIEW03&INTERVIEW_DETAIL=&m_tab_1=&m_tab_2=3&m_tab_3=&DET_GROUP_TXT=&DET_GROUP_POP_STATE=False&INTERVIEW_SELECTED=&pgsize=1035&page=1";

    @Transactional
    public void crawlAndSaveDebateTopics() {
        try {
            Document doc = Jsoup.connect(BASE_URL).get();
            Elements topics = doc.select("a.cbt"); // `class="cbt"`인 링크 태그 찾기

            for (Element topic : topics) {
                String topicText = topic.text().trim();
                
                // 중복 저장 방지
                if (debateTopicRepository.findByTopic(topicText).isEmpty()) {
                    Long nextId = debateTopicRepository.count() + 1; // ID 값을 직접 설정
                    debateTopicRepository.save(new DebateTopic(nextId, topicText));
                }
            }
        } catch (IOException e) {
            throw new RuntimeException("크롤링 중 오류 발생", e);
        }
    }

    public List<DebateTopic> getAllDebateTopics() {
        return debateTopicRepository.findAll();
    }
}
