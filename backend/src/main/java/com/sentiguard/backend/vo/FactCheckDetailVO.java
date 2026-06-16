package com.sentiguard.backend.vo;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import lombok.Data;

@Data
public class FactCheckDetailVO {

    private Long taskId;

    private Long userId;

    private Long hotEventId;

    private String inputText;

    private String status;

    private String taskType;

    private LocalDateTime submitTime;

    private LocalDateTime finishTime;

    private FactCheckResultVO result;

    private List<FactClaimVO> claims = new ArrayList<>();

    private List<EvidenceVO> evidences = new ArrayList<>();

    private AnalysisReportVO report;
}
