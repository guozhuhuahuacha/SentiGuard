package com.sentiguard.backend.agent;

import lombok.Data;

@Data
public class SentiGuardDetailApiResponse {

    private Integer code;

    private String message;

    private SentiGuardFactCheckDetailData data;
}
