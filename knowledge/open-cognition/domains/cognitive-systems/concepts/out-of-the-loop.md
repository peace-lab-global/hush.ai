---
id: out-of-the-loop
title: 脱离回路 · Out-of-the-Loop (OOTL)
type: concept
domain: cognitive-systems
school: automation-sociotechnical
era: contemporary
tags: [out-of-the-loop, automation, situation-awareness, monitoring, intervention]
aliases: [脱离回路, OOTL problem, out-of-the-loop unawareness, OOTL 困境]
sources: ["Endsley (1995)", "Endsley & Kiris (1995)", "Bainbridge (1983)"]
---

# 脱离回路 · Out-of-the-Loop (OOTL)

## 一句话定义

脱离回路（OOTL）是指当自动化系统接管了操作任务后，人类操作者因缺乏主动参与而逐渐失去对系统状态的感知与理解，导致在自动化系统失效或需要人工干预时无法有效介入。

## 提出者与背景

OOTL 问题最早由 Endsley（1995）系统描述，但其理论根基可追溯到 Bainbridge（1983）的自动化悖论。Endsley 将其与情境意识（Situation Awareness）理论结合，指出自动化系统虽然提高了常规操作的效率，却同时削弱了操作者在三个层次上的 SA：感知（Perception）、理解（Comprehension）、预测（Projection）。

## 核心要义

OOTL 困境的核心结构如下：

```
自动化接管 → 操作者被动角色 → 情境意识下降 → 无法有效干预
    ↑                                                    |
    └────────── 设计初衷是提高效率 ←─────────────────────┘
```

这一困境包含三个相互关联的维度：

### 信息获取断裂
自动化系统处理信息时，操作者不再直接接触原始数据流，而是接收经过系统过滤和总结的信息。这种信息的"中间化"导致操作者无法感知到细微但关键的状态变化。

### 心智模型退化
缺乏主动参与使操作者对系统状态的心理模型逐渐过时。当需要介入时，操作者的心智模型与实际系统状态之间存在时差，导致决策错误。

### 手动技能丧失
班布里奇（1983）指出，技能依赖于练习。长期依赖自动化使操作者的手动操作能力退化，在紧急情况下无法可靠执行手动接管。

## 通俗用法 vs 学术原义

| 维度 | 通俗用法 | 学术原义 |
|------|----------|----------|
| 含义 | "不了解情况" | 特指因自动化导致的情境意识丧失，具有特定的认知机制 |
| 场景 | 泛指任何"不在场"状态 | 特指人在回路中但因自动化角色转变而失去意识 |
| 关系 | 与自动化无关 | 是自动化的结构性后果 |

## 与相关概念的关系

- **自动化偏见**（Automation Bias）：自动化偏见是 OOTL 的前因之一——正是因为偏见，操作者才更被动地接受自动化决策
- **自动化自满**（Automation Complacency）：自满导致监控质量下降，加速 OOTL 过程
- **情境意识**（Situation Awareness）：OOTL 的本质是 SA 退化，是 SA 理论在自动化语境中的应用
- **技能退化**（Skill Degradation）：OOTL 的手动技能维度，源自 Bainbridge 的分析

## 代表思想家

- **[Endsley](../schools/naturalistic-decision/endsley.md)**：将 OOTL 与情境意识理论结合，提供了理论框架
- **Bainbridge**：从自动化悖论角度揭示了 OOTL 的结构性根源
- **Parasuraman**：通过自动化层级模型分析了哪些阶段的自动化最容易导致 OOTL
- **Woods**：从认知系统工程角度分析了自动化"惊喜"（automation surprise）与 OOTL 的关系

## 应用场景

- **自动驾驶接管**：L3 级自动驾驶中驾驶员长时间不操作后的接管困难
- **工业过程监控**：核电站、化工厂操作员对自动化系统的监控失败
- **无人机操控**：远程操作者因延迟和自动化而失去对无人机状态的感知
- **医疗监护**：护士对自动化监护仪报警的习惯化
- **网络安全**：安全分析师对自动化威胁检测系统的依赖

## 常见误读

1. **误读**：OOTL 可以通过增加屏幕信息来解决。
   **正读**：增加信息量可能加剧问题。关键不是信息量，而是信息的可理解性和操作者的主动参与程度。

2. **误读**：OOTL 是操作者的"责任心问题"。
   **正读**：OOTL 是自动化的结构性后果，不依赖于操作者的主观意愿。即使最有责任心的操作者也会在长时间被动监控中失去 SA。

3. **误读**：更好的培训可以消除 OOTL。
   **正读**：培训可以缓解但无法消除 OOTL，因为问题根植于人类注意力和学习的基本特性。

## 跨学科关联

- **情境意识理论**：OOTL 本质上是 SA 退化在自动化语境中的具体表现
- **认知负荷理论**：被动监控中的认知负荷分配与 OOTL 的关系
- **注意力科学**：人类对低频事件的监控能力有限，是 OOTL 的认知基础
- **学习科学**：技能退化与练习间隔的关系

## 进阶阅读

- Endsley, M. R. (1995). "Measurement of Situation Awareness in Dynamic Systems." *Human Factors*, 37(1), 65-84.
- Endsley, M. R. & Kiris, E. O. (1995). "The Out-of-the-Loop Performance Problem and Level of Control in Automation." *Human Factors*, 37(2), 381-394.
- Kaber, D. B. & Endsley, M. R. (2004). "The Effects of Level of Automation and Adaptive Automation on Human Performance, Situation Awareness and Workload."
