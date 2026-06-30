# AI Agent

基于 FastAPI 的 AI Agent 框架，支持多 LLM 提供商（OpenAI、DeepSeek、Ollama）和 Function Calling。

## 项目结构

参见 [structure](#)（目录树待补充）

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 启动服务
uvicorn app.main:app --reload
```

## 配置

通过 `.env` 文件配置，主要项：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_PROVIDER` | LLM 提供商 (openai/deepseek/ollama) | openai |
| `LLM_MODEL` | 模型名称 | gpt-4o |
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | - |

## API

- `GET /api/v1/health` — 健康检查
- `POST /api/v1/chat` — 聊天接口
