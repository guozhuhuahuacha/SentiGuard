package com.sentiguard.backend.agent;

import lombok.Data;

@Data
public class SentiGuardApiResponse {

    private Integer code;

    private String message;

    private SentiGuardFactCheckData data;
}
