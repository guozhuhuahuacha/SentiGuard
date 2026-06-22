package com.sentiguard.backend.vo;

import lombok.Data;

import java.math.BigDecimal;
import java.util.List;

@Data
public class HotspotVO {
    private Long id;
    private Integer rank;
    private String name;
    private BigDecimal heat;
    private String riskLevel;
    private String sentimentLabel;
    private Integer newsCount;
    private List<KeywordVO> keywords;
    private SentimentVO sentiment;
}
