package com.tp35.backend.service;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.Instant;
import java.time.temporal.ChronoUnit;

import org.springframework.stereotype.Service;

@Service
public class GeminiTokenService {

    public String createEphemeralToken() throws Exception {

        String apiKey = System.getenv("GEMINI_API_KEY");

        URL url = new URL(
            "https://generativelanguage.googleapis.com/v1alpha/auth_tokens?key="
            + apiKey
        );

        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);

        String expireTime = Instant.now().plus(60, ChronoUnit.MINUTES).toString();

        String body = """
        {
          "expireTime": "%s"
        }
        """.formatted(expireTime);

        try(OutputStream os = conn.getOutputStream()) {
            os.write(body.getBytes());
        }

        int status = conn.getResponseCode();

        BufferedReader br = new BufferedReader(
            new InputStreamReader(
                status >= 200 && status < 300
                    ? conn.getInputStream()
                    : conn.getErrorStream() != null ? conn.getErrorStream() : conn.getInputStream()
            )
        );

        StringBuilder response = new StringBuilder();
        String line;

        while((line = br.readLine()) != null) {
            response.append(line);
        }

        if (status < 200 || status >= 300) {
            throw new RuntimeException("Gemini token request failed with status " + status + ": " + response);
        }

        String raw = response.toString();
        int start = raw.indexOf("auth_tokens/");
        if (start != -1) {
            int end = raw.indexOf('"', start);
            String token = raw.substring(start, end);
            return """
            {
              "token": "%s",
              "expireTime": "%s",
              "model": "gemini-3.1-flash-live-preview",
              "wsUrl": "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent"
            }
            """.formatted(token, expireTime);
        }

        return raw;
    }
}