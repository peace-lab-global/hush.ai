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
echo "  Swagger UI:  http://localhost:8000/docs"
echo "  Press Ctrl+C to stop"
echo ""

exec python3 -m uvicorn hushai.meditation.app:get_app
