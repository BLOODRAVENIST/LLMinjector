
<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=900&size=22&duration=2500&pause=600&color=00FF41&center=true&vCenter=true&width=900&lines=%5Broot%40BLOODRAVENIST%5D%23+./run.sh;LLM+Prompt+Injection+Scanner;Web+GUI+%7C+Gemini+%2B+DeepSeek+AI;Payload+Generation+on+Autopilot" alt="Terminal" />

# LLMinjector

### LLM Prompt Injection Scanner — Web GUI

**AI-powered prompt injection scanner with Gemini / DeepSeek payload generation and live WebSocket streaming**

<img width="937" height="760" alt="Screenshot 2026-11-07 131907" src="https://github.com/user-attachments/assets/42bbe0be-31f7-4c82-899e-1ee507244054" />


**Made by [BLOODRAVENIST](https://github.com/BLOODRAVENIST)**

> **For Authorized Security Research Only**

</div>

---

## What Is LLMinjector?

**LLMinjector** is a **browser-based GUI** for LLM prompt injection testing. It combines **AI payload generation** (Gemini / DeepSeek) with a **live scan engine** and streams results to an **animated hacker interface**.

**Why LLMinjector?**

- **AI Payloads** — Gemini / DeepSeek generate targeted injection payloads
- **Live Streaming** — WebSocket output, line-by-line
- **Browser GUI** — no terminal needed for scanning
- **Engine Modules** — modular scan engine in `engine/`
- **Prompt Library** — built-in prompts in `prompts/`

---

## Features

| Feature | Description |
|---|---|
| **AI Payload Gen** | Gemini / DeepSeek integration for adaptive payloads |
| **Live Scan Output** | WebSocket streaming from `engine/` to browser |
| **Modular Engine** | `engine/` contains scan logic |
| **Prompt Library** | `prompts/` contains injection templates |
| **Auto Browser** | `./run.sh` opens `http://127.0.0.1:5000` |
| **Hacker UI** | Animated purple/black interface |
| **Flask + Socket.IO** | Real-time two-way communication |

---

## Architecture

```text
app.py (Flask + Socket.IO)
  ├── engine/          # scan engine (payload execution, response parsing)
  ├── prompts/         # injection payload templates
  ├── static/          # style.css + app.js (matrix UI, socket client)
  └── templates/       # index.html (main UI)
```

---

## Quick Start

```bash
# 1. Setup venv
cd ~/LLMinjector
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Run
chmod +x run.sh
./run.sh
```

**Browser automatically opens** at `http://127.0.0.1:5000`

---

## Usage

1. **Server chalao**: `./run.sh`
2. **Browser**: `http://127.0.0.1:5000`
3. **Target URL daalo** (vulnerable LLM endpoint)
4. **Payload source select karo**: Gemini / DeepSeek
5. **START SCAN click karo**
6. **Live output** browser mein streaming
7. **STOP** se rok sakta hai, **CLEAR** se terminal saaf

---

## File Structure

```text
LLMinjector/
├── app.py                  # Flask + Socket.IO server
├── engine/                 # scan engine modules
├── prompts/                # injection prompt templates
├── requirements.txt
├── run.sh                  # startup script
├── static/
│   ├── style.css           # animated hacker theme
│   └── app.js              # matrix rain + socket client
└── templates/
    └── index.html          # main UI
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Main UI |
| `/api/start` | POST | Start scan |
| `/api/stop` | POST | Stop scan |
| `/api/status` | GET | Scan status |

## WebSocket Events

| Event | Direction | Purpose |
|---|---|---|
| `connect` | S → C | Connection established |
| `scan_output` | S → C | Live output line |
| `scan_complete` | S → C | Scan finished |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `Port 5000 in use` | `sudo lsof -ti :5000 \| xargs -r sudo kill -9` |
| `ModuleNotFoundError` | `source .venv/bin/activate && pip install -r requirements.txt` |
| `static/*.css` or `*.js` 404 | Files missing in `static/` — recreate |
| `run.sh: permission denied` | `chmod +x run.sh` |
| Browser not opening | Manually open `http://127.0.0.1:5000` |

---

## Legal

> **ALL RESEARCH IS FOR AUTHORIZED SECURITY TESTING ONLY**
>
> Only test LLM systems you own or have **written permission** to test.
>
> Unauthorized access is illegal under CFAA, Computer Misuse Act, IT Act, and similar laws worldwide.

---

<div align="center">

<a href="https://github.com/BLOODRAVENIST"><img src="https://img.shields.io/badge/GitHub-BLOODRAVENIST-00FF41?style=flat-square&logo=github&labelColor=000000" alt="GitHub"/></a>
<a href="https://profile.hackthebox.com/profile/019eff6a-53c1-721f-a94e-f459c94dfc1f"><img src="https://img.shields.io/badge/Hack_The_Box-9FEF00?style=flat-square&logo=hackthebox&logoColor=white&labelColor=111927" alt="HTB"/></a>
<a href="https://buymeacoffee.com/bloodravenist"><img src="https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=flat-square&logo=buy-me-a-coffee&logoColor=black&labelColor=000000" alt="Coffee"/></a>

<br/><br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:000000,60:00FF41,100:9FEF00&height=100&section=footer&text=LLMinjector&fontSize=34&fontColor=00FF41&animation=twinkling" width="100%"/>

</div>
