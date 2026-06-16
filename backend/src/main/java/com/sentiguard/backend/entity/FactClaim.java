package com.sentiguard.backend.entity;

import java.time.LocalDateTime;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import lombok.Data;

@Data
@TableName("fact_claim")
public class FactClaim {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long taskId;

    private String claimText;

    private String claimType;

    private Integer claimOrder;

    private LocalDateTime createTime;
}
