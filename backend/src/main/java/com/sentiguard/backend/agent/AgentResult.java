package com.sentiguard.backend.agent;

import java.math.BigDecimal;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AgentResult {

    private String label;

    private BigDecimal confidenceScore;

    private String conclusion;

    private String analysisDetail;
}
