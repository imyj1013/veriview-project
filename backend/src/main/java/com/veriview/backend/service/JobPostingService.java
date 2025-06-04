package com.veriview.backend.service;

import com.veriview.backend.entity.JobPosting;
import com.veriview.backend.repository.JobPostingRepository;
import lombok.RequiredArgsConstructor;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.concurrent.ThreadLocalRandom;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

@Service
@RequiredArgsConstructor
public class JobPostingService {

    @Autowired
    private JobPostingRepository repository;

    private final Map<String, List<String>> categoryurl = Map.of(
        "BM", List.of("https://job.incruit.com/jobdb_list/searchjob.asp?occ1=102&occ1=101&occ1=100&occ1=210&page="),
        "SM", List.of("https://job.incruit.com/jobdb_list/searchjob.asp?occ1=160&occ1=106&page="),
        "PS", List.of("https://job.incruit.com/jobdb_list/searchjob.asp?occ2=225&occ2=631&occ1=140&occ1=103&occ1=190&page="),
        "RND", List.of("https://job.incruit.com/jobdb_list/searchjob.asp?occ1=120&occ1=107&page="),
        "ICT", List.of("https://job.incruit.com/jobdb_list/searchjob.asp?occ1=150&page="),
        "ARD", List.of("https://job.incruit.com/jobdb_list/searchjob.asp?occ2=300&occ2=596&occ1=104&occ1=200&page="),
        "MM", List.of("https://job.incruit.com/jobdb_list/searchjob.asp?occ1=170&page=")
    );


    @Transactional
    public void crawlAndSaveAll() {

        for (String category : categoryurl.keySet()) {
            List<String> urls = categoryurl.get(category);

            for (String url : urls) {

                int count = 0;
                for (int page = 0; page <= 100; page++) {
                    
                    try {
                        // User-Agent 설정 및 요청 간 랜덤 딜레이 추가
                        Document doc = Jsoup.connect(url+page)
                                .userAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
                                .timeout(10000) // 10초 타임아웃
                                .get();

                        // 랜덤 딜레이 (500ms ~ 1500ms)
                        Thread.sleep(ThreadLocalRandom.current().nextInt(500, 1501));

                        Elements jobs = doc.select("ul.c_row");

                        if (jobs.isEmpty()) break; // 다음 페이지가 없으면 중단

                        for (Element job : jobs) {
                            try {
                                String title = job.select("div.cell_mid div.cl_top a").text().trim();
                                String deadline = job.select("div.cell_last div.cl_btm span:nth-child(1)").text().trim(); // ~MM/DD(요일)

                                Elements keywordsElem = job.select("div.cell_mid div.cl_btm span");
                                StringBuilder keywordBuilder = new StringBuilder();
                                for (int i = 0; i < Math.min(5, keywordsElem.size()); i++) {
                                    keywordBuilder.append(keywordsElem.get(i).text().trim());
                                    if (i < 4 && i < keywordsElem.size() - 1) keywordBuilder.append(" ");
                                }

                                Elements conditions = job.select("div.cell_mid div.cl_md span");
                                if (conditions.size() < 4) continue;

                                String loc = conditions.get(0).text().trim();
                                String workexp = conditions.get(1).text().trim();
                                String education = conditions.get(2).text().trim();
                                String emp = conditions.get(3).text().trim();
                                String corp = job.select("div.cell_first div.cl_top a").text().trim();

                                if (!repository.existsByTitleAndCorporation(title, corp)) {
                                    JobPosting posting = new JobPosting();
                                    posting.setTitle(title);
                                    posting.setDeadline(deadline);
                                    posting.setKeyword(keywordBuilder.toString());
                                    posting.setLocation(loc);
                                    posting.setWorkexperience(workexp);
                                    posting.setEducation(education);
                                    posting.setEmploymenttype(emp);
                                    posting.setCorporation(corp);
                                    posting.setCategory(category);
                                    repository.save(posting);
                                    count++;
                                    System.out.println("제목: "+title+" 카운트: "+count);
                                }

                            } catch (Exception e) {
                                System.out.println("개별 공고 파싱 중 오류: " + e.getMessage());
                            }
                        }

                    } catch (IOException | InterruptedException e) {
                        System.out.println("페이지 요청 실패: " + url + " | 에러: " + e.getMessage());
                    }

                    if (count > 1000) break;
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

    public String importCsvData() {
        int count = 0;

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(
                        new ClassPathResource("job_postings.csv").getInputStream(), StandardCharsets.UTF_8))) {

            String line = reader.readLine(); // header skip

            while ((line = reader.readLine()) != null) {
                String[] tokens = line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1);

                for (int i = 0; i < tokens.length; i++) {
                    tokens[i] = tokens[i].trim().replaceAll("^\"|\"$", ""); // " 제거
                }

                if (tokens.length < 10) continue;

                if (!repository.existsByTitleAndCorporation(tokens[8], tokens[2])) {
                    JobPosting posting = new JobPosting();
                    posting.setCategory(tokens[1]);
                    posting.setCorporation(tokens[2]);
                    posting.setDeadline(tokens[3]);
                    posting.setEducation(tokens[4]);
                    posting.setEmploymenttype(tokens[5]);
                    posting.setKeyword(tokens[6]);
                    posting.setLocation(tokens[7]);
                    posting.setTitle(tokens[8]);
                    posting.setWorkexperience(tokens[9]);
                    repository.save(posting);
                    count++;
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
            return "CSV import failed: " + e.getMessage();
        }

        return "CSV import completed: " + count + " entries saved.";
    }
}