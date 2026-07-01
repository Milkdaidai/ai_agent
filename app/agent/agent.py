"""Agent 核心逻辑（基于 LangGraph）

使用 LangGraph 的 StateGraph 构建状态机驱动的 Agent 工作流：
  用户消息 → Agent 节点（LLM 推理）→ 是否需要调用工具？
    ├─ 是 → 工具节点（执行工具）→ 回到 Agent 节点
    └─ 否 → 返回最终回复
"""

from typing import Any, TypedDict, Literal

from langgraph.graph import StateGraph, END
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)

from app.core.config import settings
from app.agent.prompt import system_prompt
from app.agent.tools import get_tool_registry
from app.llm import LLMFactory
from app.schemas.chat import Message


class AgentState(TypedDict):
    """LangGraph 状态定义

    Attributes:
        messages: 当前对话的所有消息（LangChain BaseMessage 格式）。
    """
    messages: list[BaseMessage]


class Agent:
    """Agent 主类，使用 LangGraph StateGraph 构建对话工作流

    工作流程：
    1. 将请求消息转换为 LangChain 消息格式，注入系统提示词
    2. 进入 Agent 节点：LLM 推理，可选地返回 tool_calls
    3. 条件判断：有 tool_calls 则进入工具节点，否则结束
    4. 工具节点：执行每个工具，结果包装为 ToolMessage 回写状态
    5. 回到 Agent 节点继续推理
    """

    def __init__(self):
        """初始化 Agent，创建 LLM 实例、工具列表和 LangGraph 图"""
        self.tools = get_tool_registry()
        self.llm = LLMFactory.create()
        self.graph = self._build_graph()

    # ── 图构建 ──────────────────────────────────────────

    def _build_graph(self) -> "CompiledStateGraph":
        """构建 LangGraph StateGraph

        Returns:
            编译后的可执行图。
        """
        workflow = StateGraph(AgentState)

        # 注册节点
        workflow.add_node("agent", self._call_model)    # LLM 推理节点
        workflow.add_node("tools", self._call_tools)    # 工具执行节点

        # 设置入口
        workflow.set_entry_point("agent")

        # 条件边：根据 LLM 输出决定下一步
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {"tools": "tools", END: END},
        )

        # 工具执行完后回到 Agent 继续推理
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    # ── 图节点函数 ──────────────────────────────────────

    def _call_model(self, state: AgentState) -> dict:
        """Agent 节点：调用 LLM 进行推理

        将工具绑定到 LLM，让 LLM 可以在需要时选择调用工具。

        Args:
            state: 当前状态（包含消息列表）。

        Returns:
            包含 LLM 回复消息的状态更新。
        """
        messages = state["messages"]
        llm_with_tools = self.llm.bind_tools(self.tools)
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    async def _call_tools(self, state: AgentState) -> dict:
        """工具节点：依次执行 LLM 选择的工具

        遍历最后一条消息中的 tool_calls，逐个执行对应工具，
        并将结果包装为 ToolMessage 写回状态。

        Args:
            state: 当前状态（包含 LLM 返回的 tool_calls）。

        Returns:
            包含所有工具执行结果的状态更新。
        """
        last_message = state["messages"][-1]
        results: list[ToolMessage] = []

        for tc in last_message.tool_calls:
            # 根据工具名称查找对应的 LangChain 工具对象
            tool_map = {t.name: t for t in self.tools}
            tool_fn = tool_map.get(tc["name"])
            if tool_fn is None:
                content = f"错误：未找到工具 '{tc['name']}'"
            else:
                content = await tool_fn.ainvoke(tc["args"])
            results.append(ToolMessage(content=str(content), tool_call_id=tc["id"]))

        return {"messages": results}

    # ── 条件边函数 ──────────────────────────────────────

    @staticmethod
    def _should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        """判断是否继续执行工具

        如果 LLM 返回了 tool_calls，则路由到工具节点；
        否则结束流程。

        Args:
            state: 当前状态。

        Returns:
            下一步的路由目标（"tools" 或 END）。
        """
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # ── 对外接口 ────────────────────────────────────────

    async def run(self, messages: list[Message]) -> str:
        """运行 Agent

        将请求中的消息转换为 LangChain 格式（注入系统提示词），
        提交给 LangGraph 图执行，返回最终回复内容。

        Args:
            messages: 用户发送的消息列表。

        Returns:
            LLM 生成的最终回复文本。
        """
        lc_messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]

        for m in messages:
            if m.role == "user":
                lc_messages.append(HumanMessage(content=m.content))
            elif m.role == "assistant":
                lc_messages.append(AIMessage(content=m.content))

        result = await self.graph.ainvoke({"messages": lc_messages})
        return result["messages"][-1].content
