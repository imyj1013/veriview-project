package com.veriview.backend.repository;

import com.veriview.backend.entity.DebateFeedback;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DebateFeedbackRepository extends JpaRepository<DebateFeedback, Integer> {
    Optional<DebateFeedback> findByDebateAnswer_DebateAnswerId(int debateAnswerId);

}
