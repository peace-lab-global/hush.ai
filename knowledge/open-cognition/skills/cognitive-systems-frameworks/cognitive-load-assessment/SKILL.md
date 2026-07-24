---
name: cognitive-load-assessment
description: 评估信息呈现或教学设计是否导致认知过载，基于 Sweller 的认知负荷理论。Triggers on requests to evaluate instructional materials, interface designs, or information presentations for cognitive overload.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/naturalistic-decision/sweller.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/cognitive-load.md
  - ../../domains/cognitive-systems/concepts/bounded-rationality.md
tags:
  - cognitive-load
  - instructional-design
  - information-presentation
---

# 认知负荷评估 · Cognitive Load Assessment

## 一句话功能

系统评估一个学习材料、界面设计或信息呈现方案是否导致认知过载，并给出优化建议。

## 何时使用

- 评估教学材料或课程内容的设计
- 评估界面设计中的信息呈现方式
- 分析学习者在特定任务中为什么"跟不上"
- 设计多媒体学习内容时

## 何时不使用

- 问题不在信息呈现而在动机或先验知识
- 需要评估学习效果而非学习过程
- 分析的不是学习/理解任务

## 理论基础

- 来源思想家：[斯威勒 Sweller](../../domains/cognitive-systems/schools/naturalistic-decision/sweller.md)
- 来源概念：[认知负荷](../../domains/cognitive-systems/concepts/cognitive-load.md)
- 关键文献：Sweller, J. *Cognitive Load Theory*. Springer, 2011.

## 操作流程

### Step 1：识别认知负荷类型
对当前材料/界面中的每个信息元素，判断其属于：
- **内在负荷**：材料本身的元素交互性——这个知识点本身有多复杂？
- **外在负荷**：呈现方式造成的不必要负荷——有什么可以消除的？
- **关联负荷**：促进图式建构的"好负荷"——是否被鼓励了？

### Step 2：检查外在负荷来源
逐一排查常见的外在负荷问题：
- **分裂注意**：图与文是否分离？是否需要来回切换？
- **冗余**：是否同时呈现了相同信息的多种形式（文字+语音朗读同一内容）？
- **无关信息**：是否有吸引注意但与学习无关的元素？
- **导航复杂**：找到所需信息是否需要太多操作步骤？

### Step 3：评估学习者先验知识
- 学习者的现有图式水平如何？（新手/中级/专家）
- 当前材料是否匹配其水平？（注意专家反转效应）
- 对于新手：是否需要先建立基本图式再进行问题解决？

### Step 4：提出优化建议
根据评估结果，给出具体的优化建议：
- 消除外在负荷（整合图文、去除冗余、简化导航）
- 管理内在负荷（分步呈现、从简到繁、先整体后细节）
- 增强关联负荷（引导反思、促进图式建构、自我解释）

## 完整示例

**输入场景**：
> 一个在线课程的视频教程：画面左侧是复杂的流程图，右侧是讲师的解释文字，同时有背景音乐，底部有滚动字幕。学习者反映"跟不上"。

**Skill 应用过程**：

1. **负荷类型识别**：
   - 内在负荷：流程图包含 8 个相互关联的步骤——高元素交互性
   - 外在负荷：图文分裂、背景音乐、滚动字幕——三重外在负荷
   - 关联负荷：没有引导反思或自我解释的环节

2. **外在负荷排查**：
   - 分裂注意 ❌：流程图和解释文字分处左右，需要来回切换
   - 冗余 ❌：讲师语音 + 底部字幕 + 右侧文字 = 三重冗余
   - 无关信息 ❌：背景音乐增加不必要负荷
   - 导航：单次播放，无分段控制

3. **学习者评估**：
   - 目标学习者：新手
   - 当前材料假设了中等水平的先验知识

4. **优化建议**：
   - 将解释文字直接标注在流程图对应节点上（消除分裂注意）
   - 保留语音讲解 + 关键词标注，去除完整字幕和右侧文字（消除冗余）
   - 去除背景音乐
   - 将 8 步流程分为 2 个 4 步模块，中间插入练习（管理内在负荷）
   - 在每个模块后增加"用自己的话解释"环节（增强关联负荷）

**输出**：
> 当前设计存在严重的认知过载：三重外在负荷（分裂注意+冗余+无关信息）挤占了工作记忆。建议消除外在负荷、分步管理内在负荷、增加关联负荷引导。

## 反例（误用）

**误用场景**：
> 将"学生觉得难"全部归因于认知过载——可能问题在于先验知识不足（需要补习）或动机缺乏（需要激励）。

**正确做法**：先排除先验知识和动机问题，再聚焦认知负荷。

## 关联条目

- 思想家：[斯威勒](../../domains/cognitive-systems/schools/naturalistic-decision/sweller.md)
- 概念：[认知负荷](../../domains/cognitive-systems/concepts/cognitive-load.md)
- 相关 Skill：[认知系统设计](../cognitive-system-design/SKILL.md)
