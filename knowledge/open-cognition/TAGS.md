# 标签词典 · TAGS

本词典定义全库统一的四维标签体系。所有条目 frontmatter 中的 `tags` 字段必须从此清单中选取，避免冗余与拼写差异。

---

## 维度 1：领域 Domain

| 标签 | 含义 |
|---|---|
| `philosophy` | 哲学 |
| `religion` | 宗教 |
| `sociology` | 社会学 |
| `psychology` | 心理学 |
| `cognitive-systems` | 认知系统工程 |

## 维度 2：流派 School

### 哲学
`presocratic` `classical-greek` `hellenistic` `medieval-scholastic` `rationalism` `empiricism` `german-idealism` `existentialism` `phenomenology` `analytic` `pragmatism` `critical-theory` `confucian` `daoist` `buddhist-philosophy`

### 宗教
`buddhism-theravada` `buddhism-mahayana` `buddhism-zen` `christianity-catholic` `christianity-protestant` `christianity-orthodox` `christianity-mysticism` `islam-sunni` `islam-shia` `sufism` `judaism-rabbinic` `judaism-kabbalah` `hinduism-vedanta` `taoism-religious` `taoism-philosophical`

### 社会学
`functionalism` `conflict-theory` `symbolic-interactionism` `structuralism` `post-structuralism` `critical-theory` `phenomenological-sociology` `network-theory` `world-systems`

### 心理学
`psychoanalysis` `analytical-psychology` `individual-psychology` `behaviorism` `cognitive` `humanistic` `existential-psychology` `positive-psychology` `cognitive-behavioral` `developmental` `social-psychology`

### 认知系统工程
`cybernetics` `ecological-psychology` `distributed-cognition` `activity-theory` `cognitive-engineering` `naturalistic-decision` `resilience-engineering` `cognitive-ergonomics` `embodied-cognition` `4E-cognition` `safety-science` `safety-II` `automation-sociotechnical` `sociotechnical-systems` `human-automation-interaction` `perrow` `leveson` `endsley` `sheridan` `wickens`

## 维度 3：时代 Era

| 标签 | 范围 |
|---|---|
| `ancient` | 公元前到公元 5 世纪 |
| `medieval` | 5 世纪到 15 世纪 |
| `early-modern` | 16 世纪到 18 世纪 |
| `modern` | 19 世纪到 20 世纪初 |
| `contemporary` | 20 世纪至今 |

## 维度 4：主题 Theme

跨学科横向主题，用于 INDEX.md 横向索引：

`epistemology` `ethics` `metaphysics` `ontology` `aesthetics` `political` `power` `self` `consciousness` `unconscious` `meaning` `suffering` `death` `freedom` `community` `language` `body` `time` `truth` `god-divine` `salvation` `liberation` `ritual` `sacred-profane` `social-structure` `social-action` `culture` `class` `gender` `modernity` `rationality` `motivation` `emotion` `cognition` `development` `personality` `therapy` `wellbeing` `bounded-rationality` `affordance` `cognitive-load` `situation-awareness` `distributed-cognition` `sensemaking` `mental-model` `resilience` `joint-cognitive-system` `predictive-processing` `enaction` `human-error` `system-design` `feedback` `autopoiesis` `macrocognition` `team-cognition` `distributed-SA` `situated-cognition` `safety-paradigm` `drift-into-failure` `normal-accidents` `safety-culture` `automation-bias` `automation-paradox` `out-of-the-loop` `ecological-interface-design` `cognitive-task-analysis` `just-culture` `human-reliability` `multiple-resources` `automation-autonomy` `STAMP` `STPA` `SAGAT` `supervisory-control`

---

## 关联类型 Relation Types

跨条目互链时，必须在链接旁注明关联类型：

| 标记 | 含义 | 示例 |
|---|---|---|
| `[同源]` | 思想直接继承 | 阿德勒 [同源] 弗洛伊德 |
| `[互补]` | 不同视角解释同一现象 | 佛教苦谛 [互补] 存在主义焦虑 |
| `[对立]` | 立场相反 | 行为主义 [对立] 人本主义 |
| `[发展]` | 后者发展前者 | 新弗洛伊德主义 [发展] 弗洛伊德 |
| `[批判]` | 后者批判前者 | 福柯 [批判] 启蒙理性 |
| `[平行]` | 独立形成相似洞见 | 庄子 [平行] 维特根斯坦语言观 |

---

## 使用规范

1. 每条目 frontmatter 必须至少包含一个领域标签、一个流派标签、一个时代标签和 1–3 个主题标签。
2. 不允许在 frontmatter 中创造未登记标签；如需新增，先在本文件登记。
3. 大小写统一为小写，多词用连字符 `-`。
