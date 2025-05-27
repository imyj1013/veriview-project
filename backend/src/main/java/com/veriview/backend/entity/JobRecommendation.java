package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "job_recommendation")
public class JobRecommendation {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int jobRecommendationId;

    @ManyToOne
    @JoinColumn(name = "user_key")
    private User user;

    @Column(columnDefinition = "TEXT")
    private String education;

    @Column(columnDefinition = "TEXT")
    private String major;

    @Column(columnDefinition = "TEXT")
    private String doubleMajor;

    @Column(columnDefinition = "TEXT")
    private String workexperience;

    @Column(columnDefinition = "TEXT")
    private String techStack;

    @Column(columnDefinition = "TEXT")
    private String qualification;

    @Column(columnDefinition = "TEXT")
    private String location;

    @Column(columnDefinition = "TEXT")
    private String category;

    @Column(columnDefinition = "TEXT")
    private String employmenttype;


    public int getJobRecommendationId() {
        return jobRecommendationId;
    }

    public void setJobRecommendationId(int jobRecommendationId) {
        this.jobRecommendationId = jobRecommendationId;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public String getEducation() {        return education;    }
    public void setEducation(String education) {        this.education = education;    }

    public String getMajor() {        return major;    }
    public void setMajor(String major) {        this.major = major;    }

    public String getDoubleMajor() {        return doubleMajor;    }
    public void setDoubleMajor(String doubleMajor) {        this.doubleMajor = doubleMajor;    }

    public String getWorkexperience() {        return workexperience;    }
    public void setWorkexperience(String workexperience) {        this.workexperience = workexperience;    }

    public String getTechStack() {        return techStack;    }
    public void setTechStack(String techStack) {        this.techStack = techStack;    }

    public String getQualification() {        return qualification;    }
    public void setQualification(String qualification) {        this.qualification = qualification;    }
    
    public String getLocation() {        return location;    }
    public void setLocation(String location) {        this.location = location;    }

    public String getCategory() {        return category;    }
    public void setCategory(String category) {        this.category = category;    }

    public String getEmploymenttype() {        return employmenttype;    }
    public void setEmploymenttype(String employmenttype) {        this.employmenttype = employmenttype;    }

}
