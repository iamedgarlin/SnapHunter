package com.tp35.backend.service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Set;

import org.springframework.stereotype.Service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.tp35.backend.dto.ParkDTO;
import com.tp35.backend.dto.ParkRecommendationDTO;
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

    public List<ParkRecommendationDTO> getParksWithoutStoriesForRecommendation(Double userLatitude, Double userLongitude) {
        Integer weatherLevel = calculateWeatherLevel(userLatitude, userLongitude);
        
        // --- For testing only ---
        // System.out.println("[Weather] Calculated weatherLevel: " + weatherLevel);

        if (weatherLevel == null) {
            return List.of();
        }
        
        List<ParkRecommendationDTO> parks = parkRepository.findParksWithoutStoriesForRecommendation(userLatitude, userLongitude, weatherLevel);
        for (ParkRecommendationDTO park : parks) {
            park.setTransportAccessibility(
                    convertTransportAccessibility(park.getTransportAccessibilityScore())
            );
            park.setTaskRichness(
                    convertTaskRichness(park.getTaskRichnessScore())
            );
            park.setParkHa(
                    convertParkHaLevel(park.getParkHaLevel())
            );
        }
        return parks;
    }

    private String convertTaskRichness(Double score) {
        if (score >= 7.50) {
            return "High richness";
        } else if (score >= 5.00) {
            return "Medium richness";
        } else {
            return "Low richness";
        }
    }

    private String convertTransportAccessibility(Double score) {
        if (score >= 8.00) {
            return "High accessibility";
        } else if (score >= 5.00) {
            return "Medium accessibility";
        } else {
            return "Low accessibility";
        }
    }

    private String convertParkHaLevel(Double score) {
        if (score >= 8.00) {
            return "Large park";
        } else if (score >= 5.00) {
            return "Medium park";
        } else {
            return "Small park";
        }
    }

    private Integer calculateWeatherLevel(Double userLatitude, Double userLongitude){
        try {
            String url = String.format(
                    "https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s&current=weather_code,uv_index&timezone=auto",
                    userLatitude,
                    userLongitude
            );

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .GET()
                    .build();
            HttpResponse<String> response = HttpClient.newHttpClient()
                    .send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                return null;
            }

            ObjectMapper mapper = new ObjectMapper();
            JsonNode current = mapper.readTree(response.body()).get("current");
            int weatherCode = current.get("weather_code").asInt();
            Double uvIndex = current.get("uv_index").asDouble();

            // --- For testing only ---
            // weatherCode = 0;
            // uvIndex = 0.0;
            // System.out.println("[Weather] weatherCode: " + weatherCode);
            // System.out.println("[Weather] uvIndex: " + uvIndex);

            if (isHardVetoWeatherCode(weatherCode)) {
                return null;
            }

            if (uvIndex >= 8) {
                return null;
            }

            Integer weatherScore = getWeatherScore(weatherCode);
            Integer uvScore = getUvScore(uvIndex);

            // --- For testing only ---
            // System.out.println("[Weather] weatherScore: " + weatherScore);
            // System.out.println("[Weather] uvScore: " + uvScore);

            return weatherScore + uvScore;

        } catch (Exception e) {
            System.out.println("[Weather] Exception while calculating weather level: " + e.getMessage());
            return null;

        }
    }

    private boolean isHardVetoWeatherCode(int weatherCode) {

        Set<Integer> hardVetoCodes = Set.of(
                55,
                56, 57,
                63, 65,
                66, 67,
                71, 73, 75, 77,
                81, 82,
                85, 86,
                95, 96, 99
        );
        return hardVetoCodes.contains(weatherCode);
}
    
    private Integer getWeatherScore(int weatherCode) {
        if (weatherCode == 0 || weatherCode == 1) {
            return 5;
        }
        if (weatherCode == 2 || weatherCode == 3) {
            return 4;
        }
        if (weatherCode == 45 || weatherCode == 48) {
            return 3;
        }
        if (weatherCode == 51 || weatherCode == 53 || weatherCode == 61 || weatherCode == 80) {
            return 2;
        }
        return 3;
    }

    private Integer getUvScore(Double uvIndex) {
        if (uvIndex >= 0 && uvIndex < 3) {
            return 5;
        }
        if (uvIndex >= 3 && uvIndex < 8) {
            return 3;
        }
        return 0;
    }
}