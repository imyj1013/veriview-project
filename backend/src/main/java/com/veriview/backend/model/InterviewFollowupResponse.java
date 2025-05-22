package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class InterviewFollowupResponse {
    private int interview_id;
    private int interview_question_id;
    private String question_type;
    private String question_text;
}
