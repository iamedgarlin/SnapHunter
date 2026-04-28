package com.tp35.backend.service;

import org.springframework.stereotype.Service;

import com.tp35.backend.dto.QuestionDTO;
import com.tp35.backend.repository.QuestionRepository;

@Service
public class QuestionService {

    private final QuestionRepository questionRepository;

    public QuestionService(QuestionRepository questionRepository) {
        this.questionRepository = questionRepository;
    }

    public QuestionDTO getQuestionByStoryIdAndOrderIndex(Integer storyId, Integer orderIndex) {
        return questionRepository.findQuestionByStoryIdAndOrderIndex(storyId, orderIndex);
    }
}