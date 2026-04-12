package com.tp35.backend.dto;

public class TaskDTO {

    private Integer taskId;
    private Integer seriesId;
    private String taskName;
    private String taskDescription;
    private Double latitude;
    private Double longitude;
    private Integer baseDifficulty;
    private Integer rewardPoint;

    public TaskDTO() {
    }

    public TaskDTO(Integer taskId, Integer seriesId, String taskName,
               String taskDescription, Double latitude, Double longitude,
               Integer baseDifficulty, Integer rewardPoint) {
    this.taskId = taskId;
    this.seriesId = seriesId;
    this.taskName = taskName;
    this.taskDescription = taskDescription;
    this.latitude = latitude;
    this.longitude = longitude;
    this.baseDifficulty = baseDifficulty;
    this.rewardPoint = rewardPoint;
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

    public Double getLatitude() {
        return latitude;
    }

    public void setLatitude(Double latitude) {
        this.latitude = latitude;
    }

    public Double getLongitude() {
        return longitude;
    }

    public void setLongitude(Double longitude) {
        this.longitude = longitude;
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
}