---
id: human-reliability-analysis
title: 人因可靠性分析 · Human Reliability Analysis (HRA)
type: concept
domain: cognitive-systems
school: safety-science
era: contemporary
tags: [human-reliability, THERP, CREAM, SPAR-H, error-probability, safety-assessment]
aliases: [人因可靠性分析, HRA, Human Reliability Analysis, 人误率预测]
sources:
  - title: "Handbook of Human Reliability Analysis with Emphasis on Nuclear Power Plant Applications"
    author: A. D. Swain & H. E. Gutmann
    year: 1983
  - title: "Cognitive Reliability and Error Analysis Method (CREAM)"
    author: Erik Hollnagel
    year: 1998
---

# 人因可靠性分析 · Human Reliability Analysis (HRA)

## 一句话定义

系统性地预测和分析复杂系统中人为错误概率的方法论——不是问"人会不会犯错"，而是问"在什么条件下、以多大概率、犯什么类型的错"。

## 提出者与背景

- **开创者**：A. D. Swain & H. E. Gutmann（1983），美国桑迪亚国家实验室
- **历史语境**：三里岛核电站事故（1979）暴露了传统工程可靠性分析忽略人为因素的致命缺陷——安全系统的设计假设人总是正确操作，但事实并非如此
- **针对的问题**：如何将人为错误纳入系统可靠性量化评估？如何预测人在特定情境下的错误概率？

## 核心要义

### 三代 HRA 方法的演进

| 代际 | 代表方法 | 核心思路 | 局限 |
|------|----------|----------|------|
| 第一代 | THERP（1983） | 任务分析 + 错误概率表 | 忽略情境因素，将人视为机器组件 |
| 第二代 | CREAM（1998）、ASEP | 认知模型 + 情境依赖 | 主观性强，数据获取困难 |
| 第三代 | 贝叶斯方法 + 仿真 | 动态概率 + 不确定性建模 | 模型复杂，实际应用门槛高 |

### 关键方法

1. **THERP**（Technique for Human Error Rate Prediction）：Swain & Gutmann 开创——将任务分解为步骤，查表获取每步错误概率，通过事件树分析错误传播
2. **CREAM**（Cognitive Reliability and Error Analysis Method）：Hollnagel 提出——基于认知模型，先评估共同绩效条件（CPC），再推断错误模式和概率
3. **SPAR-H**（Standardized Plant Analysis Risk-Human Reliability Analysis）：美国核管会方法——简化的人因可靠性评估，适用于概率安全评估（PSA）
4. **HEART**（Human Error Assessment and Reduction Technique）：英国方法——通用任务类型的错误概率 + 绩效影响因子调整

### 核心概念

- **绩效塑造因子（PSFs, Performance Shaping Factors）**：影响人为错误概率的情境变量——疲劳、压力、培训水平、界面质量、时间压力等
- **人误概率（HEP, Human Error Probability）**：在特定条件下人为执行某任务时出错的概率
- **依赖性因子（Dependency Factor）**：当两个任务步骤之间存在关联时，后续步骤的错误概率需要修正

## 通俗用法 vs 学术原义

| 维度 | 通俗用法 | 学术原义 |
|------|----------|----------|
| 人因可靠性分析 | "评估人靠不靠谱" | 系统性的概率评估方法论，将人为因素纳入工程可靠性框架 |
| 人为错误概率 | "人有多大概率犯错" | 在特定情境条件（PSFs）下执行特定任务的条件概率 |
| 绩效塑造因子 | "影响表现的因素" | 可量化的情境变量，用于修正基础错误概率 |

## 与相关概念的关系

- **同源**：[正常事故论](./normal-accidents.md) — HRA 试图量化 Perrow 认为不可避免的事故概率
- **互补**：Reason 的瑞士奶酪模型 — Reason 解释错误如何穿透防线，HRA 量化穿透概率
- **基础**：[拉斯穆森 Rasmussen](../schools/cognitive-engineering/rasmussen.md) 的 SRK 模型 — HRA 的认知分类框架
- **发展**：[韧性工程](./resilience-engineering.md) — HRA 关注"为什么会失败"，韧性工程关注"为什么通常成功"
- **应用**：[联合认知系统](./joint-cognitive-system.md) — HRA 可用于评估人机联合系统的可靠性

## 代表思想家

- Swain & Gutmann — THERP 方法开创者（1983）
- [Hollnagel](../schools/safety-science/hollnagel.md) — CREAM 方法提出者（1998），安全-II 倡导者
- [Reason](../schools/safety-science/reason.md) — 瑞士奶酪模型，HRA 的理论背景
- [Rasmussen](../schools/cognitive-engineering/rasmussen.md) — SRK 认知模型，HRA 的认知分类基础
- Nancy Leveson — STAMP/STPA 方法，系统理论视角的补充

## 应用场景

- **核电安全**：概率安全评估（PSA）中的人因分析——量化操作员在应急程序中的错误概率
- **航空**：飞行员操作程序的可靠性评估——起飞、着陆、应急程序中的人误概率
- **医疗**：用药安全、手术安全中的人因可靠性评估
- **石油化工**：过程控制操作中的人误概率分析
- **自动驾驶**：人机切换场景中驾驶员接管失败的概率评估

## 常见误读

- ❌ "HRA 能精确预测人什么时候犯错" → HRA 提供的是概率区间而非精确预测——不确定性是 HRA 的固有特征。
- ❌ "THERP 已经过时了" → THERP 的任务分析方法仍是 HRA 的基础——后续方法在此基础上加入了情境因素。
- ❌ "HRA 只关注个体错误" → 现代 HRA 越来越关注团队和组织层面的人因问题——这正是 CREAM 和第三代方法的发展方向。

## 跨学科关联

- [卡尼曼 Kahneman](../../../psychology/schools/cognitive/kahneman.md) `[启发]` 双系统理论解释了 HRA 中技能型错误（系统1）和知识型错误（系统2）的认知基础
- [阿什比 Ashby](../schools/cybernetics/ashby.md) `[平行]` 必要多样性法则——当系统复杂性超出操作者处理能力时，错误概率必然上升
- [贝克 Beck](../../../sociology/schools/modernity/beck.md) `[平行]` 风险社会理论——HRA 是量化"风险"的技术手段

## 进阶阅读

- Swain, A. D. & Gutmann, H. E. *Handbook of Human Reliability Analysis with Emphasis on Nuclear Power Plant Applications*. NUREG/CR-1278, 1983.
- Hollnagel, E. *Cognitive Reliability and Error Analysis Method (CREAM)*. Elsevier, 1998.
- Kirwan, B. *A Guide to Practical Human Reliability Assessment*. Taylor & Francis, 1994.
- Hollnagel, E. *Human Reliability Analysis: Context and Control*. Academic Press, 1993.
