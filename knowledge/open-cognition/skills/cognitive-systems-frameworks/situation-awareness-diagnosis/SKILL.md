---
name: situation-awareness-diagnosis
description: 诊断操作者在动态系统中的态势感知（SA）水平，基于 Endsley 的三级模型。Triggers on requests to assess SA, diagnose why operators lost awareness, or design for better situation awareness.
domain: cognitive-systems
linked_thinker: null
linked_concepts:
  - ../../domains/cognitive-systems/concepts/situation-awareness.md
  - ../../domains/cognitive-systems/concepts/mental-model.md
tags:
  - situation-awareness
  - dynamic-systems
  - operator-performance
---

# 态势感知诊断 · Situation Awareness Diagnosis

## 一句话功能

用三级模型（感知→理解→预测）诊断操作者的态势感知水平，找到 SA 丧失的原因，提出改善建议。

## 何时使用

- 分析操作者（飞行员、医生、驾驶员）在特定事件中"为什么没注意到"
- 评估界面设计是否支持 SA
- 设计团队共享 SA 的机制
- 分析事故中的人为因素

## 何时不使用

- 问题不在感知/理解而在决策/执行
- 需要评估系统整体韧性而非实时认知状态

## 理论基础

- 来源概念：[态势感知](../../domains/cognitive-systems/concepts/situation-awareness.md)
- 关键文献：Endsley, M. "Toward a Theory of Situation Awareness in Dynamic Systems." *Human Factors* 37(1), 1995.

## 操作流程

### Step 1：确定 SA 需求
分析这个工作领域需要什么样的 SA：
- 关键的 SA 元素有哪些？（需要感知什么？理解什么？预测什么？）
- 环境是静态还是动态的？（变化越快，SA 需求越高）
- 是个人 SA 还是团队 SA？

### Step 2：诊断 SA 水平
对每个关键 SA 元素，评估当前水平：
- **Level 1（感知）**：操作者是否感知到了这个元素？
  - 如果未感知→检查：信息是否呈现？注意力是否被吸引？
- **Level 2（理解）**：操作者是否理解这个元素的意义？
  - 如果不理解→检查：心智模型是否准确？经验是否足够？
- **Level 3（预测）**：操作者是否能预测未来状态？
  - 如果不能预测→检查：是否有足够的因果关系知识？

### Step 3：识别 SA 丧失原因
常见的 SA 丧失原因：
- 注意力分散（分心任务、警报疲劳）
- 信息过载（太多数据，关键信息被淹没）
- 心智模型错误（对系统运作方式的错误理解）
- 自满（在正常情况下 SA 退化）
- 团队沟通断裂（共享 SA 丧失）

### Step 4：提出改善建议
- **Level 1 改善**：优化信息呈现、减少干扰、突出关键信息
- **Level 2 改善**：培训心智模型、提供系统状态的综合显示
- **Level 3 改善**：提供预测工具、培训因果关系理解
- **团队 SA**：建立共享情境显示、标准化沟通协议

## 完整示例

**输入场景**：
> 自动驾驶车辆在高速公路上突然变道，驾驶员未能及时介入。需要分析驾驶员的 SA 丧失原因。

**Skill 应用过程**：

1. **SA 需求**：驾驶员需要感知车辆位置/速度/周围车辆（L1），理解自动驾驶状态和能力边界（L2），预测何时需要接管（L3）

2. **SA 水平诊断**：
   - Level 1：驾驶员在看手机——未感知到车辆开始变道 ❌
   - Level 2：驾驶员不清楚自动驾驶在何种条件下会自主变道 ❌
   - Level 3：驾驶员未预测到需要接管的时间点 ❌

3. **SA 丧失原因**：
   - 注意力被手机吸引（分心）
   - 对自动驾驶能力边界的心智模型不准确
   - 系统未提供清晰的"即将自主变道"预警

4. **改善建议**：
   - L1：变道前 3 秒的听觉+触觉预警
   - L2：启动时教育用户自动驾驶的能力边界
   - L3：显示"预计 N 秒后需要接管"的倒计时

**输出**：
> 驾驶员 SA 在三个级别均丧失。根本原因是系统未能维持驾驶员对自动驾驶状态的 SA——需要改进预警机制和用户教育。

## 反例（误用）

**误用场景**：
> 把所有"没注意到"都归因于 SA 丧失——可能是感知能力问题（视力）而非认知问题。

**正确做法**：先排除感知能力问题，再聚焦认知层面的 SA。

## 关联条目

- 概念：[态势感知](../../domains/cognitive-systems/concepts/situation-awareness.md)
- 概念：[心智模型](../../domains/cognitive-systems/concepts/mental-model.md)
- 相关 Skill：[认知工作分析](../cognitive-work-analysis/SKILL.md)
