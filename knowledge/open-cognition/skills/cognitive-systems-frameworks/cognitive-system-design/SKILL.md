---
name: cognitive-system-design
description: 设计人机协作的认知系统——功能分配、自动化层级、信任校准和界面设计，综合 Norman、Woods 和 Simon 的理论。Triggers on requests to design human-AI collaboration, automation strategies, or cognitive system architectures.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/cognitive-engineering/norman.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/joint-cognitive-system.md
  - ../../domains/cognitive-systems/concepts/bounded-rationality.md
  - ../../domains/cognitive-systems/concepts/affordance.md
tags:
  - system-design
  - human-AI
  - automation
  - cognitive-engineering
---

# 认知系统设计 · Cognitive System Design

## 一句话功能

设计人-技术联合认知系统——决定什么由人做、什么由机器做、如何分配、如何协作，以及如何设计界面以优化联合认知表现。

## 何时使用

- 设计新的人机协作系统（如 AI 辅助诊断、自动驾驶）
- 评估现有系统的自动化策略
- 优化人机界面的认知支持
- 解决"过度自动化"或"自动化不足"的问题

## 何时不使用

- 纯软件/纯硬件的技术设计（不涉及认知分工）
- 界面美学设计（不涉及认知功能）
- 简单的工具选择（不涉及系统级认知分析）

## 理论基础

- 来源思想家：[诺曼 Norman](../../domains/cognitive-systems/schools/cognitive-engineering/norman.md)、[伍兹 Woods](../../domains/cognitive-systems/schools/cognitive-engineering/woods.md)、[西蒙 Simon](../../domains/cognitive-systems/schools/cybernetics/simon.md)
- 来源概念：[联合认知系统](../../domains/cognitive-systems/concepts/joint-cognitive-system.md)
- 关键文献：Norman, D. *The Design of Everyday Things*. 1988/2013.

## 操作流程

### Step 1：认知任务分析
分析系统需要完成的所有认知功能：
- 哪些是感知功能？（检测、识别、分类）
- 哪些是推理功能？（诊断、预测、规划）
- 哪些是执行功能？（操作、控制、通信）
- 每个功能的认知需求特征是什么？（时间压力、不确定性、创造性）

### Step 2：功能分配决策
对每个认知功能，决定分配策略：

| 分配方式 | 适用条件 | 风险 |
|---|---|---|
| 完全人工 | 需要判断、创造力、伦理考量 | 人可能疲劳或出错 |
| 人主+机辅 | 人做决策，机器提供信息/建议 | 信息过载 |
| 机主+人监督 | 机器执行，人监控异常 | 自满、技能退化 |
| 机器执行+人审批 | 机器准备，人确认执行 | 审批成为橡皮图章 |
| 完全自动 | 高度结构化、低风险 | 丧失人的监督 |

### Step 3：信任校准设计
确保人对自动化的信任与实际可靠性匹配：
- **信任不足**：用户不信任可靠的系统→ 增加透明性，解释推理过程
- **信任过度**：用户过度信任不完全可靠的系统→ 明确能力边界，增加不确定性显示
- **校准工具**：置信度显示、能力边界说明、错误历史记录

### Step 4：界面认知支持设计
基于认知原则设计界面：
- **可供性**（Gibson/Norman）：让功能"可见"——用户直觉知道如何操作
- **认知负荷管理**（Sweller）：消除外在负荷，管理内在负荷
- **态势感知支持**（Endsley）：提供 Level 1-2-3 所需的信息
- **反馈**（Wiener）：每个操作都有清晰、及时的反馈

### Step 5：控制权流转设计
设计控制权在人机之间的动态转移：
- **正常模式**：谁有控制权？
- **异常模式**：何时/如何将控制权转移给人？
- **紧急模式**：紧急情况下控制权如何分配？
- **转移信号**：用什么信号通知控制权转移？

## 完整示例

**输入场景**：
> 设计一个 AI 辅助放射科诊断系统。

**Skill 应用过程**：

1. **认知任务分析**：
   - 感知：检测影像异常（结节、肿块、钙化）
   - 推理：判断异常性质（良性/恶性）、严重程度
   - 执行：生成报告、通知临床医生

2. **功能分配**：
   - 检测异常：机主+人监督（AI 标记疑似，放射科医生确认）
   - 判断性质：人主+机辅（AI 提供概率参考，医生做最终判断）
   - 生成报告：机器起草+人审批

3. **信任校准**：
   - 显示 AI 的置信度和误报率
   - 保留"不确定"选项（不强制二分类）
   - 显示类似案例的历史诊断结果

4. **界面设计**：
   - AI 标记直接在影像上高亮（可供性）
   - 避免信息过载——只显示最相关的 3-5 个发现（认知负荷管理）
   - 提供"AI 为什么这样判断"的解释（SA Level 2）

5. **控制权流转**：
   - 正常：AI 预处理+医生审核
   - AI 不确定时：标记为"需要优先人工审核"
   - 紧急发现：AI 直接弹出警告

**输出**：
> 系统采用"AI 辅助而非替代"的设计——AI 处理大量影像筛选（减少人的认知负荷），医生负责判断和决策（利用人的专业直觉和伦理考量）。关键在于信任校准和清晰的 AI 能力边界显示。

## 反例（误用）

**误用场景**：
> 将"可以自动化的都自动化"——过度自动化导致人的技能退化和情境感知丧失。

**正确做法**：自动化决策应基于认知分析——考虑信任校准、技能保持和韧性需求。

## 关联条目

- 思想家：[诺曼](../../domains/cognitive-systems/schools/cognitive-engineering/norman.md)、[伍兹](../../domains/cognitive-systems/schools/cognitive-engineering/woods.md)
- 概念：[联合认知系统](../../domains/cognitive-systems/concepts/joint-cognitive-system.md)
- 相关 Skill：[认知工作分析](../cognitive-work-analysis/SKILL.md)、[可供性分析](../affordance-analysis/SKILL.md)
