package com.veriview.backend.service;

import com.veriview.backend.entity.JobPosting;
import com.veriview.backend.repository.JobPostingRepository;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.concurrent.ThreadLocalRandom;

import java.io.IOException;
import java.util.*;

@Service
public class JobPostingService {

    @Autowired
    private JobPostingRepository repository;

    private final Map<String, List<String>> categoryKeywords = Map.of(
        "BM", List.of("관리", "경영", "인사", "행정", "사무", "금융", "보험", "회계", "세무", "감정", "광고", "기획", "조사", "안내", "통계", "비서", "무역사무원", "운송사무원", "생산사무원", "품질사무원"),
        "SM", List.of("영업직", "판매", "판촉", "부동산", "텔레마케터", "매표", "매장계산원", "홍보"),
        "PS", List.of("공공서비스", "교육", "법률", "사회복지", "경찰", "소방", "군인", "보건", "의료", "미용", "호텔", "예식", "여행", "음식", "경비", "경호", "청소", "보육", "간병"),
        "RND", List.of("연구", "건축공학", "제조공학", "토목공학", "기계공학", "로봇", "금속공학", "전기공학", "전자공학", "화학공학", "에너지", "섬유공학", "식품공학", "환경공학", "재료공학", "소방기술자", "방재기술자", "산업안전기술자"),
        "ICT", List.of("정보통신", "하드웨어", "통신공학", "컴퓨터시스템", "소프트웨어", "네트워크", "데이터", "정보보안", "통신", "개발"),
        "ARD", List.of("디자인", "방송", "작가", "번역가", "학예사", "사서", "공연", "영화", "예술", "매니지먼트"),
        "MM", List.of("설치", "정비", "생산", "기계설치", "수리", "가공", "용접", "재단사", "인쇄", "제조")
    );


    @Transactional
    public void crawlAndSaveAll() {
        for (String category : categoryKeywords.keySet()) {
            List<String> keywords = categoryKeywords.get(category);

            for (String keyword : keywords) {
                int count = 0;
                for (int page = 1; page <= 20; page++) {
                    String url = "https://www.saramin.co.kr/zf_user/search?searchType=search&searchword=" + keyword +
                            "&company_type=scale004&recruitPage=" + page + "&recruitSort=relation&recruitPageCount=20";

                    try {
                        // User-Agent 설정 및 요청 간 랜덤 딜레이 추가
                        Document doc = Jsoup.connect(url)
                                .userAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
                                .timeout(10000) // 10초 타임아웃
                                .get();

                        // 랜덤 딜레이 (500ms ~ 1500ms)
                        Thread.sleep(ThreadLocalRandom.current().nextInt(500, 1501));

                        Elements jobs = doc.select("div.item_recruit");

                        if (jobs.isEmpty()) break; // 다음 페이지가 없으면 중단

                        for (Element job : jobs) {
                            try {
                                String title = job.select("h2.job_tit a").attr("title").trim();
                                String deadline = job.select("div.job_date span.date").text().trim(); // ~MM/DD(요일)

                                Elements keywordsElem = job.select("div.job_sector a");
                                StringBuilder keywordBuilder = new StringBuilder();
                                for (int i = 0; i < Math.min(5, keywordsElem.size()); i++) {
                                    keywordBuilder.append(keywordsElem.get(i).text().trim());
                                    if (i < 4 && i < keywordsElem.size() - 1) keywordBuilder.append(" ");
                                }

                                Elements conditions = job.select("div.job_condition span");
                                if (conditions.size() < 3) continue;

                                String workexp = conditions.get(1).text().trim();
                                String education = conditions.get(2).text().trim();
                                String corp = job.select("strong.corp_name a").text().trim();

                                System.out.println("현재 키워드: "+keyword+" 페이지: "+page+" 제목: "+title);

                                if (!repository.existsByTitleAndCorporation(title, corp)) {
                                    JobPosting posting = new JobPosting();
                                    posting.setTitle(title);
                                    posting.setDeadline(deadline);
                                    posting.setKeyword(keywordBuilder.toString());
                                    posting.setWorkexperience(workexp);
                                    posting.setEducation(education);
                                    posting.setCorporation(corp);
                                    posting.setCategory(category);
                                    repository.save(posting);
                                    count++;
                                    System.out.println("저장 키워드: "+keyword+" 페이지: "+page+" 제목: "+title+" 카운트: "+count);
                                }
                                else {
                                    continue;
                                }

                            } catch (Exception e) {
                                System.out.println("개별 공고 파싱 중 오류: " + e.getMessage());
                            }
                        }

                    } catch (IOException | InterruptedException e) {
                        System.out.println("페이지 요청 실패: " + url + " | 에러: " + e.getMessage());
                    }
                }
            }
        }

        long bmCount = repository.countByCategory("BM");
        System.out.println("BM 카테고리의 공고 수: " + bmCount);

        long smCount = repository.countByCategory("SM");
        System.out.println("SM 카테고리의 공고 수: " + smCount);

        long psCount = repository.countByCategory("PS");
        System.out.println("PS 카테고리의 공고 수: " + psCount);

        long rndCount = repository.countByCategory("RND");
        System.out.println("RND 카테고리의 공고 수: " + rndCount);

        long ictCount = repository.countByCategory("ICT");
        System.out.println("ICT 카테고리의 공고 수: " + ictCount);

        long ardCount = repository.countByCategory("ARD");
        System.out.println("ARD 카테고리의 공고 수: " + ardCount);

        long mmCount = repository.countByCategory("MM");
        System.out.println("MM 카테고리의 공고 수: " + mmCount);

    }
}