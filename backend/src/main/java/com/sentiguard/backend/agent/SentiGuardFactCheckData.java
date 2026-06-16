package com.sentiguard.backend.agent;

import lombok.Data;

@Data
public class SentiGuardFactCheckData {

    private Boolean isTrue;

    private String conclusion;

    private String explanation;
}
