package com.sentiguard.backend.vo;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import lombok.Data;

@Data
public class EvidenceVO {

    private Long id;

    private Long claimId;

    private String title;

    private String content;

    private String url;

    private String sourceName;

    private String evidenceType;

    private String relationType;

    private BigDecimal credibilityScore;

    private LocalDateTime publishTime;
}