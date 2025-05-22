package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class DebateClosingResponse {
    private String topic;
    private String position;
    private int debate_id;
    private String ai_closing_text;
}
