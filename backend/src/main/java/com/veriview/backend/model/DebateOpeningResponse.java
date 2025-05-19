package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class DebateOpeningResponse {
    private String topic;
    private String position;
    private int debate_id;
    private String ai_opening_text;
}