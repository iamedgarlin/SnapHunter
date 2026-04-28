package com.tp35.backend.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.tp35.backend.dto.StoryDTO;
import com.tp35.backend.service.StoryService;

@RestController
@RequestMapping("/api/epic-parks/stories")
public class StoryController {

    private final StoryService storyService;

    public StoryController(StoryService storyService) {
        this.storyService = storyService;
    }

    @GetMapping
    public ResponseEntity<List<StoryDTO>> getStoriesByParkId(
            @RequestParam Integer parkId
    ) {
        return ResponseEntity.ok(storyService.getStoriesByParkId(parkId));
    }
}