---
name: human-reliability-analysis
description: 使用人因可靠性分析方法（THERP/CREAM/SPAR-H）系统评估人为错误概率。Triggers on requests to quantify human error risk, assess system reliability, or perform probabilistic safety assessment.
domain: cognitive-systems
linked_thinker: ../../domains/cognitive-systems/schools/safety-science/hollnagel.md
linked_concepts:
  - ../../domains/cognitive-systems/concepts/human-reliability-analysis.md
  - ../../domains/cognitive-systems/concepts/joint-cognitive-system.md
tags:
  - human-reliability
  - THERP
  - CREAM
  - error-probability
  - safety-assessment
---

# 人因可靠性分析 · Human Reliability Analysis

## 一句话功能

使用人因可靠性分析方法（THERP/CREAM/SPAR-H）系统评估复杂系统中人为错误的概率——从"人会不会犯错"转向"在什么条件下以多大概率犯什么错"。

## 何时使用

- 需要量化人为错误风险（概率安全评估 PSA、人因 PRA）
- 评估核电、航空、医疗等高风险系统中操作员的可靠性
- 分析人机切换场景中驾驶员/操作员接管失败的概率
- 设计改进方案需要优先级排序（哪些人因问题最紧迫？）
- 安全审查需要人因数据支持

## 何时不使用

- 错误是故意违规而非无心之失（用纪律/管理框架）
- 不需要量化——只需定性理解错误类型（用 [人为错误分析](../human-error-analysis/SKILL.md)）
- 纯技术故障，不涉及人为因素
- 系统太简单，人为错误概率微不足道

## 理论基础

- 来源思想家：[霍伦纳格 Hollnagel](../../domains/cognitive-systems/schools/safety-science/hollnagel.md)（CREAM）、Swain & Gutmann（THERP）、[拉斯穆森 Rasmussen](../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md)（SRK 模型）
- 关键文献：Swain & Gutmann (1983) *Handbook of HRA*; Hollnagel (1998) *CREAM*

## 操作流程

### Step 1：定义系统与任务范围
明确分析对象：
- 系统是什么？（核电站应急系统、飞机自动驾驶、医疗给药流程……）
- 关注哪些任务？（应急响应、日常监控、人机切换……）
- 分析目的是什么？（PSA 量化、设计改进、安全审查……）

### Step 2：任务分析——识别步骤与潜在错误
将任务分解为可操作的步骤，对每一步识别：
- 正确执行是什么样的？
- 可能犯什么错？（遗漏、顺序错误、执行错误、选择错误）
- 错误的后果是什么？（可恢复 vs 不可恢复）

### Step 3：情境评估——绩效塑造因子（PSFs）
评估影响错误概率的情境条件：
- **人因 PSFs**：培训水平、经验、疲劳、压力、注意力
- **技术因 PSFs**：界面质量、报警设计、自动化水平
- **组织因 PSFs**：规程质量、团队沟通、管理支持
- **环境因 PSFs**：时间压力、工作环境、噪声、温度

### Step 4：错误概率估算
根据选择的方法估算：
- **THERP 方法**：查 THERP 错误概率表获取基础 HEP，用 PSFs 修正
- **CREAM 方法**：先评估共同绩效条件（CPC），推断认知控制模式，再确定错误概率区间
- **SPAR-H 方法**：选择任务类型，评估 PSFs 得到修正因子，计算最终 HEP

### Step 5：依赖性分析
检查步骤之间的关联：
- 两个步骤之间是否存在依赖？（共享信息、共享设备、时间间隔）
- 如果存在依赖，后续步骤的错误概率需要用依赖因子修正
- 依赖级别：零/低/中/高/完全

### Step 6：汇总与报告
- 计算任务总体人误概率
- 识别高风险步骤（HEP 最高的环节）
- 提出设计改进建议（优先改进哪些 PSFs）
- 不确定性分析（概率区间的上下界）

## 完整示例

**输入场景**：
> 评估核电站应急给水系统中，操纵员在失去主给水后启动应急给水程序的人因可靠性。

**Skill 应用过程**：

1. **定义范围**：核电站应急给水系统，关注"失去主给水后的应急响应"任务

2. **任务分析**：
   - 步骤 1：识别主给水丧失（报警响应）→ 可能错误：未注意报警（HEP 基础值 0.01）
   - 步骤 2：确认故障类型 → 可能错误：误判为其他故障（HEP 基础值 0.05）
   - 步骤 3：启动应急给水泵 → 可能错误：操作错误阀门（HEP 基础值 0.001）
   - 步骤 4：确认应急给水流量 → 可能错误：未确认就认为正常（HEP 基础值 0.01）

3. **PSFs 评估**：
   - 培训水平：良好（修正因子 1.0）
   - 时间压力：高——应急场景（修正因子 5.0）
   - 报警设计：多报警同时响起——信息过载（修正因子 3.0）

4. **概率估算**（使用 SPAR-H 简化方法）：
   - 步骤 1 修正后 HEP：0.01 × 5.0 × 3.0 = 0.15
   - 步骤 3 修正后 HEP：0.001 × 5.0 = 0.005

5. **依赖性分析**：步骤 1 和步骤 2 共享信息源——高依赖，步骤 2 的错误概率需修正

6. **汇总**：任务总 HEP ≈ 0.16（主要由报警响应步骤贡献）

**输出**：
> 应急给水程序的主要人因风险在报警响应阶段——多报警信息过载 + 时间压力使 HEP 从基线 0.01 上升到 0.15。建议：简化报警界面、增加优先级过滤、增加自动诊断辅助。

## 反例（误用）

**误用场景**：
> 对办公室文员的日常打字任务进行 HRA，计算每页文档打错字的概率。

**问题**：打字错误无安全后果，不值得用 HRA 这种重方法。用简单的错误率统计就够了。HRA 的价值在于高风险场景中将人为因素纳入工程可靠性框架。

## 关联条目

- 思想家：[霍伦纳格 Hollnagel](../../domains/cognitive-systems/schools/safety-science/hollnagel.md)、[Reason](../../domains/cognitive-systems/schools/safety-science/reason.md)、[Rasmussen](../../domains/cognitive-systems/schools/cognitive-engineering/rasmussen.md)
- 概念：[人因可靠性分析](../../domains/cognitive-systems/concepts/human-reliability-analysis.md)、[联合认知系统](../../domains/cognitive-systems/concepts/joint-cognitive-system.md)
- 相关 Skill：[人为错误分析](../human-error-analysis/SKILL.md)、[STPA 事故分析](../stpa-accident-analysis/SKILL.md)
