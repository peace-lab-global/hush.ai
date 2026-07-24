---
name: pleasure-calculus
description: 苦乐计算法（hedonic calculus）用于量化选项的道德价值。通过七个维度评估不同行动的快乐/痛苦产出，判断何者符合功利原则。Triggers on 需要在多个选项间做道德权衡、评估政策/行为的成本效益、或分析功利主义论证的场景。
domain: ethics-politics
linked_thinker: ../domains/ethics-politics/schools/consequentialism/bentham.md
linked_concepts:
  - ../domains/ethics-politics/concepts/pleasure.md
tags:
  - 功利主义
  - 结果主义
  - 决策分析
  - 政策评估
---

# 苦乐计算 · Pleasure Calculus

## 一句话功能

将功利原则（最大多数人的最大幸福）转化为可操作的多维评估工具，用于比较不同行动的道德价值。

## 何时使用

- 用户需要比较两个或多个行动方案的道德优劣
- 政策制定中需要成本效益分析
- 评估某项改革是否符合功利原则
- 分析功利主义论证的结构

## 何时不使用

- 问题涉及不可让渡的权利（此时功利计算可能掩盖根本的不正义）
- 缺乏足够的经验数据支撑评估
- 需要价值判断而非描述性分析时
- 情境涉及对少数群体的压迫（功利计算可能成为多数暴政的工具）

## 理论基础

- 来源思想家：[边沁 Jeremy Bentham](../domains/ethics-politics/schools/consequentialism/bentham.md)
- 来源概念：[功利 Pleasure](../domains/ethics-politics/concepts/pleasure.md)
- 关键文献：Bentham, *Principles of Morals and Legislation* Ch. I

## 操作流程

### Step 1：识别利益相关方

列出所有受该行动影响的群体或个人，区分直接相关方与间接受影响方。
**提问范式**：
- "这个决定会影响哪些群体？"
- "是否有群体在决策过程中缺席但会受到实际影响？"

### Step 2：识别快乐与痛苦来源

对每个利益相关方，列出该行动产生的快乐与痛苦。
**提问范式**：
- "这个决定会让每个群体感受到哪些快乐/好处？"
- "会产生哪些痛苦/成本？"

### Step 3：七维计算

使用边沁的七个维度对每个快乐/痛苦进行评估：

| 维度 | 含义 | 打分（1-5） |
|---|---|---|
| 强度 intensity | 感受的强烈程度 |  |
| 持久度 duration | 感受持续的时间 |  |
| 确实性 certainty | 感受发生的确定程度 |  |
| 远近度 propinquity | 感受发生的时间远近 |  |
| 丰度 fecundity | 带来后续快乐/痛苦的可能性 |  |
| 纯度 purity | 不伴随相反感受的程度 |  |
| 范围 extent | 受影响的人数 |  |

### Step 4：综合评估

将每个选项的快乐总分与痛苦总分相减，得出去权值（net value）。
**提问范式**：
- "哪个选项的去权快乐值最高？"
- "是否有选项虽然总体快乐更高，但存在无法弥补的根本伤害？"

## 完整示例

**输入场景**：
> 某城市面临公共交通补贴削减问题。有两个方案：(A) 削减补贴，票价上涨30%，财政节省用于医疗；(B) 维持现有补贴，票价不变，但削减公共图书馆服务。

**Skill 应用过程**：
1. **识别利益相关方**：公交乘客、低收入通勤者、财政纳税人、医疗系统受益者、图书馆使用者
2. **识别快乐与痛苦**：
   - 方案A：乘客（痛苦：票价上涨）、纳税人（快乐：税收减少用于医疗）、医疗受益者（快乐：更好医疗）
   - 方案B：乘客（快乐：票价不变）、图书馆用户（痛苦：服务削减）
3. **七维计算**（示例）：
   - 方案A低收入通勤者：持久度(4)×远近度(5)×范围(4)...；方案B图书馆用户：持久度(3)×范围(3)...
4. **综合评估**：方案A的痛苦更集中于低收入通勤者，方案B的痛苦更分散但强度较低

**输出**：
> 功利分析结论：方案A可能在总体数值上更优（医疗覆盖面更广），但需警惕对最脆弱群体的过度冲击。若要符合真正的功利原则，需确保节省的医疗资源能有效覆盖因票价上涨而受损的群体。

## 反例（误用）

**误用场景**：
> 当某公司面临裁员决定：方案A裁减10%员工（痛苦集中但程度高），方案B全员降薪20%（痛苦分散但持续时间长）。若简单使用苦乐计算，可能倾向方案B（总体痛苦值更低），但这掩盖了对少数人的严重不公——他们承担了不成比例的痛苦。

**正确做法**：在此类权利敏感情境中，应先用[定言命令检验](../categorical-imperative/SKILL.md)确认没有把人不当手段使用，再考虑功利计算。

## 关联条目

- 思想家：[边沁](../domains/ethics-politics/schools/consequentialism/bentham.md)、[密尔](../domains/ethics-politics/schools/consequentialism/mill.md)
- 概念：[功利 Pleasure](../domains/ethics-politics/concepts/pleasure.md)
- 相关Skill：[无知之幕分析](./veil-of-ignorance-analysis/SKILL.md)