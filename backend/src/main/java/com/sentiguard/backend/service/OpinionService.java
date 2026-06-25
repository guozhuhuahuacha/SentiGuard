package com.sentiguard.backend.service;

import java.util.Map;

import com.sentiguard.backend.dto.OpinionAnalyzeDTO;

public interface OpinionService {

    Map<String, Object> analyze(OpinionAnalyzeDTO dto);
}