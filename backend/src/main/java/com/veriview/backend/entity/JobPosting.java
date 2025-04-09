package com.veriview.backend.entity;

import jakarta.persistence.*;

@Entity
//@Table(name = "job_posting")
public class JobPosting {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;
    private String deadline;
    private String keyword;
    private String workexperience;
    private String education;
    private String corporation;
    private String category;

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDeadline() { return deadline; }
    public void setDeadline(String deadline) { this.deadline = deadline; }

    public String getKeyword() { return keyword; }
    public void setKeyword(String keyword) { this.keyword = keyword; }

    public String getWorkexperience() { return workexperience; }
    public void setWorkexperience(String workexperience) { this.workexperience = workexperience; }

    public String getEducation() { return education; }
    public void setEducation(String education) { this.education = education; }

    public String getCorporation() { return corporation; }
    public void setCorporation(String corporation) { this.corporation = corporation; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
}