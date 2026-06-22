package com.sentiguard.backend.agent;

import java.math.BigDecimal;

import lombok.Data;

@Data
public class SentiGuardResultData {

    private String resultLabel;

    private BigDecimal confidenceScore;

    private String conclusion;

    private String analysisDetail;

    private Integer supportCount;

    private Integer attackCount;
}
