package com.sentiguard.backend.vo;

import lombok.Data;

import java.math.BigDecimal;

@Data
public class DashboardStatsVO {
    private Integer totalHotspots;
    private Integer totalNews;
    private Integer highRiskCount;
    private BigDecimal negRatio;
    private BigDecimal posRatio;
    private BigDecimal neuRatio;
    private Integer lowRiskCount;
    private Integer mediumRiskCount;
    private String lastCollectTime;
}
