package com.veriview.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class DebateCounterRebuttalResponse {
    private String topic;
    private String position;
    private int debateId;
    private String aiCounterRebuttalText;
}