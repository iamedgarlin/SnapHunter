package com.tp35.backend.repository;

import com.tp35.backend.dto.TaskEvaluationInfoDTO;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class TaskEvaluationRepository {

    private final JdbcTemplate jdbcTemplate;

    public TaskEvaluationRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public TaskEvaluationInfoDTO findTaskEvaluationInfoByTaskId(Integer taskId) {
        String sql = """
                SELECT
                    task_description,
                    evaluation_criteria
                FROM task
                WHERE task_id = ?
                """;

        return jdbcTemplate.queryForObject(
                sql,
                (rs, rowNum) -> new TaskEvaluationInfoDTO(
                        rs.getString("task_description"),
                        rs.getString("evaluation_criteria")
                ),
                taskId
        );
    }
}