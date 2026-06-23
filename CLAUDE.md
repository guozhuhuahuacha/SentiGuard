# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

SentiGuard 是一个「基于多智能体协同的网络舆情监测与事实核查平台」，由两层技术栈组成：

- **Python 智能体层**（`src/main/python/`）：多智能体事实核查主流程（LangGraph）、热点挖掘（BERTopic）、实验基线方法，通过 FastAPI 暴露内部接口。
- **Java 业务层**（`backend/`，Spring Boot 2.6.13 + MyBatis-Plus + MySQL + JWT）：面向前端的对外 API、用户鉴权、历史/报告持久化，通过 HTTP 调用 Python FastAPI。

两层通过「内部 API」对接：Java → FastAPI（`POST /internal/v1/fact-check` 等），鉴权用 `X-Internal-Token` 共享密钥。接口契约见 `docs/api/internal-api.md`。

代码注释和文档大量使用中文，这是项目惯例，新增内容请保持一致。

## 常用命令

### Python（在仓库根目录执行，使用 `src.main.python.*` 这样的全限定包路径）

```bash
# 安装依赖（Python 3.11+）
pip install -r requirements.txt

# 启动 FastAPI 内部服务（端口 8000）
uvicorn src.main.python.api.app:app --host 0.0.0.0 --port 8000 --reload

# 跑实验（遍历多个模型 × 4 种基线方法 × FactAgent，读写 data/ 与 result/）
python src/main/python/run_experiments.py

# 评估结果（生成 sklearn classification_report）
python src/main/python/evaluate.py
```

测试在 `src/test/python/` 下，用 pytest：
```bash
# 跑单个测试文件
python -m pytest src/test/python/test_factagent.py -v
python -m pytest src/test/python/test_search_anspire.py -v
```

### Java 后端（`backend/`，Java 17 + Maven）

```bash
cd backend
# 默认 profile=local，连本地 MySQL（127.0.0.1:3306/sentiguard）
mvn spring-boot:run

# mock-agent profile：跳过 Python FastAPI，返回假数据，便于无算法环境联调
mvn spring-boot:run -Dspring-boot.run.profiles=mock-agent

# 测试
mvn test
```

数据库 schema 见仓库根 `database-schema.sql`，需先在 MySQL 中建库 `sentiguard` 并导入。

## 架构要点

### 1. 多智能体事实核查（`src/main/python/main_agent.py`）

`FactAgent` 用 LangGraph 构建了一个**双层 Supervisor 图**：

- 外层 Supervisor 调度：`input_ingestor` → `query_generator` → `evidence_seeker` → `verdict_predictor`
- 内层 `input_ingestor` 又是一个独立子图，由自己的 Supervisor 调度：`claim_decomposition` / `claim_classification` / `claim_splitter`

每个节点是一个 LangGraph `create_react_agent`（带 `response_format` 结构化输出）。**注意**：Supervisor 节点没有用 `with_structured_output`，而是手动调用 LLM 后用 `_extract_json_from_content` 解析 JSON（容忍 markdown 代码块），因为豆包模型要求 prompt 中显式出现 "json" 字样。

事实核查的最终标签只有两种：`supported` / `not_supported`（在 API 层映射为 `isTrue: bool`）。F1 接口当前只返回 `isTrue / conclusion / explanation` 三字段，是有意精简的结果，不要随意加字段（见 `docs/AI_COLLAB_LOG.md` 条目 #11）。

### 2. LLM 抽象层（`src/main/python/llms/`）—— 开闭原则

`BaseLLM` 是抽象基类，`create_chat_model()` / `get_llm_provider()` 是工厂入口，`detect_provider()` 按 `model_name` 前缀自动推断 provider（`ollama/` → Ollama，`doubao/` → Doubao，其余 → OpenAI）。

**新增一个模型提供商**：只需继承 `BaseLLM`、实现 4 个抽象方法，并在 `get_llm_provider` 注册表中追加一项，**不要修改既有代码**。

豆包 API Key 解析优先级（见 `doubao_client.py`）：环境变量 `DOUBAO_API_KEY` > `ARK_API_KEY` > 构造函数传入参数（环境变量优先是有意为之，见日志条目 #29）。

### 3. 证据检索（`src/main/python/tools/`）

`retrieve.py` 的 `SearchEngineRetriever` 用 Selenium 无头浏览器抓取网页正文，再用 Google Gemini 抽取与查询相关的句子。URL 合法性通过 `media_bias_data.json` + 域名后缀 + WHOIS 域龄 + 学术域名白名单综合判断。

