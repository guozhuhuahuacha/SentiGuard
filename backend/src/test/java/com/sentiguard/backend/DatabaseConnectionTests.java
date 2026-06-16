package com.sentiguard.backend;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

@SpringBootTest
class DatabaseConnectionTests {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    void shouldConnectToSentiguardDatabase() {
        Integer value = jdbcTemplate.queryForObject("SELECT 1", Integer.class);
        String databaseName = jdbcTemplate.queryForObject("SELECT DATABASE()", String.class);

        assertThat(value).isEqualTo(1);
        assertThat(databaseName).isEqualTo("sentiguard");
    }
}
