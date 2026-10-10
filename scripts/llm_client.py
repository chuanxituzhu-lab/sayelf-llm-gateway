#!/usr/bin/env python3
"""统一大模型调用入口（仅依赖 Python 标准库）。

用法：
    from llm_client import chat
    reply = chat([{"role": "user", "content": "你好"}], provider="deepseek")

命令行快速测试：
    python llm_client.py deepseek "你好"
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PROVIDERS_FILE = SKILL_DIR / "providers.json"
CRED_DIR = Path.home() / ".sayelf" / "llm"
CRED_FILE = CRED_DIR / "credentials.json"
ANTHROPIC_VERSION = "2023-06-01"
RETRY_STATUS = (429, 500, 502, 503, 504)


class ApiError(RuntimeError):
    def __init__(self, status, detail):
        super().__init__(f"HTTP {status}: {detail}")
        self.status = status


def load_providers():
    return json.loads(PROVIDERS_FILE.read_text(encoding="utf-8"))


def load_credentials():
    if not CRED_FILE.exists():
        return {}
    return json.loads(CRED_FILE.read_text(encoding="utf-8"))


def save_credentials(data):
    CRED_DIR.mkdir(parents=True, exist_ok=True)
    CRED_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(CRED_FILE, 0o600)
    except OSError:
        pass


def resolve(provider):
    providers = load_providers()
    if provider not in providers:
        raise KeyError(f"未知厂商: {provider}，可用: {', '.join(providers)}")
    base = providers[provider]
    saved = load_credentials().get(provider, {})
    api_key = os.environ.get(base.get("env_key", ""), "") or saved.get("api_key", "")
    if not api_key:
        raise RuntimeError(
            f"{provider} 未配置密钥。请运行 scripts/setup_key.py，"
            f"或设置环境变量 {base.get('env_key')}"
        )
    return {
        "protocol": base["protocol"],
        "base_url": saved.get("base_url") or base["base_url"],
        "model": saved.get("model") or base["default_model"],
        "api_key": api_key,
    }


def _post(url, headers, body, timeout=120):
    req = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, e.read().decode("utf-8", "replace")[:500]) from None


def _call_openai(cfg, messages, system, max_tokens, temperature):
    msgs = ([{"role": "system", "content": system}] if system else []) + list(messages)
    body = {
        "model": cfg["model"],
        "messages": msgs,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    data = _post(
        cfg["base_url"].rstrip("/") + "/chat/completions",
        {"Authorization": f"Bearer {cfg['api_key']}"},
        body,
    )
    return data["choices"][0]["message"]["content"]


def _call_anthropic(cfg, messages, system, max_tokens, temperature):
    body = {
        "model": cfg["model"],
        "messages": list(messages),
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if system:
        body["system"] = system
    data = _post(
        cfg["base_url"].rstrip("/") + "/v1/messages",
        {"x-api-key": cfg["api_key"], "anthropic-version": ANTHROPIC_VERSION},
        body,
    )
    return "".join(
        b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"
    )


def chat(messages, provider="deepseek", system=None, model=None,
         max_tokens=2048, temperature=0.7, retries=2):
    cfg = resolve(provider)
    if model:
        cfg["model"] = model
    if cfg["protocol"] == "openai":
        call = _call_openai
    elif cfg["protocol"] == "anthropic":
        call = _call_anthropic
    else:
        raise ValueError(f"不支持的协议: {cfg['protocol']}")

    last = None
    for attempt in range(retries + 1):
        try:
            return call(cfg, messages, system, max_tokens, temperature)
        except ApiError as e:
            last = e
            if e.status not in RETRY_STATUS:
                raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
        if attempt < retries:
            time.sleep(2 ** attempt)
    raise last


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python llm_client.py <provider> <提示词>")
        sys.exit(1)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(chat([{"role": "user", "content": sys.argv[2]}], provider=sys.argv[1]))