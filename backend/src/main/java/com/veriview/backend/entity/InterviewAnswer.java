package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "interview_answer")
public class InterviewAnswer {

        
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int interviewAnswerId;

    @ManyToOne
    @JoinColumn(name = "interview_question_id")
    private InterviewQuestion interviewQuestion;

    private String videoPath;

    @Column(columnDefinition = "TEXT")
    private String transcript;

    public int getInterviewAnswerId() {
        return interviewAnswerId;
    }

    public void setInterviewAnswerId(int interviewAnswerId) {
        this.interviewAnswerId = interviewAnswerId;
    }

    public InterviewQuestion getInterviewQuestion() {
        return interviewQuestion;
    }

    public void setInterviewQuestion(InterviewQuestion interviewQuestion) {
        this.interviewQuestion = interviewQuestion;
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
