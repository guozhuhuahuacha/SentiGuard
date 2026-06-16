package com.sentiguard.backend.entity;

import java.time.LocalDateTime;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;

import lombok.Data;

@Data
@TableName("fact_check_task")
public class FactCheckTask {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private Long hotEventId;

    private String inputText;

    private String taskStatus;

    private String taskType;

    private LocalDateTime submitTime;

    private LocalDateTime finishTime;

    private String errorMessage;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;

    @TableLogic
    private Integer isDeleted;
}
