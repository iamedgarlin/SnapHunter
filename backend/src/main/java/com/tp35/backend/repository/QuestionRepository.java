package com.tp35.backend.repository;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.tp35.backend.dto.QuestionDTO;

@Repository
public class QuestionRepository {

    private final JdbcTemplate jdbcTemplate;

    public QuestionRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public QuestionDTO findQuestionByStoryIdAndOrderIndex(Integer storyId, Integer orderIndex) {
        String sql = """
            SELECT
                question_id,
                description,
                context,
                answer,
                reward
            FROM question
            WHERE story_id = ?
              AND order_index = ?
            """;

        return jdbcTemplate.queryForObject(sql, (rs, rowNum) -> {
            QuestionDTO question = new QuestionDTO();
            question.setQuestionId(rs.getInt("question_id"));
            question.setDescription(rs.getString("description"));
            question.setContext(rs.getString("context"));
            question.setAnswer(rs.getString("answer"));
            question.setReward(rs.getInt("reward"));
            return question;
        }, storyId, orderIndex);
    }
}