package com.sentiguard.backend.vo;

import lombok.Data;

@Data
public class AnalysisReportVO {

    private Long id;

    private String title;

    private String content;

    private String format;

    private String exportUrl;
}
