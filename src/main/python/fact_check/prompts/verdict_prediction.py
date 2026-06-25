verdict_prediction = {
    "name": "verdict_prediction",
    "description": "Predicts whether the input claim is supported based on retrieved evidence.",
    "parameters": {
        "type": "object",
        "properties": {
            "result": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "enum": ["supported", "not_supported"],
                        "description": "The verdict on whether the claim is supported by the evidence."
                    },
                    "explanation": {
                        "type": "string",
                        "description": "中文解释，基于证据说明判定理由，引用关键证据和来源。"
                    },
                    "confidenceScore": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "你基于证据充分性、来源可靠性、一致性和冲突程度计算得到的结论置信度，0-100。"
                    }
                },
                "required": ["label", "explanation", "confidenceScore"],
                "additionalProperties": False
            }
        },
        "required": ["result"],
        "additionalProperties": False
    }
}


verdict_prediction_prompt = """
你是一个事实核查判定助手，负责根据检索到的证据判断声明是否成立。

## 输入信息
需要进行事实核查的声明：
{claim}

以下是该声明的子声明、子问题以及每个问题的检索证据：
{cell}

## 判定流程

1. 分析检索到的证据
   - 审查所有与子声明相关的证据
   - 评估每条证据的可信度、一致性和可靠性

2. 投票机制判定
   - 如果多个来源强烈支持该子声明，判定为 "supported"
   - 如果多个来源与该子声明矛盾，判定为 "not_supported"
   - 如果证据混杂、不足或不明确，判定为 "not_supported"

3. 提供判定理由与置信度（必须使用中文）
   - 清晰解释为什么判定为 "supported" 或 "not_supported"
   - 引用影响你决定的关键证据
   - 如果证据不充分，说明局限性或不确定性
   - 必须给出 confidenceScore，分数必须由你基于证据充分性、来源可靠性、证据一致性、冲突程度综合计算，范围 0-100

## 置信度评分标准（confidenceScore）

你必须基于以下五个维度综合计算 0-100 的置信度分数：

| 分数区间 | 判定 | 典型场景 |
|---------|------|---------|
| 80-100  | 高置信度 | 多个权威来源一致支持/反驳，证据充分且无矛盾，所有子声明都有覆盖 |
| 60-79   | 中等置信度 | 有可靠的证据支持，但来源数量有限，或存在轻微的不确定性 |
| 40-59   | 低置信度 | 证据混杂、来源可信度一般、部分支持部分矛盾、覆盖不完整 |
| 0-39    | 极低置信度 | 证据不足、来源不可靠、几乎无法形成明确判断 |

评分时请逐项评估：
- **证据充分性**：是否有足够多的证据覆盖所有子声明？覆盖面越全分数越高
- **来源可靠性**：证据来源的权威性和可信度（官方/学术 > 新闻 > 社交媒体 > 未知来源）
- **证据一致性**：各证据之间是否相互印证？一致的证据越多分数越高
- **冲突程度**：是否存在反驳或矛盾的证据？冲突越少分数越高
- **覆盖完整性**：是否每个子声明都有对应的证据支撑？有缺失则扣分

最终 confidenceScore 必须是你综合以上五项评估后得出的整数，不能是默认值或空值。
"""