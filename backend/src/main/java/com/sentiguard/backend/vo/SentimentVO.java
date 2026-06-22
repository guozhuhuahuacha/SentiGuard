package com.sentiguard.backend.vo;

import lombok.Data;

import java.math.BigDecimal;

@Data
public class SentimentVO {
    private String label;
    private BigDecimal score;
    private BigDecimal posRatio;
    private BigDecimal negRatio;
    private BigDecimal neuRatio;
    private Integer positiveCount;
    private Integer negativeCount;
    private Integer neutralCount;
}
