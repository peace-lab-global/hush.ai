---
id: automation-bias
title: 自动化偏见 · Automation Bias
type: concept
domain: cognitive-systems
school: automation-sociotechnical
era: contemporary
tags: [automation-bias, decision-making, human-automation-interaction, trust]
aliases: [自动化偏见, automation bias, 自动化偏差]
sources: ["Parasuraman & Riley (1997)", "Mosier & Skitka (1996)", "Goddard et al. (2012)"]
---

# 自动化偏见 · Automation Bias

## 一句话定义

自动化偏见是指人类在有自动化辅助时，倾向于过度依赖自动化系统的建议，即使自动化建议与可获得的其他信息相矛盾，或自动化系统本身出现错误。

## 提出者与背景

自动化偏见的概念由 Mosier & Skitka（1996）在航空领域研究中明确提出，后经 Parasuraman & Riley（1997）系统化。该概念源于对自动化系统中操作者决策行为的观察：当自动化系统可靠运行时，操作者逐渐形成了对自动化建议的依赖模式，即使面对明显的反面证据也会遵循自动化建议。

## 核心要义

自动化偏见通过两种错误形式表现：

### 委员会错误（Commission Errors）

操作者遵循了错误的自动化建议，即使有信息表明该建议不正确。例如：自动化系统错误标记了威胁，操作者根据标记采取了不必要的行动。

### 遗漏错误（Omission Errors）

操作者因自动化未发出警报而未能采取行动，即使有信息表明应当行动。例如：自动化系统未能检测到威胁，操作者因此忽略了人工检测到的信号。

自动化偏见的认知机制与卡尼曼的双系统理论相关：自动化建议为决策提供了一个"默认答案"，使操作者倾向于使用 System 1（快速直觉）而非 System 2（审慎分析）来处理信息。

## 通俗用法 vs 学术原义

| 维度 | 通俗用法 | 学术原义 |
|------|----------|----------|
| 范围 | 泛指对技术的过度信任 | 特指决策情境中对自动化建议的认知偏向 |
| 机制 | "偷懒"或"不思考" | 认知资源分配的自然倾向，在高可靠性环境中尤为突出 |
| 后果 | "科技依赖" | 系统性的决策错误（委员会错误和遗漏错误） |

## 与相关概念的关系

- **自动化自满**（Automation Complacency）：自满是自动化偏见的认知前因——因为自满而减少监控，因为减少监控而更容易接受自动化建议
- **脱离回路**（Out-of-the-Loop）：长期的自动化偏见导致操作者进一步脱离系统状态认知
- **情境意识**（Situation Awareness）：自动化偏见降低了操作者对系统状态的主动建构
- **信任校准**：自动化偏见可视为信任校准失败的表现——信任超出了系统的实际可靠性

## 代表思想家

- **Parasuraman & Riley**：系统研究了人机交互中的自动化误用与滥用
- **Mosier & Skitka**：在航空领域提出并验证了自动化偏见概念
- **Bainbridge**：自动化悖论为理解偏见产生的结构性原因提供了框架

## 应用场景

- **医疗 AI**：医生对 AI 辅助诊断建议的过度依赖，可能导致误诊
- **自动驾驶**：驾驶员对辅助驾驶系统的过度信任，降低警觉
- **航空**：飞行员对飞行管理系统的依赖，影响手动操控能力
- **司法 AI**：法官或执法人员对算法风险评估的过度依赖
- **金融**：交易员对算法交易信号的过度信任

## 常见误读

1. **误读**：自动化偏见意味着人类"懒惰"或"不理性"。
   **正读**：自动化偏见是人类认知系统在特定环境下的适应性倾向，在高可靠性系统中尤为合理但具有风险。

2. **误读**：可以通过提醒操作者"不要盲目相信"来消除偏见。
   **正读**：意识层面的提醒效果有限，因为偏见源于认知资源分配的底层机制。需要通过设计来缓解。

3. **误读**：降低自动化可靠性就能减少偏见。
   **正读**：低可靠性降低信任，但不校准信任——可能导致"自动化抛弃"（disuse）。

## 跨学科关联

- **卡尼曼双系统**：自动化偏见可理解为 System 1 对自动化默认答案的直接采纳，绕过了 System 2 的审慎审查
- **认知负荷理论**：高认知负荷条件下，自动化偏见更为显著，因为审慎分析需要更多认知资源
- **社会心理学**：自动化偏见与权威服从（Milgram）和从众效应有结构相似性

## 进阶阅读

- Parasuraman, R. & Riley, V. (1997). "Humans and Automation: Use, Misuse, Disuse, Abuse." *Human Factors*, 39(2), 230-253.
- Mosier, K. L. & Skitka, L. J. (1996). "Human Decision Makers and Automated Decision Aids." *Automation and Human Performance*, 201-218.
- Goddard, K., Roudsari, A., & Wyatt, J. C. (2012). "Automation Bias: A Systematic Review of Frequency, Effect Mediators, and Mitigators."
