package com.tp35.backend.dto;

import java.time.LocalDateTime;

public class CompletedTaskDTO {

    private Integer taskId;
    private Integer seriesId;
    private String taskName;
    private String taskDescription;
    private Integer baseDifficulty;
    private Integer rewardPoint;
    private LocalDateTime completeTime;

    public CompletedTaskDTO() {
    }

    public CompletedTaskDTO(Integer taskId, Integer seriesId, String taskName,
                            String taskDescription, Integer baseDifficulty,
                            Integer rewardPoint, LocalDateTime completeTime) {
        this.taskId = taskId;
        this.seriesId = seriesId;
        this.taskName = taskName;
        this.taskDescription = taskDescription;
        this.baseDifficulty = baseDifficulty;
        this.rewardPoint = rewardPoint;
        this.completeTime = completeTime;
    }

    public Integer getTaskId() {
        return taskId;
    }

    public void setTaskId(Integer taskId) {
        this.taskId = taskId;
    }

    public Integer getSeriesId() {
        return seriesId;
    }

    public void setSeriesId(Integer seriesId) {
        this.seriesId = seriesId;
    }

    public String getTaskName() {
        return taskName;
    }

    public void setTaskName(String taskName) {
        this.taskName = taskName;
    }

    public String getTaskDescription() {
        return taskDescription;
    }

    public void setTaskDescription(String taskDescription) {
        this.taskDescription = taskDescription;
    }

    public Integer getBaseDifficulty() {
        return baseDifficulty;
    }

    public void setBaseDifficulty(Integer baseDifficulty) {
        this.baseDifficulty = baseDifficulty;
    }

    public Integer getRewardPoint() {
        return rewardPoint;
    }

    public void setRewardPoint(Integer rewardPoint) {
        this.rewardPoint = rewardPoint;
    }

    public LocalDateTime getCompleteTime() {
        return completeTime;
    }

    public void setCompleteTime(LocalDateTime completeTime) {
        this.completeTime = completeTime;
    }
}