package com.tp35.backend.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.tp35.backend.dto.ParkDTO;
import com.tp35.backend.repository.ParkRepository;

@Service
public class ParkService {

    private final ParkRepository parkRepository;

    public ParkService(ParkRepository parkRepository) {
        this.parkRepository = parkRepository;
    }

    public List<ParkDTO> getAllParks() {
        return parkRepository.findAllParks();
    }
}