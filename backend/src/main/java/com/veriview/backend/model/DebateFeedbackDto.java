package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DebateFeedbackDto {
    private String user_text;
    private float initiative_score;
    private float collaborative_score;
    private float communication_score;
    private float logic_score;
    private float problem_solving_score;

    private String initiative_feedback;
    private String collaborative_feedback;
    private String communication_feedback;
    private String logic_feedback;
    private String problem_solving_feedback;

    private String feedback;
    private String sample_answer;
}
