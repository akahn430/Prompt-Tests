#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "Error: OPENAI_API_KEY is not set."
  echo "If you added it to ~/.zshrc, run: source ~/.zshrc"
  exit 1
fi

PORT="${PORT:-8501}"

python3 -m pip install -r requirements.txt

# Bind to all interfaces so the app is reachable from outside this machine.
python3 -m streamlit run web_app.py \
  --server.address 0.0.0.0 \
  --server.port "$PORT" \
  --server.headless true
