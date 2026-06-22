package com.sentiguard.backend.agent;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AgentEvidence {

    private Integer claimOrder;

    private String title;

    private String content;

    private String url;

    private String sourceName;

    private String evidenceType;

    private String relationType;

    private BigDecimal credibilityScore;

    private LocalDateTime publishTime;

    public AgentEvidence(Integer claimOrder,
                         String title,
                         String content,
                         String url,
                         String sourceName,
                         String evidenceType,
                         String relationType,
                         BigDecimal credibilityScore) {
        this.claimOrder = claimOrder;
        this.title = title;
        this.content = content;
        this.url = url;
        this.sourceName = sourceName;
        this.evidenceType = evidenceType;
        this.relationType = relationType;
        this.credibilityScore = credibilityScore;
    }
}