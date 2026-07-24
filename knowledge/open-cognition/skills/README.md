# Skills 总索引

本目录收录可被 AI Agent 调用的思想框架技能。每个 Skill 是一个独立目录，包含 `SKILL.md`，遵循 YAML frontmatter + 流程化操作步骤的格式。

## 调用规范

每个 Skill 的 `SKILL.md` 顶部 frontmatter 含：
- `name`：Skill 唯一标识
- `description`：功能与触发场景
- `domain`：所属领域
- `linked_thinker` / `linked_concepts`：理论支撑条目路径
- `tags`：主题标签

AI 应用流程：
1. 根据用户请求匹配 `description` 中的触发词
2. 阅读 `操作流程` 各步骤
3. 按步骤的"提问范式"提问与分析
4. 必要时跳转到 `linked_thinker` / `linked_concepts` 阅读理论背景

## 哲学框架 philosophy-frameworks

| Skill | 用途 | 理论来源 |
|---|---|---|
| [socratic-questioning](./philosophy-frameworks/socratic-questioning/SKILL.md) | 通过追问揭示预设与矛盾 | 苏格拉底 |
| [dialectical-analysis](./philosophy-frameworks/dialectical-analysis/SKILL.md) | 正反合三段式分析 | 黑格尔 |
| [phenomenological-reduction](./philosophy-frameworks/phenomenological-reduction/SKILL.md) | 悬置成见、回到现象本身 | 胡塞尔/海德格尔 |
| [language-game-analysis](./philosophy-frameworks/language-game-analysis/SKILL.md) | 在语言使用语境中澄清概念 | 维特根斯坦 |

## 宗教框架 religion-frameworks

| Skill | 用途 | 理论来源 |
|---|---|---|
| [four-noble-truths-framework](./religion-frameworks/four-noble-truths-framework/SKILL.md) | 苦-集-灭-道四步诊治分析 | 佛教 |
| [scriptural-hermeneutics](./religion-frameworks/scriptural-hermeneutics/SKILL.md) | 经文四重义层级解读 | 基督教/犹太教传统 |
| [sacred-profane-analysis](./religion-frameworks/sacred-profane-analysis/SKILL.md) | 区分神圣域与世俗域 | 涂尔干/伊利亚德 |

## 社会学框架 sociology-frameworks

| Skill | 用途 | 理论来源 |
|---|---|---|
| [bourdieu-field-analysis](./sociology-frameworks/bourdieu-field-analysis/SKILL.md) | 场域、资本、惯习三件套分析 | 布迪厄 |
| [foucault-power-analysis](./sociology-frameworks/foucault-power-analysis/SKILL.md) | 规训、话语、生命权力分析 | 福柯 |
| [goffman-dramaturgy](./sociology-frameworks/goffman-dramaturgy/SKILL.md) | 前台/后台/印象管理分析 | 戈夫曼 |
| [weber-ideal-type](./sociology-frameworks/weber-ideal-type/SKILL.md) | 构建理想类型作为分析工具 | 韦伯 |

## 心理学框架 psychology-frameworks

| Skill | 用途 | 理论来源 |
|---|---|---|
| [jungian-archetype-identification](./psychology-frameworks/jungian-archetype-identification/SKILL.md) | 识别原型与阴影 | 荣格 |
| [cbt-cognitive-distortion](./psychology-frameworks/cbt-cognitive-distortion/SKILL.md) | 识别 10 大认知扭曲并重构 | 贝克/伯恩斯 |
| [maslow-needs-diagnosis](./psychology-frameworks/maslow-needs-diagnosis/SKILL.md) | 定位当前未满足的需求层级 | 马斯洛 |
| [flow-conditions-assessment](./psychology-frameworks/flow-conditions-assessment/SKILL.md) | 评估能否进入心流的条件 | 米哈里 |

## 撰写新 Skill

参考 [templates/skill-template.md](../templates/skill-template.md) 与 [CONTRIBUTING.md · Skill 撰写要求](../CONTRIBUTING.md#六skill-撰写要求)。
