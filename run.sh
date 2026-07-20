#!/bin/bash
# EchelonShield 启动脚本
# 强制使用本地 lib 目录，避免 Flatpak 沙箱隔离问题

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/lib:${SCRIPT_DIR}:${PYTHONPATH}"
exec python3 "${SCRIPT_DIR}/__main__.py"