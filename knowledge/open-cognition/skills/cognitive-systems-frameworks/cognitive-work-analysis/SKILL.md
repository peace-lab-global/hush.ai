---
name: cognitive-work-analysis
description: 分析复杂工作领域中人的认知需求和系统约束，基于 Rasmussen 的抽象层级和 SRK 模型。Triggers on requests to analyze work systems, design interfaces, or understand cognitive demands in complex environments.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/joint-cognitive-system.md
  - ../../domains/cognitive-systems/concepts/situation-awareness.md
tags:
  - cognitive-work-analysis
  - abstraction-hierarchy
  - SRK
  - system-design
---

# 认知工作分析 · Cognitive Work Analysis (CWA)

## 一句话功能

用五层分析框架系统地理解复杂工作领域中的认知需求、约束和设计空间——回答"这个工作领域需要什么样的认知？如何设计系统来支持它？"

## 何时使用

- 需要分析复杂工作领域（医疗、航空、核安全、自动驾驶等）的认知需求
- 设计或评估人机界面时
- 理解操作者在异常/紧急情况下的认知行为时
- 进行工作系统的安全分析时

## 何时不使用

- 简单的重复性任务（用传统任务分析即可）
- 不涉及复杂认知的工作领域
- 需要快速原型而非系统分析的场景

## 理论基础

- 来源思想家：[拉斯穆森 Rasmussen](../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md)
- 来源概念：[联合认知系统](../../domains/cognitive-systems/concepts/joint-cognitive-system.md)
- 关键文献：Vicente, K. *Cognitive Work Analysis*. Lawrence Erlbaum, 1999.

## 操作流程

### Step 1：工作领域分析（Work Domain Analysis）
用**抽象层级**描述工作领域：
1. **功能目的**：系统存在的目的和约束（为什么要做？）
2. **价值/优先性**：成功运作的衡量标准（什么算好？）
3. **一般化功能**：系统的功能流程（做什么？）
4. **物理功能**：实现功能所需的物理过程（怎么做？）
5. **物理形式**：具体的物理组件和属性（用什么做？）

**提问范式**：
- "这个系统存在的根本目的是什么？"
- "什么是好的运作？什么标准定义了成功？"
- "为了实现这些功能，需要什么物理过程？"

### Step 2：控制任务分析（Control Task Analysis）
识别系统必须完成的控制任务：
- 在每种系统状态下，操作者需要做什么？
- 信息流和控制流如何组织？
- 使用决策梯子（Decision Ladder）分析信息处理过程

### Step 3：策略分析（Strategies Analysis）
分析操作者实际使用的认知策略：
- SRK 三层次——哪些是技能型（自动）、规则型（遵循规程）、知识型（需要分析）？
- 在不同条件（正常/异常/紧急）下，策略如何切换？
- 专家和新手的策略差异在哪里？

### Step 4：社会-组织分析（Social-Organizational Analysis）
分析社会结构对认知的支持/约束：
- 谁负责什么？劳动分工如何？
- 信息如何在团队成员之间流动？
- 团队如何建立共享的态势感知？

### Step 5：工作者能力分析（Worker Competencies Analysis）
分析操作者需要的认知能力：
- 需要哪些知识？（领域知识、系统知识、规程知识）
- 需要哪些技能？（感知、判断、操作）
- 培训如何支持这些能力的发展？

## 完整示例

**输入场景**：
> 医院急诊科的医疗团队正在处理一名胸痛患者。需要分析这个工作领域的认知需求。

**Skill 应用过程**：

1. **工作领域分析**：
   - 功能目的：挽救生命、缓解症状、准确诊断
   - 价值/优先性：时间效率、诊断准确性、患者安全
   - 一般化功能：分诊→评估→检查→诊断→治疗→监测
   - 物理功能：心电监测、血压测量、血液检验
   - 物理形式：监护仪、检验设备、电子病历系统

2. **控制任务分析**：
   - 分诊阶段：快速判断严重程度（STEMI vs 非 STEMI）
   - 关键信息：心电图 ST 段、肌钙蛋白、症状持续时间

3. **策略分析**：
   - 经验丰富的医生：技能型（直接识别 ECG 模式）→ 规则型（遵循胸痛流程）
   - 新手医生：知识型（需要逐步分析 ECG 的每个波形）

4. **社会-组织分析**：
   - 分诊护士→急诊医生→心内科医生的信息传递链
   - 电子病历系统是否支持信息连续传递？

5. **工作者能力分析**：
   - 核心能力：ECG 模式识别、快速鉴别诊断、团队沟通

**输出**：
> 急诊胸痛处理是一个典型的高时间压力、高不确定性的认知工作领域。系统设计应支持：(1) 信息的连续可视化以减少信息传递损失；(2) ECG 模式的自动标注以支持新手的知识型推理向规则型转变；(3) 团队共享的态势感知显示。

## 反例（误用）

**误用场景**：
> 在分析简单的数据录入工作时使用完整的五层 CWA。

**正确做法**：简单的重复性工作使用传统任务分析（Task Analysis）即可——CWA 的价值在于分析复杂、不确定、高风险的认知工作。

## 关联条目

- 思想家：[拉斯穆森](../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md)
- 概念：[联合认知系统](../../domains/cognitive-systems/concepts/joint-cognitive-system.md)
- 概念：[态势感知](../../domains/cognitive-systems/concepts/situation-awareness.md)
- 相关 Skill：[态势感知诊断](../situation-awareness-diagnosis/SKILL.md)
