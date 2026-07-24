---
id: multiple-resource-model
title: 多资源模型 · Multiple Resource Model
type: concept
domain: cognitive-systems
school: automation-sociotechnical
era: contemporary
tags: [multiple-resources, attention, dual-task, workload, display-design, engineering-psychology]
aliases: [多资源模型, Multiple Resource Model, 多重资源理论, Wickens 多资源模型]
sources: ["Wickens (2002) Multiple resources and performance prediction", "Wickens (2008) Multiple Resources and Mental Workload"]
---

# 多资源模型 · Multiple Resource Model

## 一句话定义

多资源模型认为人类的注意力不是单一容量有限的资源池，而是由多个相对独立的资源池组成，任务之间的干扰程度取决于它们是否共享相同的资源维度。

## 提出者与背景

多资源模型由 Christopher Wickens 于 1984 年首次系统提出，随后在 2002 年和 2008 年进行了重要修订。该模型源于对 Kahneman（1973）单一资源容量理论的不足的认识——单一容量模型无法解释为何某些任务组合比其他组合更少产生干扰。Wickens 通过实验发现，任务间的干扰取决于它们所占用的特定认知资源维度。

## 核心要义

模型定义了四个正交的资源维度：

1. **加工阶段**（Stage）：感知（Perception）→ 认知加工（Cognition）→ 响应（Response）
2. **感知通道**（Modality）：视觉（Visual）vs 听觉（Auditory）
3. **视觉通道**（Visual Channel）：中央/焦点视觉（Focal）vs 周边/环境视觉（Ambient）
4. **加工编码**（Code）：空间型（Spatial）vs 言语型（Verbal）

核心预测规则：两个任务占用的资源维度重叠越多，双任务干扰越大；资源维度完全分离时，并行性能最佳。

## 通俗用法 vs 学术原义

| 维度 | 通俗用法 | 学术原义 |
|------|----------|----------|
| 含义 | "多任务处理需要不同类型的注意力" | 四维度正交资源模型，可精确预测干扰模式 |
| 应用 | "一边听音乐一边工作更好" | 需具体分析音乐与工作任务的资源维度重叠程度 |
| 局限 | 被简化为"用不同感官就不会干扰" | 各通道容量仍有限，中央瓶颈（bottleneck）在某些阶段不可消除 |

## 与相关概念的关系

- **单一容量模型**（Kahneman 1973）：多资源模型是对单一容量理论的替代——从一个"总容量"变为多个独立资源池
- **认知负荷理论**（Sweller）：认知负荷关注学习任务的内在/外在/关联负荷，多资源模型关注任务间的资源竞争维度。二者平行但互补
- **注意力瓶颈理论**（Broadbent/Treisman）：多资源模型承认中央瓶颈存在，但强调其他维度的资源可以并行
- **情境意识**（Endsley）：SA 的信息提取依赖特定资源通道，显示设计应遵循多资源原则

## 代表思想家

- **Christopher Wickens**：模型的提出者与主要发展者
- **Daniel Kahneman**：单一容量理论的提出者，为多资源模型提供了对比框架
- **John Sweller**：认知负荷理论的提出者，与多资源模型平行发展
- **Mica Endsley**：将多资源模型应用于情境意识显示设计

## 应用场景

- **显示设计**：将关键信息分配到视觉与听觉通道，避免同一通道过载
- **座舱/控制室设计**：飞行信息、告警、通信信息的通道分配
- **双任务界面**：评估操作者同时执行监控与通信任务时的干扰
- **培训设计**：设计符合资源分离原则的多技能训练方案
- **AR/VR 界面**：虚拟现实中空间与言语信息的呈现策略

## 常见误读

1. **误读**：多资源模型意味着可以无限制地并行处理，只要用不同通道。
   **正读**：各资源池容量仍有限，且中央加工阶段存在不可消除的瓶颈。资源分离可减少干扰，但不能消除容量限制。

2. **误读**：资源维度是固定不变的四维结构。
   **正读**：维度划分在理论发展中经历了修订，具体维度仍有争论。模型是一个框架而非最终结论。

3. **误读**：多资源模型只适用于传统人机界面。
   **正读**：模型可扩展到任何涉及多任务并行的情境——包括 AI 辅助决策、自动驾驶接管、多屏监控等当代场景。

## 跨学科关联

- **卡尼曼双系统**：System 1 的自动加工可视为不消耗主要资源池的过程，而 System 2 的审慎加工需要特定资源
- **认知负荷理论**：Sweller 的理论与多资源模型互补——前者关注学习设计优化，后者关注任务干扰预测
- **神经科学**：多资源模型的神经基础——不同脑区的加工特化（如 Broca 区处理言语、顶叶处理空间）
- **信息论**：资源池可类比为通信通道的带宽限制

## 进阶阅读

- Wickens, C. D. (2002). "Multiple Resources and Performance Prediction." *Theoretical Issues in Ergonomics Science*, 3(2), 159-177.
- Wickens, C. D. (2008). "Multiple Resources and Mental Workload." *Human Factors*, 50(3), 449-455.
- Kahneman, D. (1973). *Attention and Effort*. Prentice-Hall.
- Tsang, P. S. & Vidulich, M. A. (2003). *Principles and Practice of Aviation Psychology*. Erlbaum.
