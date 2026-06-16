package com.sentiguard.backend.vo;

import java.math.BigDecimal;

import lombok.Data;

@Data
public class FactCheckResultVO {

    private Long id;

    private String label;

    private String labelText;

    private BigDecimal confidenceScore;

    private String conclusion;

    private String analysisDetail;

    private Integer supportCount;

    private Integer attackCount;

    private String reviewStatus;
}
