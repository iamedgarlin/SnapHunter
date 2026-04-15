package com.tp35.backend.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.tp35.backend.dto.TaskDTO;
import com.tp35.backend.service.TaskService;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @GetMapping("/random")
    public ResponseEntity<List<TaskDTO>> getRandomTasks() {
        List<TaskDTO> tasks = taskService.getRandomActiveTasks();
        return ResponseEntity.ok(tasks);
    }

    @GetMapping("/series/random")
    public ResponseEntity<List<TaskDTO>> getRandomTasksBySeries(
        @RequestParam Integer seriesId
) {
        return ResponseEntity.ok(taskService.getRandomTasksBySeries(seriesId));
}
}