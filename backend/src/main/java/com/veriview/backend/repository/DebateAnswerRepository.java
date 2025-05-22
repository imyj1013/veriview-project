package com.veriview.backend.repository;

import com.veriview.backend.entity.DebateAnswer;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DebateAnswerRepository extends JpaRepository<DebateAnswer, Integer> {
    Optional<DebateAnswer> findByDebate_DebateIdAndPhase(int debateId, DebateAnswer.Phase phase);
}
