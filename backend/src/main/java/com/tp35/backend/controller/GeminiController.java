package com.tp35.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.tp35.backend.service.GeminiTokenService;


@RestController
@RequestMapping("/api/gemini")
public class GeminiController {

    private final GeminiTokenService geminiTokenService;

    public GeminiController(GeminiTokenService geminiTokenService) {
        this.geminiTokenService = geminiTokenService;
    }

    @GetMapping("/token")
    public ResponseEntity<String> getToken() throws Exception {
        return ResponseEntity.ok(geminiTokenService.createEphemeralToken());
    }
}