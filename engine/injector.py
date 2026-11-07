import json
import re
import requests

MARKER_PATTERN = re.compile(r"§(.*?)§", re.DOTALL)


def parse_markers(template: str):
    return MARKER_PATTERN.findall(template)


def replace_markers(template: str, payload: str) -> str:
    return MARKER_PATTERN.sub(lambda m: payload, template)


def inject_json_safe(body_obj, payload: str):
    def _walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("prompt", "input", "text", "query") and isinstance(v, str):
                    obj[k] = payload
                elif k == "messages" and isinstance(v, list):
                    obj["messages"].append({"role": "user", "content": payload})
                elif isinstance(v, (dict, list)):
                    _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)
    _walk(body_obj)
    return body_obj


def reassemble_sse(body: str) -> str:
    chunks = []
    for line in body.splitlines():
        if line.startswith("data: "):
            data = line[6:].strip()
            if data == "[DONE]":
                continue
            try:
                obj = json.loads(data)
                delta = obj.get("choices", [{}])[0].get("delta", {})
                if "content" in delta:
                    chunks.append(delta["content"])
                elif "text" in obj:
                    chunks.append(obj["text"])
            except Exception:
                chunks.append(data)
    return "".join(chunks) if chunks else body


def inject_and_send(target, template, payload, method="POST", headers=None):
    headers = headers or {"Content-Type": "application/json"}
    body_str = replace_markers(template, payload)
    try:
        obj = json.loads(body_str)
        obj = inject_json_safe(obj, payload)
        safe_body = json.dumps(obj, ensure_ascii=False)
        json.loads(safe_body)
    except (json.JSONDecodeError, TypeError):
        safe_body = body_str

    resp = requests.request(method, target, data=safe_body.encode("utf-8"),
                            headers=headers, timeout=60)
    content_type = resp.headers.get("Content-Type", "")
    body = resp.text
    if "text/event-stream" in content_type:
        body = reassemble_sse(body)
    return {"status": resp.status_code, "body": body, "headers": dict(resp.headers)}
