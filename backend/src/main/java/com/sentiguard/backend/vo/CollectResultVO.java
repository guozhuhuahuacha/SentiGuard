package com.sentiguard.backend.vo;

import lombok.Data;

@Data
public class CollectResultVO {
    private String message;
    private Integer newsSaved;
    private Integer hotEvents;
    private Integer taskId;
}
