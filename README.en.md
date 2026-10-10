# sayelf-llm-gateway

A unified LLM access layer. Any agent or skill that needs a large language model loads this skill, configures its key once, and calls one function, instead of rewriting provider-specific client code in every project.

English | [中文](README.md)

## Features

- Zero dependencies: uses only the Python standard library, no pip install required
- Two protocols: OpenAI-compatible and Anthropic, covering Claude, OpenAI, DeepSeek, Qwen, Zhipu, Moonshot, Gemini and more
- Keys separated from code: keys live in the user profile, never inside the skill folder
- Verify before save: a key is tested with one minimal request; on failure it is rolled back and not saved
- Retries: exponential backoff on 429 and 5xx; other 4xx errors raise immediately
- Environment variables take priority over the credentials file

## Layout
## Requirements

- Python 3.11 or newer
- Windows, macOS or Linux

On Windows, launch Python with `py`. If `python` opens the Microsoft Store, Python is not installed or not on PATH; install from python.org and tick "Add python.exe to PATH".

## Quick start

### 1. Check syntax (optional)

```powershell
py -m py_compile scripts\llm_client.py scripts\setup_key.py scripts\check.py
```

No output means success.

### 2. Configure a key

```powershell
py scripts\setup_key.py
```

At the prompts:

1. Provider name: enter a name from `providers.json`, e.g. `deepseek`
2. API Key: paste it; input is hidden; press Enter
3. Base URL: press Enter for the default
4. Model: press Enter for the default

The script runs one connectivity test and writes the credentials file only if it prints success.

Credentials file: `~/.sayelf/llm/credentials.json` (on Windows: `C:\Users\<username>\.sayelf\llm\credentials.json`).

### 3. Check availability

```powershell
py scripts\check.py
```

Example output:[OK] deepseek available
[--] openai not configured
[XX] zhipu HTTP 401: ...
### 4. End-to-end test

```powershell
py scripts\llm_client.py deepseek "Hello, describe yourself in one sentence"
```

## Calling it from another agent or skill

```python
import sys
sys.path.insert(0, r"D:\Codex\skills\sayelf-llm-gateway\scripts")  # change to your actual path
from llm_client import chat

reply = chat(
    [{"role": "user", "content": "Hello"}],
    provider="deepseek",         # provider name from providers.json
    system="You are a concise assistant",  # optional
    max_tokens=1024,             # optional, default 2048
    temperature=0.7,             # optional
    model=None,                  # optional, overrides default model
    retries=2,                   # optional
)
print(reply)
```

## Supported providers

| Name | Protocol | Env variable | Default model |
|---|---|---|---|
| anthropic | anthropic | ANTHROPIC_API_KEY | claude-sonnet-5-5 |
| openai | openai | OPENAI_API_KEY | gpt-4o-mini |
| deepseek | openai | DEEPSEEK_API_KEY | deepseek-chat |
| deepseek-anthropic | anthropic | DEEPSEEK_API_KEY | deepseek-chat |
| qwen | openai | DASHSCOPE_API_KEY | qwen-plus |
| zhipu | openai | ZHIPU_API_KEY | glm-4-flash |
| moonshot | openai | MOONSHOT_API_KEY | moonshot-v1-8k |
| gemini | openai | GEMINI_API_KEY | gemini-2.5-flash |

**Note**: default model names change over time. Check the provider's official documentation before relying on them. To change the model, enter a new name at the "Model" prompt of `setup_key.py`; no code change is needed.

## Adding a provider

Add an entry to `providers.json`:

```json
"new-provider": {
  "protocol": "openai",
  "base_url": "https://example.com/v1",
  "env_key": "EXAMPLE_API_KEY",
  "default_model": "model-name"
}
```

`protocol` must be `openai` or `anthropic`. Most providers offer an OpenAI-compatible endpoint, so `openai` is usually the right choice.

## FAQ

**Q: Typing `python` says "Python was not found"?**
A: Use `py` instead, or install Python from python.org and tick "Add to PATH".

**Q: `setup_key.py` says "test failed, rolled back"?**
A: A wrong key, no balance, a network problem or a wrong base_url can all cause this. The HTTP status helps: 401 usually means a bad key, 403 usually means a permission or region restriction, 429 means rate limiting.

**Q: Both an environment variable and the credentials file are set. Which is used?**
A: The environment variable.

**Q: How do I remove a provider's key?**
A: Edit `~/.sayelf/llm/credentials.json` and delete that provider's entry.

## Security

- Keys are stored only in the user profile; this repository contains no keys
- On non-Windows systems the credentials file is set to owner-only (0600); on Windows it relies on the default user-profile permissions
- Never copy `~/.sayelf/` into a repository or share it
- If a key was ever exposed in chat, a screenshot or a log, revoke it in the provider console immediately and generate a new one

## Roadmap

- v1 (current): text chat, two protocols, connectivity test, retries
- v2 (planned): streaming, structured JSON output, normalized tool calling

## License

MIT