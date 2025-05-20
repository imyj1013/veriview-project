package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class InterviewFeedbackDto {
    private String question_type;
    private String question_text;
    private String answer_text;
    private Float content_score;
    private Float voice_score;
    private Float action_score;
    private String content_feedback;
    private String voice_feedback;
    private String action_feedback;
    private String feedback;

}
