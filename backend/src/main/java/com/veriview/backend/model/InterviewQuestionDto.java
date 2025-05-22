package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class InterviewQuestionDto {
    private int interview_question_id;
    private String question_type;
    private String question_text;
}
