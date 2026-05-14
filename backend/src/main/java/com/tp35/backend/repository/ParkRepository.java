package com.tp35.backend.repository;

import java.util.List;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.tp35.backend.dto.ParkDTO;
import com.tp35.backend.dto.ParkRecommendationDTO;

@Repository

public class ParkRepository {

    private final JdbcTemplate jdbcTemplate;

    public ParkRepository(JdbcTemplate jdbcTemplate) {

        this.jdbcTemplate = jdbcTemplate;

    }

    public List<ParkDTO> findParksWithStories() {
        String sql = """
        SELECT DISTINCT
            p.park_id,
            p.latitude,
            p.longitude,
            p.description,
            p.park_name
        FROM park p
        INNER JOIN story s on p.park_id = s.park_id
            """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            ParkDTO park = new ParkDTO();
            park.setParkId(rs.getInt("park_id"));
            park.setLatitude(rs.getDouble("latitude"));
            park.setLongitude(rs.getDouble("longitude"));
            park.setDescription(rs.getString("description"));
            park.setParkName(rs.getString("park_name"));
            return park;
        });

    }

    public List<ParkRecommendationDTO> findParksWithoutStoriesForRecommendation(
        Double userLatitude, 
        Double userLongitude, 
        Integer weatherLevel, 
        boolean random
        ) {
        String orderBy = random ? " ORDER BY RAND() " : " ORDER BY distance ASC ";

        String sql = """
            WITH t AS (
                SELECT
                    p.park_id,
                    p.park_name,
                    p.latitude,
                    p.longitude,
                    p.transport_accessibility_score,
                    p.task_richness_score,
                    p.park_ha_level,
                    p.recommend_description,
                    ST_Distance_Sphere(
                        p.st_point,
                        ST_SRID(POINT(?, ?), 4326)
                    ) AS distance,
                    (SELECT COUNT(*) FROM route r
                    WHERE r.park_id = p.park_id
                    ) AS route_count
                FROM park p
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM story s
                    WHERE s.park_id = p.park_id
                )
                AND p.min_weather_accept_level <= ?
            )
            SELECT
                park_id,
                park_name,
                latitude,
                longitude,
                transport_accessibility_score,
                task_richness_score,
                park_ha_level,
                recommend_description,
                distance,
                route_count
            FROM t
            """ + orderBy + """
            LIMIT 5
            """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            ParkRecommendationDTO park = new ParkRecommendationDTO();
            park.setParkId(rs.getInt("park_id"));
            park.setParkName(rs.getString("park_name"));
            park.setLatitude(rs.getDouble("latitude"));
            park.setLongitude(rs.getDouble("longitude"));
            park.setRecommendDescription(rs.getString("recommend_description"));

            park.setTransportAccessibilityScore(rs.getDouble("transport_accessibility_score"));
            park.setTaskRichnessScore(rs.getDouble("task_richness_score"));
            park.setParkHaLevel(rs.getDouble("park_ha_level"));
            park.setDistance(rs.getDouble("distance"));
            park.setRouteCount(rs.getInt("route_count"));
            return park;
        }, userLongitude, userLatitude, weatherLevel);
    }
}