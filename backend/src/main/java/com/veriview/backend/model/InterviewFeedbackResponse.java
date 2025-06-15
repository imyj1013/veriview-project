package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class InterviewFeedbackResponse {
    private int interview_id;
    private List<InterviewFeedbackDto> interview_feedback;
}
