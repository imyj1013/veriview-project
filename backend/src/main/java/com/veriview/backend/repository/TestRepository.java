package com.veriview.backend.repository;

import com.veriview.backend.entity.TestEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TestRepository extends JpaRepository<TestEntity, String> {
    
}
