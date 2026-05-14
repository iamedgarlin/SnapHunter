package com.tp35.backend.repository;

import java.util.List;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tp35.backend.dto.RouteDTO;

@Repository
public class RouteRepository {

    private final JdbcTemplate jdbcTemplate;
    private final ObjectMapper objectMapper;

    public RouteRepository(JdbcTemplate jdbcTemplate, ObjectMapper objectMapper) {
        this.jdbcTemplate = jdbcTemplate;
        this.objectMapper = objectMapper;
    }

    public List<RouteDTO> findRoutesByParkId(Integer parkId) {
        String sql = """
            SELECT
                r.route_id,
                r.difficulty_level,
                r.distance_m,
                r.estimated_time_sec,
                ST_AsGeoJSON(r.start_point) AS start_point,
                ST_AsGeoJSON(r.st_line) AS st_line,
                (
                    SELECT COUNT(*)
                    FROM route_task rt
                    WHERE rt.route_id = r.route_id
                ) AS task_count
            FROM route r
            WHERE r.park_id = ?
            """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            RouteDTO route = new RouteDTO();
            route.setRouteId(rs.getInt("route_id"));
            route.setDifficultyLevel(rs.getString("difficulty_level"));
            route.setDistanceM(rs.getDouble("distance_m"));
            route.setEstimatedTimeSec(rs.getInt("estimated_time_sec"));
            try {
                route.setStartPoint(
                        objectMapper.readTree(rs.getString("start_point"))
                );

                route.setStLine(
                        objectMapper.readTree(rs.getString("st_line"))
                );
            } catch (Exception e) {
                throw new RuntimeException("Failed to parse GeoJSON", e);
            }
            route.setTaskCount(rs.getInt("task_count"));
            return route;
        }, parkId);
    }
}