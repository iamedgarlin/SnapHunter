package com.tp35.backend.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Data
@Entity
@Table(name = "task")
public class TaskEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer taskId;

    @Column(nullable = false)
    private Integer seriesId;

    @Column(nullable = false)
    private String taskName;

    private String taskDescription;

    private String evaluationCriteria;

    @Column(nullable = false)
    private String environmentType;

    @Column(nullable = false)
    private String taskType;

    private String locationLabel;

    private Double latitude;

    private Double longitude;

    private Integer geofenceRadiusMeter;

    @Column(nullable = false)
    private Integer baseDifficulty = 1;

    @Column(nullable = false)
    private Integer rewardPoint = 10;

    @Column(nullable = false)
    private Boolean isActive = true;

    private LocalDateTime createTime;
}