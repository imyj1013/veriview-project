package com.veriview.backend.repository;

import com.veriview.backend.entity.InterviewAnswer;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface InterviewAnswerRepository extends JpaRepository<InterviewAnswer, Integer> {
    Optional<InterviewAnswer> findByInterviewQuestion_InterviewQuestionId(int interviewQuestionId);
}
