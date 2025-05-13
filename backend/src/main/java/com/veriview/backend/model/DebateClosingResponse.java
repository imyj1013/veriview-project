package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class DebateClosingResponse {
    private String topic;
    private String position;
    private int debateId;
    private String aiClosingText;
}
