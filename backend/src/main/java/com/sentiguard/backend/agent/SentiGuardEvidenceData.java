package com.sentiguard.backend.agent;

import java.math.BigDecimal;

import lombok.Data;

@Data
public class SentiGuardEvidenceData {

    private Integer claimOrder;

    private String evidenceTitle;

    private String evidenceContent;

    private String evidenceUrl;

    private String sourceName;

    private String evidenceType;

    private String relationType;

    private BigDecimal credibilityScore;

    private String publishTime;
}
