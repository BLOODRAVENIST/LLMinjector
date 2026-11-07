import threading
import time
import os
from datetime import datetime, timezone

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO

from engine.injector import inject_and_send
from engine.detector import quick_detect, confirm_with_wilson
from engine.extractor import extract_secrets
from engine.ai_generator import AIPayloadGenerator
from prompts.loader import load_prompts, add_generated_prompts

app = Flask(__name__)
app.config["SECRET_KEY"] = "bloodravenist-god"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

SCAN_STATE = {"running": False, "results": [], "baseline": None}
AI_GEN = AIPayloadGenerator()
AI_CACHE = {"gemini": [], "deepseek": []}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/prompts")
def api_prompts():
    prompts = load_prompts()
    for provider in ("gemini", "deepseek"):
        prompts.extend(AI_CACHE[provider])
    return jsonify(prompts)


@app.route("/api/ai_keys", methods=["POST"])
def set_ai_keys():
    data = request.get_json()
    AI_GEN.set_keys(
        gemini_key=data.get("gemini_key"),
        deepseek_key=data.get("deepseek_key"),
    )
    return jsonify({"status": "keys set"})


@app.route("/api/ai_generate", methods=["POST"])
def ai_generate():
    data = request.get_json()
    provider = data.get("provider", "gemini")
    category = data.get("category", "jailbreak")
    count = int(data.get("count", 5))
    payloads = AI_GEN.generate(provider, category, count)
    if not payloads:
        return jsonify({"error": "generation failed — check API key / quota / model access"}), 400
    formatted = add_generated_prompts(payloads, category)
    AI_CACHE[provider].extend(formatted)
    return jsonify(formatted)


@app.route("/api/scan", methods=["POST"])
def start_scan():
    if SCAN_STATE["running"]:
        return jsonify({"error": "scan already running"}), 409
    data = request.get_json()
    SCAN_STATE["running"] = True
    SCAN_STATE["results"] = []
    thread = threading.Thread(target=run_scan, args=(data,), daemon=True)
    thread.start()
    return jsonify({"status": "started"})


def run_scan(cfg):
    target = cfg["target"]
    template = cfg.get("request_template", "")
    payload_ids = cfg.get("payload_ids", [])
    delay = cfg.get("delay", 400) / 1000.0
    method = cfg.get("method", "POST")
    headers = cfg.get("headers", {"Content-Type": "application/json"})

    all_prompts = load_prompts()
    for provider in ("gemini", "deepseek"):
        all_prompts.extend(AI_CACHE[provider])

    selected = [p for p in all_prompts if p["id"] in payload_ids]

    if cfg.get("capture_baseline", True):
        baseline = inject_and_send(target, template, "__BASELINE__", method=method, headers=headers)
        SCAN_STATE["baseline"] = baseline
        socketio.emit("baseline_ready", {"status": baseline.get("status")})

    for i, prompt in enumerate(selected):
        if not SCAN_STATE["running"]:
            break
        resp = inject_and_send(target, template, prompt["content"], method=method, headers=headers)
        matched, reason = quick_detect(resp.get("body", ""))
        secrets = extract_secrets(resp.get("body", ""))
        finding = {
            "index": i,
            "prompt_id": prompt["id"],
            "prompt_name": prompt["name"],
            "category": prompt.get("category", "manual"),
            "status": resp.get("status"),
            "matched": matched,
            "reason": reason,
            "body_preview": resp.get("body", "")[:2000],
            "secrets": secrets,
            "confirmed": False,
        }
        SCAN_STATE["results"].append(finding)
        socketio.emit("finding", finding)
        time.sleep(delay)

    SCAN_STATE["running"] = False
    socketio.emit("scan_done", {"total": len(SCAN_STATE["results"])})


@app.route("/api/confirm/<int:index>", methods=["POST"])
def confirm_finding(index):
    finding = SCAN_STATE["results"][index]
    cfg = request.get_json()
    prompt_content = None
    for p in load_prompts() + AI_CACHE["gemini"] + AI_CACHE["deepseek"]:
        if p["name"] == finding["prompt_name"]:
            prompt_content = p["content"]
            break
    if not prompt_content:
        return jsonify({"error": "prompt content not found"}), 400
    confirmed, ci = confirm_with_wilson(
        target=cfg["target"],
        template=cfg["template"],
        prompt_content=prompt_content,
        retries=cfg.get("retries", 5),
        successes_needed=cfg.get("successes", 3),
    )
    finding["confirmed"] = confirmed
    finding["ci"] = ci
    return jsonify(finding)


@app.route("/api/export", methods=["POST"])
def export_report():
    cfg = request.get_json()
    results = SCAN_STATE["results"]
    now = datetime.now(timezone.utc)
    html = render_template("report.html", results=results, target=cfg.get("target", ""),
                           generated_at=now.isoformat())
    fname = f"reports/scan_{now.strftime('%Y%m%d_%H%M%S')}.html"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(html)
    return send_file(os.path.abspath(fname), as_attachment=True)


if __name__ == "__main__":
    socketio.run(
        app,
        host="127.0.0.1",
        port=5000,
        debug=False,
        allow_unsafe_werkzeug=True,
    )
