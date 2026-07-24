---
id: cognitive-systems.cognitive-engineering.leveson
title: 南希·莱文森 Nancy Leveson
type: thinker
domain: cognitive-systems
school: cognitive-engineering
era: modern
birth: 1944
death: null
tags: [STAMP, STPA, system-theoretic-safety, control-theory, hazard-analysis, software-safety]
aliases: [南希·莱文森, Nancy Leveson]
sources:
  - Engineering a Safer World: Systems Thinking Applied to Safety (2011)
  - Safeware: System Safety and Computers (1995)
  - System Safety Engineering and Management (1986)
---

# 南希·莱文森 Nancy Leveson

> "Accidents are not caused by failures; they are caused by inadequate control of system behavior."
> （事故不是由故障引起的，而是由对系统行为的控制不充分引起的。）

## 基本信息

- **生卒年**：1944–
- **国籍/文化背景**：美国，工程学与控制论传统
- **学术身份**：麻省理工学院航空航天系教授，美国国家工程院院士
- **学派归属**：认知工程学派（系统安全分支），STAMP/STPA方法创始人

## 核心命题

1. **安全是涌现属性**：安全不能分解到组件层面来理解或实现——它是系统各组件在动态交互中涌现出来的属性。传统"组件故障"分析忽略了涌现层面的危险。

2. **控制理论框架（STAMP）**：事故不是组件故障的链式反应，而是系统控制结构中约束不充分的结果。安全管理本质上是一个控制问题——需要对系统行为施加充分的安全约束。

3. **系统理论事故分析（STPA）**：基于控制论的危险分析方法，通过识别控制回路中的不安全控制行为来发现系统危险，替代传统的故障树和FMEA方法。

4. **超越"人为错误"**：将事故归因于"人为错误"是一种危险的简化。人的行为应在控制系统的背景下理解——操作者的决策受到组织约束、界面设计和反馈结构的塑造。

5. **软件安全的独特性**：软件不会"随机失效"，但会以设计者未预见的方式与系统环境交互。软件安全需要系统层面的分析而非传统的概率可靠性方法。

## 思想脉络

### 早期：系统安全与软件安全（1980s-1990s）

莱文森早期在航空航天和计算机科学交叉领域工作，1986年出版《System Safety Engineering and Management》，1995年出版《Safeware》。这一时期她关注计算机系统（尤其是软件）在安全关键系统中的角色，挑战了用硬件可靠性方法处理软件安全的传统做法。她继承了 Rasmussen 的系统安全思想，但认识到传统方法在软件密集型系统中的局限性。

### 中期：STAMP 理论的构建（2000s）

2000年代初，莱文森提出了 STAMP（Systems-Theoretic Accident Model and Processes），将控制论（cybernetics）系统性地引入安全分析。STAMP 将系统视为一个层次化的控制结构，安全约束通过各级控制回路来维持。这一框架直接继承了 Wiener 控制论和 Ashby 必要多样性定律的思想，将安全问题重新定义为控制约束问题。

### 晚期：STPA 方法与工程实践（2010s-至今）

2011年《Engineering a Safer World》标志着 STAMP/STPA 方法的成熟。STPA 作为基于 STAMP 的危险分析工具，已被广泛应用于航空航天、汽车（尤其是自动驾驶）、医疗设备等领域。莱文森还致力于将系统思维推广到更广泛的安全工程教育中。

## 关键著作

- *Engineering a Safer World: Systems Thinking Applied to Safety*（2011）
- *Safeware: System Safety and Computers*（1995）
- *System Safety Engineering and Management*（1986, 与 J. D. Reese 合著）

## 重要概念

- **STAMP（系统理论事故模型与过程）**：基于控制论的事故模型，将事故视为系统控制结构中约束不充分的结果
- **STPA（系统理论过程分析）**：基于 STAMP 的危险分析方法，通过分析控制回路中的不安全控制行为识别危险
- **安全约束（Safety Constraints）**：系统安全的基本单元——不是消除组件故障，而是维持对系统行为的充分约束
- **控制结构（Control Structure）**：系统中层次化的控制与反馈关系，安全管理通过该结构实现
- **不安全控制行为（Unsafe Control Actions）**：控制回路中可能导致危险的四种类型——未提供、提供过早/过晚/顺序错误、停止过早/过晚、持续时间不当

