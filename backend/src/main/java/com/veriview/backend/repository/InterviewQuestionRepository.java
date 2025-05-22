package com.veriview.backend.repository;

import com.veriview.backend.entity.InterviewQuestion;

import java.util.Optional;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

public interface InterviewQuestionRepository extends JpaRepository<InterviewQuestion, Integer> {
    Optional<InterviewQuestion> findByInterview_InterviewIdAndQuestionType(int interview_id, InterviewQuestion.QuestionType questionType);

    List<InterviewQuestion> findByInterview_InterviewId(int interviewId);

}
