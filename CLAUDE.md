# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

SentiGuard 是一个「基于多智能体协同的网络舆情监测与事实核查平台」，由两层技术栈组成：

- **Python 智能体层**（`src/main/python/`）：多智能体事实核查主流程（LangGraph）、热点挖掘（BERTopic）、实验基线方法，通过 FastAPI 暴露内部接口。
- **Java 业务层**（`backend/`，Spring Boot 2.6.13 + MyBatis-Plus + MySQL + JWT）：面向前端的对外 API、用户鉴权、历史/报告持久化，通过 HTTP 调用 Python FastAPI。

两层通过「内部 API」对接：Java → FastAPI（`POST /internal/v1/fact-check` 等），鉴权用 `X-Internal-Token` 共享密钥。接口契约见 `docs/api/internal-api.md`。

代码注释和文档大量使用中文，这是项目惯例，新增内容请保持一致。

## 目录结构

```
SentiGuard/
├── CLAUDE.md                        ← 本文件
├── .env.example                     环境变量模板
├── requirements.txt                 Python 依赖
├── database-schema.sql              MySQL 建库脚本
├── docs/                            项目文档
│   └── api/internal-api.md          内部 API 契约
├── data/                            数据目录（不入库）
├── result/                          实验结果（不入库）
│
├── src/main/python/                 Python 智能体层
│   ├── api/                         FastAPI 框架层
│   │   ├── app.py                       ASGI 入口，注册路由 + 全局异常处理
│   │   ├── deps.py                      共享鉴权（X-Internal-Token）
│   │   ├── schemas.py                   ApiResponse + 各模块 schema 重导出
│   │   └── routers/                     向后兼容重导出层
│   │
│   ├── providers/                   外部 API 适配层（开闭原则）
│   │   ├── llm/                         OpenAI / Ollama / 豆包
│   │   ├── search/                      Anspire 搜索引擎
│   │   └── trending/                    百度热搜
│   │
│   ├── search/                      搜索业务逻辑（构建在 providers/search/ 之上）
│   │   ├── retriever.py                 Selenium + LLM 网页内容抽取
│   │   ├── service.py                   summary / fulltext 两种搜索策略
│   │   └── media_bias_data.json         媒体偏见数据库
│   │
│   ├── fact_check/                  事实核查模块（自包含：Agent + API + 报告）
│   │   ├── api.py                       POST /fact-check/quick, /deep
│   │   ├── schemas.py                   FactCheckRequest, EvidenceItem, F3* 等
│   │   ├── agent.py                     FactAgent（LangGraph 双层 Supervisor）
│   │   ├── reflective.py                ReflectiveFactAgent（反思循环）
│   │   ├── tracing.py                   TraceCollector（推断路径追踪）
│   │   ├── decomposer.py                DeepClaimDecomposer（深度声明拆分）
│   │   ├── prompts/                     事实核查提示词模板（7 个文件）
│   │   └── report/                      事实核查报告生成
│   │       ├── generator.py                 3 个 Generator（数据驱动 / LLM 叙事 / 深度）
│   │       ├── models.py                    数据模型
│   │       ├── ir/schema.py                 9 种 block 类型结构化 IR
│   │       ├── renderers/                   HTML / Markdown 渲染器
│   │       ├── sections/                    5 个报告 Section
│   │       └── templates/                   报告 Template
│   │
│   ├── services/                    热点服务模块（自包含：Agent + API + DB）
│   │   ├── api.py                       GET /hotspots, POST /collect
│   │   ├── schemas.py                   Hotspot, Keyword, Sentiment 等
│   │   ├── pipeline.py                  HotspotPipeline（编排采集→聚类→情感→入库）
│   │   ├── clusterer.py                 TF-IDF + 余弦相似度新闻聚类
│   │   ├── sentiment_analyzer.py        SnowNLP 中文情感分析
│   │   ├── db.py                        MySQL 连接（pymysql）
│   │   └── db_writer.py                 数据库写入器（6 张表）
│   │
│   ├── opinion/                     舆论监测模块（自包含：Agent + API + 报告）
│   │   ├── api.py                       POST /opinion/analyze
│   │   ├── schemas.py                   OpinionAnalyzeRequest, OpinionDetailData 等
│   │   ├── monitor_agent.py             OpinionMonitorAgent（5 步管道）
│   │   ├── generator.py                 OpinionReportGenerator（复用 HTMLRenderer）
│   │   └── prompts/                     搜索/抽取/聚类/摘要提示词
│   │
│   ├── experiments/                 实验基线方法
│   │   ├── direct.py                    直接判定
│   │   ├── cot.py                       思维链
│   │   ├── folk.py                      一阶逻辑
│   │   └── sase.py                      Self-Ask
│   │
│   ├── hot_topic/                   BERTopic 离线热点挖掘
│   │   ├── config.py                    集中配置（路径/API/预设）
│   │   ├── data_source/                 GDELT / RSS / THUCNews 数据源
│   │   ├── preprocessing/               jieba 分词 + 停用词过滤
│   │   ├── modeling/                    BERTopic 模型训练/保存/加载
│   │   ├── storage/                     CSV 增量持久化
│   │   ├── visualization/               Plotly 交互式可视化
│   │   ├── scripts/                     CLI 脚本（fetch / train / demo）
│   │   └── tests/                       数据源单元测试
│   │
│   ├── tools/                       LangChain @tool 兼容层（向后兼容重导出）
│   ├── llms/                        向后兼容重导出 → providers/llm/
│   ├── report/                      向后兼容重导出 → fact_check/report/
│   ├── prompts/                     向后兼容重导出 → fact_check/prompts/
│   ├── utils.py                     Google Serper 摘要 + use_gpt/use_ollama 兼容
│   ├── evaluate.py                  实验评估（sklearn classification_report）
│   ├── run_experiments.py           实验入口脚本
│   └── (其他根目录脚本待清理)
│
├── src/test/python/                 Python 测试
│
└── backend/                         Java 业务层（Spring Boot）
    └── src/main/java/...
```

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

