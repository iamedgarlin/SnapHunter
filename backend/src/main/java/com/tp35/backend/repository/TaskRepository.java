package com.tp35.backend.repository;

import java.util.List;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.tp35.backend.dto.TaskDTO;

@Repository
public class TaskRepository {

    private final JdbcTemplate jdbcTemplate;

    public TaskRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public List<TaskDTO> findRandomActiveTasks() {
        String sql = """
                SELECT
                    task_id,
                    series_id,
                    task_name,
                    task_description,
                    latitude,
                    longitude,
                    base_difficulty,
                    reward_point
                FROM task
                WHERE is_active = true
                ORDER BY RAND()
                LIMIT 5
                """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            TaskDTO task = new TaskDTO();
            task.setTaskId(rs.getInt("task_id"));
            task.setSeriesId(rs.getInt("series_id"));
            task.setTaskName(rs.getString("task_name"));
            task.setTaskDescription(rs.getString("task_description"));
            task.setLatitude(rs.getDouble("latitude"));
            task.setLongitude(rs.getDouble("longitude"));
            task.setBaseDifficulty(rs.getInt("base_difficulty"));
            task.setRewardPoint(rs.getInt("reward_point"));
            return task;
        });
    }

    public List<TaskDTO> findRandomTasksBySeries(Integer seriesId) {
        String sql = """
            SELECT
                task_id,
                series_id,
                task_name,
                task_description,
                latitude,
                longitude,
                base_difficulty,
                reward_point
            FROM task
            WHERE series_id = ?
            AND is_active = true
            ORDER BY RAND()
            LIMIT 3
            """;
        
        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            TaskDTO task = new TaskDTO();
            task.setTaskId(rs.getInt("task_id"));
            task.setSeriesId(rs.getInt("series_id"));
            task.setTaskName(rs.getString("task_name"));
            task.setTaskDescription(rs.getString("task_description"));
            task.setLatitude(rs.getDouble("latitude"));
            task.setLongitude(rs.getDouble("longitude"));
            task.setBaseDifficulty(rs.getInt("base_difficulty"));
            task.setRewardPoint(rs.getInt("reward_point"));
            return task;
        }, seriesId);
    }

    public List<TaskDTO> findAllTasksBySeries(Integer seriesId) {
        String sql = """
            SELECT
                task_id,
                series_id,
                task_name,
                task_description,
                latitude,
                longitude,
                base_difficulty,
                reward_point
            FROM task
            WHERE series_id = ?
            AND is_active = true
            """;
        
        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            TaskDTO task = new TaskDTO();
            task.setTaskId(rs.getInt("task_id"));
            task.setSeriesId(rs.getInt("series_id"));
            task.setTaskName(rs.getString("task_name"));
            task.setTaskDescription(rs.getString("task_description"));
            task.setLatitude(rs.getDouble("latitude"));
            task.setLongitude(rs.getDouble("longitude"));
            task.setBaseDifficulty(rs.getInt("base_difficulty"));
            task.setRewardPoint(rs.getInt("reward_point"));
            return task;
        }, seriesId);
    }
}