搜索引擎通过**注册表模式**接入（`search_base.py` 的 `SearchEngineRegistry`）：新增引擎继承 `BaseSearchEngine` 并 `register_search_engine` 注册即可，`retrieve.py` 取 `list_search_engines()[0]` 使用（当前实现是 Anspire）。`tools/__init__.py` 必须 import 具体实现模块以触发注册。

### 4. 实验基线方法（`src/main/python/experiments/`）

四种基线 + 主流程，统一签名 `method(model, claim) -> dict[label, explanation]`：`direct` / `cot` / `folk` / `sase`(Self-Ask)。`experiments/__init__.py` 导出这些函数。`run_experiments.py` 会按 `result/{method}/{model}/{data_type}/` 组织输出，`evaluate.py` 再按该结构读回算指标。标签归一化见 `evaluate.py` 的 `LABEL_MAP`。

### 5. 热点挖掘（`src/main/python/hot_topic/`）

独立子包，BERTopic 端到端聚类（Embedding → UMAP → HDBSCAN → c-TF-IDF）。核心是可调用的 Python API 而非 CLI：`topic_model_trainer.py` 的 `TopicModelTrainer` 类 + `topic_model_config.py` 集中配置（支持 test/small/medium/large/full 预设、断点续训）。所有数据源（GDELT / RSS / THUCNews）统一输出 `config.DOC_COLUMNS` schema。`hot_topic/config.py` 的 `REPO_ROOT` 通过 `parents[4]` 推算，移动该文件需同步调整。

### 6. 报告模块（`src/main/python/report/`）

两层架构，符合开闭原则：
- **数据驱动模式**（`ReportGenerator`）：用 section/template/renderer 三层策略模式将结构化数据填入模板章节，输出 Markdown。
- **LLM 叙事模式**（`LLMReportGenerator`，主力路径）：多阶段流水线（布局设计 → 逐章生成结构化 IR → 文档 IR 组装 → HTML 渲染），采用 **结构化 IR（中间表示）** 方案——LLM 输出 9 种 block 类型的 JSON（heading/paragraph/list/table/callout/kpiGrid/blockquote/evidenceCard/hr），渲染器按 block type 分派渲染，而非正则转换 Markdown。失败时自动降级为 Markdown 模式。

`report/ir/schema.py` 定义 block 类型和校验函数，`report/renderers/html.py` 用 `render_ir()` 方法处理 IR 渲染（callout 四色调、evidenceCard 带可信度进度条、kpiGrid 卡片网格等）。

### 7. API 响应体约定

FastAPI 与 Spring Boot 都遵循统一响应体：`{code, message, data}`，`code=0` 表示成功。FastAPI 端在 `api/app.py` 用全局异常处理器保证错误响应也符合该格式。

## 环境变量

复制 `.env.example` → `.env`。关键变量：
- `OPENAI_API_KEY` / `GOOGLE_API_KEY`（Gemini，用于 retrieve 内容抽取）
- `DOUBAO_API_KEY` + `DOUBAO_BASE_URL`（或 `ARK_*` 兼容）
- `ANSPIRE_API_KEY` + `ANSPIRE_BASE_URL`（证据检索搜索引擎）
- `INTERNAL_API_TOKEN`（FastAPI 内部鉴权，默认 `dev-internal-token`）
- Java 端：`MYSQL_USERNAME` / `MYSQL_PASSWORD` / `JWT_SECRET` / `SENTIGUARD_AGENT_BASE_URL` / `SENTIGUARD_INTERNAL_TOKEN`

## 工作约定

- **`docs/AI_COLLAB_LOG.md` 是「AI 辅助开发日志」**，是课程报告第 7 章的原始素材。开发过程中每完成一项有价值的工作（设计/编码/调试/文档/解答）后，**及时**按文件末尾模板追加一条条目（正序），并更新末尾「阶段性统计」表——不要攒到事后补记。维护该日志是项目明确要求。
- 文档与代码需保持单一真理源：改接口时**文档 / Pydantic schema / Java DTO / router 四处同步**（见日志条目 #13）。
- `.gitignore` 已排除 `data/hot_topic/`、`result/`、`eval/`、`test_results.json`、`*.doc`/`*.docx`（任务书不入库）、临时测试脚本（`simple_gdelt_test.py` 等）。生成数据不要提交。
- 默认开发 token 仅用于开发，生产环境必须用环境变量覆盖。
