package com.sentiguard.backend.agent;

import lombok.Data;

@Data
public class SentiGuardReportData {

    private String reportTitle;

    private String reportContent;

    private String reportFormat;
}
