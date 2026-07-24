# 贡献指南 · CONTRIBUTING

欢迎为 open-cognition 提交内容。本指南规定贡献的格式、流程与质量要求。

## 一、贡献类型

1. **新增条目**：思想家、概念、学派、宗教传统
2. **新增 Skill**：将思想框架转化为可复用的 AI 调用模板
3. **完善互链**：补充已有条目之间的跨学科关联
4. **修订错误**：纠正事实性错误、引用错误、翻译歧义

## 二、写作流程

1. 在 [templates/](./templates/) 中选择匹配模板复制
2. 根据模板填写所有必填字段
3. 在 frontmatter 中按 [TAGS.md](./TAGS.md) 规范打标
4. 至少添加 2 条权威引用（原典或重要二手研究）
5. 如条目涉及其他领域，按 [TAGS.md 关联类型](./TAGS.md#关联类型-relation-types) 标注互链
6. 在 [INDEX.md](./INDEX.md) 对应位置增加链接
7. 提交 PR 前对照 [meta/quality-criteria.md](./meta/quality-criteria.md) 自检

## 三、文件命名

- 思想家：`schools/<学派>/<姓氏拼音或英文>.md`，如 `socrates.md` `kant.md` `kongzi.md`
- 概念：`concepts/<概念英文小写连字符>.md`，如 `dialectics.md` `cultural-capital.md`
- Skill：`<领域>-frameworks/<skill-id>/SKILL.md`

## 四、引用规范

- **原典**：作者《书名》(出版年)，章节或边码
- **二手文献**：作者《书名》(出版年)，出版社
- **学术论文**：作者，论文标题，期刊名 卷(期), 出版年
- 中译本须同时标注原文标题与译者

## 五、质量底线

- 拒绝原创理论或个人感悟
- 拒绝政治/宗教传教式表达
- 拒绝引用未经核实的网络材料
- 争议性观点必须呈现至少两方立场

## 六、Skill 撰写要求

详见 [templates/skill-template.md](./templates/skill-template.md)。每个 Skill 必须：
- 使用 YAML frontmatter（name、description、triggers）
- 包含明确的"何时使用 / 何时不使用"
- 提供 1 个完整使用示例与 1 个反例
- 链接到 `domains/` 下对应的理论条目

## 七、审核标准

由维护者按 [meta/quality-criteria.md](./meta/quality-criteria.md) 审核，重点检查：
1. 事实准确性
2. 引用可靠性
3. 标签合规性
4. 互链有效性
5. 是否符合"拒绝主观评价"原则
