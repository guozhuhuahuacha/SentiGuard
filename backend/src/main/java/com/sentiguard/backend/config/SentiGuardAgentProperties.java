package com.sentiguard.backend.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import lombok.Data;

@Data
@ConfigurationProperties(prefix = "sentiguard.agent")
public class SentiGuardAgentProperties {

    private String baseUrl = "http://127.0.0.1:8000";

    private String factCheckPath = "/internal/v1/fact-check";

    private String internalToken = "dev-internal-token";

    private int connectTimeoutMs = 10000;

    private int readTimeoutMs = 300000;
}
