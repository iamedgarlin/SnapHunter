package com.tp35.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.tp35.backend.dto.TaskEvaluationResultDTO;
import com.tp35.backend.service.TaskEvaluationService;

@RestController
@RequestMapping("/api/tasks")
public class TaskEvaluationController {

    private final TaskEvaluationService taskEvaluationService;

    public TaskEvaluationController(TaskEvaluationService taskEvaluationService) {
        this.taskEvaluationService = taskEvaluationService;
    }

    @PostMapping("/evaluate")
    public ResponseEntity<?> evaluateTask(
            @RequestParam("taskId") Integer taskId,
            @RequestParam("file") MultipartFile file
    ) {
        try {
            TaskEvaluationResultDTO result = taskEvaluationService.evaluateTask(taskId, file);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(
                    new TaskEvaluationResultDTO(false, "Evaluation failed: " + e.getMessage())
            );
        }
    }
}