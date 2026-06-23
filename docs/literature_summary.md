# 文献综述：事实核查方法与多智能体系统

> 本文档对项目中参考的四篇核心文献进行详细的方法总结，为 SentiGuard 后续升级提供理论依据。
> 整理日期：2026-06-22

---

## 目录

1. [FEVEROUS Shared Task — 基准任务与数据集](#1-feverous-shared-task--基准任务与数据集)
2. [Veracity — 开源 AI 事实核查系统](#2-veracity--开源-ai-事实核查系统)
3. [SAFE — 基于论辩结构的事实核查与解释生成](#3-safe--基于论辩结构的事实核查与解释生成)
4. [Towards Robust Fact-Checking — 多智能体系统与高级证据检索](#4-towards-robust-fact-checking--多智能体系统与高级证据检索)
5. [文献对比与对本项目的启示](#5-文献对比与对本项目的启示)

---

## 1. FEVEROUS Shared Task — 基准任务与数据集

**原文**：*The Fact Extraction and VERification Over Unstructured and Structured information (FEVEROUS) Shared Task*
**作者**：Rami Aly, Zhijiang Guo, Michael Schlichtkrull, James Thorne, Andreas Vlachos (Cambridge) 等
**出处**：FEVER Workshop @ EMNLP 2021

### 1.1 背景与定位

FEVEROUS 是 FEVER 2018 共享任务的延续，核心差异在于：**证据类型从纯文本扩展到结构化数据（表格和列表）**。这意味着参与系统需要同时处理：

- 纯文本证据（Wikipedia 文章段落）
- 表格证据（Wikipedia 信息框、数据表）
- 混合证据（文本 + 表格联合推理）

### 1.2 数据集

| 项目 | 数值 |
|------|------|
| 总 claims 数 | 87,026 条 |
| 平均 claim 长度 | 25.3 词（FEVER 2018 仅 9.4 词） |
| 标签分布 | Supported ~41K, Refuted ~27K, NEI ~2K（训练集） |
| 证据类型 | 纯文本 ~31K, 纯表格 ~25K, 混合 ~20K |

### 1.3 任务定义

给定一条人工撰写的声明，系统需要：

1. **证据检索**：从 Wikipedia 中检索相关的句子和表格单元格，每个证据需附带其页面/章节标题和列标题上下文
2. **标签分类**：判定声明是 `SUPPORTED`（支持）、`REFUTED`（反驳）还是 `NOTENOUGHINFO`（证据不足）
3. **评分标准（FEVEROUS Score）**：只有预测的证据集包含至少一个完整的黄金证据集 **且** 标签正确，才算正确。这是一个联合评分，同时考察证据召回和标签准确率

### 1.4 基线系统架构

基线采用**多阶段检索流水线**：

```
声明 → 页面检索(实体匹配 + TF-IDF)
         → 句子选择(RoBERTa NLI 分类器)
         → 表格选择(单元格线性化 + 序列标注)
           → Verdict 预测(RoBERTa 分类器)
```

### 1.5 参赛队伍的最佳实践

**冠军团队 "Bust a move!"**（FEVEROUS Score 27%）：

- **页面检索**：BM25
- **句子选择**：三阶段流水线（密集检索 → BM25 过滤 → RoBERTa 重排序），用**难负样本迭代训练**
- **单元格选择**：表格线性化 + 独立模型
- **Verdict 预测**：两个 TAPAS 模型 + MLP 聚合，将所有证据视为表格形式
- **NEI 处理**：直接不预测 NEI，退化为二分类

**亚军 "Papelo"**（FEVEROUS Score 26%）：

- **句子选择**：RoBERTa + T5 下一跳预测器（迭代检索）
- **数值推理**：将数字和关系编码为 "math hints" 添加到输入前缀，在数值推理任务上大幅领先
- **Verdict 预测**：T5 模型，将所有证据视为句子形式（用特殊标记编码表格结构）
- **NEI 处理**：训练集 NEI 替换为 Supported，完全二分类

### 1.6 关键发现

1. **NEI 处理极难**：冠军和亚军都放弃了三分类，退化为二分类。NEI 类训练样本太少（仅 5%）是主因
2. **表格证据仍是瓶颈**：所有系统在混合证据上的表现都低于纯文本或纯表格
3. **连续表示优于专用方法**：用通用模型处理表格（线性化）比专用表格模型（TAPAS）效果更好
4. **数值推理需要特殊处理**：Papelo 的 "math hints" 方法显著领先

---

## 2. Veracity — 开源 AI 事实核查系统

**原文**：*Veracity: An Open-Source AI Fact-Checking System*
**作者**：Taylor Lynn Curtis 等 (Mila - Quebec AI Institute, McGill University)
**出处**：IJCAI-25 Demonstrations Track

### 2.1 核心方法：LLM + Web Search Agent 双引擎协同

Veracity 的核心思路是 **LLM 与 Web 检索代理协同工作**，而非单独依赖 LLM 的参数化知识。

```
用户提交 Claim
       ↓
  LLM 判断是否需要搜索
       ↓
  Web Agent 检索互联网
       ↓
  LLM 结合检索结果 → 评分 + 解释
```

### 2.2 系统特色

#### 2.2.1 数值化可靠性评分

不同于简单的 true/false 二分类，Veracity 输出 **0-100% 的可靠性评分**：

| 分数区间 | 含义 | 推荐操作 |
|---------|------|---------|
| ≥ 60% | 可信 | 可以分享 |
| < 60% | 不可信 | 谨慎对待 |

评分附带**可操作的文字说明**和 LLM 推理过程的自然语言解释。

#### 2.2.2 来源透明展示

- 所有检索到的来源**全部展示给用户**
- 附带每个来源的**文档化可信度评级**（基于 Lin et al. 2023）
- 聚合展示：来源总数、平均可信度排名

#### 2.2.3 其他特性

- **多语言支持**：不限于英语
- **用户反馈机制**：1-5 星评分 + 标签 + 评论，用于持续改进
- **专家仪表盘**：聚合展示用户提交 claims 的趋势聚类图

### 2.3 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Next.js + Sass + TypeScript + Chart.js |
| 后端 API | FastAPI |
| 数据库 | PostgreSQL + SQLAlchemy |
| 部署 | GCP Kubernetes + Cloud SQL |

### 2.4 与本项目的差异

| 维度 | Veracity | SentiGuard（当前） |
|------|----------|-------------------|
| 判定输出 | 数值评分 0-100% | 布尔值 true/false |
| 来源展示 | 全部展示给用户 | 仅 trace 中记录 |
| 证据深度 | Web 检索 | Web 检索 |
| 声明拆解 | 无（整体判断） | 多智能体拆解 |
| 可解释性 | LLM 自然语言解释 | LLM 自然语言解释 |

---

## 3. SAFE — 基于论辩结构的事实核查与解释生成

**原文**：*SAFE: Structured Argumentation for Fact-checking with Explanations*
**作者**：Xiaoou Wang, Elena Cabrio, Serena Villata (Université Côte d'Azur, Inria)
**出处**：IJCAI-25 Demonstrations Track

### 3.1 核心思想

SAFE 的核心创新在于：**将事实核查的解释从"自由文本摘要"提升为"论辩结构化的论证分析"**。它模仿专业事实核查员的工作方式——分析新闻声明中的每条证据对声明的**支持/攻击**关系。

### 3.2 三大模块

```
模块一：论辩结构化摘要
  输入: 声明 + 人工撰写的事实核查文章
  输出: 每条证据对声明的支持/攻击关系 + 论证图

模块二：检索式摘要（当没有人工文章时）
  输入: 声明
  输出: 检索的证据列表 + 论辩结构化摘要 + 论证图

模块三：声明验证
  输入: 声明 + 论辩结构化摘要
  输出: 真伪标签
```

#### 模块一：论辩结构化摘要

- **方法**：微调 Mixtral-8x22B 在 LIARArg 数据集上
- **输出格式**：每条证据标注其对声明的论辩关系：
  - `supports`（支持）
  - `partially supports`（部分支持）
  - `attacks`（攻击）
  - `partially attacks`（部分攻击）
- **可视化**：自动生成**论证图（argument graph）**，直观展示声明与证据间的论辩关系

**示例**：
> 声明："伊朗可能不是超级大国，但奥巴马说伊朗构成的威胁绝不微小"
> - 前提 "奥巴马从未说伊朗的威胁是'微小'或'微不足道'" → **攻击** 声明
> - 前提 "只是说威胁与苏联构成的威胁相比是微小的" → **部分支持** 声明

#### 模块二：检索式摘要

- **骨干**：Atlas（检索增强生成框架）
- **训练**：联合优化两个损失函数
  - 事实核查文章与检索文档的相似度损失
  - 生成摘要与检索文档的攻击性得分分布的 Cauchy 损失
- **推理时不需要人工文章**，完全自动化

#### 模块三：声明验证

- **方法**：将声明和论辩摘要用 `[SEP]` 拼接，提取 `[CLS]` 嵌入
- **增强**：基于 Wikidata 构建实体图，用**图注意力网络（GAT）**提取图嵌入
- **分类**：softmax 层融合文本嵌入 + 图嵌入
- **标签**：支持多数据集多标签，通用模式合并为 True / False / Unknown

### 3.3 实验结果

#### 论辩摘要质量（ROUGE）

| 方法 | R1 | R2 | RL |
|------|----|----|----|
| CDAE（SOTA 摘要） | **0.348** | **0.159** | **0.272** |
| SAFE | 0.268 | 0.128 | 0.143 |

> SAFE 的 ROUGE 分数更低，但这是意料之中的——论辩结构化摘要追求的是**论证关系清晰**而非词汇重叠。

#### 下游验证任务 F1 分数

| 输入 | LIAR-PLUS | FNC-1 | Check-COVID |
|------|-----------|-------|-------------|
| 人工文章(Ground) | 0.51 | 0.90 | 0.76 |
| CDAE 摘要 | 0.41 | 0.76 | 0.62 |
| **SAFE 摘要** | **0.54** | **0.92** | **0.74** |

> **关键发现**：SAFE 的论辩结构化摘要**甚至优于人工撰写的原文**（LIAR-PLUS +0.03, FNC-1 +0.02）。可能原因：①生成的摘要覆盖了更全面的证据 ②显式的 support/attack 关系对验证模型更有帮助。

#### 检索式摘要对比（ExClaim 数据集）

| 指标 | JustiLM（SOTA） | SAFE |
|------|-----------------|------|
| Top-5 Recall | 15% | **20%** |
| Top-10 Recall | 18% | **27%** |
| Top-15 Recall | 25% | **31%** |
| Top-20 Recall | 30% | **40%** |
| F1 (验证任务) | 0.67 | **0.74** |

### 3.4 对本项目的启示

1. **论辩关系细粒度化**：当前 SentiGuard 只用了 `support` / `attack` / `neutral` 三级，SAFE 的 `partially supports` / `partially attacks` 更细粒度
2. **论证图可视化**：可以作为前端展示的增强功能
3. **ROUGE 不是好指标**：事实核查领域的摘要评估应关注下游任务效果而非词汇重叠
4. **实体图增强**：Wikidata 实体图 + GAT 的方法可以提升验证准确率

---

## 4. Towards Robust Fact-Checking — 多智能体系统与高级证据检索

**原文**：*Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval*
**作者**：Tam Trinh, Manh Nguyen, Truong-Son Hy
**出处**：arXiv:2506.17878, 2025.06

> ⚠️ **这篇与 SentiGuard 架构最为相似**，都是四智能体多阶段流水线，但做了大量深度增强。

### 4.1 系统架构

```
声明
  ↓
┌──────────────────────────────────────────────┐
│              Orchestrator                     │
│  (管理智能体间通信和工作流)                     │
│                                              │
│  ┌──────────────┐  ┌──────────────┐          │
│  │ Input        │  │ Query        │          │
│  │ Ingestion    │→ │ Generation   │          │
│  │ Agent        │  │ Agent        │          │
│  └──────────────┘  └──────┬───────┘          │
│                           ↓                  │
│  ┌──────────────┐  ┌──────────────┐          │
│  │ Verdict      │  │ Evidence     │          │
│  │ Prediction   │← │ Seeking      │          │
│  │ Agent        │  │ Agent        │          │
│  └──────────────┘  └──────────────┘          │
└──────────────────────────────────────────────┘
  ↓
Veracity Result (label + explanation)
```

### 4.2 四个智能体的详细方法

#### 4.2.1 Input Ingestion Agent（声明摄入智能体）

**SentiGuard 当前做法**：简单拆成子声明列表 + 分类为 verifiable/non-verifiable

**本文改进 — 一阶逻辑（FOL）谓词分解**：

将声明转化为一阶逻辑原子谓词：

```
原始声明: "相扑选手 Toyozakura Toshiaki 参与假赛，
           结束了他始于1989年、于2011年结束的职业生涯"

FOL 分解:
  Occupation(Toyozakura Toshiaki, "sumo wrestler")
  Commit(Toyozakura Toshiaki, "match-fixing")
  Ending(Toyozakura Toshiaki, "his career in 2011")
  Starting(Toyozakura Toshiaki, "his career in 1989")
```

每个谓词附带**自然语言验证目标**（如"验证 Toyozakura Toshiaki 是否是相扑选手"）。

**逻辑基础**：声明 C = p₁ ∧ p₂ ∧ ... ∧ pₙ（所有谓词的合取）

- 所有谓词为 True → SUPPORTED
- 任一谓词为 False → NOT SUPPORTED

**可核查性过滤**：基于 Micallef et al. 和 Konstantinovskiy et al. 的标准，过滤掉主观/情绪化/无法客观验证的子声明。

#### 4.2.2 Query Generation Agent（查询生成智能体）

**SentiGuard 当前做法**：每个子声明生成若干自然语言问题

**本文改进 — SEO 驱动多角度查询生成**：

引入**搜索引擎优化（SEO）**原则来生成查询：

1. **关键词/实体**：从声明中提取具体实体
2. **同义词/替代表述**：同一概念的不同表达
3. **平衡的特异性**：不太宽泛也不太狭窄
4. **基于问题的表述**：符合自然搜索习惯

每个子声明生成 **k 个**不同角度的搜索查询（实验表明 k=3~4 最优）。从 k=1→3 时 F1 显著提升，超过 3 后收益递减或略有下降。

#### 4.2.3 Evidence Seeking Agent（证据搜索智能体）

**这是本文最大的增强点**，分为三层：

##### 第一层：搜索引擎检索

- **API**：SerperAPI（Google Search API 的高性能封装）
- **配置**：每次返回 top 10 结果，US 区域
- **时间边界**：按数据集设定截止日期（FEVEROUS: 2021-10-12），防止时间穿越

##### 第二层：来源可信度评估 ⭐ 核心改进

集成 **Media Bias/Fact Check (MBFC) API** 进行专业来源评级：

**过滤前** → **过滤后保留**

| 事实性维度 | 政治偏见维度 |
|-----------|-------------|
| very high ✓ | least biased ✓ |
| high ✓ | left-center ✓ |
| mostly factual ✓ | right-center ✓ |
| mixed ✗ | left ✗ |
| low ✗ | right ✗ |
| very low ✗ | extremely left/right ✗ |

**MBFC 未覆盖的域名，使用兜底策略**：

- **域名后缀**：.edu / .gov / .org 加分
- **域龄**：长期运营的域名更可信
- **引用模式**：Google Scholar / PubMed 中出现的来源优先

**实验结果**：HoVER 数据集中仅 9.6%~15.8% 的链接通过可信度过滤，FEVEROUS 和 SciFact 保留率超过 86%。

##### 第三层：全文档内容提取

**不同于传统方法仅依赖搜索片段（snippet）**，本文方法：

1. **Selenium** 无头浏览器抓取完整网页
2. **BeautifulSoup** HTML 解析
3. **Gemini 1.5 Flash**（百万 token 上下文窗口）分析全文，提取与声明最相关的段落

#### 4.2.4 Verdict Prediction Agent（判定预测智能体）

**SentiGuard 当前做法**：单一 LLM 直接判定

**本文改进 — 结构化多步判定**：

1. **证据分析**：检查多条证据间的一致性，高一致性 → 高置信度
2. **加权投票机制**：
   - 多条强支持证据 → `supported`
   - 存在矛盾或不可靠证据 → `not_supported`
3. **解释生成**：每条判定附带引用具体证据的详细解释

### 4.3 实验结果

#### 主要结果（GPT-4o-mini, 3 queries/subclaim）

| 数据集 | 指标 | Direct | CoT | SA+SE | FOLK | **MAS (Ours)** |
|--------|------|--------|-----|-------|------|----------------|
| HoVER 2-hop | Macro F1 | 0.521 | 0.540 | 0.542 | 0.595 | **0.600** |
| HoVER 3-hop | Macro F1 | — | 0.449 | 0.466 | 0.489 | **0.617** |
| HoVER 4-hop | Macro F1 | 0.419 | 0.440 | 0.460 | 0.466 | **0.507** |
| FEVEROUS Numerical | Macro F1 | — | 0.465 | 0.496 | 0.553 | 0.487 |
| FEVEROUS Multi-hop | Macro F1 | — | 0.502 | 0.609 | 0.612 | **0.630** |
| FEVEROUS Text+Table | Macro F1 | — | 0.591 | 0.618 | 0.542 | **0.681** |
| SciFact-Open | Macro F1 | 0.497 | 0.634 | 0.609 | 0.737 | **0.770** |

**相对基线提升 12.3% Macro F1**。

#### 查询数量实验

| 查询数 | HoVER 2-hop | HoVER 4-hop | SciFact-Open |
|--------|------------|------------|-------------|
| 1 | 0.472 | 0.416 | 0.462 |
| 2 | 0.557 | 0.452 | 0.638 |
| 3 | **0.600** | 0.507 | **0.770** |
| 4 | 0.561 | **0.515** | 0.752 |
| 5 | 0.538 | 0.512 | 0.755 |

结论：3~4 个查询/子声明是最优平衡点。

#### 小模型表现（Llama-3.2-1B / Qwen-2.5-3B）

- **小模型上 CoT 反而最优**：MAS 和 FOLK 在小模型上表现接近随机，说明多智能体/多跳策略对模型容量有硬要求
- **Qwen-2.5-3B 上 MAS 开始展现优势**：模型容量增大时，高级策略的效果逐渐显现

### 4.4 基线方法说明

论文对比了四种基线，这也是本项目 `src/main/python/experiments/` 中实现的四种方法：

| 方法 | 原理 | 弱点 |
|------|------|------|
| **Direct** | LLM 闭卷直接回答 | 知识陈旧、幻觉、无透明度 |
| **CoT** | 逐步推理 + 分解验证子问题 | 级联错误、依赖分解质量 |
| **SA+SE** | Self-Ask + 搜索引擎实时检索 | 查询质量不可控、无来源可信度评估 |
| **FOLK** | FOL 分解 + 外部知识检索 | 冗余谓词、仅依赖 snippet、缺可信度评估 |

---

## 5. 文献对比与对本项目的启示

### 5.1 四篇文献核心方法一览

| 维度 | FEVEROUS (2021) | Veracity (2025) | SAFE (2025) | Robust MAS (2025) |
|------|-----------------|-----------------|-------------|-------------------|
| **核心贡献** | 数据集 + 评估体系 | LLM + Web Agent 协同 | 论辩结构化解释 | 多智能体增强流水线 |
| **证据类型** | Wikipedia 文本+表格 | 互联网 | 新闻文章 | 互联网 |
| **声明拆解** | 隐式（检索阶段） | 无 | 显式（论辩关系） | **FOL 谓词分解** |
| **来源可信度** | 无（Wikipedia 本身可信） | 文档化评级 | 无（预设语料库） | **MBFC API + 多维度** |
| **证据深度** | 句子/单元格 | Web 检索 | 全文文章 | **全文档 Selenium + Gemini** |
| **判定输出** | Supported/Refuted/NEI | **数值评分 0-100%** | 多标签分类 | Supported/Not Supported |
| **可解释性** | 无 | LLM 自然语言 | **论证图 + 论辩关系** | LLM + 加权投票理由 |
| **数值推理** | 需特殊处理(math hints) | — | — | 待改进 |

### 5.2 对 SentiGuard 升级的潜在方向

按实施优先级排序：

1. **⭐ FOL 谓词分解**（文献4）— Input Ingestion Agent 的升级，让声明拆解更精确、可追溯
2. **⭐ 来源可信度评估**（文献4）— 集成 MBFC API + 域名/域龄兜底，过滤低质量来源
3. **⭐ 加权投票判定**（文献4）— Verdict Prediction 从单 LLM 判定升级为结构化投票
4. **数值评分输出**（文献2）— 从布尔值升级为 0-100 评分，附带置信度
5. **论辩关系细粒度化**（文献3）— 从 support/attack 扩展到 partially support/attack
6. **论证图可视化**（文献3）— 前端展示论辩关系图
7. **NEI（证据不足）分类**（文献1）— 处理当前无法判定的情况
8. **表格证据支持**（文献1）— 扩展到结构化数据

---

## 参考文献

1. Aly, R., Guo, Z., Schlichtkrull, M., Thorne, J., Vlachos, A., et al. (2021). *The Fact Extraction and VERification Over Unstructured and Structured information (FEVEROUS) Shared Task*. FEVER Workshop @ EMNLP 2021.

2. Curtis, T. L., Touzel, M. P., Garneau, W., et al. (2025). *Veracity: An Open-Source AI Fact-Checking System*. IJCAI-25 Demonstrations Track.

3. Wang, X., Cabrio, E., Villata, S. (2025). *SAFE: Structured Argumentation for Fact-checking with Explanations*. IJCAI-25 Demonstrations Track.

4. Trinh, T., Nguyen, M., Hy, T-S. (2025). *Towards Robust Fact-Checking: A Multi-Agent System with Advanced Evidence Retrieval*. arXiv:2506.17878.
