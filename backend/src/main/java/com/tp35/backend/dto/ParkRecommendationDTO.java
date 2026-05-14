package com.tp35.backend.dto;

import com.fasterxml.jackson.annotation.JsonIgnore;

public class ParkRecommendationDTO {

    private Integer parkId;
    private String parkName;
    private Double latitude;
    private Double longitude;
    private String transportAccessibility;
    private String taskRichness;
    private String parkHa;
    private String recommendDescription;
    private Double distance;
    private Integer routeCount;

    @JsonIgnore
    private Double transportAccessibilityScore;
    @JsonIgnore
    private Double taskRichnessScore;
    @JsonIgnore
    private Double parkHaLevel;

    public ParkRecommendationDTO() {
    }

    public ParkRecommendationDTO(Integer parkId, String parkName, Double latitude, Double longitude,
                                 String transportAccessibility, String taskRichness,
                                 String parkHa, String recommendDescription, Double transportAccessibilityScore,
                                 Double taskRichnessScore, Double parkHaLevel, Double distance, Integer routeCount) {
        this.parkId = parkId;
        this.parkName = parkName;
        this.latitude = latitude;
        this.longitude = longitude;
        this.transportAccessibility = transportAccessibility;
        this.taskRichness = taskRichness;
        this.parkHa = parkHa;
        this.recommendDescription = recommendDescription;
        this.transportAccessibilityScore = transportAccessibilityScore;
        this.taskRichnessScore = taskRichnessScore;
        this.parkHaLevel = parkHaLevel;
        this.distance = distance;
        this.routeCount = routeCount;
    }

    public Integer getParkId() {
        return parkId;
    }

    public void setParkId(Integer parkId) {
        this.parkId = parkId;
    }

    public String getParkName() {
        return parkName;
    }

    public void setParkName(String parkName) {
        this.parkName = parkName;
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

    public String getTransportAccessibility() {
        return transportAccessibility;
    }

    public void setTransportAccessibility(String transportAccessibilityScore) {
        this.transportAccessibility = transportAccessibilityScore;
    }

    public String getTaskRichness() {
        return taskRichness;
    }

    public void setTaskRichness(String taskRichness) {
        this.taskRichness = taskRichness;
    }

    public String getParkHa() {
        return parkHa;
    }

    public void setParkHa(String parkHa) {
        this.parkHa = parkHa;
    }

    public String getRecommendDescription() {
        return recommendDescription;
    }

    public void setRecommendDescription(String recommendDescription) {
        this.recommendDescription = recommendDescription;
    }

    public Double getTransportAccessibilityScore() {
        return transportAccessibilityScore;
    }

    public void setTransportAccessibilityScore(Double transportAccessibilityScore) {
        this.transportAccessibilityScore = transportAccessibilityScore;
    }

    public Double getTaskRichnessScore() {
        return taskRichnessScore;
    }

    public void setTaskRichnessScore(Double taskRichnessScore) {
        this.taskRichnessScore = taskRichnessScore;
    }

    public Double getParkHaLevel() {
        return parkHaLevel;
    }

    public void setParkHaLevel(Double parkHaLevel) {
        this.parkHaLevel = parkHaLevel;
    }

    public Double getDistance() {
        return distance;
    }

    public void setDistance(Double distance) {
        this.distance = distance;
    }

    public Integer getRouteCount() {
        return routeCount;
    }

    public void setRouteCount(Integer routeCount) {
        this.routeCount = routeCount;
    }
}
