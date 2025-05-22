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

    //private float contentScore;
    private float voiceScore;
    private float actionScore;
    private float initiativeScore;
    private float communicationScore;
    private float logicScore;    
    private float collaborativeScore;
    private float problemSolvingScore;

    @Column(columnDefinition = "TEXT")
    private String feedback;

    @Column(columnDefinition = "TEXT")
    private String initiativeFeedback;

    @Column(columnDefinition = "TEXT")
    private String communicationFeedback;

    @Column(columnDefinition = "TEXT")
    private String logicFeedback;
    
    @Column(columnDefinition = "TEXT")
    private String collaborativeFeedback;

    @Column(columnDefinition = "TEXT")
    private String problemSolvingFeedback;

    @Column(columnDefinition = "TEXT")
    private String sampleAnswer;

    public int getDebateFeedbackId() {       return debateFeedbackId;    }
    public void setDebateFeedbackId(int debateFeedbackId) {        this.debateFeedbackId = debateFeedbackId;    }

    public DebateAnswer getDebateAnswer() {        return debateAnswer;    }
    public void setDebateAnswer(DebateAnswer debateAnswer) {        this.debateAnswer = debateAnswer;    }

    // public float getContentScore() {
    //     return contentScore;
    // }

    // public void setContentScore(float contentScore) {
    //     this.contentScore = contentScore;
    // }

    public float getVoiceScore() {        return voiceScore;    }
    public void setVoiceScore(float voiceScore) {        this.voiceScore = voiceScore;    }

    public float getActionScore() {        return actionScore;    }
    public void setActionScore(float actionScore) {        this.actionScore = actionScore;    }

    public float getInitiativeScore() {        return initiativeScore;    }
    public void setInitiativeScore(float initiativeScore) {        this.initiativeScore = initiativeScore;    }

    public float getCommunicationScore() {        return communicationScore;    }
    public void setCommunicationScore(float communicationScore) {        this.communicationScore = communicationScore;    }

    public float getLogicScore() {        return logicScore;    }
    public void setLogicScore(float logicScore) {        this.logicScore = logicScore;    }

    public float getCollaborativeScore() {        return collaborativeScore;    }
    public void setCollaborativeScore(float collaborativeScore) {        this.collaborativeScore = collaborativeScore;    }

    public float getProblemSolvingScore() {        return problemSolvingScore;    }
    public void setProblemSolvingScore(float problemSolvingScore) {        this.problemSolvingScore = problemSolvingScore;    }

    public String getFeedback() {        return feedback;    }
    public void setFeedback(String feedback) {        this.feedback = feedback;    }

    public String getInitiativeFeedback() {        return initiativeFeedback;    }
    public void setInitiativeFeedback(String initiativeFeedback) {        this.initiativeFeedback = initiativeFeedback;    }
    
    public String getCommunicationFeedback() {        return communicationFeedback;    }
    public void setCommunicationFeedback(String communicationFeedback) {        this.communicationFeedback = communicationFeedback;    }
    
    public String getLogicFeedback() {        return logicFeedback;    }
    public void setLogicFeedback(String logicFeedback) {        this.logicFeedback = logicFeedback;    }
    
    public String getCollaborativeFeedback() {        return collaborativeFeedback;    }
    public void setCollaborativeFeedback(String collaborativeFeedback) {        this.collaborativeFeedback = collaborativeFeedback;    }
    
    public String getProblemSolvingFeedback() {        return problemSolvingFeedback;    }
    public void setProblemSolvingFeedback(String problemSolvingFeedback) {        this.problemSolvingFeedback = problemSolvingFeedback;    }
    
    public String getSampleAnswer() {        return sampleAnswer;    }
    public void setSampleAnswer(String sampleAnswer) {        this.sampleAnswer = sampleAnswer;    }

}