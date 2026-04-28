package com.tp35.backend.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.tp35.backend.dto.ParkDTO;
import com.tp35.backend.service.ParkService;

@RestController
@RequestMapping("/api/epic-parks")
public class ParkController {

    private final ParkService parkService;

    public ParkController(ParkService parkService) {
        this.parkService = parkService;
    }

    @GetMapping
    public ResponseEntity<List<ParkDTO>> getAllParks() {
        return ResponseEntity.ok(parkService.getAllParks());
    }
}