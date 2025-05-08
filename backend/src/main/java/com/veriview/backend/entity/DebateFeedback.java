package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "debate_feedback")
public class DebateFeedback {
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int debateFeedbackId;

    @OneToOne
    @JoinColumn(name = "debate_answer_id")
    private DebateAnswer debateAnswer;

    private float contentScore;
    private float voiceScore;
    private float actionScore;

    @Column(columnDefinition = "TEXT")
    private String feedback;

    public int getDebateFeedbackId() {
        return debateFeedbackId;
    }

    public void setDebateFeedbackId(int debateFeedbackId) {
        this.debateFeedbackId = debateFeedbackId;
    }

    public DebateAnswer getDebateAnswer() {
        return debateAnswer;
    }

    public void setDebateAnswer(DebateAnswer debateAnswer) {
        this.debateAnswer = debateAnswer;
    }

    public float getContentScore() {
        return contentScore;
    }

    public void setContentScore(float contentScore) {
        this.contentScore = contentScore;
    }

    public float getVoiceScore() {
        return voiceScore;
    }

    public void setVoiceScore(float voiceScore) {
        this.voiceScore = voiceScore;
    }

    public float getActionScore() {
        return actionScore;
    }

    public void setActionScore(float actionScore) {
        this.actionScore = actionScore;
    }

    public String getFeedback() {
        return feedback;
    }

    public void setFeedback(String feedback) {
        this.feedback = feedback;
    }
}