package com.sentiguard.backend.agent;

import java.math.BigDecimal;

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
}
