package com.sentiguard.backend.service.impl;

import java.util.Map;
import java.util.UUID;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import com.sentiguard.backend.config.SentiGuardAgentProperties;
import com.sentiguard.backend.dto.OpinionAnalyzeDTO;
import com.sentiguard.backend.service.OpinionService;

@Service
public class OpinionServiceImpl implements OpinionService {

    private final RestTemplate agentRestTemplate;
    private final SentiGuardAgentProperties properties;

    public OpinionServiceImpl(RestTemplate agentRestTemplate, SentiGuardAgentProperties properties) {
        this.agentRestTemplate = agentRestTemplate;
        this.properties = properties;
    }

    @Override
    @SuppressWarnings("unchecked")
    public Map<String, Object> analyze(OpinionAnalyzeDTO dto) {
        String url = properties.getBaseUrl() + properties.getOpinionAnalyzePath();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-Internal-Token", properties.getInternalToken());
        headers.set("X-Trace-Id", UUID.randomUUID().toString());

        HttpEntity<OpinionAnalyzeDTO> entity = new HttpEntity<>(dto, headers);
        try {
            ResponseEntity<Map> response = agentRestTemplate.exchange(url, HttpMethod.POST, entity, Map.class);
            Map<String, Object> body = response.getBody();
            if (body == null) {
                throw new IllegalStateException("SentiGuard 舆情观点分析响应为空");
            }
            Object code = body.get("code");
            if (code instanceof Number && ((Number) code).intValue() != 0) {
                throw new IllegalStateException("SentiGuard 舆情观点分析失败：" + body.get("message"));
            }
            Object data = body.get("data");
            if (!(data instanceof Map)) {
                throw new IllegalStateException("SentiGuard 舆情观点分析返回数据为空");
            }
            return (Map<String, Object>) data;
        } catch (RestClientException ex) {
            throw new IllegalStateException("无法调用 SentiGuard 舆情观点分析接口：" + ex.getMessage(), ex);
        }
    }
}