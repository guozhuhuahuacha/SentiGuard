package com.sentiguard.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("sentiment_analysis")
public class SentimentAnalysis {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long hotEventId;
    private Integer positiveCount;
    private Integer neutralCount;
    private Integer negativeCount;
    private BigDecimal positiveRatio;
    private BigDecimal neutralRatio;
    private BigDecimal negativeRatio;
    private String sentimentLabel;
    private LocalDateTime analysisTime;
    private LocalDateTime createTime;
}
