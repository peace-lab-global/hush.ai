---
name: naturalistic-decision-analysis
description: 分析专家在时间压力、高不确定性下的真实决策模式，基于 Klein 的识别启动决策（RPD）模型。Triggers on requests to understand expert decision-making, analyze decisions under time pressure, or evaluate intuitive judgment.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/naturalistic-decision/klein.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/situation-awareness.md
tags:
  - naturalistic-decision
  - RPD
  - expertise
  - intuition
---

# 自然决策分析 · Naturalistic Decision Analysis

## 一句话功能

分析专家在真实世界（时间压力、信息不完整、高风险）中如何做决策——识别其模式匹配、心理模拟和情境评估过程。

## 何时使用

- 分析专家（医生、消防员、指挥官、交易员）在压力下的决策
- 理解"直觉决策"的实际机制
- 设计专家决策支持系统
- 培训新手的决策能力

## 何时不使用

- 决策环境高度结构化（用理性分析模型即可）
- 缺乏足够信息判断决策过程
- 需要规范性建议（"应该怎么做"）而非描述性分析

## 理论基础

- 来源思想家：[克莱因 Klein](../../domains/cognitive-systems/schools/naturalistic-decision/klein.md)
- 来源概念：[态势感知](../../domains/cognitive-systems/concepts/situation-awareness.md)
- 关键文献：Klein, G. *Sources of Power*. MIT Press, 1998.

## 操作流程

### Step 1：情境评估
分析决策者面对的情境特征：
- **时间压力**：有多少时间做决策？
- **信息完整性**：有哪些信息？缺什么？
- **风险水平**：决策后果的严重性？
- **不确定性**：情况是否在变化？未来是否可预测？
- **经验水平**：决策者在这个领域有多少经验？

### Step 2：识别决策模式
判断决策者使用了哪种模式：

**识别启动决策（RPD）**——专家的默认模式：
1. 当前情境匹配哪个已知模式？（情境评估）
2. 这个模式通常对应什么行动？（模式匹配）
3. 在心理上模拟这个行动——可行吗？（心理模拟）
4. 如果可行→执行；如果不可行→调整方案或寻找新模式

**分析决策**——在陌生情境下的备选模式：
- 逐一比较多个选项的利弊
- 计算期望效用
- 选择最优方案

### Step 3：评估直觉的可靠性
根据 Klein-Kahneman 共识，检查两个条件：
- **有规律的环境**：这个领域的因果关系是否稳定可学习？
- **充分的练习和反馈**：决策者是否积累了足够的经验和反馈？
- 两个条件都满足→直觉可靠；不满足→需要分析补充

### Step 4：提出改进建议
- 新手：增加案例学习以积累模式库
- 中级：增加情境变化的练习以提升心理模拟能力
- 专家：关注"黑天鹅"情境——经验可能误导的罕见事件

## 完整示例

**输入场景**：
> 一位有 15 年经验的急诊医生在患者到达后 30 秒内判断"这是主动脉夹层"，直接启动紧急手术流程。

**Skill 应用过程**：

1. **情境评估**：极高时间压力、信息不完整（仅有主诉和初步体征）、高风险（误诊=死亡）

2. **决策模式**：RPD
   - 情境评估：胸痛+撕裂感+双臂血压差
   - 模式匹配：匹配"主动脉夹层"模式
   - 心理模拟：紧急 CT 确认可行→启动手术流程
   - 没有逐一比较所有胸痛原因（不是分析决策）

3. **直觉可靠性**：
   - 有规律的环境：✅ 主动脉夹层有典型的症状模式
   - 充分的练习和反馈：✅ 15 年经验，见过大量类似案例
   - 结论：直觉可靠

4. **改进建议**：对年轻医生进行案例培训，积累"主动脉夹层"的模式库

**输出**：
> 这是一次典型的 RPD 决策——专家通过模式匹配在 30 秒内识别出罕见但致命的疾病。其可靠性来自 15 年经验和主动脉夹层的典型症状模式。

## 反例（误用）

**误用场景**：
> 在低经验决策者身上套用 RPD 分析——新手没有足够的模式库，他们的"直觉"不是 RPD，而是猜测。

**正确做法**：对新手使用分析决策支持——提供清单、决策树、比较框架。

## 关联条目

- 思想家：[克莱因](../../domains/cognitive-systems/schools/naturalistic-decision/klein.md)
- 概念：[态势感知](../../domains/cognitive-systems/concepts/situation-awareness.md)
- 相关 Skill：[意义建构引导](../sensemaking-guidance/SKILL.md)
