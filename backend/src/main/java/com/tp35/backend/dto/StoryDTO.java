package com.tp35.backend.dto;

public class StoryDTO {

    private Integer storyId;
    private String content;
    private String name;
    private Integer expectedDurationSec;

    public StoryDTO() {
    }

    public StoryDTO(Integer storyId, String content, String name, Integer expectedDurationSec) {
        this.storyId = storyId;
        this.content = content;
        this.name = name;
        this.expectedDurationSec = expectedDurationSec;
    }

    public Integer getStoryId() {
        return storyId;
    }

    public void setStoryId(Integer storyId) {
        this.storyId = storyId;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getExpectedDurationSec() {
        return expectedDurationSec;
    }

    public void setExpectedDurationSec(Integer expectedDurationSec) {
        this.expectedDurationSec = expectedDurationSec;
    }
}