---
name: automation-level-assessment
description: 基于 Parasuraman 四阶段模型评估任务的自动化级别，识别自动化偏见和脱离回路风险。Triggers on questions about automation design, human-AI task allocation, or automation risks.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/automation-sociotechnical/parasuraman.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/automation-bias.md
  - ../../domains/cognitive-systems/concepts/out-of-the-loop.md
tags:
  - automation-assessment
  - automation-bias
  - human-automation-interaction
  - automation-paradox
---

# 自动化级别评估 · Automation Level Assessment

## 一句话功能

使用 Parasuraman 的四阶段信息处理模型，系统评估任务中每个阶段的自动化级别，并识别自动化偏见、脱离回路和技能退化等风险——回答"哪些部分应该自动化？自动化到什么程度？"

## 何时使用

- 设计或评估人机混合系统时
- 决定人与 AI 之间的任务分配时
- 评估现有自动化系统的风险
- 分析自动化事故（如自动驾驶事故）
- 设计从手动到全自动的过渡方案

## 何时不使用

- 全自动系统无需人的参与（无任务分配问题）
- 使用计算器进行简单计算（无评估必要）
- 纯人工操作（无自动化成分）

## 理论基础

- 来源思想家：[帕拉休拉曼 Parasuraman](../../domains/cognitive-systems/schools/automation-sociotechnical/parasuraman.md)
- 来源概念：[自动化偏见](../../domains/cognitive-systems/concepts/automation-bias.md)、[脱离回路](../../domains/cognitive-systems/concepts/out-of-the-loop.md)
- 关键文献：Parasuraman, R. & Riley, V. "Humans and Automation." *Human Factors* 39(2), 1997.

## 操作流程

### Step 1：任务分解

将目标任务分解为四个信息处理阶段：

| 阶段 | 描述 | 示例（医疗诊断） |
|---|---|---|
| 1. **信息获取**（Information Acquisition） | 获取和感知信息 | 查看患者影像、读取化验结果 |
| 2. **信息分析**（Information Analysis） | 整合信息、识别模式 | 将影像特征与疾病模式匹配 |
| 3. **决策选择**（Decision Selection） | 从选项中做出选择 | 确定最可能的诊断和治疗方案 |
| 4. **行动实施**（Action Implementation） | 执行所选择的行动 | 开具处方、实施手术 |

### Step 2：四阶段自动化级别评估

对每个阶段，评估当前或计划的自动化级别（1-10 级）：

| 级别 | 描述 | 含义 |
|---|---|---|
| 1 | 全人工 | 人完全手动执行 |
| 2-3 | 计算机辅助 | 计算机提供建议，人做决定 |
| 4-5 | 共享控制 | 人和计算机共同完成 |
| 6-7 | 监督控制 | 计算机执行，人监督 |
| 8-9 | 管理例外 | 计算机自主执行，仅在例外时通知人 |
| 10 | 全自动 | 计算机完全自主 |

### Step 3：自动化风险分析

对每个阶段评估三种风险：

**自动化偏见（Automation Bias）**：
- 人过度依赖自动化建议，忽略了与之矛盾的正确信息
- 风险条件：自动化被感知为"权威"、时间压力高、人疲劳
- 缓解：要求操作者先独立判断再看自动化建议

**脱离回路（Out-of-the-Loop, OOTL）**：
- 人长时间不参与决策，当需要干预时无法有效接管
- 风险条件：高自动化级别 + 低参与度 + 紧急干预需求
- 缓解：定期的手动任务、情境意识训练

**技能退化（Skill Degradation）**：
- 长期不使用某项技能导致技能退化
- 风险条件：持续的高自动化 + 无定期手动练习
- 缓解：定期的手动操作训练

### Step 4：信任校准建议

基于风险分析，提出自动化设计建议：
- **适当降低自动化级别**：在高风险阶段保留人的参与
- **设计校准机制**：让操作者理解自动化的能力和限制
- **设计干预窗口**：确保人可以在需要时有效地接管
- **设计定期互动**：防止脱离回路和技能退化

## 完整示例

**输入场景**：
> 评估一个 AI 辅助医学影像诊断系统的自动化级别和风险。

**Skill 应用过程**：

1. **任务分解**：
   - 信息获取：CT 扫描数据
   - 信息分析：AI 标记可疑区域
   - 决策选择：AI 给出初步诊断建议
   - 行动实施：医生确定最终诊断

2. **自动化级别评估**：
   - 信息获取：级别 9（自动采集，异常时通知）
   - 信息分析：级别 6（AI 标记可疑区域，医生审核）
   - 决策选择：级别 4（AI 建议 + 医生判断）
   - 行动实施：级别 1（医生完全手动）

3. **风险分析**：
   - 自动化偏见（高风险）：医生可能直接采纳 AI 建议而不独立判断
   - OOTL（中风险）：信息分析自动化程度高，医生可能错过 AI 遗漏的异常
   - 技能退化（中风险）：长期依赖 AI 标记可能降低医生独立识别的能力

4. **建议**：
   - 要求医生先独立查看影像再看 AI 标记
   - 保留 AI 未标记区域的随机抽查机制
   - 定期进行无 AI 辅助的诊断练习

**输出**：
> AI 辅助影像诊断系统的信息分析阶段自动化级别为 6 级（监督控制）。主要风险是自动化偏见——医生可能直接信任 AI 标记而忽略 AI 未标记的异常。建议实施"先独立判断再查看 AI 建议"的工作流程，并定期进行无 AI 的诊断练习以维持技能水平。

## 反例（误用）

**误用场景**：
> 对日常使用的计算器进行自动化级别评估。

**正确做法**：计算器是完全自动化的计算工具，无任务分配问题，无自动化偏见风险。自动化级别评估适用于涉及人机交互、需要考虑信任和技能维持的复杂系统。

## 关联条目

- 思想家：[帕拉休拉曼 Parasuraman](../../domains/cognitive-systems/schools/automation-sociotechnical/parasuraman.md)
- 概念：[自动化偏见](../../domains/cognitive-systems/concepts/automation-bias.md)
- 概念：[脱离回路](../../domains/cognitive-systems/concepts/out-of-the-loop.md)
- 相关 Skill：[人 AI 协作设计](../human-ai-teaming/SKILL.md)
