package com.tp35.backend.dto;

public class TaskDTO {

    private Integer taskID;
    private Integer seriesID;
    private String taskName;
    private String taskDescription;
    private Double latitude;
    private Double longitude;
    private Integer baseDifficulty;
    private Integer rewardPoint;

    public TaskDTO() {
    }

    public Integer getTaskID() {
        return taskID;
    }

    public void setTaskID(Integer taskID) {
        this.taskID = taskID;
    }

    public Integer getSeriesID() {
        return seriesID;
    }

    public void setSeriesID(Integer seriesID) {
        this.seriesID = seriesID;
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