#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "Error: OPENAI_API_KEY is not set."
  echo "If you added it to ~/.zshrc, run: source ~/.zshrc"
  exit 1
fi

python3 -m pip install -r requirements.txt
streamlit run web_app.py
