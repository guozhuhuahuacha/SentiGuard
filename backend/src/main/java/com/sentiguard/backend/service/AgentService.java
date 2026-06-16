package com.sentiguard.backend.service;

import com.sentiguard.backend.agent.AgentCheckRequest;
import com.sentiguard.backend.agent.AgentCheckResponse;

public interface AgentService {

    AgentCheckResponse check(AgentCheckRequest request);
}
