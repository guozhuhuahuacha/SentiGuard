package com.sentiguard.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("topic_keyword")
public class TopicKeyword {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long hotEventId;
    private String keyword;
    private BigDecimal weight;
    private Integer rankNo;
    private LocalDateTime createTime;
}
