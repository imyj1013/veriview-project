package com.veriview.backend.model;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class RecruitmentDto {
    private int job_posting_id;
    private String title;
    private String keyword;
    private String corporation;
    
}
