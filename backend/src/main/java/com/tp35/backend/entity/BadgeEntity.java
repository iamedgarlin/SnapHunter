package com.tp35.backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Data
@Entity
@Table(name = "badge")
public class BadgeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer badgeId;

    @Column(nullable = false)
    private String badgeName;

    private String description;

    @Column(nullable = false)
    private String triggerType;

    private Integer targetTaskId;

    private Integer targetSeriesId;

    private Integer requiredCount;
}