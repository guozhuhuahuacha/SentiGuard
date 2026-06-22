package com.sentiguard.backend.agent;

import lombok.Data;

@Data
public class SentiGuardClaimData {

    private Integer claimOrder;

    private String claimText;

    private String claimType;
}
