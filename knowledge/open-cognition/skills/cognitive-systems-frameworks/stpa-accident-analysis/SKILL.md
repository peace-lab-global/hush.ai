---
name: stpa-accident-analysis
description: 基于 Leveson 的系统理论事故模型（STPA），从控制论角度分析系统事故的控制缺陷。Triggers on accident analysis, safety analysis, or system failure investigation.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/joint-cognitive-system.md
  - ../../domains/cognitive-systems/concepts/safety-paradigm.md
tags:
  - STPA
  - accident-analysis
  - safety-analysis
  - control-theory
  - system-safety
---

# STPA 事故分析 · System-Theoretic Process Analysis

## 一句话功能

使用 Leveson 的系统理论事故模型，通过分析系统的控制结构来识别不安全的控制行为和事故场景——从"事故是组件故障的结果"转变为"事故是控制缺陷的结果"。

## 何时使用

- 分析复杂系统中的事故或险些事故
- 进行前瞻性的安全分析（设计阶段）
- 理解自动化系统中的安全问题
- 传统故障树分析（FTA）不适用的系统级事故
- 分析涉及人机交互的安全问题

## 何时不使用

- 简单的设备/组件故障（使用传统根因分析）
- 仅有单一故障原因的简单事件
- 纯粹的自然灾害（非系统控制问题）

## 理论基础

- 来源思想家：[拉斯穆森 Rasmussen](../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md)（控制论安全分析基础）、Nancy Leveson（STPA 提出者）
- 来源概念：[联合认知系统](../../domains/cognitive-systems/concepts/joint-cognitive-system.md)、[安全范式](../../domains/cognitive-systems/concepts/safety-paradigm.md)
- 关键文献：Leveson, N. *Engineering a Safer World*. MIT Press, 2011.

## 操作流程

### Step 1：定义分析目的

明确分析的范围和目标：
1. **识别损失**：系统中可能发生的不可接受的损失是什么？（生命损失、设备损坏、环境破坏等）
2. **识别系统级危害**：什么系统状态或条件会导致这些损失？
3. **识别安全约束**：为了防止这些危害，系统必须满足什么约束？

**输出格式**：
```
损失：L-1 人员伤亡
危害：H-1 自动驾驶车辆与其他道路使用者碰撞
安全约束：SC-1 车辆必须在检测到障碍物时采取避让措施
```

### Step 2：建模控制结构

绘制系统的控制层次结构图：
```
控制器（Controller）
  ↓ 控制输入（Control Actions）
被控过程（Controlled Process）
  ↑ 反馈（Feedback）
```

**关键元素**：
- **控制器**：做出决策的实体（人类操作员、自动控制器、管理层）
- **控制行为**：控制器对被控过程施加的影响
- **被控过程**：被控制的系统部分
- **反馈**：被控过程状态的信息回传

### Step 3：识别不安全的控制行为（UCAs）

对每个控制行为，考虑四种可能导致危害的情况：

| 类型 | 描述 | 问题 |
|---|---|---|
| UCA-1 | 未提供导致危害 | 什么情况下应该提供但没有提供？ |
| UCA-2 | 提供了导致危害 | 什么情况下不应该提供但提供了？ |
| UCA-3 | 过早/过晚/顺序错误 | 什么时机问题是不安全的？ |
| UCA-4 | 停止过早/持续过长 | 什么情况下控制行为的持续时间有问题？ |

### Step 4：识别损失场景

对每个 UCA，追溯其产生的原因：
- **控制算法缺陷**：控制器的决策逻辑有误
- **不充分的反馈**：控制器没有获得正确的状态信息
- **不恰当的输入**：控制器接收了误导性的输入
- **过程模型错误**：控制器对被控过程的理解有误

## 完整示例

**输入场景**：
> 分析一起自动驾驶车辆在十字路口撞击行人的事故。

**Skill 应用过程**：

1. **定义目的**：
   - 损失：L-1 行人伤亡
   - 危害：H-1 车辆在行人穿越时未减速或停车
   - 约束：SC-1 检测到行人时必须减速或停车

2. **建模控制结构**：
   - 控制器：自动驾驶决策系统
   - 控制行为：加速/减速/转向
   - 被控过程：车辆在十字路口的运动
   - 反馈：传感器数据（摄像头、雷达、激光雷达）

3. **识别 UCAs**：
   - UCA-1：行人已进入路口，但系统未提供减速命令
   - UCA-4：系统继续执行先前规划的加速行为，即使行人已进入感知范围

4. **损失场景**：
   - 场景 A：传感器在特定光照条件下未能检测到行人（反馈不足）
   - 场景 B：算法将行人误分类为非威胁（过程模型错误）
   - 场景 C：从检测到决策的延迟导致制动过晚（控制算法时序问题）

**输出**：
> 事故根因不是单一的传感器故障，而是系统级的控制缺陷：(1) 感知算法对低对比度行人的检测不足；(2) 检测-决策-执行链路的时序约束未充分设计；(3) 缺乏"不确定即停车"的故障安全策略。建议修改控制算法增加保守性，缩短处理时序，并增加对不确定检测结果的安全约束。

## 反例（误用）

**误用场景**：
> 轮胎爆裂导致车辆失控——使用 STPA 分析"轮胎爆裂"的原因。

**正确做法**：轮胎爆裂是组件故障，使用传统故障模式分析（FMEA）或根因分析（RCA）。STPA 的价值在于分析系统级的控制缺陷——即使是组件正常工作，系统仍可能因控制设计不当而产生不安全状态。

## 关联条目

- 思想家：[拉斯穆森 Rasmussen](../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md)
- 概念：[联合认知系统](../../domains/cognitive-systems/concepts/joint-cognitive-system.md)
- 概念：[安全范式](../../domains/cognitive-systems/concepts/safety-paradigm.md)
- 相关 Skill：[人为错误分析](../human-error-analysis/SKILL.md)
