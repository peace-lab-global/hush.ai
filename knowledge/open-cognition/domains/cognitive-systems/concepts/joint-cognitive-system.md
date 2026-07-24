---
id: joint-cognitive-system
title: 联合认知系统 · Joint Cognitive System
type: concept
domain: cognitive-systems
school: cognitive-engineering
era: contemporary
tags: [joint-cognitive-system, human-machine, cognition, automation, trust]
aliases: [联合认知系统, JCS, 人-机联合认知系统, Joint Cognitive System]
sources:
  - title: "Joint Cognitive Systems: Foundations of Cognitive Systems Engineering"
    author: Erik Hollnagel, David Woods
    year: 2005
---

# 联合认知系统 · Joint Cognitive System

## 一句话定义

人（们）与技术人工制品（工具、计算机、AI）共同构成的认知整体——分析单元不是人或机器单独一方，而是联合系统整体的认知过程。

## 提出者与背景

- **首要提出者**：Hollnagel & [伍兹 David Woods](../schools/cognitive-engineering/woods.md)
- **历史语境**：2005 年《联合认知系统》出版，CSE 的核心概念——回应"人因工程"和"AI"两个领域的个体主义倾向
- **针对的问题**：自动化时代，人不再是独立的操作者，而是联合认知系统的参与者——如何分析这种新型认知？

## 核心要义

### 关键论点
1. **认知不可分割**：在联合系统中，认知过程不归属于人或机器，而是涌现于二者的耦合
2. **功能分配而非任务分配**：不是简单地"把任务分给人和机器"，而是理解联合系统如何实现认知功能
3. **信任校准**：人对自动化的信任需要与实际可靠性匹配——过度信任和信任不足都是问题
4. **控制权的流动性**：控制权在人和自动化之间动态转移——关键时刻的控制权转移是安全的焦点

### 联合认知系统的设计原则
- **可观察性**：人应能观察到联合系统的状态和推理过程
- **可引导性**：人应能引导和修正联合系统的行为
- **协调性**：人和自动化的行动应协调而非冲突
- **透明性**：自动化的推理过程应对人透明

## 通俗用法 vs 学术原义

| 维度 | 通俗用法 | 学术原义 |
|---|---|---|
| 联合认知系统 | "人+机器一起工作" | "认知过程涌现于人与技术的耦合——不可还原为个体" |
| 人机协作 | "人和机器各司其职" | "认知功能的联合实现——不是简单的任务分配" |

## 与相关概念的关系

- **同源**：[分布式认知](./distributed-cognition.md) — JCS 的理论基础之一
- **互补**：[态势感知](./situation-awareness.md) — JCS 需要共享的 SA
- **发展**：[韧性工程](./resilience-engineering.md) — JCS 的韧性是核心关注
- **互补**：[心智模型](./mental-model.md) — 用户对自动化的心智模型决定联合系统的表现

## 代表思想家

- Hollnagel & Woods — JCS 概念提出者
- Parasuraman — 自动化层级模型
- [Sheridan](../schools/automation-sociotechnical/sheridan.md) — 人机监督控制

## 应用场景

- **自动驾驶**：驾驶员和自动驾驶系统构成 JCS——控制权转移是关键安全问题
- **AI 辅助医疗**：医生和 AI 构成联合诊断系统——AI 的推理过程需要对医生透明
- **航空**：飞行员-自动驾驶-管制员构成多层 JCS
- **LLM 协作**：用户和 LLM 构成新型 JCS——如何设计这个联合系统？

## 常见误读

- ❌ "JCS = 人+机器的简单加和" → JCS 的认知是涌现的——整体大于部分之和。
- ❌ "自动化越高越好" → 过度自动化可能导致人的技能退化和信任失调。
- ❌ "JCS 让人成为多余" → JCS 的核心主张是人在联合系统中的不可替代性——人是韧性的来源。

## 跨学科关联

- [伍兹 Woods](../schools/cognitive-engineering/woods.md) `[原创]` JCS 核心推动者
- [哈钦斯 Hutchins](../schools/distributed/hutchins.md) `[互补]` 分布式认知为 JCS 提供理论基础
- [克拉克 Clark](../schools/ecological/clark.md) `[互补]` 延展心智是个体层面的 JCS
- [佛教心物一元](../../../religion/buddhism/concepts/cognitive-theory/mind-world.md) `[平行]` 心与物不是二元对立——JCS 也反对人-机二元论

## 进阶阅读

- Hollnagel, E. & Woods, D. *Joint Cognitive Systems*. Ashgate, 2005.
- Woods, D. "Decomposing Automation: Apparent Simplicity, Real Complexity." In Sheridan, 1992.
- Parasuraman, R. et al. "A Model for Types and Levels of Human Interaction with Automation." *IEEE Trans. SMC* 30(3), 2000.
