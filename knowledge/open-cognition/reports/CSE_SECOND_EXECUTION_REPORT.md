# 认知系统工程（CSE）二次扩展执行报告

> 执行日期：2026-05-23
> 状态：✅ 全部完成

---

## 一、执行概览

根据 [CSE 二次缺口分析报告](./CSE_SECOND_GAP_ANALYSIS.md)，从全球 CSE 知识体系视角补充了 6 个结构性缺口：安全科学、自动化与人-AI 协作、社会技术系统、宏观认知、认知工效学方法论、跨学科对话。

---

## 二、新增内容清单

### 2.1 新增学派（2 个）

| 学派 | 路径 | 定位 |
|---|---|---|
| 安全科学 Safety Science | `schools/safety-science/` | CSE 的另一半核心——复杂系统为何失败、如何建设韧性 |
| 自动化与社会技术 Automation & Sociotechnical | `schools/automation-sociotechnical/` | 自动化交互、社会技术系统、人-AI 协作 |

### 2.2 新增思想家（6 位）

| 思想家 | 学派 | 路径 | 核心贡献 |
|---|---|---|---|
| Erik Hollnagel | safety-science | `hollnagel.md` | Safety-II、ETTO 原则、CREAM、FRAM |
| James Reason | safety-science | `reason.md` | 瑞士奶酪模型、组织事故、主动失效/潜在条件 |
| Sidney Dekker | safety-science | `dekker.md` | 漂移进入失败、公正文化、Safety Differently |
| Lisanne Bainbridge | automation-sociotechnical | `bainbridge.md` | 自动化的讽刺(1983)——HF/E 最高引论文之一 |
| Raja Parasuraman | automation-sociotechnical | `parasuraman.md` | 自动化四阶段模型、人机信任、自动化自满 |
| Kim Vicente | automation-sociotechnical | `vicente.md` | CWA 五层框架、生态界面设计、社会技术系统 |

### 2.3 新增概念（12 个）

| 概念 | 路径 | 核心定义 |
|---|---|---|
| Safety-I vs Safety-II | `safety-paradigm.md` | 从"消除失败"到"确保成功"的范式转换 |
| 漂移进入失败 | `drift-into-failure.md` | 系统通过局部合理决策逐步走向灾难 |
| 正常事故 | `normal-accidents.md` | 紧耦合+交互复杂性→事故不可避免 |
| 安全文化与公正文化 | `safety-culture.md` | 组织对安全的价值观与公正问责 |
| 自动化偏见 | `automation-bias.md` | 倾向于信任自动化输出而非矛盾的非自动化信息 |
| 脱离回路 | `out-of-the-loop.md` | 自动化接管后操作者丧失态势感知 |
| 社会技术系统 | `sociotechnical-system.md` | 技术与社会子系统必须联合优化 |
| 生态界面设计 | `ecological-interface-design.md` | 界面应揭示工作领域的深层结构 |
| 宏观认知 | `macrocognition.md` | 专家在真实复杂环境中的高级认知过程 |
| 团队认知 | `team-cognition.md` | 团队层面涌现的认知属性（共享心智模型等） |
| 分布式态势感知 | `distributed-sa.md` | SA 分布在团队/系统中而非仅在个体 |
| 情境化认知 | `situated-cognition.md` | 认知根本性地嵌入物理和社会情境 |

### 2.4 新增 Skills（5 个）

| Skill | 路径 | 功能 |
|---|---|---|
| 认知任务分析 | `cognitive-task-analysis/` | 挖掘专家隐性认知策略和决策过程 |
| STPA 事故分析 | `stpa-accident-analysis/` | 基于 Leveson 系统理论的控制缺陷分析 |
| 自动化级别评估 | `automation-level-assessment/` | Parasuraman 四阶段模型评估自动化风险 |
| 人-AI 团队设计 | `human-ai-teaming/` | 设计人与 AI Agent 的协作认知系统 |
| Safety-II 学习分析 | `safety-learning-analysis/` | 分析日常工作为何通常成功（而非仅分析失败） |

---

## 三、更新文件清单

| 文件 | 更新内容 |
|---|---|
| `INDEX.md` | 扩展 CSE 索引（+2 学派、+6 思想家、+12 概念、+5 Skills）；新增"安全与风险管理""自动化与人机协作"横向主题 |
| `TAGS.md` | 新增 ~20 个标签覆盖安全科学、自动化、社会技术系统、宏观认知等 |
| `README.md` | 更新统计数字（~115 思想家 / ~84 概念 / ~82 Skills）；路线图更新至 v0.5 |

---

## 四、数量变化

| 维度 | 执行前 | 执行后 | 变化 |
|---|---|---|---|
| CSE 学派 | 5 | 7 | +2 |
| CSE 思想家 | 15 | 21 | +6 |
| CSE 概念 | 12 | 24 | +12 |
| CSE Skills | 10 | 15 | +5 |
| 全库思想家 | ~109 | ~115 | +6 |
| 全库概念 | ~73 | ~84 | +11 |
| 全库 Skills | ~77 | ~82 | +5 |
| 新增文件 | — | 25 | — |
| 修改文件 | — | 3 | — |

---

## 五、结构性影响

### 之前
CSE 领域覆盖了控制论、生态心理学、分布式认知、认知工程、自然决策五个学派，但缺少：
- 安全科学（CSE 的另一半核心）
- 自动化与人-AI 协作（AI 时代最紧迫议题）
- 社会技术系统理论（CSE 的根之一）
- 宏观认知、团队认知等高级认知概念

### 之后
```
颅内认知 ←→ 系统认知 ←→ 安全科学（新增）
(Piaget, Kahneman)  (Wiener→Rasmussen→Clark)  (Reason→Hollnagel→Dekker)
                              ↓
                    自动化与人-AI 协作（新增）
                    (Bainbridge→Parasuraman)
                              ↓
                    社会技术系统（新增）
                    (Emery/Trist→Vicente)
```

### AI 时代的关键回应
- **自动化讽刺**：LLM 越强大，人类的监控能力越差——如何设计？
- **自动化偏见**：人过度信任 AI 输出——如何校准信任？
- **Safety-II**：AI 安全不应仅关注"AI 何时出错"，更应关注"AI 通常如何成功"
- **人-AI 团队设计**：新 Skill 直接提供框架

---

## 六、下一步建议

1. **深化质量**：审核新条目的学术准确性，补充更多原典引用
2. **英文版**：将核心 CSE 条目翻译为英文
3. **可视化**：用图数据库呈现 CSE 子领域的概念网络
4. **Agent SDK**：让 AI Agent 能直接调用新增 Skills

---

**报告保存路径**：`reports/CSE_SECOND_EXECUTION_REPORT.md`
