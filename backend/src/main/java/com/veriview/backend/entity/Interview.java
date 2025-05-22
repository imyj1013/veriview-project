package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "interview")
public class Interview {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int interviewId;

    @ManyToOne
    @JoinColumn(name = "user_key")
    private User user;

    private String jobCategory;

    private String workexperience;

    private String education;

    @Column(columnDefinition = "TEXT")
    private String experienceDescription;

    @Column(columnDefinition = "TEXT")
    private String techStack;

    @Column(columnDefinition = "TEXT")
    private String personality;


    public int getInterviewId() {
        return interviewId;
    }

    public void setInterviewId(int interviewId) {
        this.interviewId = interviewId;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public String getJobCategory() {
        return jobCategory;
    }

    public void setJobCategory(String jobCategory) {
        this.jobCategory = jobCategory;
    }

    public String getWorkexperience() {
        return workexperience;
    }

    public void setWorkexperience(String workexperience) {
        this.workexperience = workexperience;
    }

    public String getEducation() {
        return education;
    }

    public void setEducation(String education) {
        this.education = education;
    }

    public String getExperienceDescription() {
        return experienceDescription;
    }

    public void setExperienceDescription(String experienceDescription) {
        this.experienceDescription = experienceDescription;
    }

    public String getTechStack() {
        return techStack;
    }

    public void setTechStack(String techStack) {
        this.techStack = techStack;
    }

    public String getPersonality() {
        return personality;
    }

    public void setPersonality(String personality) {
        this.personality = personality;
    }

    
}
