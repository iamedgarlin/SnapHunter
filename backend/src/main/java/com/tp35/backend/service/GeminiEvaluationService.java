package com.tp35.backend.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.genai.Client;
import com.google.genai.types.Content;
import com.google.genai.types.GenerateContentResponse;
import com.google.genai.types.Part;
import com.tp35.backend.dto.TaskEvaluationResultDTO;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
public class GeminiEvaluationService {

    private final Client client;
    private final ObjectMapper objectMapper;

    public GeminiEvaluationService(
            @Value("${gemini.api.key}") String apiKey,
            ObjectMapper objectMapper
    ) {
        this.client = Client.builder().apiKey(apiKey).build();
        this.objectMapper = objectMapper;
    }

    public TaskEvaluationResultDTO evaluateTask(
            String taskDescription,
            String evaluationCriteria,
            MultipartFile file
    ) throws Exception {

        byte[] imageBytes = file.getBytes();
        String mimeType = file.getContentType();
        if (mimeType == null || mimeType.isBlank()) {
            mimeType = "image/jpeg";
        }

        String prompt = """
                You are a task checker.

                Return ONLY valid JSON.
                Do NOT include any explanation, text, or markdown.
                Do NOT wrap the JSON in ```json or ```.
                The output must be pure JSON only.

                Task Description: %s
                Task Evaluation Criteria: %s

                Check whether the submitted image clearly satisfies the task.

                Rules:
                1. Only return matched=true if the image clearly satisfies the task.
                2. If the image is blurry, ambiguous, or unrelated, return matched=false.
                3. Do not guess.
                4. Keep reason under 20 words.

                Format:
                {
                  "matched": true or false,
                  "reason": "short explanation"
                }
                """.formatted(taskDescription, evaluationCriteria);

        GenerateContentResponse response = client.models.generateContent(
                "gemini-2.5-flash",
                Content.fromParts(
                        Part.fromText(prompt),
                        Part.fromBytes(imageBytes, mimeType)
                ),
                null
        );

        String cleanText = response.text().trim();

        if (cleanText.startsWith("```")) {
            String[] lines = cleanText.split("\\R");
            int start = 0;
            int end = lines.length;

            if (lines.length > 0 && lines[0].startsWith("```")) {
                start = 1;
            }
            if (end > start && lines[end - 1].trim().equals("```")) {
                end--;
            }

            StringBuilder sb = new StringBuilder();
            for (int i = start; i < end; i++) {
                sb.append(lines[i]);
                if (i < end - 1) {
                    sb.append("\n");
                }
            }
            cleanText = sb.toString().trim();
        }

        return objectMapper.readValue(cleanText, TaskEvaluationResultDTO.class);
    }
}