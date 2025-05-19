package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DebateFeedbackResponse {
    private int debate_id;
    private List<DebateFeedbackDto> debate_feedback;
}
