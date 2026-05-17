package com.tp35.backend.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.tp35.backend.dto.ParkDTO;
import com.tp35.backend.dto.ParkRecommendationDTO;
import com.tp35.backend.service.ParkService;

@RestController
@RequestMapping("/api")
public class ParkController {

    private final ParkService parkService;

    public ParkController(ParkService parkService) {
        this.parkService = parkService;
    }

    @GetMapping("/epic-parks")
    public ResponseEntity<List<ParkDTO>> getParksWithStories() {
        return ResponseEntity.ok(parkService.getParksWithStories());
    }

    @GetMapping("/common-parks")
    public ResponseEntity<List<ParkRecommendationDTO>> getParkRecommendations(
        @RequestParam Double latitude,
        @RequestParam Double longitude,
        @RequestParam(defaultValue = "false") boolean random
    ) {
        return ResponseEntity.ok(parkService.getParksWithoutStoriesForRecommendation(latitude, longitude, random));
    }

    @GetMapping("/common-route-parks")
    public ResponseEntity<List<ParkRecommendationDTO>> getParkWithRoutes(
        @RequestParam Double latitude,
        @RequestParam Double longitude
    ) {
        return ResponseEntity.ok(parkService.getParksWithRoutesForRecommendation(latitude, longitude));
    }

    @GetMapping("/all-parks")
    public ResponseEntity<List<ParkRecommendationDTO>> getAllParks(
        @RequestParam Double latitude,
        @RequestParam Double longitude
    ) {
        return ResponseEntity.ok(
            parkService.getAllParksForRecommendation(latitude, longitude)
        );
    }
}