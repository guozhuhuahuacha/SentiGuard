package com.sentiguard.backend.controller;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/health")
public class HealthController {

    private final JdbcTemplate jdbcTemplate;

    public HealthController(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @GetMapping
    public Map<String, Object> health() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", "ok");
        result.put("service", "sentiguard-backend");
        return result;
    }

    @GetMapping("/db")
    public Map<String, Object> databaseHealth() {
        Integer value = jdbcTemplate.queryForObject("SELECT 1", Integer.class);
        String databaseName = jdbcTemplate.queryForObject("SELECT DATABASE()", String.class);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", "ok");
        result.put("database", databaseName);
        result.put("checkValue", value);
        return result;
    }
}
