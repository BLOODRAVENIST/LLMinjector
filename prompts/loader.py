import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILTIN_DIR = os.path.join(BASE_DIR, "builtin")


def _load_yaml(filename: str):
    path = os.path.join(BUILTIN_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "prompts" in data:
        return data["prompts"]
    return []


def load_prompts():
    prompts = []
    for fname in ("jailbreak.yaml", "leak.yaml", "super.yaml", "security.yaml"):
        for item in _load_yaml(fname):
            prompts.append({
                "id": item.get("id", f"{fname}:{item.get('name', '')}"),
                "name": item.get("name", "Unnamed"),
                "category": item.get("category", fname.split(".")[0]),
                "content": item.get("content", ""),
            })
    return prompts


def get_prompt_by_id(prompt_id: str):
    for p in load_prompts():
        if p["id"] == prompt_id:
            return p
    return None


def add_generated_prompts(prompts_list, category="ai_generated"):
    result = []
    for i, content in enumerate(prompts_list):
        result.append({
            "id": f"ai:{category}:{i}",
            "name": f"AI-{category}-{i+1}",
            "category": category,
            "content": content,
        })
    return result
