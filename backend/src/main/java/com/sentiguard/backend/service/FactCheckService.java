package com.sentiguard.backend.service;

import java.util.List;

import com.sentiguard.backend.dto.FactCheckAnalyzeDTO;
import com.sentiguard.backend.vo.AnalysisReportVO;
import com.sentiguard.backend.vo.FactCheckDetailVO;
import com.sentiguard.backend.vo.HistoryVO;

public interface FactCheckService {

    FactCheckDetailVO analyze(FactCheckAnalyzeDTO dto);

    FactCheckDetailVO getDetail(Long taskId);

    List<HistoryVO> getHistory(Long userId);

    AnalysisReportVO getReportByTaskId(Long taskId);
}
