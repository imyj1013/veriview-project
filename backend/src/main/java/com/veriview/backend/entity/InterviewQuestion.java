package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "interview_question")
public class InterviewQuestion {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int interviewQuestionId;

    @ManyToOne
    @JoinColumn(name = "interview_id")
    private Interview interview;

    @Enumerated(EnumType.STRING)
    private QuestionType questionType;

    public enum QuestionType { INTRO, FIT, PERSONALITY, TECH, FOLLOWUP }
    
    private String aiVideoPath;

    @Column(columnDefinition = "TEXT")
    private String questionText;

    public int getInterviewQuestionId() {
        return interviewQuestionId;
    }

    public void setInterviewQuestionId(int interviewQuestionId) {
        this.interviewQuestionId = interviewQuestionId;
    }

    public Interview getInterview() {
        return interview;
    }

    public void setInterview(Interview interview) {
        this.interview = interview;
    }
    
    public QuestionType getQuestionType() {
        return questionType;
    }

    public void setQuestionType(QuestionType questionType) {
        this.questionType = questionType;
    }
    
    public String getQuestionText() {
        return questionText;
    }

    public void setQuestionText(String questionText) {
        this.questionText = questionText;
    }

    public String getAiVideoPath() {
        return aiVideoPath;
    }

    public void setAiVideoPath(String aiVideoPath) {
        this.aiVideoPath = aiVideoPath;
    }
}
