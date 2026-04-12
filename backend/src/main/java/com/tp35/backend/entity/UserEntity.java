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
@Table(name = "user")
public class UserEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer userId;

    @Column(nullable = false, unique = true)
    private String firebaseUid;

    @Column(nullable = false)
    private String username;

    @Column(nullable = false)
    private Integer totalPoint = 0;

    @Column(nullable = false)
    private LocalDateTime createTime;

    // @PrePersist
    // public void prePersist() {
    //     if (this.createTime == null) {
    //     this.createTime = LocalDateTime.now(ZoneOffset.UTC);
    //     }
    // }
}