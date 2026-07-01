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

---

## 代码阅读顺序

建议按照以下顺序阅读源码，从外到内、从入口到核心：

```
阅读顺序  文件                                   说明
────────────────────────────────────────────────────────────────────
   1      app/main.py                          应用入口，从这里看起
   2      app/schemas/chat.py                  数据模型，理解请求/响应结构
   3      app/api/chat.py                      HTTP 接口，看请求如何进入 Agent
   4      app/core/config.py                   配置项，了解全局可调参数
   5      app/agent/prompt.py                  系统提示词，理解 Agent 的行为约束
   6      app/agent/memory.py                  对话记忆，理解上下文如何保存
   7      app/tools/weather.py                 一个具体工具的实现 👈 从最简单的看起
   8      app/agent/tools.py                   工具注册，看工具如何汇集
   9      app/llm/base.py                      LLM 封装，看 LLM 如何创建
  10      app/llm/__init__.py                  LLM 工厂，看供应商切换逻辑
  11      app/agent/agent.py                  ⭐ 核心文件，LangGraph 状态图
  12      app/tools/browser.py                 其他工具（有异常处理，稍复杂）
  13      app/tools/search.py                  其他工具（骨架实现）
  14      app/tools/db.py                      其他工具（骨架实现）
  15      app/core/logging.py                  日志配置
  16      app/core/exceptions.py               自定义异常
  17      app/utils/text.py                    工具函数
  18      app/utils/time.py                    工具函数
```

---

## 逐文件说明

### 1. `app/main.py` — 应用入口

```python
# 创建 FastAPI 应用
app = FastAPI(title=..., version=..., lifespan=lifespan)
# 注册路由
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
```

| 项目 | 说明 |
|------|------|
| **作用** | FastAPI 应用创建、路由注册、生命周期管理 |
| **关键对象** | `app`（FastAPI 实例）、`lifespan`（启动/关闭回调） |
| **路由** | `POST /api/v1/chat` — 唯一的对外接口 |

---

### 2. `app/schemas/chat.py` — 聊天数据模型

```python
class Message(BaseModel):
    role: str    # "user" | "assistant" | "system"
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]

class ChatResponse(BaseModel):
    reply: str
```

| 项目 | 说明 |
|------|------|
| **作用** | 定义 HTTP 接口的请求/响应结构，FastAPI 自动做校验和生成文档 |
| **关键点** | Agent 内部使用 LangChain 的 `BaseMessage`，API 层负责在两者之间转换 |

---

### 3. `app/api/chat.py` — 聊天接口

```python
@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    agent = Agent()
    response = await agent.run(request.messages)
    return ChatResponse(reply=response)
```

| 项目 | 说明 |
|------|------|
| **作用** | 接收 HTTP 请求，创建 Agent 实例，调用 `run()`，返回响应 |
| **注意** | 每次请求创建一个新的 `Agent` 实例（无状态设计）；如需多轮对话，需在外层管理 Memory |

---

### 4. `app/core/config.py` — 全局配置

```python
class Settings(BaseSettings):
    LLM_PROVIDER: str = "openai"    # 可选: openai / deepseek / ollama
    OPENAI_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    ...
settings = Settings()  # 全局单例
```

| 项目 | 说明 |
|------|------|
| **作用** | 从 `.env` 和环境变量加载所有配置项 |
| **关键点** | 使用 `pydantic-settings`，字段默认值 + `.env` 覆盖 + 环境变量覆盖 |
| **配置项** | LLM 供应商、API Key、工具密钥、数据库地址等 |

---

### 5. `app/agent/prompt.py` — 系统提示词

```python
system_prompt = """你是 AI Agent，一个智能助手。
你可以使用提供的工具来帮助用户完成任务。
请始终用中文回复。"""
```

| 项目 | 说明 |
|------|------|
| **作用** | 定义 LLM 的行为风格和约束 |
| **关键点** | 这是影响 LLM 回答质量最关键的位置，调整这里比改代码更有效 |

---

### 6. `app/agent/memory.py` — 对话记忆

```python
class Memory:
    def add_messages(self, messages): ...  # 批量添加
    def add(self, role, content): ...      # 添加单条
    def get_messages(self): ...            # 获取全部
    def clear(self): ...                   # 清空
```

| 项目 | 说明 |
|------|------|
| **作用** | 保存对话上下文，支持自动裁剪（默认保留最近 20 轮） |
| **关键点** | 当前版本作为简单历史存储使用，实际对话编排由 LangGraph 的 AgentState 管理 |

