---
id: automation-autonomy-spectrum
title: 自动化-自主性光谱 · Automation-Autonomy Spectrum
type: concept
domain: cognitive-systems
school: automation-sociotechnical
era: contemporary
tags: [automation-levels, autonomy, human-automation-interaction, supervisory-control, function-allocation]
aliases: [自动化光谱, Automation-Autonomy Spectrum, 自动化层级, 自主性等级]
sources: ["Sheridan & Verplank (1978)", "Parasuraman, Sheridan & Wickens (2000)", "Parsons (1985)"]
---

# 自动化-自主性光谱 · Automation-Autonomy Spectrum

## 一句话定义

自动化-自主性光谱描述了从完全人工控制到完全机器自主之间的连续梯度，强调自动化不是"有或无"的二元选择，而是包含众多中间层级的设计空间。

## 提出者与背景

自动化层级的概念由 Thomas Sheridan 与 William Verplank 于 1978 年首次系统提出（10 级模型），源于水下远程操作器的控制需求。Parsons（1985）将其扩展为按功能阶段分解的框架。2000 年，Parasuraman、Sheridan 与 Wickens 将两种思路整合为四阶段 × 多层级的分析矩阵，成为当代自动化设计的标准工具。

## 核心要义

### Sheridan 十级（1978）

从 Level 1（人类做所有决策与动作）到 Level 10（计算机完全自主决定与行动），中间包含建议、推荐、许可、通知等渐进层级。关键在于：每一级都定义了人类与计算机在决策-执行链上的不同分工。

### Parsons 四阶段扩展（1985）

将自动化分解为四个功能阶段：
1. **数据采集**（Data Acquisition）
2. **数据分析**（Data Analysis）
3. **决策选择**（Decision Selection）
4. **行动实施**（Action Implementation）

每个阶段可独立设定自动化水平。

### Parasuraman-Sheridan-Wickens 整合（2000）

将 Sheridan 的十级应用于 Parsons 的四个阶段，形成 4×10 矩阵。设计者可针对每个功能阶段独立选择自动化层级，实现精细化的自动化设计。

## 通俗用法 vs 学术原义

| 维度 | 通俗用法 | 学术原义 |
|------|----------|----------|
| 理解 | "自动化有高低之分" | 多维连续光谱，每个功能阶段独立可调 |
| 设计 | "尽量提高自动化水平" | 应针对每个阶段的风险-收益选择适当层级 |
| 讨论 | "AI 会不会取代人类" | 问题不是取代与否，而是如何在各阶段分配功能 |

## 与相关概念的关系

- **自动化偏见**（Automation Bias）：过度信任自动化建议是光谱高层级的常见风险
- **脱离回路**（Out-of-the-Loop）：高层级自动化导致操作者对系统状态认知不足
- **联合认知系统**（Joint Cognitive Systems）：光谱描述了人机功能分配的多种可能配置
- **海德格尔上手状态**：自动化层级影响人与工具的关系——从"上手"（直接使用）到"在手"（监控反思）
- **维特根斯坦语言游戏**：不同自动化层级对应不同的人机"游戏规则"

## 代表思想家

- **Thomas Sheridan**：十级模型的提出者，监督控制理论的奠基人
- **Raja Parasuraman**：四阶段模型的提出者，将光谱精细化为多维分析
- **Christopher Wickens**：与 Parasuraman 和 Sheridan 合作完成整合模型
- **Lisanne Bainbridge**：从批判角度揭示光谱高层级的监控困境

## 应用场景

- **自动驾驶分级**：SAE L0-L5 级别是光谱思想的直接应用
- **AI 代理设计**：LLM agent 的自主程度需要在光谱上选择适当位置
- **医疗 AI**：AI 辅助诊断的建议层级 vs 自主诊断的层级选择
- **军事自动化**：致命性武器中"人在回路"（human-in-the-loop）vs "人在回路上"（human-on-the-loop）的争论
- **工业过程控制**：核电站、化工厂中各功能阶段的自动化层级配置

## 常见误读

1. **误读**：自动化层级越高越好。
   **正读**：高层级自动化增加监控困境、技能退化和脱离回路的风险。最佳层级取决于任务特性、错误代价和人类认知约束。

2. **误读**：光谱是单一维度的。
   **正读**：整合模型是多维的——同一系统的不同功能阶段可以处于不同的自动化层级。

3. **误读**：光谱描述的是技术能力。
   **正读**：光谱描述的是人机功能分配（function allocation）——同一个技术能力可以配置在不同层级，取决于设计决策。

## 跨学科关联

- **海德格尔上手状态**：自动化层级改变人与工具的存在关系——从"上手使用"到"在手监控"
- **维特根斯坦语言游戏**：不同层级的人机交互遵循不同的"游戏规则"
- **伦理学**：自主性层级直接关联道德责任分配——机器自主决策的责任归属问题
- **组织理论**：自动化层级影响组织结构——高层级自动化趋向集中化监控

## 进阶阅读

- Sheridan, T. B. & Verplank, W. L. (1978). "Human and Computer Control of Undersea Teleoperators." MIT Man-Machine Systems Laboratory.
- Parasuraman, R., Sheridan, T. B., & Wickens, C. D. (2000). "A Model for Types and Levels of Human Interaction with Automation." *IEEE Transactions on Systems, Man, and Cybernetics*, 30(3), 286-297.
- Parasuraman, R. & Riley, V. (1997). "Humans and Automation: Use, Misuse, Disuse, Abuse." *Human Factors*, 39(2), 230-253.
- Endsley, M. R. (2017). "From Here to Autonomy: Lessons Learned from Human-Automation Research." *Human Factors*, 59(1), 5-27.
