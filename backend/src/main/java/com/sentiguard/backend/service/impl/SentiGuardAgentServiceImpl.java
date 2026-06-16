package com.sentiguard.backend.service.impl;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.UUID;

import org.springframework.context.annotation.Profile;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import com.sentiguard.backend.agent.AgentCheckRequest;
import com.sentiguard.backend.agent.AgentCheckResponse;
import com.sentiguard.backend.agent.AgentClaim;
import com.sentiguard.backend.agent.AgentEvidence;
import com.sentiguard.backend.agent.AgentReport;
import com.sentiguard.backend.agent.AgentResult;
import com.sentiguard.backend.agent.SentiGuardApiRequest;
import com.sentiguard.backend.agent.SentiGuardApiResponse;
import com.sentiguard.backend.agent.SentiGuardFactCheckData;
import com.sentiguard.backend.config.SentiGuardAgentProperties;
import com.sentiguard.backend.service.AgentService;

@Service
@Profile("!mock-agent")
public class SentiGuardAgentServiceImpl implements AgentService {

    private final RestTemplate agentRestTemplate;
    private final SentiGuardAgentProperties properties;

    public SentiGuardAgentServiceImpl(RestTemplate agentRestTemplate,
                                      SentiGuardAgentProperties properties) {
        this.agentRestTemplate = agentRestTemplate;
        this.properties = properties;
    }

    @Override
    public AgentCheckResponse check(AgentCheckRequest request) {
        SentiGuardApiResponse apiResponse = callFastApi(request.getInputText());
        SentiGuardFactCheckData data = apiResponse.getData();
        if (data == null) {
            throw new IllegalStateException("SentiGuard 返回数据为空");
        }

        boolean isTrue = Boolean.TRUE.equals(data.getIsTrue());
        String resultLabel = isTrue ? "true" : "false";
        String relationType = isTrue ? "support" : "attack";

        AgentCheckResponse response = new AgentCheckResponse();
        response.setClaims(Collections.singletonList(
                new AgentClaim(request.getInputText(), "fact_check_claim", 1)
        ));
        response.setEvidences(Collections.singletonList(
                new AgentEvidence(
                        1,
                        "SentiGuard 智能体核查解释",
                        data.getExplanation(),
                        null,
                        "SentiGuard FastAPI",
                        "model_generated",
                        relationType,
                        null
                )
        ));
        response.setResult(new AgentResult(
                resultLabel,
                null,
                data.getConclusion(),
                data.getExplanation()
        ));
        response.setReport(new AgentReport(
                request.getInputText() + "事实核查报告",
                buildReport(request.getInputText(), isTrue, data),
                "markdown"
        ));
        return response;
    }

    private SentiGuardApiResponse callFastApi(String claim) {
        String url = properties.getBaseUrl() + properties.getFactCheckPath();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-Internal-Token", properties.getInternalToken());
        headers.set("X-Trace-Id", UUID.randomUUID().toString());

        HttpEntity<SentiGuardApiRequest> entity = new HttpEntity<>(new SentiGuardApiRequest(claim), headers);
        try {
            ResponseEntity<SentiGuardApiResponse> response = agentRestTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    SentiGuardApiResponse.class
            );
            SentiGuardApiResponse body = response.getBody();
            if (body == null) {
                throw new IllegalStateException("SentiGuard 响应为空");
            }
            if (body.getCode() == null || body.getCode() != 0) {
                throw new IllegalStateException("SentiGuard 调用失败：" + body.getMessage());
            }
            return body;
        } catch (RestClientException ex) {
            throw new IllegalStateException("无法调用 SentiGuard FastAPI：" + ex.getMessage(), ex);
        }
    }

    private String buildReport(String claim, boolean isTrue, SentiGuardFactCheckData data) {
        return "## 核查对象\n" + claim + "\n\n"
                + "## 核查结论\n" + data.getConclusion() + "\n\n"
                + "## 真实性判断\n" + (isTrue ? "真实" : "虚假") + "\n\n"
                + "## 智能体解释\n" + data.getExplanation();
    }
}
