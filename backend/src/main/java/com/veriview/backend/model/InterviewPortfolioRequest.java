package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class InterviewPortfolioRequest {
    private String user_id;
    private String job_category;
    private String workexperience;
    private String education;
    private String experience_description;
    private String tech_stack;
    private String personality;
    
}
