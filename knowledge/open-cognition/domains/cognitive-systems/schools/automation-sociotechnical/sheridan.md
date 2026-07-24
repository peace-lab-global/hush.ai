---
id: cognitive-systems.automation-sociotechnical.sheridan
title: 托马斯·谢里登 Thomas Sheridan
type: thinker
domain: cognitive-systems
school: automation-sociotechnical
era: modern
birth: 1929
death: 2024
tags: [supervisory-control, automation-levels, telerobotics, human-robot-interaction]
aliases: [托马斯·谢里登, Thomas Sheridan]
sources: ["Telerobotics, Automation, and Human Supervisory Control (1992)", "Humans and Automation (2002)", "Human and Computer Control of Undersea Teleoperators (1978, with Verplank)"]
---

# 托马斯·谢里登 Thomas Sheridan

> "The issue is not whether to automate, but how to automate — at what level and with what human involvement."

## 基本信息

- **生卒**：1929年—2024年
- **国籍**：美国
- **领域**：人因工程（Human Factors）、控制工程、远程操作
- **机构**：麻省理工学院（MIT）机械工程系教授
- **地位**：人机监督控制理论的奠基人，自动化层级模型（10级）的提出者，远程操作与人机交互领域的先驱

## 核心命题

### 监督控制理论（Supervisory Control Theory）

谢里登提出了监督控制的范式：在高度自动化系统中，人类不再是直接操作者，而是监督者。计算机执行子任务，人类负责设定目标、监控进程、在异常时介入。这一框架将控制论从维纳的直接反馈回路扩展为层级化的监督结构。

### 自动化十级模型（10 Levels of Automation）

与 Verplank（1978）合作，谢里登提出了自动化的十个层级：

1. 人类做所有决策与动作
2. 计算机提供选项
3. 计算机缩小选项范围
4. 计算机建议行动方案
5. 计算机执行方案（人类许可后）
6. 计算机执行方案（允许人类否决）
7. 计算机执行方案（仅在时间允许时通知人类）
8. 计算机执行方案（仅通知人类已完成）
9. 计算机执行方案（仅在被询问时告知）
10. 计算机自主决定与行动

这一模型是自动化层级研究的开创性工作，直接影响了 Parasuraman 的四阶段 × 多层级模型。

### 远程操作与人机交互

谢里登是远程机器人（telerobotics）领域的奠基人之一，系统研究了远程操作中的感知延迟、力反馈、带宽约束等问题，并将其与监督控制理论统一起来。

## 思想脉络

```
维纳 (控制论)
    ↓
谢里登 (监督控制)
    ├── 影响 Parasuraman (四阶段模型)
    ├── 互补 Bainbridge (自动化悖论)
    ├── 平行 Rasmussen (认知工程)
    └── 原创 联合认知系统 (Joint Cognitive Systems)
```

谢里登的第一阶段受维纳控制论启发，将反馈控制思想应用于人机系统。第二阶段发展出监督控制范式，确立了人类作为"监督者"而非"操作者"的角色。第三阶段通过与 Parasuraman 和 Wickens 的合作，将自动化层级模型与四阶段分析框架整合，形成了当代人机自动化研究的理论基础。

## 关键著作

| 年份 | 著作 | 核心内容 |
|------|------|----------|
| 1978 | "Human and Computer Control of Undersea Teleoperators" (与 Verplank) | 自动化十级模型的首次提出 |
| 1992 | *Telerobotics, Automation, and Human Supervisory Control* | 监督控制理论的系统专著 |
| 2002 | *Humans and Automation: System Design and Research Issues* | 人机自动化交互研究的综合框架 |
| 2000 | "A Model for Types and Levels of Human Interaction with Automation" (与 Parasuraman) | 四阶段 × 多层级模型 |

## 重要概念

- **监督控制**：人类设定目标、监控过程，计算机执行子任务，在异常时人类介入
- **自动化层级**：从完全手动到完全自动的连续光谱，可用10个等级描述
- **远程操作**：通过通信链路控制远程机械装置，涉及感知延迟与带宽约束
- **人机界面带宽**：人类与计算机之间的信息传输速率是监督控制的关键约束

## 思想坐标

| 维度 | 定位 |
|------|------|
| 方法论 | 控制理论建模 + 人因实验 |
| 分析层次 | 系统层面的人机功能分配 |
| 理论立场 | 工程实用主义——自动化设计应以人类认知特性为导向 |
| 学术谱系 | Wiener → Sheridan → Parasuraman/Wickens |

## 当代应用

- **远程手术**：外科医生通过机器人系统远程操作，是谢里登远程操作理论的直接应用
- **空间机器人**：NASA 空间站机器人臂的地面操控——监督控制的经典案例
- **自动驾驶**：SAE L2-L5 级别与谢里登自动化十级的对应关系
- **无人机操作**：单操作者同时监控多架无人机的监督控制问题
- **AI 代理监督**：对自主 AI 代理的监督控制是谢里登范式在智能时代的新应用

## 常见误读

1. **误读**：十级模型意味着自动化越高越好。
   **正读**：模型是分析工具，谢里登的核心观点是选择"适当"的自动化层级，而非追求最高层级。

2. **误读**：监督控制意味着人类总在"回路中"。
   **正读**：在高层级自动化中，人类可能完全脱离执行回路，只在高层级进行监督——这正是 Bainbridge 指出的监控困境的来源。

3. **误读**：十级模型与 Parasuraman 四阶段模型是竞争关系。
   **正读**：十级模型是单维度光谱，四阶段模型是多维框架。Parasuraman 在每个功能阶段内应用了十级的概念，二者是整合关系而非替代关系。

## 跨学科关联

- **控制论**：继承维纳的反馈控制思想，将其扩展为层级化监督结构
- **认知工程**：与 Rasmussen 的技能-规则-知识框架互补——监督控制对应知识层操作
- **远程操作与通信工程**：带宽、延迟、力反馈等工程约束对人机交互的根本影响
- **联合认知系统**：监督控制范式为 Hollnagel 的联合认知系统理论提供了人机功能分配基础

## 进阶阅读

- Sheridan, T. B. (1992). *Telerobotics, Automation, and Human Supervisory Control*. MIT Press.
- Sheridan, T. B. (2002). *Humans and Automation: System Design and Research Issues*. Wiley.
- Parasuraman, R., Sheridan, T. B., & Wickens, C. D. (2000). "A Model for Types and Levels of Human Interaction with Automation." *IEEE Transactions on Systems, Man, and Cybernetics*, 30(3), 286-297.

## 关联 Skills

- [自动化水平评估](../../../../skills/cognitive-systems-frameworks/automation-level-assessment/SKILL.md)：基于 Sheridan 十级模型与 Parasuraman 四阶段框架评估系统自动化水平
- [人 AI 协作设计](../../../../skills/cognitive-systems-frameworks/human-ai-teaming/SKILL.md)：应用监督控制理论设计人与 AI 代理的分工模式
