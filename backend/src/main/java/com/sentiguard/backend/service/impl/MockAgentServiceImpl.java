package com.sentiguard.backend.service.impl;

import java.math.BigDecimal;
import java.util.Arrays;

import org.springframework.stereotype.Service;
import org.springframework.context.annotation.Profile;

import com.sentiguard.backend.agent.AgentCheckRequest;
import com.sentiguard.backend.agent.AgentCheckResponse;
import com.sentiguard.backend.agent.AgentClaim;
import com.sentiguard.backend.agent.AgentEvidence;
import com.sentiguard.backend.agent.AgentReport;
import com.sentiguard.backend.agent.AgentResult;
import com.sentiguard.backend.service.AgentService;

@Service
@Profile("mock-agent")
public class MockAgentServiceImpl implements AgentService {

    @Override
    public AgentCheckResponse check(AgentCheckRequest request) {
        String inputText = request.getInputText();

        AgentCheckResponse response = new AgentCheckResponse();
        response.setClaims(Arrays.asList(
                new AgentClaim(inputText + "是否存在明确事实依据", "event_verification", 1),
                new AgentClaim(inputText + "相关网络传播内容是否存在夸大或误导", "misinformation_check", 2),
                new AgentClaim(inputText + "是否有权威来源能够支撑最终判断", "source_verification", 3)
        ));

        response.setEvidences(Arrays.asList(
                new AgentEvidence(
                        1,
                        "权威媒体对事件核心事实的报道",
                        "多方报道显示，该事件存在可核验的事实线索，但仍需要结合权威来源进行交叉验证。",
                        "https://example.com/evidence/official-report",
                        "示例权威新闻源",
                        "web",
                        "support",
                        new BigDecimal("86.00")
                ),
                new AgentEvidence(
                        2,
                        "社交平台传播内容与原始信息存在差异",
                        "部分转述内容缺少直接证据，存在将个别说法扩大为确定事实的风险。",
                        "https://example.com/evidence/social-spread",
                        "示例网络来源",
                        "web",
                        "attack",
                        new BigDecimal("72.00")
                ),
                new AgentEvidence(
                        3,
                        "公开资料暂未形成完全一致结论",
                        "现有资料能够支撑初步判断，但仍建议等待进一步官方通报或更多交叉证据。",
                        "https://example.com/evidence/context",
                        "示例资料库",
                        "web",
                        "neutral",
                        new BigDecimal("65.00")
                )
        ));

        response.setResult(new AgentResult(
                "partly_true",
                new BigDecimal("82.50"),
                "经核查：该内容存在一定事实依据，但部分传播表述需要谨慎看待",
                "系统根据声明拆解、证据检索和支持/反驳关系分析后认为，输入内容并非完全无依据，但网络传播中存在夸大、简化或证据不足的部分。建议将结论表述为“部分真实”，并继续关注权威来源更新。"
        ));

        response.setReport(new AgentReport(
                inputText + "事实核查报告",
                "## 核查对象\n" + inputText + "\n\n"
                        + "## 核查结论\n经核查：该内容存在一定事实依据，但部分传播表述需要谨慎看待。\n\n"
                        + "## 证据分析\n- 支持证据：权威媒体报道提供了事件基础事实。\n"
                        + "- 反驳证据：部分社交平台传播内容存在夸大风险。\n"
                        + "- 中立证据：公开资料尚未形成完全一致结论。\n\n"
                        + "## 综合判断\n当前适合标记为“部分真实”，后续可根据官方通报更新结论。",
                "markdown"
        ));

        return response;
    }
}
