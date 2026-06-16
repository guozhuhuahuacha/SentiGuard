package com.sentiguard.backend.agent;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AgentClaim {

    private String claimText;

    private String claimType;

    private Integer claimOrder;
}
