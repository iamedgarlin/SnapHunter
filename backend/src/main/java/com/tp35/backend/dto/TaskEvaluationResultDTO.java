package com.tp35.backend.dto;

public class TaskEvaluationResultDTO {
    private Boolean matched;
    private String reason;

    public TaskEvaluationResultDTO() {
    }

    public TaskEvaluationResultDTO(Boolean matched, String reason) {
        this.matched = matched;
        this.reason = reason;
    }

    public Boolean getMatched() {
        return matched;
    }

    public void setMatched(Boolean matched) {
        this.matched = matched;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }
}