package com.sentiguard.backend.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import lombok.Data;

@Data
@TableName("evidence")
public class Evidence {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long taskId;

    private Long claimId;

    private Long newsId;

    private String evidenceTitle;

    private String evidenceContent;

    @TableField("evidence_url")
    private String evidenceUrl;

    @TableField("source_name")
    private String sourceName;

    private String evidenceType;

    private String relationType;

    @TableField("credibility_score")
    private BigDecimal credibilityScore;

    @TableField("publish_time")
    private LocalDateTime publishTime;

    private LocalDateTime createTime;
}

