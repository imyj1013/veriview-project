package com.veriview.backend.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.veriview.backend.entity.TestEntity;
import com.veriview.backend.repository.TestRepository;

@Service
public class TestService {

    @Autowired
    private TestRepository testRepository;

    public void saveTestEntity(TestEntity testEntity) {
        testRepository.save(testEntity);
    }

    public List<TestEntity> getAllTestEntities() {
        return testRepository.findAll();
    }
    
}
