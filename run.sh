#!/bin/bash
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  BLOODRAVENIST — LLM Prompt Injection Scanner           ║"
echo "║  Web GUI · Gemini / DeepSeek AI Payload Generator      ║"
echo "╚══════════════════════════════════════════════════════════╝"
cd "$(dirname "$0")"
source .venv/bin/activate 2>/dev/null || true
python app.py &
sleep 1
xdg-open http://127.0.0.1:5000 2>/dev/null || echo "[*] Open http://127.0.0.1:5000"
wait
