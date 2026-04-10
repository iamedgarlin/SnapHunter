package com.tp35.backend.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.tp35.backend.dto.CompletedTaskDTO;
import com.tp35.backend.repository.CompletedTaskRepository;

@Service
public class CompletedTaskService {

    private final CompletedTaskRepository completedTaskRepository;

    public CompletedTaskService(CompletedTaskRepository completedTaskRepository) {
        this.completedTaskRepository = completedTaskRepository;
    }

    public List<CompletedTaskDTO> getCompletedTasksByUserId(Integer userId) {
        return completedTaskRepository.findCompletedTasksByUserId(userId);
    }
}