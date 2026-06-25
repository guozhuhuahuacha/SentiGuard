package com.sentiguard.backend.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;

import lombok.Data;

@Data
public class OpinionAnalyzeDTO {

    @NotBlank(message = "请输入需要分析的舆情事件")
    @Size(max = 500, message = "舆情事件长度不能超过500个字符")
    private String event;

    @Size(max = 2000, message = "事件描述长度不能超过2000个字符")
    private String description;
}