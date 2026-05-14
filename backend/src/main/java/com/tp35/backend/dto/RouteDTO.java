package com.tp35.backend.dto;

import com.fasterxml.jackson.databind.JsonNode;

public class RouteDTO {

    private Integer routeId;
    private String difficultyLevel;
    private Double distanceM;
    private Integer estimatedTimeSec;
    private JsonNode startPoint;
    private JsonNode stLine;
    private Integer taskCount;

    public RouteDTO() {
    }

    public Integer getRouteId() {
        return routeId;
    }

    public void setRouteId(Integer routeId) {
        this.routeId = routeId;
    }

    public String getDifficultyLevel() {
        return difficultyLevel;
    }

    public void setDifficultyLevel(String difficultyLevel) {
        this.difficultyLevel = difficultyLevel;
    }

    public Double getDistanceM() {
        return distanceM;
    }

    public void setDistanceM(Double distanceM) {
        this.distanceM = distanceM;
    }

    public Integer getEstimatedTimeSec() {
        return estimatedTimeSec;
    }

    public void setEstimatedTimeSec(Integer estimatedTimeSec) {
        this.estimatedTimeSec = estimatedTimeSec;
    }

    public JsonNode getStartPoint() {
        return startPoint;
    }

    public void setStartPoint(JsonNode startPoint) {
        this.startPoint = startPoint;
    }

    public JsonNode getStLine() {
        return stLine;
    }

    public void setStLine(JsonNode stLine) {
        this.stLine = stLine;
    }

    public Integer getTaskCount() {
        return taskCount;
    }

    public void setTaskCount(Integer taskCount) {
        this.taskCount = taskCount;
    }
}

