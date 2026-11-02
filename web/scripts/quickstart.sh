#!/usr/bin/env bash
# 新用户入口：无需记住目录，直接启动原生本地版。
set -euo pipefail
cd "$(dirname "$0")/.."
exec bash scripts/run-native.sh "$@"
