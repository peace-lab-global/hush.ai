---
name: resilience-assessment
description: 评估系统在面对意外和压力时的韧性水平，基于 Woods 和 Hollnagel 的韧性工程理论。Triggers on requests to evaluate system resilience, safety-II analysis, or assess how systems handle unexpected events.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/cognitive-engineering/woods.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/resilience-engineering.md
  - ../../domains/cognitive-systems/concepts/joint-cognitive-system.md
tags:
  - resilience
  - safety
  - adaptation
  - system-performance
---

# 韧性评估 · Resilience Assessment

## 一句话功能

评估系统（组织、团队、技术系统）在面对意外、压力和失败时保持功能的韧性能力——从"防止错误"的视角转向"建设适应能力"。

## 何时使用

- 评估组织/系统在意外事件中的表现
- 理解"为什么有些系统在压力下崩溃，而有些能挺过去"
- 设计韧性改进计划
- 从安全-I（防错）转向安全-II（韧性）

## 何时不使用

- 需要传统的根因分析（用人为错误分析）
- 问题是简单的设计缺陷而非系统性韧性问题
- 系统面临的是可预测的常规问题

## 理论基础

- 来源思想家：[伍兹 Woods](../../domains/cognitive-systems/schools/cognitive-engineering/woods.md)
- 来源概念：[韧性工程](../../domains/cognitive-systems/concepts/resilience-engineering.md)
- 关键文献：Hollnagel, E. *Safety-I and Safety-II*. Ashgate, 2014.

## 操作流程

### Step 1：绘制系统运行边界
理解系统在什么条件下运行：
- **正常运行范围**：系统通常面对的条件
- **边界条件**：系统接近能力极限的情况
- **超出边界**：系统设计时未预见的情况
- 系统的"性能可变性"——在正常范围内，表现如何波动？

### Step 2：评估四项韧性能力
对每项能力进行评估（强/中/弱）：

| 能力 | 评估问题 | 强韧标志 |
|---|---|---|
| **监测 Monitor** | 系统是否能感知到潜在威胁和异常？ | 主动监测、预警系统、一线人员的报告 |
| **预测 Anticipate** | 系统是否能预见可能的变化和需求？ | 情景规划、压力测试、对弱信号的敏感 |
| **响应 Respond** | 系统在变化发生时能否做出适当反应？ | 灵活性、资源冗余、快速重组能力 |
| **学习 Learn** | 系统是否能从经验中提取教训？ | 事后回顾、经验分享、流程更新 |

### Step 3：识别韧性表达和韧性陷阱
- **韧性表达**：系统在什么事件中展现了韧性？（成功恢复的案例）
- **韧性陷阱**：
  - **效率-韧性权衡**：追求效率（精益）是否削弱了韧性（冗余消失）？
  - **成功的代价**：过去的成功是否导致了自满和能力退化？
  - **渐进侵蚀**：安全边际是否在不知不觉中逐步缩小？

### Step 4：提出韧性改进建议
- **增强监测**：建立弱信号捕捉机制、鼓励一线报告
- **增强预测**：定期情景规划、压力测试、预验尸（pre-mortem）
- **增强响应**：保持资源冗余、建立灵活的组织结构
- **增强学习**：系统化的事后回顾、跨团队经验分享

## 完整示例

**输入场景**：
> 评估一家在线金融平台在突发市场波动（如闪崩）中的系统韧性。

**Skill 应用过程**：

1. **运行边界**：
   - 正常：日均交易量、正常波动范围
   - 边界：高波动日、大型事件驱动的交易峰值
   - 超出：闪崩（毫秒级价格暴跌）

2. **四项韧性能力评估**：
   - 监测：✅ 强——实时监控系统状态和市场异常
   - 预测：⚠️ 中——有压力测试但未覆盖极端闪崩场景
   - 响应：⚠️ 中——有熔断机制但触发条件可能过晚
   - 学习：❌ 弱——事后分析不够系统化，经验未有效传播

3. **韧性陷阱**：
   - 效率-韧性权衡：追求低延迟导致系统复杂度增加，韧性降低
   - 渐进侵蚀：熔断阈值在"从未触发"后被逐步放宽

4. **改进建议**：
   - 增强预测：增加极端闪崩场景的压力测试
   - 增强响应：优化熔断触发条件，增加渐进式减速机制
   - 增强学习：建立系统化的事件回顾流程

**输出**：
> 平台在监测方面表现强劲，但在预测极端场景和学习方面存在缺口。最大韧性陷阱是"追求低延迟牺牲了系统鲁棒性"。

## 反例（误用）

**误用场景**：
> 用韧性评估替代传统安全分析——两者互补而非替代。韧性工程不否定防错，而是在防错之上建设适应能力。

**正确做法**：安全-I（防错）+ 安全-II（韧性）= 完整的安全管理。

## 关联条目

- 思想家：[伍兹](../../domains/cognitive-systems/schools/cognitive-engineering/woods.md)
- 概念：[韧性工程](../../domains/cognitive-systems/concepts/resilience-engineering.md)
- 相关 Skill：[人为错误分析](../human-error-analysis/SKILL.md)
