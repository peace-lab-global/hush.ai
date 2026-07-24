---
id: affordance
title: 可供性 · Affordance
type: concept
domain: cognitive-systems
school: ecological
era: modern
tags: [affordance, perception, action, ecological-psychology, design]
aliases: [可供性, 示能, 功能可见性, Affordance]
sources:
  - title: "The Ecological Approach to Visual Perception"
    author: James J. Gibson
    year: 1979
  - title: "The Design of Everyday Things"
    author: Donald Norman
    year: 1988
---

# 可供性 · Affordance

## 一句话定义

环境直接为行动者提供的行动可能性——它既非纯客观属性也非纯主观投射，而是行动者与环境关系的直接呈现。

## 提出者与背景

- **首要提出者**：[吉布森 J.J. Gibson](../schools/ecological/gibson.md)
- **历史语境**：1979 年《视觉感知的生态进路》，针对传统知觉理论（建构主义）的"先感知属性，再推断用途"
- **设计领域传播者**：[诺曼 Donald Norman](../schools/cognitive-engineering/norman.md)（1988，将其引入产品设计）

## 核心要义

### 关键论点
1. **关系性**：可供性是行动者-环境的关系属性——椅子对人提供"坐下"，对猫提供"跳上"，对大象不提供"坐下"
2. **直接可感知**：可供性不需要推理——有经验的登山者直接"看到"岩壁的可抓握处
3. **独立于需求**：可供性存在与否不依赖于行动者当前的需求——即使你不渴，水杯仍然"提供"喝水
4. **行动导向**：感知的对象不是属性（颜色、形状），而是可供性（可走、可抓、可扔）

### Gibson 的 Affordance vs Norman 的 Affordance

| 维度 | Gibson（生态心理学） | Norman（设计） |
|---|---|---|
| 定义 | 环境提供的行动可能性 | 让用户感知到功能的设计提示 |
| 性质 | 客观存在的关系属性 | 被感知到的功能暗示 |
| 例子 | 地面"提供"行走 | 按钮"看起来"可以按 |
| 关键差异 | affordance 不需要被感知就存在 | affordance 必须被用户感知到 |

## 通俗用法 vs 学术原义

| 维度 | 通俗用法 | 学术原义 |
|---|---|---|
| Affordance | "功能"或"用途" | "环境为特定行动者提供的行动可能性" |
| 好的 affordance | "一看就知道怎么用" | "设计与行动者的身体/认知结构匹配" |

## 与相关概念的关系

- **同源**：[生成认知](./enaction.md) — 两者都强调行动者在认知中的主动角色
- **对立**：表征主义 — 认为感知需要内部表征，可供性理论认为感知是直接的
- **发展**：生态界面设计（Rasmussen/Vicente） — 将 affordance 理论应用于复杂系统界面
- **互补**：[认知负荷](./cognitive-load.md) — 好的 affordance 降低认知负荷

## 代表思想家

- [Gibson](../schools/ecological/gibson.md) — 原创者，生态心理学
- [Norman](../schools/cognitive-engineering/norman.md) — 设计领域的应用（感知可供性）
- [Chemero](#) — 激进具身认知中的 affordance 理论

## 应用场景

- **产品设计**：门把手的设计应该让用户直觉知道"推"还是"拉"
- **UI/UX 设计**：按钮、链接、输入框应该"看起来"可以被操作
- **建筑设计**：空间的布局应提供预期的行动路径
- **教育环境**：教室的布置应该提供协作、探索的行动可能
- **AI 界面**：AI 系统应该让用户感知到它"能做什么"和"不能做什么"

## 常见误读

- ❌ "Affordance = 功能" → 功能是物体属性，affordance 是关系属性——同一物体对不同行动者有不同 affordance。
- ❌ "Affordance 是主观的" → Gibson 的 affordance 是客观存在的关系——不依赖于是否被感知。
- ❌ "好的设计 = 越多 affordance 越好" → 有时候需要**反可供性**（anti-affordance）——比如防止误操作的保险栓。

## 跨学科关联

- [梅洛-庞蒂](../../../philosophy/schools/phenomenology/merleau-ponty.md) `[同源]` 身体现象学是 affordance 的哲学基础
- [吉布森](../schools/ecological/gibson.md) `[原创]` 生态心理学
- [海德格尔](../../../philosophy/schools/existentialism/heidegger.md) `[平行]` "上手状态"（ready-to-hand）与 affordance 的直接性
- [佛教六根六尘](../../../religion/buddhism/concepts/cognitive-theory/six-constituents.md) `[平行]` 感知是根-尘交互而非被动接收

## 进阶阅读

- Gibson, J.J. *The Ecological Approach to Visual Perception*. Houghton Mifflin, 1979.
- Norman, D. *The Design of Everyday Things*. Basic Books, 1988/2013.
- Chemero, A. *Radical Embodied Cognitive Science*. MIT Press, 2009.
