package com.veriview.backend.repository;

import com.veriview.backend.entity.JobPosting;
import org.springframework.data.jpa.repository.JpaRepository;

public interface JobPostingRepository extends JpaRepository<JobPosting, Long> {
    boolean existsByTitleAndCorporation(String title, String corporation);

    long countByCategory(String category);
}