---
name: affordance-analysis
description: 分析环境或界面如何提供或限制行动可能性，基于 Gibson 的生态心理学和 Norman 的设计心理学。Triggers on requests to analyze usability, evaluate interface design, or understand how environments enable or constrain action.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/ecological/gibson.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/affordance.md
tags:
  - affordance
  - design
  - usability
  - ecological-psychology
---

# 可供性分析 · Affordance Analysis

## 一句话功能

分析环境、界面或产品如何提供（或限制）行动可能性——找到"用户为什么不知道怎么操作"的根因，并提出改善建议。

## 何时使用

- 评估产品/界面/环境的可用性
- 理解用户为什么"不知道怎么用"
- 设计新功能时分析行动可能性
- 分析物理或数字空间中的行动引导

## 何时不使用

- 问题是技术性的（功能缺失而非可供性问题）
- 用户有明确的使用说明书（依赖文档而非直觉）
- 需要评估审美而非功能

## 理论基础

- 来源思想家：[吉布森 Gibson](../../domains/cognitive-systems/schools/ecological/gibson.md)、[诺曼 Norman](../../domains/cognitive-systems/schools/cognitive-engineering/norman.md)
- 来源概念：[可供性](../../domains/cognitive-systems/concepts/affordance.md)
- 关键文献：Norman, D. *The Design of Everyday Things*. 1988/2013.

## 操作流程

### Step 1：识别目标行动者
明确分析面向谁：
- 行动者的身体特征（身高、手的大小、视力）
- 行动者的经验和知识水平
- 行动者的文化和语言背景
- **同一物体对不同行动者有不同可供性**——门把手对儿童可能不提供"拉"

### Step 2：列举预期行动
这个界面/产品/环境应该支持哪些行动？
- 核心行动（必须能做的）
- 次要行动（可以做的）
- 禁止行动（不应该做的）

### Step 3：分析可供性状态
对每个预期行动，分析当前状态：

| 状态 | 含义 | 表现 |
|---|---|---|
| **强可供性** | 行动直觉明显 | 用户一看就知道怎么用 |
| **弱可供性** | 行动存在但不明显 | 用户需要探索或提示 |
| **假可供性** | 看起来可以做但实际不能 | 用户尝试后失败（最糟糕） |
| **反可供性** | 阻止某行动 | 防止误操作 |
| **隐藏可供性** | 存在但用户不知道 | 高级功能未被使用 |

### Step 4：提出改善建议
- **弱→强**：增加视觉/触觉提示，让功能更"可见"
- **消除假可供性**：让不可操作元素"看起来"不可操作（灰色化、去除按钮样式）
- **增强反可供性**：用物理约束或逻辑约束防止误操作
- **揭示隐藏可供性**：通过教程、渐进式披露让高级功能变得可见

## 完整示例

**输入场景**：
> 一款新设计的玻璃门，用户经常推而不是拉，导致撞门。

**Skill 应用过程**：

1. **目标行动者**：成年人（身高 150-190cm），有门的使用经验

2. **预期行动**：
   - 核心：打开门（拉）
   - 禁止：推门

3. **可供性状态分析**：
   - 当前设计：门两侧都有竖直把手
   - 把手对"拉"提供弱可供性（可以拉，但也可以推）
   - 平面门板对"推"提供强可供性（平面暗示推）
   - **假可供性**：推的一侧看起来可以推（平面），但实际需要拉
   - 结果：用户推门→撞门

4. **改善建议**：
   - 拉的一侧：安装横向把手（强"拉"可供性）
   - 推的一侧：安装平板推板（强"推"可供性）
   - 添加"拉/推"文字（补充弱可供性）
   - 最佳：去掉把手一侧的横杆——只留推板（消除假可供性）

**输出**：
> 撞门不是用户的问题——是门的设计创造了假可供性。解决方案是让拉/推的物理提示与实际操作方向一致。

## 反例（误用）

**误用场景**：
> 把所有可用性问题都归为"可供性不足"——可能是认知负荷过高、反馈不足或心智模型错误。

**正确做法**：可供性分析是可用性诊断的一部分——结合认知负荷、反馈和心智模型综合判断。

## 关联条目

- 思想家：[吉布森](../../domains/cognitive-systems/schools/ecological/gibson.md)、[诺曼](../../domains/cognitive-systems/schools/cognitive-engineering/norman.md)
- 概念：[可供性](../../domains/cognitive-systems/concepts/affordance.md)
- 相关 Skill：[认知系统设计](../cognitive-system-design/SKILL.md)、[认知负荷评估](../cognitive-load-assessment/SKILL.md)
