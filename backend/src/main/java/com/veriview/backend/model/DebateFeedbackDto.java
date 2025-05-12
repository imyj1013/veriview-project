package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DebateFeedbackDto {
    private String userText;
    private float initiativeScore;
    private float collaborativeScore;
    private float communicationScore;
    private float logicScore;
    private float problemSolvingScore;

    private String initiativeFeedback;
    private String collaborativeFeedback;
    private String communicationFeedback;
    private String logicFeedback;
    private String problemSolvingFeedback;

    private String feedback;
    private String sampleAnswer;
}
