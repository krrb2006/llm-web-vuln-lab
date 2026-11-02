#!/usr/bin/env bash
# 一键启动 VulnLab（Linux / macOS / WSL）
set -euo pipefail

cd "$(dirname "$0")/.."

if ! docker version --format '{{.Server.Version}}' >/dev/null 2>&1; then
  echo "Docker 引擎未运行：请先启动 Docker Desktop / dockerd，再重试。" >&2
  exit 1
fi

docker compose up -d

port=$(sed -n 's/^HTTP_PORT=\([0-9]\+\).*/\1/p' .env 2>/dev/null || true)
port=${port:-8080}
url="http://localhost:${port}"

for _ in $(seq 1 40); do
  if curl -fsS "${url}/api/health" >/dev/null 2>&1; then
    echo "已就绪：${url}（演示账号 demo@vulnlab.local / demo-vulnlab-2026）"
    exit 0
  fi
  sleep 2
done

echo "容器已启动，但健康检查未通过：docker compose logs backend --tail 50" >&2
