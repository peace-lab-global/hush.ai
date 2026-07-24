---
name: human-ai-teaming
description: 设计人与 AI Agent 的协作认知系统，优化功能分配、信任校准和交接机制。Triggers on human-AI collaboration design, AI agent integration, or joint cognitive system design.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/automation-sociotechnical/bainbridge.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/joint-cognitive-system.md
  - ../../domains/cognitive-systems/concepts/automation-bias.md
  - ../../domains/cognitive-systems/concepts/team-cognition.md
tags:
  - human-ai-teaming
  - function-allocation
  - trust-calibration
  - joint-cognitive-system
---

# 人 AI 协作设计 · Human-AI Teaming

## 一句话功能

设计人与 AI Agent 的协作认知系统——包括功能分配、信任校准和交接机制——避免 Bainbridge 自动化悖论，实现人机互补的认知增强。

## 何时使用

- 设计人与 AI 系统的协作方案
- 确定哪些任务交给 AI、哪些留给人
- 设计人机交接（handoff）协议
- 分析现有 AI 协作系统的问题
- 设计信任校准机制

## 何时不使用

- 完全自主的 AI 系统（无人参与）
- 完全人工的任务（无 AI 参与）
- 简单的工具使用（如搜索、计算器）

## 理论基础

- 来源思想家：[班布里奇 Bainbridge](../../domains/cognitive-systems/schools/automation-sociotechnical/bainbridge.md)
- 来源概念：[联合认知系统](../../domains/cognitive-systems/concepts/joint-cognitive-system.md)、[自动化偏见](../../domains/cognitive-systems/concepts/automation-bias.md)、[团队认知](../../domains/cognitive-systems/concepts/team-cognition.md)
- 关键文献：Bainbridge, L. "Ironies of Automation." *Automatica* 19(6), 1983.

## 操作流程

### Step 1：认知任务分析

分析领域中的认知任务：
- 识别所有认知任务（感知、推理、决策、行动）
- 对每个任务评估复杂性、时间压力、可预测性
- 识别任务中哪些适合 AI（模式识别、数据处理）哪些适合人（异常处理、伦理判断）

### Step 2：功能分配

基于任务特征进行人机功能分配：

| 适合 AI | 适合人 | 适合协作 |
|---|---|---|
| 大量数据处理 | 伦理和价值判断 | 复杂决策（AI 建议 + 人判断） |
| 重复性模式识别 | 创造性问题解决 | 异常检测（AI 标记 + 人确认） |
| 高速精确计算 | 理解社会和情感语境 | 信息综合（AI 整合 + 人解读） |

**关键原则**：
- **不是非此即彼**：大多数任务是人机协作完成
- **考虑 Bainbridge 悖论**：自动化越高的部分，恰恰是人最需要能力但最可能退化的部分
- **保留人的参与感**：避免完全脱离回路

### Step 3：交接协议设计

设计人机之间的交接（handoff）机制：

**AI → 人的交接**（AI 遇到不确定/超出能力）：
- 交接触发条件：置信度低于阈值、遇到训练数据外的情况
- 交接方式：明确的警报 + 当前状态摘要 + 不确定性说明
- 交接时间要求：给人足够的接管准备时间

**人 → AI 的交接**（人让 AI 接管常规操作）：
- 交接前提：AI 确认理解当前状态
- 交接方式：人明确确认 + AI 状态验证
- 监督要求：人保持最低水平的情境意识

### Step 4：信任校准机制

设计机制确保人的信任与 AI 的实际能力匹配：

- **能力透明性**：让操作者理解 AI 能做什么、不能做什么
- **不确定性表达**：AI 应清晰表达其判断的不确定性
- **历史表现反馈**：让操作者了解 AI 的历史表现
- **模式切换**：允许操作者在不同自动化级别间切换

### Step 5：监控与干预设计

- **情境意识维护**：设计确保人保持对系统状态的理解
- **干预能力保障**：确保人可以在任何时候接管
- **定期互动**：设计需要人参与的环节，防止技能退化

### Step 6：评估标准

定义人机协作系统的评估指标：
- 系统整体绩效（速度、准确性、安全性）
- 人的信任校准度（信任与实际能力的匹配程度）
- 人的干预效果（接管时的反应时间和决策质量）
- 人的技能维持度（手动操作能力的变化）

## 完整示例

**输入场景**：
> 设计一个人类作者与 LLM 协作的写作系统。

**Skill 应用过程**：

1. **认知任务分析**：
   - 内容生成：创意构思、论证构建、文风把控
   - 信息处理：资料搜集、事实核查、信息综合
   - 编辑优化：语法检查、结构调整、逻辑验证

2. **功能分配**：
   - AI 做：资料搜集、初稿生成、语法检查、风格建议
   - 人做：创意方向、核心论点、价值判断、最终审定
   - 协作做：论证构建（AI 提供论据 + 人选择和组织）

3. **交接协议**：
   - AI 生成初稿后，显示不确定性和替代选项
   - 人可以随时要求 AI 重新生成或修改特定部分
   - 最终编辑和发布始终由人确认

4. **信任校准**：
   - 显示 AI 生成内容的事实准确率
   - 标注 AI 不确定的部分
   - 提供 AI 信息来源

5. **评估**：
   - 写作效率（时间节省）
   - 内容质量（读者反馈）
   - 创意保持度（人的独特贡献是否被保留）

**输出**：
> 人 LLM 协作写作系统的核心设计原则是"AI 增强而非替代"。功能分配上，AI 处理信息搜集和初稿生成等可规模化的任务，人掌控创意方向和价值判断。信任校准通过标注 AI 不确定性实现。交接设计确保人在任何环节都可以介入和修改。系统评估应关注创意保持度，防止过度依赖 AI 导致人的创意退化。

## 反例（误用）

**误用场景**：
> 设计一个完全自主的 AI 写作系统，自动生成、编辑并发布内容，无需人参与。

**正确做法**：完全自主的 AI 不是"协作"——无团队认知、无功能分配、无信任校准问题。人 AI 协作设计的前提是人和 AI 都在回路中，发挥各自优势。

## 关联条目

- 思想家：[班布里奇 Bainbridge](../../domains/cognitive-systems/schools/automation-sociotechnical/bainbridge.md)
- 概念：[联合认知系统](../../domains/cognitive-systems/concepts/joint-cognitive-system.md)
- 概念：[自动化偏见](../../domains/cognitive-systems/concepts/automation-bias.md)
- 概念：[团队认知](../../domains/cognitive-systems/concepts/team-cognition.md)
- 相关 Skill：[自动化级别评估](../automation-level-assessment/SKILL.md)
