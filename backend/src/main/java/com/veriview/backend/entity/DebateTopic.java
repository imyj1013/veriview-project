package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
public class DebateTopic {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int debateTopicId;

    @Column(nullable = false)
    private String topic;

    public DebateTopic() {}

    public DebateTopic(int id, String topic) {
        this.debateTopicId = id;
        this.topic = topic;
    }

    public int getId() {
        return debateTopicId;
    }

    public void setId(int id) {
        this.debateTopicId = id;
    }

    public String getTopic() {
        return topic;
    }

    public void setTopic(String topic) {
        this.topic = topic;
    }
}