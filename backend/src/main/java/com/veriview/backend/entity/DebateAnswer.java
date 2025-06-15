package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "debate_answer")
public class DebateAnswer {
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int debateAnswerId;

    @ManyToOne
    @JoinColumn(name = "debate_id")
    private Debate debate;

    @Enumerated(EnumType.STRING)
    private Phase phase;

    @Column(columnDefinition = "TEXT")
    private String aiAnswer;

    private String aiVideoPath;

    private String videoPath;

    @Column(columnDefinition = "TEXT")
    private String transcript;

    public enum Phase {
        OPENING, REBUTTAL, COUNTER_REBUTTAL, CLOSING
    }

    public int getDebateAnswerId() {
        return debateAnswerId;
    }

    public void setDebateAnswerId(int debateAnswerId) {
        this.debateAnswerId = debateAnswerId;
    }

    public Debate getDebate() {
        return debate;
    }

    public void setDebate(Debate debate) {
        this.debate = debate;
    }

    public Phase getPhase() {
        return phase;
    }

    public void setPhase(Phase phase) {
        this.phase = phase;
    }

    public String getAiAnswer() {
        return aiAnswer;
    }

    public void setAiAnswer(String aiAnswer) {
        this.aiAnswer = aiAnswer;
    }

    public String getAiVideoPath() {
        return aiVideoPath;
    }

    public void setAiVideoPath(String aiVideoPath) {
        this.aiVideoPath = aiVideoPath;
    }

    public String getVideoPath() {
        return videoPath;
    }

    public void setVideoPath(String videoPath) {
        this.videoPath = videoPath;
    }

    public String getTranscript() {
        return transcript;
    }

    public void setTranscript(String transcript) {
        this.transcript = transcript;
    }
}