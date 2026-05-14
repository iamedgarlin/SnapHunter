package com.tp35.backend.dto;

public class RouteTaskDTO {

    private Integer taskId;
    private Double distanceFromRouteM;
    private Double latitude;
    private Double longitude;

    public RouteTaskDTO() {
    }

    public Integer getTaskId() {
        return taskId;
    }

    public void setTaskId(Integer taskId) {
        this.taskId = taskId;
    }

    public Double getDistanceFromRouteM() {
        return distanceFromRouteM;
    }

    public void setDistanceFromRouteM(Double distanceFromRouteM) {
        this.distanceFromRouteM = distanceFromRouteM;
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
}