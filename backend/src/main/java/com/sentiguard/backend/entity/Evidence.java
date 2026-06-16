package com.sentiguard.backend.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.baomidou.mybatisplus.annotation.IdType;
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

    private String evidenceUrl;

    private String sourceName;

    private String evidenceType;

    private String relationType;

    private BigDecimal credibilityScore;

    private LocalDateTime publishTime;

    private LocalDateTime createTime;
}
