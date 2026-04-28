package com.tp35.backend.repository;

import java.util.List;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.tp35.backend.dto.StoryDTO;

@Repository
public class StoryRepository {

    private final JdbcTemplate jdbcTemplate;

    public StoryRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public List<StoryDTO> findStoriesByParkId(Integer parkId) {
        String sql = """
            SELECT
                story_id,
                content,
                name,
                expected_duration_sec
            FROM story
            WHERE park_id = ?
            """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            StoryDTO story = new StoryDTO();
            story.setStoryId(rs.getInt("story_id"));
            story.setContent(rs.getString("content"));
            story.setName(rs.getString("name"));
            story.setExpectedDurationSec(rs.getInt("expected_duration_sec"));
            return story;
        }, parkId);
    }
}