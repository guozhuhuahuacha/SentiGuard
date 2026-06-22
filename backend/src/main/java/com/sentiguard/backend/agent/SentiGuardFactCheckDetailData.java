package com.sentiguard.backend.agent;

import java.util.ArrayList;
import java.util.List;

import lombok.Data;

@Data
public class SentiGuardFactCheckDetailData {

    private List<SentiGuardClaimData> claims = new ArrayList<>();

    private List<SentiGuardEvidenceData> evidences = new ArrayList<>();

    private SentiGuardResultData result;

    private SentiGuardReportData report;
}
