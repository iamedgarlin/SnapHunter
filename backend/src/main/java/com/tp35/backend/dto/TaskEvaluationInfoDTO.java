package com.tp35.backend.dto;

public class TaskEvaluationInfoDTO {
    private String taskDescription;
    private String evaluationCriteria;

    public TaskEvaluationInfoDTO() {
    }

    public TaskEvaluationInfoDTO(String taskDescription, String evaluationCriteria) {
        this.taskDescription = taskDescription;
        this.evaluationCriteria = evaluationCriteria;
    }

    public String getTaskDescription() {
        return taskDescription;
    }

    public void setTaskDescription(String taskDescription) {
        this.taskDescription = taskDescription;
    }

    public String getEvaluationCriteria() {
        return evaluationCriteria;
    }

    public void setEvaluationCriteria(String evaluationCriteria) {
        this.evaluationCriteria = evaluationCriteria;
    }
}