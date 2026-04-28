package com.tp35.backend.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.tp35.backend.dto.StoryDTO;
import com.tp35.backend.repository.StoryRepository;

@Service
public class StoryService {

    private final StoryRepository storyRepository;

    public StoryService(StoryRepository storyRepository) {
        this.storyRepository = storyRepository;
    }

    public List<StoryDTO> getStoriesByParkId(Integer parkId) {
        return storyRepository.findStoriesByParkId(parkId);
    }
}