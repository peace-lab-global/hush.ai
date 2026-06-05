#!/usr/bin/env bash
set -e

db_file="$(dirname "$0")/meditation_local.db"

export MEDITATION_JWT_SECRET="${MEDITATION_JWT_SECRET:-dev-secret-change-me}"
export MEDITATION_DEBUG="${MEDITATION_DEBUG:-true}"

if [ "$1" = "--postgresql" ]; then
    export MEDITATION_POSTGRES_URL="postgresql://hush:hush123@localhost:5432/hush_meditation"
else
    export MEDITATION_POSTGRES_URL=""
fi

echo "冥想老师 AI 分身 — Starting..."
echo "  Database: ${MEDITATION_POSTGRES_URL:-SQLite ($db_file)}"
echo "  OpenAPI:     http://localhost:8000/debug"
echo "  Press Ctrl+C to stop"
echo ""

script_dir="$(cd "$(dirname "$0")" && pwd)"
venv_python="${script_dir}/../.venv/bin/python"

if [ -x "$venv_python" ]; then
    exec "$venv_python" -m uvicorn hushai.meditation.app:get_app --factory --host "${MEDITATION_HOST:-0.0.0.0}" --port "${MEDITATION_PORT:-8000}"
else
    echo "错误: 未找到虚拟环境 Python ($venv_python)"
    echo "请先运行: python3 -m venv .venv && source .venv/bin/activate && pip install -e ."
    exit 1
fi
