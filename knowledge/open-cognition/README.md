# Open Cognition · 开放认知数据库

> 一个面向**人类深度阅读**与 **AI Agent 调用**的跨学科认知资源库。
> 把哲学、宗教、社会学、心理学、伦理学、美学中**最值得反复使用的思想、命题、方法**整理成可链接、可检索、可复用的开源知识结构。

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](./LICENSE)
[![Status](https://img.shields.io/badge/status-v0.1%20foundation-blue.svg)](#)

---

## 项目目标

跨学科的洞见常常分散在难以阅读的原典与互不通话的学派之中。本项目希望：

1. **降低门槛** — 用 ~100 行的紧凑条目快速建立对一个思想家/概念的整体感。
2. **保持深度** — 拒绝鸡汤式简化，每条目附原典、研究、入门三层进阶阅读。
3. **跨学科互链** — 显式标注 `[同源]/[互补]/[对立]/[发展]/[批判]/[平行]/[张力]/[继承]/[借用]/[下位]` 等关联类型。
4. **可被 Agent 直接调用** — 提炼出标准化的 **Skill**（操作框架），让 LLM 与人类都能用同一份知识做事。

---

## 内容总览

```
7 个领域 × N 思想家/条目 + 概念条目 + Skills
= ~120 思想家 + ~87 概念 + ~83 Skills
```

| 领域 | 条目结构 | 入口 |
|---|---|---|
| 哲学 Philosophy | 28 思想家 / 8 概念 / 19 Skills | [domains/philosophy](./domains/philosophy/README.md) |
| 宗教 Religion | 16 条目 / 4 跨传统概念 / 14 Skills | [domains/religion](./domains/religion/README.md) |
| 社会学 Sociology | 18 思想家 / 7 概念 / 15 Skills | [domains/sociology](./domains/sociology/README.md) |
| 心理学 Psychology | 25 思想家 / 8 概念 / 16 Skills | [domains/psychology](./domains/psychology/README.md) |
| 伦理学与政治哲学 Ethics & Political Philosophy | 15 思想家 / 11 概念 / 10 Skills | [domains/ethics-politics](./domains/ethics-politics/README.md) |
| 美学与艺术哲学 Aesthetics | 23 思想家 / 7 概念 / 3 Skills | [domains/aesthetics](./domains/aesthetics/README.md) |
| 认知系统工程 Cognitive Systems Engineering | ~25 思想家 / ~26 概念 / ~16 Skills | [domains/cognitive-systems](./domains/cognitive-systems/README.md) |

完整索引见 [INDEX.md](./INDEX.md) ｜ 标签词典见 [TAGS.md](./TAGS.md)。

---

## 仓库结构

```
open-cognition/
├── README.md                   # 本文件
├── INDEX.md                    # 全库双视角索引（领域 + 主题 + Skills）
├── TAGS.md                     # 统一标签词典与关联类型
├── CONTRIBUTING.md             # 贡献指南
├── domains/                    # 知识条目主体
│   ├── philosophy/
│   │   ├── README.md
│   │   ├── schools/<流派>/<思想家>.md
│   │   └── concepts/<概念>.md
│   ├── religion/
│   │   ├── README.md
│   │   ├── traditions/<传统>/<条目>.md
│   │   └── concepts/<跨传统概念>.md
│   ├── sociology/
│   │   ├── README.md
│   │   ├── schools/<流派>/<思想家>.md
│   │   └── concepts/<概念>.md
│   ├── psychology/
│   │   ├── README.md
│   │   ├── schools/<流派>/<思想家>.md
│   │   └── concepts/<概念>.md
│   ├── ethics-politics/
│   │   ├── README.md
│   │   ├── schools/<学派>/<思想家>.md
│   │   └── concepts/<概念>.md
│   └── cognitive-systems/
│       ├── README.md
│       ├── schools/<学派>/<思想家>.md
│       └── concepts/<概念>.md
├── skills/                     # Agent 可调用的操作框架
│   ├── philosophy-frameworks/<skill>/SKILL.md
│   ├── religion-frameworks/
│   ├── sociology-frameworks/
│   ├── psychology-frameworks/
│   ├── ethics-politics-frameworks/
│   └── cognitive-systems-frameworks/
├── templates/                  # 思想家/概念/学派/Skill 模板
└── meta/                       # 分类法、引用源、质量标准
```

---

## 三种条目类型

### 1. 思想家 Thinker
固定结构：基本信息 / 核心命题 / 思想脉络 / 关键著作 / 重要概念 / 思想坐标 / 当代应用 / 常见误读 / 跨学科关联 / 进阶阅读 / 关联 Skills。

例：[弗洛伊德](./domains/psychology/schools/psychoanalysis/freud.md)、[韦伯](./domains/sociology/schools/classical/weber.md)、[康德](./domains/philosophy/schools/german-idealism/kant.md)。

### 2. 概念 Concept
固定结构：一句话定义 / 历史脉络 / 核心要义 / 通俗 vs 学术 / 与相关概念关系 / 代表思想家 / 应用场景 / 常见误读 / 跨学科关联 / 进阶阅读。

例：[心流 Flow](./domains/psychology/concepts/flow.md)、[文化资本](./domains/sociology/concepts/cultural-capital.md)、[神圣性](./domains/religion/concepts/sacred.md)。

### 3. Skill
agent 可执行的操作框架，含 YAML frontmatter + 一句话功能 + 何时用/不用 + 理论基础 + 操作流程（Step 1–N） + 完整示例 + 反例。

例：[CBT 认知扭曲识别](./skills/psychology-frameworks/cbt-cognitive-distortion/SKILL.md)、[布迪厄场域分析](./skills/sociology-frameworks/bourdieu-field-analysis/SKILL.md)、[四圣谛诊断](./skills/religion-frameworks/four-noble-truths-framework/SKILL.md)。

---

## 使用方式

### 给人类读者
- **横向阅读**：选一个主题（如 [自我 Self](./INDEX.md#自我-self)），跨四个领域纵览不同视角。
- **纵向阅读**：从领域 README 进入流派，深度走完一个学派。
- **诊断式阅读**：遇到具体困境时，使用对应 Skill（例如个人迷茫 → [马斯洛需求诊断](./skills/psychology-frameworks/maslow-needs-diagnosis/SKILL.md)）。

### 给 AI Agent
所有 Skill 文件遵循统一 frontmatter 格式：

```yaml
---
name: <skill-id>
description: <一句话功能>
domain: <philosophy|religion|sociology|psychology>
linked: [相关条目相对路径...]
tags: [...]
---
```

可被 agent runtime（如 Claude Skills、自定义 RAG）直接索引、调用。条目之间的跨链使用相对路径与显式关联类型，便于 LLM 推理图谱。

### 示例 Prompt
> "用 [CBT 认知扭曲识别](./skills/psychology-frameworks/cbt-cognitive-distortion/SKILL.md) 分析下面这段独白：……"
>
> "把以下职场困境同时用 [马斯洛需求诊断](./skills/psychology-frameworks/maslow-needs-diagnosis/SKILL.md) 与 [布迪厄场域分析](./skills/sociology-frameworks/bourdieu-field-analysis/SKILL.md) 跑一遍。"

---

## 设计原则

1. **紧凑而非压缩** — 每条目控制在约 100 行内，但保留必要的张力与原文语境。
2. **多源验证** — 条目以原典为锚，二手研究为镜，中文资源为桥。
3. **诚实标注误读** — 每条目设"常见误读"，明确说明哪些流行说法偏离原意。
4. **关联可追溯** — 跨学科链接使用统一的关联类型标注，便于追问"为什么相关"。
5. **持续可贡献** — 模板与质量标准开放，欢迎补充传统与流派。

---

## 路线图

- ✅ **v0.1**：五领域基础骨架。
- ✅ **v0.2**：六领域全面扩展 + 全球顶尖人物全量补充。
- ✅ **v0.3**：文学家/文艺家全面融合。美学领域从 7 人扩展到 23 人。
- ✅ **v0.4**：新增**认知系统工程**领域——控制论(维纳/阿什比/西蒙)、生态心理学(吉布森/克拉克/瓦雷拉)、分布式认知(哈钦斯/恩格斯托姆/列昂捷夫)、认知系统工程(拉斯穆森/伍兹/诺曼)、自然决策(克莱因/维克/斯威勒)。15 位思想家 + 12 个概念 + 10 个 Skills。补齐"认知作为人-技术-环境联合系统的涌现"这条缺失轴线。
- ✅ **v0.5（当前）**：CSE 领域深度扩展——新增安全科学学派(霍伦纳格/里森/德克尔)、自动化与社会技术学派(班布里奇/帕拉休拉曼/维森特)。新增 4 个概念(宏观认知/团队认知/分布式态势感知/情境化认知)和 5 个 Skills(认知任务分析/STPA 事故分析/自动化级别评估/人 AI 协作设计/安全学习分析)。补齐安全科学和人机协作两条关键轴线。
- 🔮 **v0.6**：英文版、可视化关联图谱、Agent SDK 集成示例。

---

## 贡献

欢迎贡献新条目、修订误读、补充跨学科链接。请先阅读：

- [CONTRIBUTING.md](./CONTRIBUTING.md) — 贡献流程
- [meta/quality-criteria.md](./meta/quality-criteria.md) — 质量标准
- [TAGS.md](./TAGS.md) — 标签与关联类型规范
- [templates/](./templates/) — 各类型条目模板

---

## 许可

内容采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可，欢迎在标注来源的前提下自由使用、修改与分发。

---

## 致谢

本项目站在每位被收录思想家与无数学者的肩膀上。所列条目仅为入门指引，原典与一流二手研究永远是不可替代的。