## 模块架构

### 依赖层级

```
api/  (FastAPI 框架层)
 │
 ├── fact_check/api.py  ──→  fact_check/agent.py  ──→  providers/llm/
 │                         │                         └──→  search/retriever.py
 │                         └──→  fact_check/report/  ──→  providers/llm/
 │
 ├── services/api.py    ──→  services/pipeline.py  ──→  providers/trending/
 │                         │                        └──→  services/clusterer.py
 │                         │                        └──→  services/sentiment_analyzer.py
 │                         └──→  services/db.py
 │
 └── opinion/api.py     ──→  opinion/monitor_agent.py  ──→  providers/llm/
                                                        └──→  search/retriever.py
                                                        └──→  fact_check/report/renderers/html.py
```

### 1. 事实核查模块（`fact_check/`）

`FactAgent` 用 LangGraph 构建了一个**双层 Supervisor 图**：

- 外层 Supervisor 调度：`input_ingestor` → `query_generator` → `evidence_seeker` → `verdict_predictor`
- 内层 `input_ingestor` 又是一个独立子图，由自己的 Supervisor 调度：`claim_decomposition` / `claim_classification` / `claim_splitter`

每个节点是一个 LangGraph `create_react_agent`（带 `response_format` 结构化输出）。**注意**：Supervisor 节点没有用 `with_structured_output`，而是手动调用 LLM 后用 `_extract_json_from_content` 解析 JSON（容忍 markdown 代码块），因为豆包模型要求 prompt 中显式出现 "json" 字样。

事实核查的最终标签只有两种：`supported` / `not_supported`（在 API 层映射为 `isTrue: bool`）。F1 接口当前只返回 `isTrue / conclusion / explanation` 三字段，是有意精简的结果，不要随意加字段（见 `docs/AI_COLLAB_LOG.md` 条目 #11）。

`ReflectiveFactAgent` 通过组合（composition）包装 `FactAgent`，额外加入反思循环：
1. 首次调用 FactAgent 完成标准核查
2. 反思当前证据是否充足（Reflection LLM）
3. 如不足，生成新的搜索查询 → 补充搜索（search_fulltext）→ 重新判定
4. 最多重复 N 次

`fact_check/report/` 提供三种报告生成模式：
- **数据驱动**（`ReportGenerator`）：section/template/renderer 三层策略模式，输出 Markdown
- **LLM 叙事**（`LLMReportGenerator`，主力路径）：LLM 布局设计 → 逐章生成结构化 IR → HTML 渲染，9 种 block 类型
- **深度**（`DeepLLMReportGenerator`）：deep claim decomposition + per-claim HTML card generation