---

### 7. `app/tools/weather.py` — 天气工具

```python
@tool
async def get_weather(city: str) -> str:
    """查询指定城市的当前天气"""
    url = f"...api.openweathermap.org...{city}..."
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        ...
```

| 项目 | 说明 |
|------|------|
| **作用** | 调用 OpenWeather API 查询天气 |
| **关键点** | 使用 `@tool` 装饰器，LangChain 自动生成 JSON Schema；使用 `async` 避免阻塞事件循环 |

---

### 8. `app/agent/tools.py` — 工具注册

```python
def get_tool_registry() -> list:
    return [get_weather, web_search, query_database, browse]
```

| 项目 | 说明 |
|------|------|
| **作用** | 汇集所有工具为一个列表，供 Agent 绑定到 LLM |
| **关键点** | 添加新工具时只需在此处追加一项 |

---

### 9. `app/llm/base.py` — LLM 基类

```python
class BaseLLM:
    def __init__(self, model, temperature, api_key, base_url):
        ...
    def build(self) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=..., temperature=..., api_key=..., base_url=...)
```

| 项目 | 说明 |
|------|------|
| **作用** | 封装 `ChatOpenAI` 的创建参数 |
| **关键点** | 所有供应商都通过 `ChatOpenAI` 创建（因为 DeepSeek、Ollama 都兼容 OpenAI API） |

---

### 10. `app/llm/__init__.py` — LLM 工厂

```python
class LLMFactory:
    _providers = {
        "openai":   lambda: BaseLLM(..., base_url=settings.OPENAI_BASE_URL),
        "deepseek": lambda: BaseLLM(..., base_url=settings.DEEPSEEK_BASE_URL),
        "ollama":   lambda: BaseLLM(..., base_url=settings.OLLAMA_BASE_URL + "/v1"),
    }
    @classmethod
    def create(cls) -> ChatOpenAI:
        return cls._providers[settings.LLM_PROVIDER]().build()
```

| 项目 | 说明 |
|------|------|
| **作用** | 根据 `LLM_PROVIDER` 配置选择对应的供应商并创建 LLM 实例 |
| **关键点** | 通过 `bind_tools()` 将工具注入 LLM，是 Function Calling 的桥梁 |

---

### 11. `app/agent/agent.py` — ⭐ 核心文件（LangGraph Agent）

```python
class AgentState(TypedDict):
    messages: list[BaseMessage]       # LangGraph 状态定义

class Agent:
    def __init__(self):
        self.tools = get_tool_registry()
        self.llm = LLMFactory.create()
        self.graph = self._build_graph()

    def _build_graph(self):            # 构建 StateGraph
        workflow.add_node("agent", _call_model)
        workflow.add_node("tools",  _call_tools)
        workflow.add_conditional_edges("agent", _should_continue, ...)
        workflow.add_edge("tools", "agent")
        return workflow.compile()

    def _call_model(self, state):      # Agent 节点：LLM 推理
        llm_with_tools = self.llm.bind_tools(self.tools)
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    async def _call_tools(self, state): # Tools 节点：执行工具
        for tc in last_msg.tool_calls:
            result = await tool.ainvoke(tc["args"])
            ...

    def _should_continue(self, state):  # 条件边：判断是否继续
        return "tools" if has_tool_calls else END

    async def run(self, messages):      # 对外接口
        lc_messages = [SystemMessage(system_prompt), ...]
        result = await self.graph.ainvoke({"messages": lc_messages})
        return result["messages"][-1].content
```

| 项目 | 说明 |
|------|------|
| **作用** | 整个项目的核心，定义 Agent 工作流 |
| **关键点** | `_build_graph()` 编排状态图；`bind_tools()` 让 LLM 感知可用工具；`_should_continue()` 决定是否循环调用工具 |
| **LangGraph 概念** | `StateGraph`（状态图）、`Node`（节点）、`Edge`（边）、`ConditionalEdge`（条件边）、`CompiledStateGraph`（编译后的可执行图） |

---

### 12. `app/tools/browser.py` — 网页抓取工具

```python
@tool
async def browse(url: str) -> str:
    """访问网页并提取文本内容"""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers={"User-Agent": ...})
        soup = BeautifulSoup(resp.text, "html.parser")
        return soup.get_text(...)[:2000]
```

| 项目 | 说明 |
|------|------|
| **作用** | 抓取网页并提取纯文本（前 2000 字符） |
| **关键点** | 包含异常处理；设置 User-Agent 和超时；使用 BeautifulSoup 解析 HTML |

