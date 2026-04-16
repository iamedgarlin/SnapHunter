package com.tp35.backend.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.tp35.backend.dto.TaskDTO;
import com.tp35.backend.repository.TaskRepository;

@Service
public class TaskService {

    private final TaskRepository taskRepository;

    public TaskService(TaskRepository taskRepository) {
        this.taskRepository = taskRepository;
    }

    public List<TaskDTO> getRandomActiveTasks() {
        return taskRepository.findRandomActiveTasks();
    }

    public List<TaskDTO> getRandomTasksBySeries(Integer seriesId) {
        return taskRepository.findRandomTasksBySeries(seriesId);
    }

    public List<TaskDTO> getAllTasksBySeries(Integer seriesId) {
        return taskRepository.findAllTasksBySeries(seriesId);
    }
}