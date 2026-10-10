#!/usr/bin/env python3
"""交互式配置厂商密钥：输入 → 连通性测试 → 通过才保存，失败自动回滚。"""
import getpass
import sys

from llm_client import CRED_FILE, chat, load_credentials, load_providers, save_credentials


def main():
    providers = load_providers()
    print("可用厂商:", ", ".join(providers))
    name = input("厂商名: ").strip()
    if name not in providers:
        sys.exit(f"未知厂商: {name}")

    key = getpass.getpass("API Key（输入不显示）: ").strip()
    if not key:
        sys.exit("密钥为空，已取消")

    base_url = input(f"Base URL（回车使用默认 {providers[name]['base_url']}）: ").strip()
    model = input(f"模型名（回车使用默认 {providers[name]['default_model']}）: ").strip()

    old = load_credentials()
    entry = {"api_key": key}
    if base_url:
        entry["base_url"] = base_url
    if model:
        entry["model"] = model
    new = dict(old)
    new[name] = entry
    save_credentials(new)

    try:
        reply = chat(
            [{"role": "user", "content": "只回复两个字：正常"}],
            provider=name, max_tokens=16, retries=0,
        )
    except Exception as e:
        save_credentials(old)
        sys.exit(f"连通测试失败，已回滚，未保存新密钥: {e}")

    print(f"连通成功: {reply.strip()[:40]}")
    print(f"已保存到 {CRED_FILE}")


if __name__ == "__main__":
    main()