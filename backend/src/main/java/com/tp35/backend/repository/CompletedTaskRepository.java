package com.tp35.backend.repository;

import java.util.List;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.tp35.backend.dto.CompletedTaskDTO;

@Repository
public class CompletedTaskRepository {

    private final JdbcTemplate jdbcTemplate;

    public CompletedTaskRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public List<CompletedTaskDTO> findCompletedTasksByUserId(Integer userId) {
        String sql = """
                SELECT
                    t.task_id,
                    t.series_id,
                    t.task_name,
                    t.task_description,
                    t.base_difficulty,
                    t.reward_point,
                    ut.complete_time
                FROM user_task ut
                JOIN task t ON ut.task_id = t.task_id
                WHERE ut.user_id = ?
                  AND ut.status = TRUE
                ORDER BY ut.complete_time DESC
                """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            CompletedTaskDTO dto = new CompletedTaskDTO();
            dto.setTaskId(rs.getInt("task_id"));
            dto.setSeriesId(rs.getInt("series_id"));
            dto.setTaskName(rs.getString("task_name"));
            dto.setTaskDescription(rs.getString("task_description"));
            dto.setBaseDifficulty(rs.getInt("base_difficulty"));
            dto.setRewardPoint(rs.getInt("reward_point"));
            dto.setCompleteTime(
                    rs.getTimestamp("complete_time") != null
                            ? rs.getTimestamp("complete_time").toLocalDateTime()
                            : null
            );
            return dto;
        }, userId);
    }
}