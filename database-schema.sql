-- SentiGuard 网络舆情监测与事实核查平台数据库表结构
-- MySQL 8.x / InnoDB / utf8mb4

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `agent_execution_log`;
DROP TABLE IF EXISTS `analysis_report`;
DROP TABLE IF EXISTS `fact_check_result`;
DROP TABLE IF EXISTS `evidence`;
DROP TABLE IF EXISTS `fact_claim`;
DROP TABLE IF EXISTS `fact_check_task`;
DROP TABLE IF EXISTS `sentiment_analysis`;
DROP TABLE IF EXISTS `topic_keyword`;
DROP TABLE IF EXISTS `hot_event_news`;
DROP TABLE IF EXISTS `hot_event`;
DROP TABLE IF EXISTS `news`;
DROP TABLE IF EXISTS `news_collect_task`;
DROP TABLE IF EXISTS `user_role`;
DROP TABLE IF EXISTS `role`;
DROP TABLE IF EXISTS `user`;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    `nickname` VARCHAR(50) DEFAULT NULL COMMENT '昵称',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像地址',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1启用，0禁用',
    `last_login_time` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0未删除，1已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

CREATE TABLE `role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '角色ID',
    `role_code` VARCHAR(50) NOT NULL COMMENT '角色编码：admin/auditor/user',
    `role_name` VARCHAR(50) NOT NULL COMMENT '角色名称',
    `description` VARCHAR(255) DEFAULT NULL COMMENT '角色描述',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1启用，0禁用',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0未删除，1已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色信息表';

CREATE TABLE `user_role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_role` (`user_id`, `role_id`),
    KEY `idx_user_role_user_id` (`user_id`),
    KEY `idx_user_role_role_id` (`role_id`),
    CONSTRAINT `fk_user_role_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
    CONSTRAINT `fk_user_role_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

CREATE TABLE `news_collect_task` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '采集任务ID',
    `task_name` VARCHAR(100) NOT NULL COMMENT '采集任务名称',
    `source_type` VARCHAR(50) NOT NULL DEFAULT 'GDELT' COMMENT '数据源类型：GDELT/MANUAL/MOCK',
    `keyword` VARCHAR(100) DEFAULT NULL COMMENT '采集关键词',
    `status` VARCHAR(30) NOT NULL DEFAULT 'pending' COMMENT '任务状态：pending/running/success/failed',
    `start_time` DATETIME DEFAULT NULL COMMENT '开始时间',
    `end_time` DATETIME DEFAULT NULL COMMENT '结束时间',
    `total_count` INT NOT NULL DEFAULT 0 COMMENT '采集总数',
    `success_count` INT NOT NULL DEFAULT 0 COMMENT '成功数量',
    `fail_count` INT NOT NULL DEFAULT 0 COMMENT '失败数量',
    `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0未删除，1已删除',
    PRIMARY KEY (`id`),
    KEY `idx_collect_task_status` (`status`),
    KEY `idx_collect_task_keyword` (`keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='新闻采集任务表';

CREATE TABLE `news` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '新闻ID',
    `collect_task_id` BIGINT DEFAULT NULL COMMENT '采集任务ID',
    `title` VARCHAR(500) NOT NULL COMMENT '新闻标题',
    `summary` TEXT DEFAULT NULL COMMENT '新闻摘要',
    `content` LONGTEXT DEFAULT NULL COMMENT '新闻正文',
    `source_name` VARCHAR(100) DEFAULT NULL COMMENT '新闻来源名称',
    `source_url` VARCHAR(800) NOT NULL COMMENT '新闻链接',
    `publish_time` DATETIME DEFAULT NULL COMMENT '发布时间',
    `language` VARCHAR(20) DEFAULT NULL COMMENT '语言',
    `country` VARCHAR(50) DEFAULT NULL COMMENT '国家或地区',
    `author` VARCHAR(100) DEFAULT NULL COMMENT '作者',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0未删除，1已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_news_source_url` (`source_url`(255)),
    KEY `idx_news_collect_task_id` (`collect_task_id`),
    KEY `idx_news_publish_time` (`publish_time`),
    KEY `idx_news_source_name` (`source_name`),
    CONSTRAINT `fk_news_collect_task` FOREIGN KEY (`collect_task_id`) REFERENCES `news_collect_task` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='新闻数据表';

CREATE TABLE `hot_event` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '热点事件ID',
    `event_title` VARCHAR(200) NOT NULL COMMENT '热点事件标题',
    `event_summary` TEXT DEFAULT NULL COMMENT '热点事件摘要',
    `topic_id` VARCHAR(100) DEFAULT NULL COMMENT '主题模型生成的主题ID',
    `heat_score` DECIMAL(8,2) NOT NULL DEFAULT 0.00 COMMENT '热度分数',
    `risk_level` VARCHAR(30) DEFAULT 'low' COMMENT '风险等级：low/medium/high',
    `sentiment_label` VARCHAR(30) DEFAULT 'neutral' COMMENT '情感倾向：positive/neutral/negative',
    `news_count` INT NOT NULL DEFAULT 0 COMMENT '关联新闻数量',
    `start_time` DATETIME DEFAULT NULL COMMENT '事件开始时间',
    `end_time` DATETIME DEFAULT NULL COMMENT '事件结束时间',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0未删除，1已删除',
    PRIMARY KEY (`id`),
    KEY `idx_hot_event_heat_score` (`heat_score`),
    KEY `idx_hot_event_sentiment_label` (`sentiment_label`),
    KEY `idx_hot_event_risk_level` (`risk_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='热点事件表';

CREATE TABLE `hot_event_news` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `hot_event_id` BIGINT NOT NULL COMMENT '热点事件ID',
    `news_id` BIGINT NOT NULL COMMENT '新闻ID',
    `relevance_score` DECIMAL(6,4) DEFAULT NULL COMMENT '新闻与热点的相关度',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_hot_event_news` (`hot_event_id`, `news_id`),
    KEY `idx_hot_event_news_event_id` (`hot_event_id`),
    KEY `idx_hot_event_news_news_id` (`news_id`),
    CONSTRAINT `fk_hot_event_news_event` FOREIGN KEY (`hot_event_id`) REFERENCES `hot_event` (`id`),
    CONSTRAINT `fk_hot_event_news_news` FOREIGN KEY (`news_id`) REFERENCES `news` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='热点事件新闻关联表';

CREATE TABLE `topic_keyword` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '关键词ID',
    `hot_event_id` BIGINT NOT NULL COMMENT '热点事件ID',
    `keyword` VARCHAR(100) NOT NULL COMMENT '主题关键词',
    `weight` DECIMAL(8,4) DEFAULT NULL COMMENT '关键词权重',
    `rank_no` INT DEFAULT NULL COMMENT '关键词排序',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_topic_keyword_event_id` (`hot_event_id`),
    KEY `idx_topic_keyword_keyword` (`keyword`),
    CONSTRAINT `fk_topic_keyword_event` FOREIGN KEY (`hot_event_id`) REFERENCES `hot_event` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='主题关键词表';

CREATE TABLE `sentiment_analysis` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '情感分析ID',
    `hot_event_id` BIGINT NOT NULL COMMENT '热点事件ID',
    `positive_count` INT NOT NULL DEFAULT 0 COMMENT '正面数量',
    `neutral_count` INT NOT NULL DEFAULT 0 COMMENT '中性数量',
    `negative_count` INT NOT NULL DEFAULT 0 COMMENT '负面数量',
    `positive_ratio` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '正面比例',
    `neutral_ratio` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '中性比例',
    `negative_ratio` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '负面比例',
    `sentiment_label` VARCHAR(30) NOT NULL DEFAULT 'neutral' COMMENT '总体情感倾向',
    `analysis_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '分析时间',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_sentiment_event_id` (`hot_event_id`),
    KEY `idx_sentiment_analysis_time` (`analysis_time`),
    CONSTRAINT `fk_sentiment_event` FOREIGN KEY (`hot_event_id`) REFERENCES `hot_event` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='舆情情感分析结果表';

CREATE TABLE `fact_check_task` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '事实核查任务ID',
    `user_id` BIGINT DEFAULT NULL COMMENT '发起用户ID',
    `hot_event_id` BIGINT DEFAULT NULL COMMENT '关联热点事件ID',
    `input_text` TEXT NOT NULL COMMENT '用户输入的核查内容',
    `task_status` VARCHAR(30) NOT NULL DEFAULT 'pending' COMMENT '任务状态：pending/running/success/failed',
    `task_type` VARCHAR(30) NOT NULL DEFAULT 'manual_input' COMMENT '任务类型：manual_input/hot_event_check',
    `submit_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    `finish_time` DATETIME DEFAULT NULL COMMENT '完成时间',
    `error_message` TEXT DEFAULT NULL COMMENT '任务错误信息',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0未删除，1已删除',
    PRIMARY KEY (`id`),
    KEY `idx_fact_task_user_id` (`user_id`),
    KEY `idx_fact_task_event_id` (`hot_event_id`),
    KEY `idx_fact_task_status` (`task_status`),
    KEY `idx_fact_task_submit_time` (`submit_time`),
    CONSTRAINT `fk_fact_task_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
    CONSTRAINT `fk_fact_task_event` FOREIGN KEY (`hot_event_id`) REFERENCES `hot_event` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='事实核查任务表';

CREATE TABLE `fact_claim` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '事实声明ID',
    `task_id` BIGINT NOT NULL COMMENT '事实核查任务ID',
    `claim_text` TEXT NOT NULL COMMENT '拆解后的事实声明',
    `claim_type` VARCHAR(50) DEFAULT NULL COMMENT '声明类型',
    `claim_order` INT NOT NULL DEFAULT 1 COMMENT '声明顺序',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_fact_claim_task_id` (`task_id`),
    CONSTRAINT `fk_fact_claim_task` FOREIGN KEY (`task_id`) REFERENCES `fact_check_task` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='事实声明表';

CREATE TABLE `evidence` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '证据ID',
    `task_id` BIGINT NOT NULL COMMENT '事实核查任务ID',
    `claim_id` BIGINT DEFAULT NULL COMMENT '事实声明ID',
    `news_id` BIGINT DEFAULT NULL COMMENT '关联新闻ID',
    `evidence_title` VARCHAR(300) DEFAULT NULL COMMENT '证据标题',
    `evidence_content` LONGTEXT DEFAULT NULL COMMENT '证据内容或摘要',
    `evidence_url` VARCHAR(800) DEFAULT NULL COMMENT '证据链接',
    `source_name` VARCHAR(100) DEFAULT NULL COMMENT '证据来源',
    `evidence_type` VARCHAR(30) DEFAULT 'web' COMMENT '证据类型：news/web/official/model_generated',
    `relation_type` VARCHAR(30) DEFAULT 'neutral' COMMENT '论辩关系：support/attack/neutral',
    `credibility_score` DECIMAL(5,2) DEFAULT NULL COMMENT '证据可信度评分',
    `publish_time` DATETIME DEFAULT NULL COMMENT '证据发布时间',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_evidence_task_id` (`task_id`),
    KEY `idx_evidence_claim_id` (`claim_id`),
    KEY `idx_evidence_news_id` (`news_id`),
    KEY `idx_evidence_relation_type` (`relation_type`),
    CONSTRAINT `fk_evidence_task` FOREIGN KEY (`task_id`) REFERENCES `fact_check_task` (`id`),
    CONSTRAINT `fk_evidence_claim` FOREIGN KEY (`claim_id`) REFERENCES `fact_claim` (`id`),
    CONSTRAINT `fk_evidence_news` FOREIGN KEY (`news_id`) REFERENCES `news` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='事实核查证据表';

CREATE TABLE `fact_check_result` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '核查结果ID',
    `task_id` BIGINT NOT NULL COMMENT '事实核查任务ID',
    `result_label` VARCHAR(30) NOT NULL COMMENT '核查标签：true/false/partly_true/insufficient_evidence',
    `confidence_score` DECIMAL(5,2) DEFAULT NULL COMMENT '置信度评分',
    `conclusion` TEXT DEFAULT NULL COMMENT '简要结论',
    `analysis_detail` LONGTEXT DEFAULT NULL COMMENT '详细分析',
    `support_count` INT NOT NULL DEFAULT 0 COMMENT '支持证据数量',
    `attack_count` INT NOT NULL DEFAULT 0 COMMENT '反驳证据数量',
    `review_status` VARCHAR(30) NOT NULL DEFAULT 'pending' COMMENT '审核状态：pending/approved/rejected/revised',
    `reviewer_id` BIGINT DEFAULT NULL COMMENT '审核员ID',
    `review_time` DATETIME DEFAULT NULL COMMENT '审核时间',
    `review_comment` TEXT DEFAULT NULL COMMENT '审核意见',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_fact_result_task_id` (`task_id`),
    KEY `idx_fact_result_label` (`result_label`),
    KEY `idx_fact_result_reviewer_id` (`reviewer_id`),
    CONSTRAINT `fk_fact_result_task` FOREIGN KEY (`task_id`) REFERENCES `fact_check_task` (`id`),
    CONSTRAINT `fk_fact_result_reviewer` FOREIGN KEY (`reviewer_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='事实核查结果表';

CREATE TABLE `analysis_report` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '报告ID',
    `task_id` BIGINT NOT NULL COMMENT '事实核查任务ID',
    `report_title` VARCHAR(200) NOT NULL COMMENT '报告标题',
    `report_content` LONGTEXT NOT NULL COMMENT '报告内容',
    `report_format` VARCHAR(30) NOT NULL DEFAULT 'markdown' COMMENT '报告格式：markdown/html/pdf/docx',
    `export_url` VARCHAR(800) DEFAULT NULL COMMENT '导出文件地址',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0未删除，1已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_report_task_id` (`task_id`),
    CONSTRAINT `fk_report_task` FOREIGN KEY (`task_id`) REFERENCES `fact_check_task` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析报告表';

CREATE TABLE `agent_execution_log` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '智能体执行日志ID',
    `task_id` BIGINT DEFAULT NULL COMMENT '事实核查任务ID',
    `agent_name` VARCHAR(100) NOT NULL COMMENT '智能体名称',
    `step_name` VARCHAR(100) DEFAULT NULL COMMENT '步骤名称',
    `input_summary` TEXT DEFAULT NULL COMMENT '输入摘要',
    `output_summary` TEXT DEFAULT NULL COMMENT '输出摘要',
    `status` VARCHAR(30) NOT NULL DEFAULT 'running' COMMENT '执行状态：running/success/failed',
    `start_time` DATETIME DEFAULT NULL COMMENT '开始时间',
    `end_time` DATETIME DEFAULT NULL COMMENT '结束时间',
    `duration_ms` INT DEFAULT NULL COMMENT '耗时毫秒',
    `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_agent_log_task_id` (`task_id`),
    KEY `idx_agent_log_agent_name` (`agent_name`),
    KEY `idx_agent_log_status` (`status`),
    CONSTRAINT `fk_agent_log_task` FOREIGN KEY (`task_id`) REFERENCES `fact_check_task` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='智能体执行日志表';

INSERT INTO `role` (`role_code`, `role_name`, `description`) VALUES
('admin', '管理员', '拥有系统最高权限，可管理用户、采集任务和智能体日志'),
('auditor', '审核员', '负责复核事实核查结果和分析报告'),
('user', '普通用户', '可查看热点、发起事实核查并查看自己的历史记录');

