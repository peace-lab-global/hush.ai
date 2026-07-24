---
name: human-error-analysis
description: 分析复杂系统中人为错误的类型和根因，基于 Rasmussen 的 SRK 模型和 Reason 的瑞士奶酪模型。Triggers on requests to analyze human errors, investigate accidents, or understand why people make mistakes in complex systems.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/joint-cognitive-system.md
tags:
  - human-error
  - safety
  - accident-analysis
  - SRK
---

# 人为错误分析 · Human Error Analysis

## 一句话功能

系统分析复杂系统中人为错误的类型、传播路径和系统性根因——超越"人的失误"的简单归因，发现设计层面的问题。

## 何时使用

- 分析事故/事件的人为因素
- 理解操作者为什么"犯错"
- 设计防错（error-proof）系统
- 评估安全管理系统的有效性

## 何时不使用

- 错误是故意的违规（用纪律/管理框架）
- 纯技术问题（不涉及人为因素）
- 需要法律归因而非系统分析

## 理论基础

- 来源思想家：[拉斯穆森 Rasmussen](../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md)、[诺曼 Norman](../../domains/cognitive-systems/schools/cognitive-engineering/norman.md)
- 关键文献：Reason, J. *Human Error*. Cambridge University Press, 1990.

## 操作流程

### Step 1：错误分类（SRK 模型）
判断错误发生在哪个认知层次：
- **技能型错误（Slips/Lapses）**：执行自动化操作时的失误
  - 滑误（Slip）：意图正确但执行错误（按错按钮）
  - 遗漏（Lapse）：忘记某个步骤
  - 原因：注意力分散、程序干扰
- **规则型错误（Mistakes - Rule-based）**：应用了错误的规则
  - 原因：规则过时、规则冲突、情境不匹配
- **知识型错误（Mistakes - Knowledge-based）**：在未知情况下分析推理出错
  - 原因：心智模型不完整、信息不足、认知负荷过高

### Step 2：防御层分析（瑞士奶酪模型）
检查系统中的多层防御：
- 有哪些防御层？（培训、规程、检查、自动化监控、物理安全装置）
- 每一层的"孔洞"在哪里？（在什么条件下会失效？）
- 多层防御的孔洞是否恰好对齐？（导致错误穿透所有防御）

### Step 3：组织因素分析
追溯错误的组织根因：
- **管理决策**：哪些管理决策创造了错误条件？（人员配置、培训投入、设备采购）
- **组织文化**：文化是否鼓励报告错误？还是隐藏错误？
- **工作条件**：疲劳、时间压力、沟通不畅、界面复杂

### Step 4：设计改进建议
- **技能型错误**：防呆设计、强制功能、确认步骤
- **规则型错误**：更新规程、改善情境识别、提供决策支持
- **知识型错误**：改善界面信息呈现、培训心智模型、限制系统复杂性
- **组织层面**：改善报告文化、增加安全投资、优化人员配置

## 完整示例

**输入场景**：
> 护士在给患者注射时选错了药物。需要分析这个错误。

**Skill 应用过程**：

1. **错误分类**：
   - 两种药物外观相似、存放位置相邻
   - 护士在繁忙中拿错了药物
   - 分类：**技能型错误（Slip）**——意图正确（要给正确的药），但执行错误

2. **防御层分析**：
   - 防御层 1：药物存放位置 → 孔洞：相似药物放在一起
   - 防御层 2：药物标签 → 孔洞：标签字体小、颜色相似
   - 防御层 3：核对流程 → 孔洞：繁忙时跳过核对
   - 防御层 4：条形码扫描 → 孔洞：该药物未启用条码系统
   - 孔洞对齐 → 错误穿透所有防御

3. **组织因素**：
   - 护士/患者比例过高（管理决策）
   - 条码系统未覆盖所有药物（投资决策）
   - 错误报告文化薄弱（文化因素）

4. **设计改进**：
   - 相似药物分区存放 + 颜色编码（消除技能型错误条件）
   - 全面推行条码扫描系统（增加有效防御层）
   - 合理配置护士/患者比例（解决组织根因）

**输出**：
> 这不是"护士粗心"——是系统设计创造了错误条件。技能型错误在繁忙环境中不可避免，关键在于系统防御层是否足够有效。

## 反例（误用）

**误用场景**：
> 把所有错误都归为"人的失误"并要求"加强培训"——这是最无效的安全改进策略。

**正确做法**：区分错误类型——技能型错误需要设计改进，不是培训。

## 关联条目

- 思想家：[拉斯穆森](../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md)、[诺曼](../../domains/cognitive-systems/schools/cognitive-engineering/norman.md)
- 概念：[联合认知系统](../../domains/cognitive-systems/concepts/joint-cognitive-system.md)
- 相关 Skill：[韧性评估](../resilience-assessment/SKILL.md)
