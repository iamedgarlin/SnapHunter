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
@Table(name = "user_badge")
public class UserBadgeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer userBadgeId;

    @Column(nullable = false)
    private Integer userId;

    @Column(nullable = false)
    private Integer badgeId;

    @Column(nullable = false)
    private LocalDateTime unlockedTime;
}