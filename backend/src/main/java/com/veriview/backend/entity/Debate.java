package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
public class Debate {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int debateId;

    @ManyToOne
    @JoinColumn(name = "user_key")
    private User user;

    @ManyToOne
    @JoinColumn(name = "debate_topic_id")
    private DebateTopic topic;

    @Enumerated(EnumType.STRING)
    private Stance stance;

    public enum Stance { PRO, CON }

    public int getDebateId() {
        return debateId;
    }

    public void setDebateId(int debateId) {
        this.debateId = debateId;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public DebateTopic getTopic() {
        return topic;
    }

    public void setTopic(DebateTopic topic) {
        this.topic = topic;
    }

    public Stance getStance() {
        return stance;
    }

    public void setStance(Stance stance) {
        this.stance = stance;
    }
}