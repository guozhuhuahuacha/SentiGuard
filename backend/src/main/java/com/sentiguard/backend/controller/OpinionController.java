package com.sentiguard.backend.controller;

import java.util.Map;

import javax.validation.Valid;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.sentiguard.backend.common.Result;
import com.sentiguard.backend.dto.OpinionAnalyzeDTO;
import com.sentiguard.backend.service.OpinionService;

@RestController
@RequestMapping("/api/opinion")
public class OpinionController {

    private final OpinionService opinionService;

    public OpinionController(OpinionService opinionService) {
        this.opinionService = opinionService;
    }

    @PostMapping("/analyze")
    public Result<Map<String, Object>> analyze(@Valid @RequestBody OpinionAnalyzeDTO dto) {
        return Result.ok(opinionService.analyze(dto));
    }
}