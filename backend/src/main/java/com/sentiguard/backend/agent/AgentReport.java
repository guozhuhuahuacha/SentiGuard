package com.sentiguard.backend.agent;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AgentReport {

    private String title;

    private String content;

    private String format;
}
