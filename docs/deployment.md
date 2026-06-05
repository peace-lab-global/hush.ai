# 冥想服务部署指南（可逐步执行）

本文档描述 **小观 / 冥想导师数字人平台**（`hushai.meditation`）从开发到生产落地的部署步骤。按章节顺序执行即可。
**只要最少命令跑起来**，请直接看 [最小化部署](deployment-minimal.md)；本文从 **阶段一** 起与最小化重叠，并继续覆盖 PostgreSQL、向量持久化与生产运维。

---

## 1. 架构与组件

| 组件 | 作用 | 典型部署 |
|------|------|----------|
| **FastAPI 应用** | HTTP API、静态对话页、管理后台 | 单进程 Uvicorn 或多 Worker + 反代 |
| **关系库** | 用户、对话、消息、记忆、知识块元数据 | SQLite（开发）或 **PostgreSQL**（生产） |
| **Chroma 向量** | 记忆与知识库语义检索（RAG） | 本机目录 **`MEDITATION_CHROMA_DIR`** 持久化（推荐） |
| **LLM / Embedding** | 对话与向量化 | OpenAI 兼容 API（密钥与可选 Base URL） |

说明：仓库内 `docker-compose.yml` 中的 **ChromaDB 容器**对外暴露 `8001` 端口；**当前应用代码默认使用嵌入式 Chroma**（`PersistentClient` + 本地目录），**不会自动连接该容器**。生产环境推荐为应用挂载一块磁盘并设置 `MEDITATION_CHROMA_DIR`，无需单独跑 Chroma 容器，除非自行扩展为 HttpClient 连接远程 Chroma（需改代码）。PostgreSQL 容器与 Compose 中的 `postgres` 服务一致，应用通过 `MEDITATION_POSTGRES_URL` 连接。

---

## 2. 前置条件

- **操作系统**：Linux / macOS（Windows 可用 WSL2）
- **Python**：3.9+（推荐 3.11+）
- **可选**：Docker 与 Docker Compose（用于 PostgreSQL；Chroma 见上文）
- **网络**：能访问所选 LLM 与 Embedding API（如 OpenAI 或兼容网关）

---

## 阶段 0：获取代码与虚拟环境

```bash
git clone https://github.com/peace-lab-global/hush.ai.git
cd hush.ai
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

python3 -m pip install -U pip
python3 -m pip install -e ".[meditation]"
```

验证：

```bash
python3 -c "from hushai.meditation.app import create_app; create_app(); print('ok')"
```

---

## 阶段 1：最小可运行（SQLite + 本机开发）

不启动 Docker，使用默认 **SQLite**（数据库文件一般在项目目录下的 `meditation_local.db`，由 `hushai/meditation/db/session.py` 解析）。

**1）设置最小环境变量**

```bash
export MEDITATION_JWT_SECRET="请替换为足够长的随机字符串"
export MEDITATION_OPENAI_API_KEY="sk-..."   # 或你使用的兼容 API Key
```

**2）启动服务（必须使用 factory）**

```bash
python3 -m uvicorn hushai.meditation.app:get_app --factory --host 0.0.0.0 --port 8000
```

**3）验证**

| 检查项 | 命令或操作 |
|--------|------------|
| 健康检查 | `curl -s http://127.0.0.1:8000/health` → `{"status":"ok"}` |
| 对客页 | 浏览器打开 `http://127.0.0.1:8000/` |
| 管理后台 | `http://127.0.0.1:8000/admin/`（默认账号见登录页或下方管理员变量） |
| API 文档 | `http://127.0.0.1:8000/debug`（Swagger） |

可选：复制环境变量模板并编辑：

```bash
cp .env.example .env
# 使用 direnv 或手动 export：在启动前 source 或注入进程环境
```

---

## 阶段 2：使用 Docker 启动 PostgreSQL

适用于需要 **并发写入、备份、多实例** 的生产库。

**1）启动数据库**

```bash
docker compose up -d postgres
```

默认凭据与 `docker-compose.yml` 一致：`hush` / `hush123`，库名 `hush_meditation`，端口 `5432`。

**2）配置应用连接**

应用支持 `postgresql://` 写法，会在内部转为 `postgresql+asyncpg://`：

```bash
export MEDITATION_POSTGRES_URL="postgresql://hush:hush123@localhost:5432/hush_meditation"
```

**3）启动应用**（同阶段 1 的 uvicorn 命令）

首次启动会执行 `init_db()` 建表，无需单独跑 Alembic（若仓库后续加入迁移，以仓库说明为准）。

**4）验证**

