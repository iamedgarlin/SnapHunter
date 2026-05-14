package com.tp35.backend.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.tp35.backend.dto.RouteDTO;
import com.tp35.backend.dto.RouteTaskDTO;
import com.tp35.backend.repository.RouteRepository;

@Service
public class RouteService {

    private final RouteRepository routeRepository;

    public RouteService(RouteRepository routeRepository) {
        this.routeRepository = routeRepository;
    }

    public List<RouteDTO> getRoutesByParkId(Integer parkId) {
        return routeRepository.findRoutesByParkId(parkId);
    }

    public List<RouteTaskDTO> getTasksByRouteId(Integer routeId) {
        return routeRepository.findTasksByRouteId(routeId);
    }
}