package com.veriview.backend.model;

public class DebateStartRequest {
    private String user_id;

    public DebateStartRequest() {}

    public DebateStartRequest(String user_id) {
        this.user_id = user_id;
    }

    public String getUser_id() {
        return user_id;
    }

    public void setUser_id(String user_id) {
        this.user_id = user_id;
    }
}