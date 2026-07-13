---
kind: design
name: 敏感咨询记录使用 Fernet 对称加密存储
source: session
category: adr
---

# 敏感咨询记录使用 Fernet 对称加密存储

_来源：3d2d275 → 2997860 提交周期内记录的编码计划——内容为规划时意图，实现可能滞后或有出入。_

**状态：** accepted

## 背景
ServiceRecord 的 summary 和 counselor_notes 包含来访者隐私信息，属于合规要求的敏感数据，需在数据库中以密文形式持久化。

## 决策驱动
- 合规要求（PII 保护）
- 性能开销可控
- 密钥轮换能力

## 备选方案
- **应用层 Fernet 对称加密** — 优点：实现简单，加解密在 ORM 读写时透明完成；密钥由环境变量 MEDITATION_ENCRYPTION_KEY 管理，支持滚动更新；缺点：无法对密文进行模糊搜索；所有能访问 DB 的应用进程都需要持有同一密钥
- **数据库列级加密（如 PostgreSQL pgcrypto）** _（已否决）_ — 优点：密钥由数据库引擎管理，应用无需持钥；缺点：依赖特定数据库方言；查询性能更差；迁移成本高

## 决策
在 core/encryption.py 中封装 Fernet 加解密方法，ServiceRecord.summary 和 counselor_notes 字段在写入前加密、读取后解密；手机号、身份证号等 PII 字段在 API 响应层脱敏。

## 影响
满足合规要求且实现成本低；但无法对加密字段做索引或全文检索，如需搜索只能依赖非加密辅助字段；密钥泄露风险集中在单点，需配合 KMS 或外部密钥管理服务。