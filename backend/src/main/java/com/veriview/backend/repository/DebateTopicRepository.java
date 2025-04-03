package com.veriview.backend.repository;

import com.veriview.backend.entity.DebateTopic;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DebateTopicRepository extends JpaRepository<DebateTopic, Long> {
    Optional<DebateTopic> findByTopic(String topic);
}
