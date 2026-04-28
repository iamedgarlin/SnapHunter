package com.tp35.backend.dto;

public class ParkDTO {

    private Integer parkId;
    private Double latitude;
    private Double longitude;
    private String description;
    private String parkName;

    public ParkDTO() {
    }

    public ParkDTO(Integer parkId, Double latitude, Double longitude,
                   String description, String parkName) {
        this.parkId = parkId;
        this.latitude = latitude;
        this.longitude = longitude;
        this.description = description;
        this.parkName = parkName;
    }

    public Integer getParkId() {
        return parkId;
    }

    public void setParkId(Integer parkId) {
        this.parkId = parkId;
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

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getParkName() {
        return parkName;
    }

    public void setParkName(String parkName) {
        this.parkName = parkName;
    }
}