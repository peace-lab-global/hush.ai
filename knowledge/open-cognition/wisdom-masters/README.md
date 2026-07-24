# 智慧导师 · Wisdom Masters

本目录收录全世界高僧大德的思想蒸馏——以五层框架（说话/思考/判断/不做/局限）提取操作化智慧，转化为 AI Agent 可调用的 skills。

## 五层框架

| 层次 | 说明 | 映射位置 |
|------|------|----------|
| 怎么说话 | 表达 DNA——语气、节奏、用词偏好 | 触发语义 + 提问范式 |
| 怎么想 | 心智模型、认知框架 | 操作流程 Step 1-3 |
| 怎么判断 | 决策启发式 | Step N + 条件判断 |
| 什么不做 | 反模式、价值观底线 | 何时不使用 |
| 知道局限 | 诚实边界 | 反例 + 适用边界 |

## 目录结构

```
wisdom-masters/
├── masters/              # 高僧条目（人物文档）
│   ├── china/            # 中国
│   ├── india/            # 印度
│   ├── tibet/            # 藏传
│   ├── japan/            # 日本
│   └── west/             # 西方
└── skills/               # 操作化技能
```

## 已收录人物

| 人物 | 传统 | 产出 Skills |
|------|------|------------|
| [慧能](./masters/china/hui-neng.md) | 中国禅 | [无住心法](./skills/hui-neng-no-dwelling/SKILL.md) · [顿悟检验](./skills/hui-neng-sudden-awakening/SKILL.md) · [平常心引导](./skills/hui-neng-ordinary-mind/SKILL.md) |
| [临济义玄](./masters/china/linji-yixuan.md) | 中国禅·临济宗 | [无事贵人](./skills/linji-no-thing/SKILL.md) · [棒喝当下](./skills/linji-pointer-blow/SKILL.md) |
| [米拉日巴](./masters/tibet/milarepa.md) | 藏传·噶举派 | [裸见觉性](./skills/milarepa-naked-awareness/SKILL.md) · [苦行炼金](./skills/milarepa-alchemy/SKILL.md) |
| [道元](./masters/japan/dogen.md) | 日本·曹洞宗 | [只管打坐](./skills/dogen-shikantaza/SKILL.md) · [当下圆满](./skills/dogen-presence/SKILL.md) |
| [一行禅师](./masters/west/thich-nhat-hanh.md) | 入世佛教 | [正念呼吸](./skills/thich-nhat-hanh-mindful-breathing/SKILL.md) · [慈悲拥抱](./skills/thich-nhat-hanh-compassion/SKILL.md) |
| [宗喀巴](./masters/tibet/tsongkhapa.md) | 藏传·格鲁派 | [菩提道次第修行阶段指导](../skills/religion-frameworks/lamrim-stages/SKILL.md) |
| [阿底峡](./masters/tibet/atisha.md) | 藏传·噶当派 | [菩提道灯引导](../skills/religion-frameworks/bodhisattva-path-guidance/SKILL.md) |
| [莲花生大士](./masters/tibet/padmasambhava.md) | 藏传·宁玛派 | [大圆满引导](../skills/religion-frameworks/dzogchen-guidance/SKILL.md) |
| [阿姜查](./masters/thailand/ajahn-chah.md) | 南传·森林传统 | [森林禅修引导](../skills/religion-frameworks/forest-meditation-guidance/SKILL.md) |
| [佛使比丘](./masters/thailand/buddhadasa.md) | 南传佛教 | [缘起法分析](../skills/religion-frameworks/dependent-origination-analysis/SKILL.md) |
| [达摩](./masters/china/bodhidharma.md) | 中国禅宗初祖 | [壁观禅修引导](../skills/religion-frameworks/biguan-meditation/SKILL.md) |
| [马祖道一](./masters/china/mazu-daoyi.md) | 中国禅宗·洪州宗 | [平常心引导](../skills/religion-frameworks/ordinary-mind-guidance/SKILL.md) |

## 设计原则

1. **五层完整**：每条人物记录必须包含五层，不遗漏
2. **五层入 SKILL**：五层信息必须嵌入 SKILL.md 各 section
3. **反例必填**：每个 SKILL 必须有"反例（误用）"section
4. **跨传统关联**：每个条目必须连接到 domains/ 下的相关思想家
5. **不添加未经核实的信息**：所有内容需有可靠来源
6. **Compact**：人物文档 ~100 行，SKILL ~150 行

## 扩展计划

- 中国：太虚大师、南怀瑾
- 日本：铃木大拙
- 苏菲：鲁米、伊本·阿拉比
- 基督教神秘主义：十字架约翰、埃克哈特
- 印度教：室利·罗摩克里希那、室利·阿罗频多