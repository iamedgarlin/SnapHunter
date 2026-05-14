package com.tp35.backend.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.tp35.backend.dto.RouteDTO;
import com.tp35.backend.service.RouteService;

@RestController
@RequestMapping("/api/common-parks/routes")
public class RouteController {

    private final RouteService routeService;

    public RouteController(RouteService routeService) {
        this.routeService = routeService;
    }

    @GetMapping
    public ResponseEntity<List<RouteDTO>> getRoutesByParkId(
            @RequestParam Integer parkId
    ) {
        return ResponseEntity.ok(routeService.getRoutesByParkId(parkId));
    }
}