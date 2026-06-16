package com.sentiguard.backend.agent;

import java.util.ArrayList;
import java.util.List;

import lombok.Data;

@Data
public class AgentCheckResponse {

    private List<AgentClaim> claims = new ArrayList<>();

    private List<AgentEvidence> evidences = new ArrayList<>();

    private AgentResult result;

    private AgentReport report;
}
