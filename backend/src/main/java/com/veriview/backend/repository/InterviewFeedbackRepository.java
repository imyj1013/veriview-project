package com.veriview.backend.repository;

import com.veriview.backend.entity.InterviewFeedback;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface InterviewFeedbackRepository extends JpaRepository<InterviewFeedback, Integer> {
    Optional<InterviewFeedback> findByInterviewAnswer_InterviewAnswerId(int interviewAnswerId);

}
