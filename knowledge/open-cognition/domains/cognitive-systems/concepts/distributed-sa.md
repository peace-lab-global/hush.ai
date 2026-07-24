---
id: distributed-sa
title: 分布式态势感知 · Distributed Situation Awareness
type: concept
domain: cognitive-systems
school: cognitive-engineering
era: contemporary
tags: [distributed-SA, team-SA, information-distribution]
aliases: [分布式态势感知, Distributed SA, DSA, Distributed Situation Awareness]
sources:
  - title: "Distributed Situation Awareness in Dynamic Environments"
    author: Neville Stanton et al.
    year: 2006
  - title: "Distributed Situation Awareness"
    author: Neville Stanton et al.
    year: 2017
---

# 分布式态势感知 · Distributed Situation Awareness

## 一句话定义

态势感知不是纯粹存在于个体头脑中的东西——它通过信息在团队成员和人工物之间的分布而存在于系统层面，不同agent持有不同的SA组件，系统的SA是这些分布信息的整合。

## 提出者与背景

- **首要提出者**：Neville Stanton、Robert Stewart、Guy Walker（2006）
- **历史语境**：2000 年代，Endsley 的个体 SA 模型难以解释复杂团队和系统中的 SA 现象
- **针对的问题**：在一个多人协作的系统中，SA 应该被认为是"共享的"还是"分布的"？

## 核心要义

### 核心理念：SA 是分布式的，不是共享的

**"共享"SA 的问题**：暗示每个成员都拥有相同的信息——但实际上团队成员持有不同、互补的信息。

**分布式 SA 的模型**：

```
Agent A 的 SA ──┐
Agent B 的 SA ──┼──→ 系统 SA（信息通过交互整合）
Agent C 的 SA ──┤
人工物（显示器、手册等）──┘
```

### 分布式 SA 的关键概念

1. **SA 元素（SA elements）**：特定信息片段（如"飞机高度 35000 英尺"）
2. **SA 水平（SA levels）**：感知、理解、预测（保留 Endsley 框架）
3. **共享信息 vs 不共享信息**：不同agent需要不同的SA组件——不是所有信息都需要共享
4. **信息协调**：系统中的信息流动和整合机制
5. **SA 传导（SA transaction）**：agent 之间通过信息交换实现 SA 的传递和整合

### 与传统共享 SA 模型的对比

| 维度 | 共享 SA | 分布式 SA |
|---|---|---|
| 假设 | 所有成员应拥有相同的 SA | 成员持有不同的、互补的 SA |
| 目标 | 最大化重叠 | 最优化分布 |
| 分析层级 | 个体层面 | 系统层面 |
| 理论基础 | 个体认知 | 分布式认知 |
| 设计含义 | 共享显示、统一看法 | 个性化显示、信息流设计 |

## 通俗用法 vs 学术原义

| 维度 | 通俗用法 | 学术原义 |
|---|---|---|
| 分布式态势感知 | "大家都知道情况" | 信息通过agent和人工物的分布实现系统级SA |
| 共享理解 | "信息同步" | 不是同步，而是适当的信息分布和协调 |

## 与相关概念的关系

- **发展**：[态势感知](./situation-awareness.md) — 将 Endsley 的个体 SA 模型扩展到系统层面
- **上位**：[分布式认知](./distributed-cognition.md) — 分布式 SA 是分布式认知在态势感知领域的应用
- **互补**：[团队认知](./team-cognition.md) — 分布式 SA 是团队认知的重要组成部分
- **互补**：[联合认知系统](./joint-cognitive-system.md) — 分布式 SA 描述了 JCS 中的信息感知层面

## 代表思想家

- Stanton, N. — 分布式 SA 模型的提出者
- Stewart, R. — 分布式 SA 框架的共同开发者
- [Endsley](../schools/naturalistic-decision/endsley.md) — 原始 SA 理论，分布式 SA 的基础
- [Hutchins](../schools/distributed/hutchins.md) — 分布式认知理论的基础

## 应用场景

- **空中交通管制**：管制员团队之间的 SA 分布
- **军事指挥控制**：作战信息在不同层级和角色之间的分布
- **核电站控制室**：操纵员团队的信息共享和协调
- **紧急救援**：不同救援队伍之间的态势共享
- **自动驾驶**：人机共享控制中的 SA 分布

## 常见误读

- ❌ "分布式 SA = 信息广播" → 不是让所有人知道所有事，而是让正确的信息在正确的地方。
- ❌ "SA 完全存在于个体头脑中" → SA 可以分布在团队和工具之间——这是分布式认知的核心主张。
- ❌ "分布式 SA 否定了共享理解" → 部分信息需要共享，但不是所有信息——关键是区分哪些信息需要被谁拥有。

## 跨学科关联

- [哈钦斯 Hutchins](../schools/distributed/hutchins.md) `[同源]` 分布式认知是分布式 SA 的理论基础
- [拉图尔 Latour](../../../sociology/schools/actor-network/latour.md) `[平行]` 行动者网络——非人行动者（工具、显示器）也是 SA 的载体
- [维特根斯坦 Wittgenstein](../../../philosophy/schools/analytic/wittgenstein.md) `[启发]` 语言游戏——信息的意义在特定语境和使用中确定

## 进阶阅读

- Stanton, N., Stewart, R. & Walker, D. "Distributed Situation Awareness in Dynamic Environments." *Ergonomics* 49(12-13), 2006.
- Stanton, N. et al. *Distributed Situation Awareness*. Ashgate, 2017.
- Salmon, P. et al. "What Really Is Going On? Review of Situation Awareness Models for Sociotechnical Systems." *Safety Science* 46(5), 2008.
