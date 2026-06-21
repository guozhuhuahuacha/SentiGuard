package com.sentiguard.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("hot_event")
public class HotEvent {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String eventTitle;
    private String eventSummary;
    private String topicId;
    private BigDecimal heatScore;
    private String riskLevel;
    private String sentimentLabel;
    private Integer newsCount;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;

    @TableLogic
    private Integer isDeleted;
}
