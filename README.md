# sayelf-llm-gateway

统一大模型接入层。任何 agent 或 skill 需要调用大模型时，直接加载本 skill，配置一次密钥即可使用，不必在每个项目里重复编写接入代码。

[English](README.en.md) | 中文

## 特性

- 零依赖：只使用 Python 标准库，无需 pip 安装任何包
- 两种协议：OpenAI 兼容协议、Anthropic 协议，覆盖 Claude、OpenAI、DeepSeek、通义、智谱、Kimi、Gemini 等厂商
- 密钥与代码分离：密钥保存在用户目录，不在 skill 文件夹内
- 保存前校验：输入密钥后自动做一次连通性测试，失败则回滚，不会保存错误密钥
- 自动重试：对 429 和 5xx 错误指数退避重试，4xx 直接报错
- 环境变量优先：设置了 `DEEPSEEK_API_KEY` 等变量时，优先使用环境变量

## 目录结构

## 环境要求

- Python 3.11 或更高版本
- Windows、macOS、Linux 均可

Windows 上请使用 `py` 命令启动 Python。如果输入 `python` 弹出 Microsoft Store，说明未安装 Python 或未加入 PATH，请从 python.org 安装并勾选 "Add python.exe to PATH"。

## 快速开始

### 1. 检查语法（可选）

```powershell
py -m py_compile scripts\llm_client.py scripts\setup_key.py scripts\check.py
```

无输出即通过。

### 2. 配置密钥

```powershell
py scripts\setup_key.py
```

按提示操作：

1. 厂商名：输入 `providers.json` 中的名称，例如 `deepseek`
2. API Key：粘贴密钥，输入时不显示，粘贴后直接回车
3. Base URL：回车使用默认值
4. 模型名：回车使用默认值

脚本会先做一次连通测试，显示"连通成功"后才写入凭据文件。

凭据保存位置：`~/.sayelf/llm/credentials.json`（Windows 为 `C:\Users\<用户名>\.sayelf\llm\credentials.json`）。

### 3. 检查可用性

```powershell
py scripts\check.py
```

输出示例：[OK] deepseek 可用
[--] openai 未配置
[XX] zhipu HTTP 401: ...
### 4. 端到端测试

```powershell
py scripts\llm_client.py deepseek "你好，请用一句话介绍你自己"
```

## 在其他 agent 或 skill 中调用

```python
import sys
sys.path.insert(0, r"D:\Codex\skills\sayelf-llm-gateway\scripts")  # 改为你的实际路径
from llm_client import chat

reply = chat(
    [{"role": "user", "content": "你好"}],
    provider="deepseek",         # 厂商名，见 providers.json
    system="你是简洁的助手",      # 可选
    max_tokens=1024,             # 可选，默认 2048
    temperature=0.7,             # 可选
    model=None,                  # 可选，覆盖默认模型
    retries=2,                   # 可选，重试次数
)
print(reply)
```

## 支持的厂商

| 名称 | 协议 | 环境变量 | 默认模型 |
|---|---|---|---|
| anthropic | anthropic | ANTHROPIC_API_KEY | claude-sonnet-5-5 |
| openai | openai | OPENAI_API_KEY | gpt-4o-mini |
| deepseek | openai | DEEPSEEK_API_KEY | deepseek-chat |
| deepseek-anthropic | anthropic | DEEPSEEK_API_KEY | deepseek-chat |
| qwen | openai | DASHSCOPE_API_KEY | qwen-plus |
| zhipu | openai | ZHIPU_API_KEY | glm-4-flash |
| moonshot | openai | MOONSHOT_API_KEY | moonshot-v1-8k |
| gemini | openai | GEMINI_API_KEY | gemini-2.5-flash |

**注意**：默认模型名会随厂商更新而变化。使用前请以厂商官方文档为准。需要更换时，运行 `setup_key.py` 时在"模型名"处输入新名称即可，无需修改代码。

## 添加新厂商

在 `providers.json` 中增加一条记录：

```json
"新厂商名": {
  "protocol": "openai",
  "base_url": "https://example.com/v1",
  "env_key": "EXAMPLE_API_KEY",
  "default_model": "model-name"
}
```

`protocol` 只能是 `openai` 或 `anthropic`。大多数国产厂商提供 OpenAI 兼容端点，直接使用 `openai` 即可。

## 常见问题

**Q：输入 `python` 提示 "Python was not found"？**
A：使用 `py` 代替 `python`，或从 python.org 安装 Python 并勾选加入 PATH。

**Q：`setup_key.py` 提示"连通测试失败，已回滚"？**
A：密钥错误、余额不足、网络不通或 base_url 错误都会导致此结果。错误信息中的 HTTP 状态码可以帮助定位：401 通常是密钥错误，403 通常是权限或地区限制，429 是频率限制。

**Q：环境变量和凭据文件同时存在，用哪个？**
A：环境变量优先。

**Q：如何删除某个厂商的密钥？**
A：编辑 `~/.sayelf/llm/credentials.json`，删除对应条目即可。

## 安全

- 密钥只保存在用户目录，本仓库不包含任何密钥
- 凭据文件在非 Windows 系统上会设置为仅当前用户可读（0600）；Windows 依赖用户目录的默认权限
- 请勿把 `~/.sayelf/` 复制进任何仓库或分享给他人
- 如果密钥曾在聊天、截图或日志中暴露，请立即到厂商控制台作废并重新生成

## 路线图

- v1（当前）：文本对话，两种协议，连通测试，自动重试
- v2（计划）：流式输出、JSON 结构化输出、工具调用归一化

## 许可

MIT