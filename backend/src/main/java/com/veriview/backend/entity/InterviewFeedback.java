package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "interview_feedback")
public class InterviewFeedback {
        
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int interviewFeedbackId;

    @ManyToOne
    @JoinColumn(name = "interview_answer_id")
    private InterviewAnswer interviewAnswer;

    private Float actionScore;
    private Float voiceScore;
    private Float contentScore;

    @Column(columnDefinition = "TEXT")
    private String actionFeedback;
    @Column(columnDefinition = "TEXT")
    private String voiceFeedback;
    @Column(columnDefinition = "TEXT")
    private String contentFeedback;
    @Column(columnDefinition = "TEXT")
    private String feedback;

    public int getInterviewFeedbackId() {
        return interviewFeedbackId;
    }

    public void setInterviewFeedbackId(int interviewFeedbackId) {
        this.interviewFeedbackId = interviewFeedbackId;
    }

    public InterviewAnswer getInterviewAnswer() {
        return interviewAnswer;
    }

    public void setInterviewAnswer(InterviewAnswer interviewAnswer) {
        this.interviewAnswer = interviewAnswer;
    }
    
    public Float getActionScore() {     return actionScore;    }
    public void setActionScore(Float actionScore) {     this.actionScore = actionScore;    }
    public Float getVoiceScore() {     return voiceScore;    }
    public void setVoiceScore(Float voiceScore) {     this.voiceScore = voiceScore;    }
    public Float getContentScore() {     return contentScore;    }
    public void setContentScore(Float contentScore) {     this.contentScore = contentScore;    }
    
    public String getActionFeedback() {     return actionFeedback;    }
    public void setActionFeedback(String actionFeedback) {     this.actionFeedback = actionFeedback;    }
    public String getVoiceFeedback() {     return voiceFeedback;    }
    public void setVoiceFeedback(String voiceFeedback) {     this.voiceFeedback = voiceFeedback;    }
    public String getContentFeedback() {     return contentFeedback;    }
    public void setContentFeedback(String contentFeedback) {     this.contentFeedback = contentFeedback;    }
    public String getFeedback() {     return feedback;    }
    public void setFeedback(String feedback) {     this.feedback = feedback;    }
    
    
}
