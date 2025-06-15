package com.veriview.backend.repository;

import com.veriview.backend.entity.DebateTopic;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.Optional;

public interface DebateTopicRepository extends JpaRepository<DebateTopic, Integer> {
    Optional<DebateTopic> findByTopic(String topic);

    @Query(value = "SELECT * FROM debate_topic ORDER BY RAND() LIMIT 1", nativeQuery = true)
    DebateTopic findRandomTopic();
    
    // @Query("SELECT t FROM DebateTopic t WHERE t.id = (SELECT FLOOR(RAND() * (SELECT COUNT(*) FROM DebateTopic)) FROM DebateTopic)")
    // DebateTopic findRandomTopic();
}