### 2. 外部服务提供方（`providers/`）

统一的外部 API 适配层，按能力域分三个子包。**新增外部服务只需新增文件并注册，不修改既有代码（开闭原则）。**

#### LLM（`providers/llm/`）

`BaseLLM` 是抽象基类，`create_chat_model()` / `get_llm_provider()` 是工厂入口，`detect_provider()` 按 `model_name` 前缀自动推断 provider：
- `ollama/` → Ollama
- `doubao/` → Doubao
- 其余 → OpenAI

**新增模型提供商**：继承 `BaseLLM`、实现 4 个抽象方法，在 `get_llm_provider` 注册表中追加一项即可。

豆包 API Key 解析优先级：环境变量 `DOUBAO_API_KEY` > `ARK_API_KEY` > 构造函数传入参数。

#### 搜索（`providers/search/`）

`BaseSearchEngine` 抽象基类 + `SearchEngineRegistry` 注册表模式。当前实现为 Anspire（`providers/search/anspire.py`），通过 `register_search_engine("anspire", AnspireSearchEngine)` 注册。

**新增搜索引擎**：继承 `BaseSearchEngine`，调用 `register_search_engine` 注册即可。

#### 热搜平台（`providers/trending/`）

当前实现为百度热搜（`BaiduCollector`），通过百度内部 API JSON 接口获取实时热搜，HTML 解析为回退方案。**新增热搜平台**：参照 `BaiduCollector` 实现，在 `__init__.py` 中导出即可。

### 3. 搜索业务逻辑（`search/`）

构建在 `providers/search/` API 之上的业务逻辑：

- **`SearchEngineRetriever`**：Selenium 无头浏览器抓取网页正文 + LLM 抽取与查询相关的句子。URL 合法性通过 `media_bias_data.json` + 域名后缀 + WHOIS 域龄 + 学术域名白名单综合判断。
- **两种搜索策略**：
  - `search_summary()` — 摘要搜索，直接调搜索引擎取 title/snippet，快（无 Selenium），用于标准 FactAgent
  - `search_fulltext()` — 全文搜索，对每条结果 Selenium 抓取 + LLM 抽取，慢但详细，用于 ReflectiveFactAgent 反思循环

### 4. 热点服务模块（`services/`）

百度热搜实时采集→分析→入库管道：

```
BaiduCollector.fetch()
  → DbWriter.insert_news()    （URL 去重入库）
  → Clusterer.cluster()       （TF-IDF + 余弦相似度聚类）
  → SentimentAnalyzer.analyze()（SnowNLP 情感分析）
  → DbWriter 写入 hot_event / sentiment_analysis / topic_keyword / hot_event_news
```

对外 API：
- `GET /internal/v1/hotspots` — 从 MySQL 读取热点列表（按热度降序）
- `POST /internal/v1/collect` — 手动触发一次百度热搜采集与分析

### 5. 舆论监测模块（`opinion/`）

5 步流水线：LLM 搜索查询生成 → 批量搜索 → LLM 观点抽取（stance/sentiment/coreArgument）→ LLM 观点聚类 → 舆论画像 + HTML 报告。

复用 `search/retriever.py`（搜索）和 `fact_check/report/renderers/html.py`（报告框架），不修改既有代码。

### 6. 实验基线（`experiments/`）

四种基线 + 主流程，统一签名 `method(model, claim) -> dict[label, explanation]`：`direct` / `cot` / `folk` / `sase`(Self-Ask)。`run_experiments.py` 按 `result/{method}/{model}/{data_type}/` 组织输出，`evaluate.py` 按该结构读回算指标。标签归一化见 `evaluate.py` 的 `LABEL_MAP`。

### 7. 离线热点挖掘（`hot_topic/`）

BERTopic 端到端聚类（Embedding → UMAP → HDBSCAN → c-TF-IDF）。三阶段管道：数据摄入（GDELT / RSS / THUCNews → 统一 DataFrame）→ 建模（BERTopic）→ 输出（CSV + Plotly 可视化）。所有数据源统一输出 `config.DOC_COLUMNS` schema。`hot_topic/config.py` 的 `REPO_ROOT` 通过 `parents[4]` 推算，移动该文件需同步调整。

### 8. API 响应体约定

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
- 新增外部服务接入时，遵循 `providers/` 的开闭原则：新增文件 + 注册，不修改既有代码。
