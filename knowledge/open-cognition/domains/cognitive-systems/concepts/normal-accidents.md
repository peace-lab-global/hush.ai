---
id: cognitive-systems.safety-science.normal-accidents
title: 正常事故 · Normal Accidents Theory
type: concept
domain: cognitive-systems
school: safety-science
era: contemporary
tags: [normal-accidents, tight-coupling, interactive-complexity, system-failure, inevitable-accidents]
aliases: [正常事故论, 正常意外理论, normal-accident-theory]
sources:
  - title: Normal Accidents
    author: Charles Perrow
    year: 1984
  - title: The Next Catastrophe
    author: Charles Perrow
    year: 2007
---

# 正常事故 · Normal Accidents Theory

## 一句话定义

在紧密耦合且具有交互复杂性的系统中，事故不是异常，而是系统运作的"正常"产物——不可避免，只能管理。

## 提出者与背景

- **核心推动者**：Charles Perrow（1925-2019），耶鲁大学社会学教授
- **历史语境**：1979年三里岛核电站事故促使 Perrow 思考：为什么一个"小故障"会级联成重大事故？他的答案是——系统本身的特性使然。
- **针对的问题**：为什么在拥有先进技术、严格规程和训练有素人员的系统中，仍然会发生重大事故？

## 核心要义

Perrow 提出了两个关键维度来分析复杂系统：**交互复杂性**和**耦合紧密度**。

**交互复杂性**指的是系统各部分之间相互作用的方式。在线性系统中，各部分之间的交互是直接的、可预见的；在交互复杂系统中，各部分之间存在隐藏的、非预期的相互作用——一个部分的变化可能以难以预料的方式影响其他部分。

**耦合紧密度**指的是系统各部分之间连接的松紧程度。在紧密耦合系统中，一个部分的变化会立即、不可避免地影响其他部分；在松散耦合系统中，变化可以被缓冲和吸收。

Perrow 的核心论点是：当一个系统同时具有高交互复杂性和紧密耦合时，事故是"正常"的——不是因为人的疏忽或技术的缺陷，而是因为系统本身的特性使事故不可避免。三里岛、切尔诺贝利、挑战者号都是这类"正常事故"。

## 通俗用法 vs 学术原义

| 维度 | 通俗用法 | 学术原义 |
|------|----------|----------|
| 正常事故 | "事故总会发生" | 紧密耦合+交互复杂系统的内在特性导致的不可避免的多重故障级联 |
| 交互复杂性 | "系统很复杂" | 系统组件间存在非线性的、难以预见的相互作用路径 |
| 紧密耦合 | "牵一发动全身" | 系统组件间缺乏缓冲和延迟，变化即时传播 |
| 不可避免 | "认命吧" | 需要不同管理策略（预防+缓冲+冗余），而非放弃安全管理 |

## 与相关概念的关系

- **同源**：[漂移失败 Drift into Failure](drift-into-failure.md) — 两者都关注复杂系统中事故的系统性根源
- **互补**：Reason 的瑞士奶酪模型 — Perrow 解释为什么事故会发生，Reason 解释事故如何穿透防线
- **对立**：高可靠性组织理论（HRO） — HRO 认为紧密耦合复杂系统可以通过特殊组织实践实现高可靠性
- **承继**：Rasmussen 的风险梯度理论 — 两者都关注系统向安全边界移动的动态过程
- **承继**：[韧性工程](resilience-engineering.md) — 韧性工程可以看作对正常事故理论的建设性回应

## 代表思想家

- **[Charles Perrow](../schools/safety-science/perrow.md)**：《Normal Accidents》（1984）——正常事故理论的原创者
- **Diane Vaughan**：《The Challenger Launch Decision》（1996）——正常事故理论在挑战者号事故中的应用
- **Scott Sagan**：《The Limits of Safety》（1993）——将正常事故理论应用于核武器安全
- **Andrew Hopkins**：《Lessons from Longford》（2000）——正常事故理论在工业事故中的应用

## 应用场景

- **核电安全**：三里岛、切尔诺贝利事故分析——交互复杂性+紧密耦合的经典案例
- **金融系统**：2008年金融危机——金融衍生品的交互复杂性和金融市场的紧密耦合
- **AI 系统安全**：AI 系统的不透明决策 + 与其他系统的紧密集成 = 新型"正常事故"风险
- **互联网基础设施**：云服务、CDN、DNS 的紧密耦合导致级联故障
- **气候变化**：地球气候系统的交互复杂性使精确预测几乎不可能

## 常见误读

- ❌ **"正常事故理论是悲观宿命论"**：Perrow 不是说"不要管安全了"——他主张的是对不同类型系统采用不同策略：对紧密耦合系统应尽量解耦，对复杂系统应增加冗余。
- ❌ **"正常事故理论意味着所有复杂系统都不安全"**：Perrow 区分了不同类型的系统——许多复杂但松散耦合的系统（如大学、多数企业）并不面临正常事故风险。
- ❌ **"正常事故理论与 HRO 理论完全对立"**：两者存在深层对话——HRO 提供了在紧密耦合系统中提高可靠性的方法，但不否认系统本身的根本脆弱性。

## 跨学科关联

- **复杂系统理论**：涌现、级联、相变——正常事故理论是复杂系统理论在安全领域的应用
- **社会学**：Perrow 本人是社会学家——正常事故理论将安全问题置于社会组织分析之中
- **系统工程**：紧耦合、松耦合概念与系统架构设计直接相关
- **风险管理**：对风险评估方法的深刻挑战——如果事故是"正常的"，传统风险评估是否足够？

## 进阶阅读

- Perrow, C. (1984). *Normal Accidents: Living with High-Risk Technologies*.
- Perrow, C. (2007). *The Next Catastrophe: Reducing Our Vulnerabilities to Natural, Industrial, and Terrorist Disasters*.
- Vaughan, D. (1996). *The Challenger Launch Decision*.
- Sagan, S. (1993). *The Limits of Safety: Organizations, Accidents, and Nuclear Weapons*.
