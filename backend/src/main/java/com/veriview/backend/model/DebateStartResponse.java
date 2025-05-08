package com.veriview.backend.model;

public class DebateStartResponse {
    private String topic;
    private String position;
    private int debate_id;
    private String ai_opening_text;

    public DebateStartResponse() {}

    public DebateStartResponse(String topic, String position, int debate_id, String ai_opening_text) {
        this.topic = topic;
        this.position = position;
        this.debate_id = debate_id;
        this.ai_opening_text = ai_opening_text;
    }

    public String getTopic() {
        return topic;
    }

    public void setTopic(String topic) {
        this.topic = topic;
    }

    public String getPosition() {
        return position;
    }

    public void setPosition(String position) {
        this.position = position;
    }

    public int getDebate_id() {
        return debate_id;
    }

    public void setDebate_id(int debate_id) {
        this.debate_id = debate_id;
    }

    public String getAi_opening_text() {
        return ai_opening_text;
    }

    public void setAi_opening_text(String ai_opening_text) {
        this.ai_opening_text = ai_opening_text;
    }
}