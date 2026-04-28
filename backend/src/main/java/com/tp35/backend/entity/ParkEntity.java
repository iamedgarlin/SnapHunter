package com.tp35.backend.entity;

import org.locationtech.jts.geom.Point;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Data
@Entity
@Table(name = "park")
public class ParkEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer parkId;

    private Double latitude;

    private Double longitude;

    @Column(columnDefinition = "geometry(Point,4326)")
    private Point stPoint;

    @Column(columnDefinition = "TEXT")
    private String description;

    private String parkName;
}