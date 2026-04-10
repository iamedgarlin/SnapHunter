package com.tp35.backend.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.tp35.backend.dto.CompletedTaskDTO;
import com.tp35.backend.service.CompletedTaskService;

@RestController
@RequestMapping("/api/user-tasks")
public class CompletedTaskController {

    private final CompletedTaskService completedTaskService;

    public CompletedTaskController(CompletedTaskService completedTaskService) {
        this.completedTaskService = completedTaskService;
    }

    @GetMapping("/completed")
    public ResponseEntity<List<CompletedTaskDTO>> getCompletedTasks() {
        Integer userId = 1; // temporary test user
        List<CompletedTaskDTO> tasks = completedTaskService.getCompletedTasksByUserId(userId);
        return ResponseEntity.ok(tasks);
    }
}