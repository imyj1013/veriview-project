package com.veriview.backend.service;

import com.veriview.backend.repository.*;
import com.veriview.backend.entity.*;
import com.veriview.backend.model.*;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;

import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;

import lombok.RequiredArgsConstructor;


@Service
@RequiredArgsConstructor
public class RecruitmentService {

    private final JobPostingRepository jobPostingRepository;
    private final JobRecommendationRepository jobRecommendationRepository;
    private final RecommendationResultRepository recommendationResultRepository;
    private final UserRepository userRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    public RecruitmentResponse recommendation(RecruitmentRequest request) {

        User user = userRepository.findByUserId(request.getUser_id()).orElseThrow(() -> new RuntimeException("User not found"));

        JobRecommendation jobRecommendation = new JobRecommendation();
        jobRecommendation.setUser(user);
        jobRecommendation.setCategory(request.getCategory());
        jobRecommendation.setWorkexperience(request.getWorkexperience());
        jobRecommendation.setEducation(request.getEducation());
        jobRecommendation.setMajor(request.getMajor());
        jobRecommendation.setDoubleMajor(request.getDouble_major());
        jobRecommendation.setTechStack(request.getTech_stack());
        jobRecommendation.setQualification(request.getQualification());
        jobRecommendation.setLocation(request.getLocation());
        jobRecommendation.setEmploymenttype(request.getEmploymenttype());
        jobRecommendationRepository.save(jobRecommendation);

        // String flaskUrl = "http://localhost:5000/ai/recruitment/posting";
        // HttpHeaders headers = new HttpHeaders();
        // headers.setContentType(MediaType.APPLICATION_JSON);
        // HttpEntity<RecruitmentRequest> entity = new HttpEntity<>(request, headers);

        // ResponseEntity<RecruitmentResponse> aiResult = restTemplate.exchange(flaskUrl, HttpMethod.POST, entity, RecruitmentResponse.class);

        // RecruitmentResponse response = aiResult.getBody();

        // if (response != null && response.getPosting() != null) {
        //     for (RecruitmentDto posting : response.getPosting()) {
        //         RecommendationResult recommendedJob = new RecommendationResult();
        //         JobPosting jobPosting = jobPostingRepository.findById(Long.valueOf(posting.getJob_posting_id())).orElseThrow(() -> new RuntimeException("JobPosting not found"));
        //         recommendedJob.setJobPosting(jobPosting);
        //         recommendedJob.setJobRecommendation(jobRecommendation);
        //         recommendedJob.setTitle(posting.getTitle());
        //         recommendedJob.setKeyword(posting.getKeyword());
        //         recommendedJob.setCorporation(posting.getCorporation());
        //         recommendationResultRepository.save(recommendedJob);
        //     }
        // }

                ArrayList<RecruitmentDto> dummyPostings = new ArrayList<>();
        for (int i = 1; i <= 5; i++) {
            RecruitmentDto dto = new RecruitmentDto();
            dto.setJob_posting_id(i);
            dto.setTitle("개발자 채용");
            dto.setKeyword("개발, 파이썬");
            dto.setCorporation("네이버");
            dummyPostings.add(dto);

            JobPosting jobPosting = jobPostingRepository.findById(Long.valueOf(i))
                .orElseThrow(() -> new RuntimeException("JobPosting not found"));

            RecommendationResult result = new RecommendationResult();
            result.setJobPosting(jobPosting);
            result.setJobRecommendation(jobRecommendation);
            result.setTitle(dto.getTitle());
            result.setKeyword(dto.getKeyword());
            result.setCorporation(dto.getCorporation());
            recommendationResultRepository.save(result);
        }

        RecruitmentResponse response = new RecruitmentResponse();
        response.setPosting(dummyPostings);

        return response;

    }
    
}
