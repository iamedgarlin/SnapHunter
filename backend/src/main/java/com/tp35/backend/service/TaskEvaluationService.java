package com.tp35.backend.service;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.tp35.backend.dto.TaskEvaluationInfoDTO;
import com.tp35.backend.dto.TaskEvaluationResultDTO;
import com.tp35.backend.repository.TaskEvaluationRepository;

@Service
public class TaskEvaluationService {

    private final TaskEvaluationRepository taskEvaluationRepository;
    private final GeminiEvaluationService geminiEvaluationService;

    public TaskEvaluationService(
            TaskEvaluationRepository taskEvaluationRepository,
            GeminiEvaluationService geminiEvaluationService
    ) {
        this.taskEvaluationRepository = taskEvaluationRepository;
        this.geminiEvaluationService = geminiEvaluationService;
    }

    public TaskEvaluationResultDTO evaluateTask(Integer taskId, MultipartFile file) throws Exception {
        TaskEvaluationInfoDTO taskInfo = taskEvaluationRepository.findTaskEvaluationInfoByTaskId(taskId);

        if (taskInfo == null) {
            throw new RuntimeException("Task not found");
        }

        return geminiEvaluationService.evaluateTask(
                taskInfo.getTaskDescription(),
                taskInfo.getEvaluationCriteria(),
                file
        );
    }
}