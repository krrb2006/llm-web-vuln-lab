#!/usr/bin/env bash
# VulnLab 原生模式（Linux / macOS / WSL）：不依赖 Docker
#   ./scripts/run-native.sh          # 默认 8081
#   PORT=9000 ./scripts/run-native.sh
set -euo pipefail

cd "$(dirname "$0")/.."
WEB_ROOT="$(pwd)"
PORT="${PORT:-8081}"
BIND="${BIND:-127.0.0.1}"   # BIND=0.0.0.0 可让局域网访问

PY="${PYTHON:-python3}"
if ! "$PY" --version >/dev/null 2>&1; then
  echo "找不到 python3，请先安装 Python 3.10+" >&2
  exit 1
fi

if [ ! -f "static/index.html" ]; then
  echo "缺少预构建前端 static/，请先运行 npm run build 并复制到 static/" >&2
  exit 1
fi

if [ ! -x ".venv-native/bin/python" ]; then
  echo "首次运行：创建虚拟环境…"
  "$PY" -m venv .venv-native
fi

if ! .venv-native/bin/python -c 'import fastapi, sqlalchemy, uvicorn' >/dev/null 2>&1; then
  echo "安装/修复依赖（首次约 1-2 分钟）…"
  .venv-native/bin/python -m pip install --upgrade pip --quiet
  .venv-native/bin/python -m pip install -r backend/requirements.txt --quiet
fi

mkdir -p data
if [ ! -f local-native.env ]; then
  echo "JWT_SECRET=$("$PY" -c 'import secrets; print(secrets.token_hex(32))')" > local-native.env
fi

set -a
# shellcheck disable=SC1091
. ./local-native.env
set +a
export DATABASE_URL="sqlite:///${WEB_ROOT}/data/vulnlab.db"
export DATA_DIR="${WEB_ROOT}/data"
export FRONTEND_DIR="${WEB_ROOT}/static"
export SEED_DEMO=true
export APP_ENV=native

echo ""
echo "VulnLab 原生模式：http://127.0.0.1:${PORT}"
echo "演示账号 demo@vulnlab.local / demo-vulnlab-2026"
echo ""

cd backend
exec "${WEB_ROOT}/.venv-native/bin/python" -m uvicorn app.main:app --host "$BIND" --port "$PORT"
