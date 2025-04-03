package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
public class DebateTopic {

    @Id
    private Long id; // @GeneratedValue 제거

    @Column(nullable = false, unique = true)
    private String topic;

    public DebateTopic() {}

    public DebateTopic(Long id, String topic) {
        this.id = id;
        this.topic = topic;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTopic() {
        return topic;
    }

    public void setTopic(String topic) {
        this.topic = topic;
    }
}