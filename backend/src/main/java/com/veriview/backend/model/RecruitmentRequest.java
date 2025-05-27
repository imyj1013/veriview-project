package com.veriview.backend.model;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class RecruitmentRequest {

    private String user_id;
    private String education;
    private String major;
    private String double_major;
    private String workexperience;
    private String tech_stack;
    private String qualification;
    private String location;
    private String category;
    private String employmenttype;
    
}