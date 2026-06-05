# 最小化部署（单机开发 / 轻量试用）

目标：**最少依赖、最少配置**，在本机跑起「小观」对话页 + 管理后台 + API。
默认使用 **SQLite**（无需 Docker）、不强制配置 **Chroma 持久化目录**（向量可随进程重启丢失，适合先跑通流程）。完整生产方案见 [deployment.md](deployment.md)。

---

## 前置条件

- Python **3.9+**
- 能访问 **OpenAI 兼容 API**（用于对话；不配置则对话会失败）

---

## 步骤（复制执行）

**1）克隆并进入仓库**

```bash
git clone https://github.com/peace-lab-global/hush.ai.git
cd hush.ai
```

**2）虚拟环境并安装「冥想」依赖**

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

python3 -m pip install -U pip
python3 -m pip install -e ".[meditation]"
```

**3）只设两个必需环境变量**

```bash
export MEDITATION_JWT_SECRET="请改成随机长字符串"
export MEDITATION_OPENAI_API_KEY="sk-你的-key"
```

**4）启动服务**

```bash
python3 -m uvicorn hushai.meditation.app:get_app --factory --host 0.0.0.0 --port 8000
```

**5）验证**

| 项目 | 地址 / 命令 |
|------|-------------|
| 健康检查 | `curl -s http://127.0.0.1:8000/health` |
| 对客对话 | 浏览器打开 `http://127.0.0.1:8000/` |
| 管理后台 | `http://127.0.0.1:8000/admin/` |

---

## 最小化方案里「不包含」什么

| 项目 | 说明 |
|------|------|
| Docker | 不使用；数据库为本地 SQLite 文件 |
| PostgreSQL | 未配置 `MEDITATION_POSTGRES_URL` 时自动 SQLite |
| Chroma 持久化 | 未设置 `MEDITATION_CHROMA_DIR` 时多为内存/临时，**重启后 RAG 向量可能丢失**；要长期保留知识检索，见 [deployment.md](deployment.md) 阶段 3 |
| HTTPS / 反代 | 本机 HTTP 直连，无 Nginx |

---

## 可选：用脚本启动

```bash
bash scripts/start_server.sh
```

脚本会设置默认 `MEDITATION_JWT_SECRET` 与 `MEDITATION_DEBUG`，并启动 Uvicorn（含 `--factory`）。

---

## 下一步

- 需要 **PostgreSQL、向量持久化、systemd、HTTPS**：阅读 [deployment.md](deployment.md)  
- 环境变量大全：仓库根目录 [.env.example](../.env.example)
