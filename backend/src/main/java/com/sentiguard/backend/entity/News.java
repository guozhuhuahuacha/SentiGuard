package com.sentiguard.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("news")
public class News {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long collectTaskId;
    private String title;
    private String summary;
    private String content;
    private String sourceName;
    private String sourceUrl;
    private LocalDateTime publishTime;
    private String language;
    private String country;
    private String author;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;

    @TableLogic
    private Integer isDeleted;
}