登录管理后台，新建用户或对话，确认数据写入 PostgreSQL（可用 `psql` 或 GUI 连接查看表）。

---

## 阶段 3：向量库与 RAG（知识库 / 记忆检索）

**1）持久化目录（推荐）**

```bash
export MEDITATION_CHROMA_DIR="/var/lib/hush/chroma_data"   # 示例路径，请换为你的卷
mkdir -p "$MEDITATION_CHROMA_DIR"
```

确保运行进程的用户对该目录 **可读写**。重启应用后，导入知识库与记忆向量会写入该目录。

**2）Embedding 配置**

默认使用 OpenAI 兼容 Embedding：

```bash
export MEDITATION_EMBEDDING_PROVIDER=openai
export MEDITATION_EMBEDDING_MODEL=text-embedding-3-small
# 可选：单独指定（否则复用 MEDITATION_OPENAI_API_KEY）
# export MEDITATION_EMBEDDING_API_KEY=sk-...
# export MEDITATION_EMBEDDING_BASE_URL=https://api.openai.com/v1
```

未设置 `MEDITATION_CHROMA_DIR` 时，Chroma 可能以内存模式运行，**进程重启后向量丢失**，生产环境务必设置持久化路径。

**3）验证 RAG**

在管理后台 **导入知识库**（文本或 Markdown），发起与内容相关的对话，观察模型是否引用「相关理论参考」（由 `get_knowledge_context_for_prompt` 注入）。

---

## 阶段 4：安全与运维相关环境变量

| 变量 | 说明 |
|------|------|
| `MEDITATION_JWT_SECRET` | **必填（生产）**，用户 JWT 签名密钥 |
| `MEDITATION_ADMIN_USERNAME` / `MEDITATION_ADMIN_PASSWORD` | 管理后台登录，**生产必须修改** |
| `MEDITATION_DEBUG` | 生产设为 `false` |
| `MEDITATION_HOST` / `MEDITATION_PORT` | 监听地址与端口 |
| `MEDITATION_DEFAULT_LLM_PROVIDER` / `MEDITATION_DEFAULT_LLM_MODEL` | 默认模型 |
| `MEDITATION_MEMORY_TOP_K` / `MEDITATION_KNOWLEDGE_TOP_K` | 检索条数 |

完整示例见仓库根目录 **[.env.example](../.env.example)**。

---

## 阶段 5：生产进程与反向代理

**1）使用 systemd（示例）**

创建 `/etc/systemd/system/hush-meditation.service`（路径与用户请按实际修改）：

```ini
[Unit]
Description=Hush Meditation FastAPI
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/hush.ai
EnvironmentFile=/opt/hush.ai/.env
ExecStart=/opt/hush.ai/.venv/bin/python -m uvicorn hushai.meditation.app:get_app --factory --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hush-meditation.service
sudo systemctl status hush-meditation.service
```

**2）Nginx 反向代理 + HTTPS（示例片段）**

```nginx
server {
    listen 443 ssl;
    server_name your.domain.com;
    # ssl_certificate / ssl_certificate_key ...

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**3）防火墙**

仅对外开放 `80/443`，数据库与 Chroma 目录不对外网暴露。

---

## 阶段 6：部署后检查清单

- [ ] `GET /health` 返回 `ok`
- [ ] 对客页 `/` 可打开并完成 dev-login 对话（或正式登录流程）
- [ ] `/admin/` 使用强密码登录
- [ ] PostgreSQL（若使用）连接正常、表已创建
- [ ] `MEDITATION_CHROMA_DIR` 已挂载且重启后知识检索仍可用
- [ ] `.env` 未提交到 Git（确认 `.gitignore`）

---

## 7. 常见问题

**Q：脚本 `scripts/start_server.sh` 与文档命令不一致？**  
A：请以本文与根目录 **README** 为准，使用 `uvicorn ... get_app --factory`。若脚本未带 `--factory`，请手动补上。

**Q：Compose 里的 Chroma 容器要不要开？**  
A：当前默认实现 **不依赖** 该容器；向量持久化靠 **`MEDITATION_CHROMA_DIR`**。若不开 Chroma 容器，可只起 `postgres`：`docker compose up -d postgres`。

**Q：生产环境 CORS？**  
A：默认配置较宽松；若前端与 API 不同域，需在应用配置中收紧 `allow_origins`（当前 `MeditationConfig.cors_origins` 需通过代码或扩展环境变量映射，部署前请评估）。

---

## 8. 相关文档

- [配置说明](configuration.md)（CLI 与冥想模块配置交叉引用时）
- [仓库 README](../README.md)（功能列表、API 速览）
- [.env.example](../.env.example)（变量模板）
