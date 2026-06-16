package com.sentiguard.backend.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import lombok.Data;

@Data
@TableName("fact_check_result")
public class FactCheckResult {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long taskId;

    private String resultLabel;

    private BigDecimal confidenceScore;

    private String conclusion;

    private String analysisDetail;

    private Integer supportCount;

    private Integer attackCount;

    private String reviewStatus;

    private Long reviewerId;

    private LocalDateTime reviewTime;

    private String reviewComment;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
