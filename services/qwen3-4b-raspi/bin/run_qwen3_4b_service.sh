#!/usr/bin/env bash
set -euo pipefail

# Simple runner script to start the uvicorn service. Expects a Python venv with deps installed.
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export PYTHONPATH="$(pwd)/src:${PYTHONPATH:-}"

uvicorn services.qwen3_4b_raspi.src.api:app --host ${SERVICE_HOST:-127.0.0.1} --port ${SERVICE_PORT:-8080}
