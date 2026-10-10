#!/usr/bin/env python3
"""检查所有已配置厂商的连通性，只测试有密钥的厂商。"""
import os

from llm_client import chat, load_credentials, load_providers


def main():
    creds = load_credentials()
    for name, p in load_providers().items():
        has_key = bool(os.environ.get(p.get("env_key", ""))) or bool(
            creds.get(name, {}).get("api_key")
        )
        if not has_key:
            print(f"[--] {name:20s} 未配置")
            continue
        try:
            chat([{"role": "user", "content": "回复 OK"}],
                 provider=name, max_tokens=8, retries=0)
            print(f"[OK] {name:20s} 可用")
        except Exception as e:
            print(f"[XX] {name:20s} {str(e)[:120]}")


if __name__ == "__main__":
    main()