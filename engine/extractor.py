import re

SECRET_PATTERNS = [
    ("openai_key", r"sk-[A-Za-z0-9]{20,}"),
    ("anthropic_key", r"sk-ant-[A-Za-z0-9\-_]{20,}"),
    ("github_token", r"gh[pous]_[A-Za-z0-9]{20,}"),
    ("jwt", r"eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+"),
    ("aws_key", r"AKIA[0-9A-Z]{16}"),
    ("google_api_key", r"AIza[0-9A-Za-z\-_]{35}"),
    ("slack_token", r"xox[baprs]-[0-9A-Za-z\-]+"),
    ("private_key", r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ("connection_string", r"(mongodb|postgres|mysql|redis)://[^\s\"']+"),
    ("internal_ip", r"\b(10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)\b"),
    ("system_prompt_leak", r"(?i)(you are .{10,200}|your role is .{10,200})"),
    ("password_field", r"(?i)password[\"']?\s*[:=]\s*[\"']?[^\s\"']{6,}"),
]


def extract_secrets(body: str):
    found = []
    for label, pattern in SECRET_PATTERNS:
        for match in re.finditer(pattern, body):
            found.append({"type": label, "value": match.group(0)[:300]})
    return found
