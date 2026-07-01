# AI Agent 项目架构文档

## 项目概述

基于 **LangChain + LangGraph** 构建的 AI Agent 框架，支持多 LLM 供应商（OpenAI、DeepSeek、Ollama）和 Function Calling 工具系统。通过 LangGraph 的状态图（StateGraph）驱动 Agent 工作流，实现"推理→工具调用→再推理"的循环。

## 技术栈

| 组件 | 用途 |
|------|------|
| **FastAPI** | HTTP 接口层 |
| **LangChain Core** | LLM 抽象、消息模型、工具定义 |
| **LangChain OpenAI** | OpenAI / DeepSeek / Ollama 的统一调用入口 |
| **LangGraph** | Agent 工作流编排（状态图） |
| **Pydantic** | 配置加载与请求/响应校验 |

## 目录结构

```
ai-agent/
├── app/                          # 主应用
│   ├── main.py                   # FastAPI 入口
│   ├── api/
│   │   └── chat.py               # 聊天 HTTP 接口
│   ├── core/
│   │   ├── config.py             # pydantic-settings 配置
│   │   ├── logging.py            # 日志配置
│   │   └── exceptions.py         # 自定义异常
│   ├── agent/                    # ⭐ Agent 核心
│   │   ├── agent.py              # LangGraph StateGraph
│   │   ├── tools.py              # 工具注册
│   │   ├── prompt.py             # 系统提示词
│   │   └── memory.py             # 对话记忆
│   ├── llm/                      # LLM 工厂
│   │   ├── __init__.py           # LLMFactory
│   │   └── base.py               # 基于 ChatOpenAI 的通用实现
│   ├── tools/                    # ⭐ 工具集
│   │   ├── weather.py            # 天气查询
│   │   ├── search.py             # 网络搜索（骨架）
│   │   ├── db.py                 # 数据库查询（骨架）
│   │   └── browser.py            # 网页抓取
│   ├── schemas/                  # Pydantic 模型
│   │   ├── chat.py               # 聊天请求/响应
│   │   └── tool.py               # 工具模型
│   └── utils/
│       ├── text.py               # 文本工具
│       └── time.py               # 时间工具
├── docs/
│   └── architecture.md           # ← 本文档
├── tests/                        # 测试
├── scripts/                      # 初始化脚本
├── requirements.txt
├── .env / .env.example
└── README.md
```

---

## LangGraph Agent 工作流

这是项目的核心——一张**有向状态图**（StateGraph）：

```
                        ┌──────────────┐
                        │  入口         │
                        │  Entry Point  │
                        └──────┬───────┘
                               │
                               ▼
                     ┌─────────────────┐
                     │  Agent 节点      │  ← LLM 推理
                     │  _call_model()   │
                     └────────┬────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
              有 tool_calls          无 tool_calls
                    │                    │
                    ▼                    ▼
             ┌────────────┐      ┌──────────────┐
             │ Tools 节点   │      │ 结束          │
             │ _call_tools │      │ END           │
             └──────┬─────┘      └──────────────┘
                    │
                    ▼
             ┌────────────┐
             │ 回到 Agent  │  ← 带上工具结果继续推理
             └────────────┘
```

### 节点说明

| 节点 | 函数 | 职责 |
|------|------|------|
| **Agent** | `_call_model()` | 将工具绑定到 LLM，调用 `ChatOpenAI.bind_tools().invoke()` 进行推理 |
| **Tools** | `_call_tools()` | 遍历 LLM 返回的 `tool_calls`，异步执行每个工具，结果包装为 `ToolMessage` |

### 条件边

`_should_continue()` 判断 LLM 的回复是否包含 `tool_calls`：
- **有** → 路由到 Tools 节点
- **无** → 路由到 END（返回最终回复）

### 关键优势

- LLM 可以**多次调用工具**（Tools → Agent 形成回路）
- 工具结果自动注入上下文，LLM 据此生成最终回答
- 状态通过 `TypedDict` 类型安全传递

---

## LLM 模块

基于 `ChatOpenAI`（OpenAI 兼容 API）的统一封装：

```
LLMFactory.create()
    │
    ├─ LLM_PROVIDER=openai   → ChatOpenAI(base_url=api.openai.com)
    ├─ LLM_PROVIDER=deepseek → ChatOpenAI(base_url=api.deepseek.com)
    └─ LLM_PROVIDER=ollama   → ChatOpenAI(base_url=localhost:11434/v1)
```

所有供应商都使用 OpenAI 兼容的 `/v1/chat/completions` 接口，因此可以统一使用 `langchain_openai.ChatOpenAI`。

## 工具系统

每个工具使用 `@tool` 装饰器定义：

```python
from langchain_core.tools import tool

@tool
async def browse(url: str) -> str:
    """访问网页并提取文本内容"""
    ...
```

`@tool` 自动生成 JSON Schema（Function Calling 格式），无需手动维护 `parameters` 定义。

### 工具注册

`app/agent/tools.py` 中的 `get_tool_registry()` 汇集所有工具为列表：

```python
def get_tool_registry() -> list:
    return [get_weather, web_search, query_database, browse]
```

LangGraph Agent 通过 `self.llm.bind_tools(self.tools)` 将工具定义传给 LLM。

---

## 完整请求生命周期

```
客户端 POST /api/v1/chat  { messages: [...] }
  │
  ▼
app/api/chat.py  chat()
  │  Agent.run(messages)
  ▼
app/agent/agent.py
  │  1. 将 Message → LangChain BaseMessage（注入 SystemMessage）
  │  2. self.graph.ainvoke({"messages": [...]})
  │
  ▼
        ┌─ [Agent 节点] ──────────────────────────┐
        │  llm_with_tools = llm.bind_tools(tools) │
        │  response = llm_with_tools.invoke(msg)  │
        └────────────────┬────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
        has tool_calls         no tool_calls
              │                     │
              ▼                     ▼
   ┌─ [Tools 节点] ─────┐   返回最终 content
   │ for tc in calls:   │
   │   tool.ainvoke()   │
   └────────┬───────────┘
            │
            └──→ 回到 Agent 节点 ──→ ...
  │
  ▼
返回 ChatResponse { reply: "..." }  给客户端
```

---

## 如何扩展

### 添加新工具

1. 在 `app/tools/` 下新建文件
2. 使用 `@tool` 装饰器定义异步函数
3. 在 `app/agent/tools.py` 中导入并加入 `get_tool_registry()` 返回列表

### 添加新 LLM 供应商

1. 在 `app/core/config.py` 中添加 API Key / Base URL 字段
2. 在 `app/llm/__init__.py` 的 `_providers` 字典中注册
3. 设置 `.env` 的 `LLM_PROVIDER` 为你的供应商名称

### 修改系统提示词

编辑 `app/agent/prompt.py` 中的 `system_prompt` 变量。

---

## 关键依赖

| 包 | 用途 |
|----|------|
| `langchain-core` | 消息模型（BaseMessage、ToolMessage）、@tool 装饰器 |
| `langchain-openai` | ChatOpenAI 模型（兼容 OpenAI / DeepSeek / Ollama） |
| `langgraph` | StateGraph 工作流 |
| `httpx` | 工具使用的异步 HTTP 客户端 |
| `beautifulsoup4` | 网页内容解析 |