## 思想坐标

- **承接**：Rasmussen 的系统安全与认知工作分析；Wiener 的控制论；Ashby 的必要多样性定律
- **批判**：传统的"事故链"因果模型；故障树分析（FTA）和失效模式分析（FMEA）的简化主义；将"人为错误"作为事故原因的做法
- **影响**：航空航天和汽车行业安全标准的更新；STPA 被多家汽车制造商用于自动驾驶安全分析；对韧性工程的理论贡献

## 当代应用

- **自动驾驶安全**：STPA 已成为自动驾驶车辆安全分析的主要方法之一，被 Waymo、GM Cruise 等公司采用
- **医疗设备安全**：FDA 已接受 STPA 作为医疗设备安全论证的方法
- **软件安全**：STAMP 框架为软件密集型系统（如航空电子、核电控制）的安全分析提供了理论基础
- **AI 安全分析**：将 STAMP 的控制论视角应用于 AI 系统的安全约束设计
- **航天安全**：NASA 将 STPA 纳入航天系统安全分析流程
- **国防系统**：美国国防部采纳 STAMP/STPA 作为系统安全工程方法

## 常见误读

- ❌ **"STAMP 取代了所有传统安全方法"**：STAMP 是对传统方法（如 FTA、FMEA）的补充而非替代——传统方法在组件层面仍有价值，STAMP 在系统交互层面提供更深入的洞察
- ❌ **"STPA 仅适用于技术系统"**：STPA 同样适用于组织和社会系统中的控制结构分析，如医疗流程、管理决策链
- ❌ **"控制论框架意味着中央控制"**：STAMP 的"控制"概念是分布式的——系统中存在多个层次的控制回路，安全约束通过多层交互维持

## 跨学科关联

- **[继承] Rasmussen 的系统安全**：继承了 Rasmussen 对复杂系统安全的系统分析方法，将之推向控制论框架
- **[继承] Wiener 的控制论**：将 Wiener 的控制论核心思想应用于安全分析，重新定义安全为控制约束问题
- **[互补] Hollnagel 的 Safety-II**：两者都强调系统视角，Hollnagel 关注"如何成功"，Leveson 关注"如何维持约束"
- **[平行] Woods 的韧性工程**：同为系统安全理论，Woods 更强调系统的适应性能力，Leveson 更强调控制结构的设计
- **[互补] Reason 的瑞士奶酪模型**：STAMP 将 Reason 的"潜在条件"概念重新表述为"控制约束不足"
- **[参考] 漂移失败**：[参见](../../../concepts/drift-into-failure.md) — Leveson 的约束松动概念与 Dekker 的漂移概念相通

## 进阶阅读

### 原典
- Leveson, N. G. (2011). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press.
- Leveson, N. G. (1995). *Safeware: System Safety and Computers*. Addison-Wesley.
- Leveson, N. G. (2004). "A New Accident Model for Engineering Safer Systems." *Safety Science*, 42(4), 237-270.

### 二手研究
- Fleming, C. H. (2015). "Safety Assurance in Next-Generation Transportation Systems." MIT PhD Thesis.
- Abdulkhaleq, A., & Wagner, S. (2015). "Integrated Safety Analysis using Systems-Theoretic Process Analysis and Software Model Checking." *SAFECOMP 2015*.
- Thomas, J. (2013). "Extending and Automating a Systems-Theoretic Hazard Analysis Technique." MIT PhD Thesis.

## 关联 Skills

- [STPA 事故分析](../../../../skills/cognitive-systems-frameworks/stpa-accident-analysis/SKILL.md)
- [人因错误分析 Human Error Analysis](../../../../skills/cognitive-systems-frameworks/human-error-analysis/SKILL.md)
- [韧性评估 Resilience Assessment](../../../../skills/cognitive-systems-frameworks/resilience-assessment/SKILL.md)
