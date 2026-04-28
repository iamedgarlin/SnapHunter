package com.tp35.backend.repository;

import java.util.List;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.tp35.backend.dto.ParkDTO;

@Repository

public class ParkRepository {

    private final JdbcTemplate jdbcTemplate;

    public ParkRepository(JdbcTemplate jdbcTemplate) {

        this.jdbcTemplate = jdbcTemplate;

    }

    public List<ParkDTO> findAllParks() {
        String sql = """
        SELECT
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

}