---

### 13. `app/tools/search.py` — 搜索工具（骨架）

```python
@tool
async def web_search(query: str) -> str:
    """搜索互联网信息（需配置搜索 API）"""
    return f"搜索功能待配置。查询: {query}"
```

| 项目 | 说明 |
|------|------|
| **作用** | 搜索工具的骨架实现，需要接入具体的搜索 API（如 SerpAPI、Bing Search） |
| **关键点** | 保持接口稳定，方便后续替换实现 |

---

### 14. `app/tools/db.py` — 数据库查询工具（骨架）

```python
@tool
async def query_database(sql: str) -> str:
    """执行 SQL 查询"""
    return f"数据库查询功能待实现。SQL: {sql}"
```

| 项目 | 说明 |
|------|------|
| **作用** | 数据库查询工具的骨架，需要接入具体的数据库驱动 |
| **关键点** | 实现时注意 SQL 注入防护和连接池管理 |

---

### 15. `app/core/logging.py` — 日志配置

```python
def setup_logging(level=logging.INFO):
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s  %(name)s  %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
```

| 项目 | 说明 |
|------|------|
| **作用** | 统一日志格式，输出到标准输出 |
| **调用时机** | 在 `lifespan` 中调用，应用启动时执行 |

---

### 16. `app/core/exceptions.py` — 自定义异常

```python
class AgentError(Exception):    # 通用错误
class ConfigError(AgentError):  # 配置错误
```

| 项目 | 说明 |
|------|------|
| **作用** | 定义项目中可能抛出的自定义异常，方便上层统一捕获和处理 |

---

### 17. `app/utils/text.py` — 文本工具

```python
def truncate(text, max_length=2000) -> str:
    """截断文本，超过部分以 ... 替代"""

def remove_extra_whitespace(text) -> str:
    """将连续空白替换为单个空格，去除首尾空白"""
```

| 项目 | 说明 |
|------|------|
| **作用** | 提供通用的文本处理函数 |
| **用途** | `truncate` 可用于工具返回结果过长时截断；`remove_extra_whitespace` 可用于清理爬取内容 |

---

### 18. `app/utils/time.py` — 时间工具

```python
def now_utc() -> datetime:
    """获取当前 UTC 时间"""

def format_timestamp(dt=None) -> str:
    """格式化为 YYYY-MM-DD HH:MM:SS"""
```

| 项目 | 说明 |
|------|------|
| **作用** | 提供常用的时间操作函数 |
| **用途** | 日志时间戳、工具返回结果中附带时间信息等 |

---

### 19. `app/schemas/tool.py` — 工具数据模型

```python
class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str

class ToolResult(BaseModel):
    tool_call_id: str
    content: str
```

| 项目 | 说明 |
|------|------|
| **作用** | 定义工具调用和结果的 Pydantic 模型 |
| **当前用途** | 预留，供未来需要显式序列化工具调用时使用；当前 Agent 内部直接使用 LangChain 的 `ToolMessage` |

### 20. `requirements.txt` — 依赖清单

```
langchain>=0.3.0          # LLM 抽象、工具装饰器
langgraph>=0.2.0          # Agent 工作流（StateGraph）
langchain-openai          # ChatOpenAI 模型
langchain-core            # BaseMessage、@tool 等核心类型
httpx                     # 异步 HTTP 客户端
beautifulsoup4            # HTML 解析
fastapi / uvicorn         # HTTP 服务
pydantic / pydantic-settings  # 配置与校验
```

| 项目 | 说明 |
|------|------|
| **作用** | 项目的全部 Python 依赖 |
| **安装** | `pip install -r requirements.txt` |

---

## 快速速查卡

| 如果你想... | 应该看... |
|-------------|-----------|
| 理解请求的完整处理流程 | `main.py` → `api/chat.py` → `agent/agent.py` |
| 修改 Agent 的行为风格 | `agent/prompt.py` 的 `system_prompt` |
| 添加一个新工具 | 在 `tools/` 下用 `@tool` 定义，在 `agent/tools.py` 注册 |
| 切换 LLM 供应商 | 修改 `.env` 的 `LLM_PROVIDER` |
| 调整 LLM 参数（温度/模型） | 修改 `.env` 的 `LLM_TEMPERATURE` / `LLM_MODEL` |
| 调试 LangGraph 工作流 | `agent/agent.py` 的 `_should_continue()` 和 `_call_tools()` |
| 配置新的 API Key | `core/config.py` 添加字段，`.env` 填入值 |
