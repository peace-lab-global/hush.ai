---
name: cognitive-task-analysis
description: 通过深度访谈、观察和知识提取，挖掘专家的隐性认知策略和决策过程。Triggers on requests to understand expert knowledge, extract decision strategies, or design training.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/naturalistic-decision/klein.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/macrocognition.md
  - ../../domains/cognitive-systems/concepts/mental-model.md
tags:
  - cognitive-task-analysis
  - expertise
  - knowledge-elicitation
  - expert-cognition
---

# 认知任务分析 · Cognitive Task Analysis (CTA)

## 一句话功能

通过系统化的知识提取方法，挖掘专家在复杂任务中的隐性认知策略、心智模型和决策过程——揭示"专家知道什么"和"专家怎么想"。

## 何时使用

- 需要理解领域专家的隐性知识和决策策略
- 设计专家系统的知识库
- 设计培训课程或模拟训练方案
- 评估复杂系统的认知需求
- 分析为什么新手和专家的表现存在差距

## 何时不使用

- 简单的重复性任务（无专家知识可提取）
- 标准化的流程操作（已有明确的 SOP）
- 用户体验调研（使用 UX 研究方法）

## 理论基础

- 来源思想家：[克莱因 Klein](../../domains/cognitive-systems/schools/naturalistic-decision/klein.md)
- 来源概念：[宏观认知](../../domains/cognitive-systems/concepts/macrocognition.md)、[心智模型](../../domains/cognitive-systems/concepts/mental-model.md)
- 关键文献：Crandall, B. et al. *Working Minds: A Practitioner's Guide to Cognitive Task Analysis*. MIT Press, 2006.

## 操作流程

### Step 1：任务识别与专家选择

1. **界定任务范围**：明确要分析的认知任务是什么
2. **选择专家**：选择在该领域有 10+ 年经验、公认的高水平表现者
3. **选择对照组**：如有需要，选择中等水平的执行者进行对比

**关键问题**：
- 这个任务的关键认知挑战是什么？
- 谁是这个领域的公认专家？
- 专家和新手之间的差距在哪里？

### Step 2：知识提取

使用多种方法提取专家知识：

**关键事件技术（Critical Incident Technique）**：
- 请专家描述具体的成功/失败案例
- 追问："你当时注意到了什么？""你为什么做出那个决定？"
- 关注意外、转折点和决策节点

**概念图（Concept Mapping）**：
- 请专家画出他们对任务领域的概念关系
- 揭示心智模型的结构

**概念化口头报告（Conceptual Verbal Protocol）**：
- 让专家在执行任务时"出声思考"
- 记录认知策略和决策点

**时间线访谈（Timeline Interview）**：
- 按时间顺序梳理任务过程
- 在每个节点追问认知活动

### Step 3：认知需求分析

从提取的知识中识别：
- **关键决策点**：哪些决策最依赖专家判断？
- **模式识别需求**：专家识别哪些模式？
- **心理模型**：专家如何理解和表征任务领域？
- **元认知策略**：专家如何监控和调节自己的认知过程？
- **困难情境**：什么条件下认知需求最高？

### Step 4：知识表示

将提取的知识整理为结构化表示：
- **决策树**：专家的决策路径
- **概念图**：专家的心智模型结构
- **认知策略表**：不同情境下的认知策略
- **情境-行动规则**：在 X 情境下，专家做 Y

### Step 5：验证与应用

1. **专家验证**：请专家审查结果，确认准确性
2. **对比验证**：与中等水平执行者对比，确认差异
3. **应用设计**：基于分析结果设计培训、界面或决策支持系统

## 完整示例

**输入场景**：
> 需要理解经验丰富的放射科医生如何在 CT 影像中检测早期肺结节——以便设计 AI 辅助诊断系统。

**Skill 应用过程**：

1. **任务识别**：在胸部 CT 影像中识别小于 6mm 的肺结节
2. **知识提取**（关键事件 + 口头报告）：
   - 专家描述："我会先快速扫一遍整个肺野，注意任何不规则密度...当看到疑似区域时，我会回看上下层面确认是否是血管断面..."
   - 关键发现：专家使用"排除法"——先看是否是血管、支气管等正常结构，只有排除这些后才考虑结节
3. **认知需求分析**：
   - 关键决策点：血管断面 vs 真结节的区分
   - 模式识别：结节的灰度、边缘、形状特征
   - 心理模型：正常肺部的三维结构表征
4. **知识表示**：决策路径图 + 特征识别规则表
5. **验证**：请 3 位资深放射科医生审查

**输出**：
> 放射科医生的肺结节检测是一个典型的宏观认知过程——结合了模式识别（技能型）、排除推理（规则型）和三维空间想象（知识型）。AI 辅助系统应重点关注血管断面 vs 真结节的区分，并在关键决策点提供支持而非替代。

## 反例（误用）

**误用场景**：
> 对银行柜员的日常存取款操作进行完整的认知任务分析。

**正确做法**：存取款操作是标准化流程——使用传统任务分析（Task Analysis）记录步骤即可。CTA 适用于需要专家判断的复杂认知任务，而非标准化的重复操作。

## 关联条目

- 思想家：[克莱因 Klein](../../domains/cognitive-systems/schools/naturalistic-decision/klein.md)
- 概念：[宏观认知](../../domains/cognitive-systems/concepts/macrocognition.md)
- 概念：[心智模型](../../domains/cognitive-systems/concepts/mental-model.md)
- 相关 Skill：[自然决策分析](../naturalistic-decision-analysis/SKILL.md)
