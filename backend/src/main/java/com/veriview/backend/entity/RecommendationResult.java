package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "recommendation_result")
public class RecommendationResult {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int recommendationResultId;

    @ManyToOne
    @JoinColumn(name = "job_posting_id")
    private JobPosting jobPosting;

    @ManyToOne
    @JoinColumn(name = "job_recommendation_id")
    private JobRecommendation jobRecommendation;

    private String title;

    private String keyword;

    private String corporation;


    public int getRecommendationResultId() {
        return recommendationResultId;
    }

    public void setRecommendationResultId(int recommendationResultId) {
        this.recommendationResultId = recommendationResultId;
    }

    public JobPosting getJobPosting() {
        return jobPosting;
    }

    public void setJobPosting(JobPosting jobPosting) {
        this.jobPosting = jobPosting;
    }

    public JobRecommendation getJobRecommendation() {
        return jobRecommendation;
    }

    public void setJobRecommendation(JobRecommendation jobRecommendation) {
        this.jobRecommendation = jobRecommendation;
    }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getKeyword() { return keyword; }
    public void setKeyword(String keyword) { this.keyword = keyword; }

    public String getCorporation() { return corporation; }
    public void setCorporation(String corporation) { this.corporation = corporation; }

}
