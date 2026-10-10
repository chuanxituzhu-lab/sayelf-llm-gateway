---
name: sayelf-llm-gateway
description: 统一大模型接入层。任何 agent 或 skill 需要调用大模型（Claude、OpenAI、DeepSeek、通义、智谱、Kimi、Gemini 等）时加载本 skill，直接使用 chat()，不要在各自项目里重复编写接入代码。首次使用或换密钥时运行 setup_key.py。
---

# sayelf-llm-gateway

## 何时使用
- 任何 agent 或 skill 需要调用大模型
- 用户提供新的 API Key 或 Token，需要接入
- 检查哪些厂商已配置、是否可用
- 作为 Agent Ops 的直连模型端口，使 agent 无需依赖 AI 宿主平台即可运行

## 首次配置
运行 `python D:\Codex\skills\sayelf-llm-gateway\scripts\setup_key.py`，按提示选择厂商、粘贴密钥（输入不显示）。保存前会自动做一次连通性测试，失败则回滚，不会保存错误密钥。

也可以用环境变量代替，例如 `DEEPSEEK_API_KEY`。环境变量优先级高于凭据文件。

## 调用方式
```python
import sys
sys.path.insert(0, r"D:\Codex\skills\sayelf-llm-gateway\scripts")
from llm_client import chat

reply = chat(
    [{"role": "user", "content": "你好"}],
    provider="deepseek",        # 厂商名，见 providers.json
    system="你是简洁的助手",     # 可选
    max_tokens=1024,            # 可选
)
```

## 检查可用性
`python D:\Codex\skills\sayelf-llm-gateway\scripts\check.py` 逐个测试已配置的厂商。

## 支持的厂商
见 `providers.json`。新增厂商只需在该文件加一条记录，协议为 `openai` 或 `anthropic`。

## 注意
- 默认模型名会随厂商更新而变化，使用前以厂商官方文档为准，必要时在凭据文件中为该厂商设置 `model`。
- 密钥只保存在 `C:\Users\<用户名>\.sayelf\llm\credentials.json`，不在 skill 目录内，不要提交到任何仓库。
- 当前版本只支持文本对话。流式输出、JSON 模式、工具调用将在第二版加入。