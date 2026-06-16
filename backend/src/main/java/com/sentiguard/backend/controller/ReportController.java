package com.sentiguard.backend.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.sentiguard.backend.common.Result;
import com.sentiguard.backend.service.FactCheckService;
import com.sentiguard.backend.vo.AnalysisReportVO;

@RestController
@RequestMapping("/api/reports")
public class ReportController {

    private final FactCheckService factCheckService;

    public ReportController(FactCheckService factCheckService) {
        this.factCheckService = factCheckService;
    }

    @GetMapping("/tasks/{taskId}")
    public Result<AnalysisReportVO> getReportByTaskId(@PathVariable Long taskId) {
        return Result.ok(factCheckService.getReportByTaskId(taskId));
    }
}
