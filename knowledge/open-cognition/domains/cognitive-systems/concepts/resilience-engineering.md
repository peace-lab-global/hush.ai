---
id: resilience-engineering
title: 韧性工程 · Resilience Engineering
type: concept
domain: cognitive-systems
school: cognitive-engineering
era: contemporary
tags: [resilience, safety, adaptation, failure, recovery]
aliases: [韧性工程, 弹性工程, Resilience Engineering]
sources:
  - title: "Resilience Engineering: Concepts and Precepts"
    author: Erik Hollnagel, David Woods, Nancy Leveson
    year: 2006
  - title: "Four Concepts for Resilience"
    author: David Woods
    year: 2015
---

# 韧性工程 · Resilience Engineering

## 一句话定义

研究系统如何在面对意外、压力和失败时保持功能的工程方法——安全不是"没有错误"，而是"在错误发生时仍能运作"的能力。

## 提出者与背景

- **核心推动者**：[伍兹 David Woods](../schools/cognitive-engineering/woods.md)、Hollnagel、Leveson
- **历史语境**：2006 年《韧性工程》出版，标志着从"安全-I"（防止错误）到"安全-II"（建设韧性）的范式转变
- **针对的问题**：传统安全工程聚焦于"消除错误原因"，但复杂系统中的失败往往是"成功运行的意外后果"

## 核心要义

### 安全-I vs 安全-II

| 维度 | 安全-I（传统） | 安全-II（韧性工程） |
|---|---|---|
| 安全定义 | 没有事故 | 系统在变化中保持功能的能力 |
| 错误观 | 错误是偏差，需要消除 | 错误是正常的，需要建设恢复能力 |
| 分析方法 | 找原因（根因分析） | 理解"通常为什么成功"（成功分析） |
| 人的角色 | 人是错误的来源 | 人是韧性的来源 |
| 目标 | 减少变异性 | 建设适应能力 |

### 韧性的四个能力
1. **监测（Monitor）**：感知系统状态和潜在威胁
2. **预测（Anticipate）**：预见可能的变化和需求
3. **响应（Respond）**：在变化发生时做出适当反应
4. **学习（Learn）**：从经验中提取教训并改进系统

## 通俗用法 vs 学术原义

| 维度 | 通俗用法 | 学术原义 |
|---|---|---|
| 韧性 | "坚强、扛得住" | "系统在变化和压力下保持功能的动态能力" |
| 韧性工程 | "加固系统" | "建设系统的监测-预测-响应-学习能力" |

## 与相关概念的关系

- **同源**：[联合认知系统](./joint-cognitive-system.md) — 韧性是联合认知系统的属性
- **对立**：传统安全工程（安全-I） — 关注消除错误 vs 建设韧性
- **互补**：[人为错误分析](./situation-awareness.md) — 理解错误是韧性的前提
- **互补**：[意义建构](./sensemaking.md) — 危机中的意义建构是韧性的关键

## 代表思想家

- [Woods](../schools/cognitive-engineering/woods.md) — 韧性工程四概念
- Hollnagel — 安全-I/安全-II 框架
- Leveson — 系统理论事故模型（STAMP）
- Nemeth — 韧性在医疗中的应用

## 应用场景

- **医疗安全**：从"消除医疗差错"到"建设韧性医疗系统"
- **航空安全**：飞行员如何从异常状态中恢复
- **网络安全**：系统在遭受攻击后如何保持核心功能
- **AI 安全**：人+AI 系统的韧性——当 AI 出错时人如何介入
- **气候适应**：社会系统如何适应气候变化带来的冲击

## 常见误读

- ❌ "韧性 = 坚固（robustness）" → 坚固是抵抗变化，韧性是适应变化——包括重组和学习。
- ❌ "韧性工程 = 不关心错误" → 韧性工程关心错误，但视角从"消除错误"转向"建设恢复能力"。
- ❌ "韧性是系统的固有属性" → 韧性是动态的——需要持续投资和维护。

## 跨学科关联

- [伍兹 Woods](../schools/cognitive-engineering/woods.md) `[原创]` 韧性工程核心推动者
- [贝克 Beck](../../../sociology/schools/modernity/beck.md) `[平行]` 风险社会理论也关注系统性风险
- [佛教转识成智](../../../religion/buddhism/concepts/cognitive-theory/consciousness-transformation.md) `[平行]` "转化"而非"消除"
- [阿什比 Ashby](../schools/cybernetics/ashby.md) `[继承]` 必要多样性法则是韧性的数学基础

## 进阶阅读

- Hollnagel, E., Woods, D. & Leveson, N. *Resilience Engineering*. Ashgate, 2006.
- Woods, D. "Four Concepts for Resilience." *Reliability Engineering & System Safety* 141, 2015.
- Hollnagel, E. *Safety-I and Safety-II*. Ashgate, 2014.
