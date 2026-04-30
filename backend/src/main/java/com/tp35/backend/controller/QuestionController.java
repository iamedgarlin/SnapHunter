package com.tp35.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.tp35.backend.dto.QuestionDTO;
import com.tp35.backend.service.QuestionService;

@RestController
@RequestMapping("/api/epic-parks/stories/question")
public class QuestionController {

    private final QuestionService questionService;

    public QuestionController(QuestionService questionService) {
        this.questionService = questionService;
    }

    @GetMapping
    public ResponseEntity<QuestionDTO> getQuestionByStoryIdAndOrderIndex(
            @RequestParam Integer storyId,
            @RequestParam Integer orderIndex
    ) {
        QuestionDTO question = questionService.getQuestionByStoryIdAndOrderIndex(storyId, orderIndex);
        if (question != null) {
            return ResponseEntity.ok(question);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}