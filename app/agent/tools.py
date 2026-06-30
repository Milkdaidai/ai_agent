"""工具注册与调度"""

from typing import Any, Callable

from app.core.exceptions import ToolError


class ToolRegistry:
    """工具注册表，管理工具的定义和调度"""

    def __init__(self):
        """初始化工具注册表"""
        self._tools: dict[str, dict] = {}

    def register(self, name: str, fn: Callable, definition: dict) -> None:
        """注册工具

        Args:
            name: 工具名称。
            fn: 工具函数。
            definition: OpenAI 格式的工具定义。
        """
        self._tools[name] = {"fn": fn, "definition": definition}

    def get_tool_definitions(self) -> list[dict]:
        """获取所有工具的定义

        Returns:
            OpenAI Function Calling 格式的工具定义列表。
        """
        return [t["definition"] for t in self._tools.values()]

    async def execute(self, name: str, arguments: str) -> Any:
        """执行指定工具

        Args:
            name: 工具名称。
            arguments: 工具参数字符串。

        Returns:
            工具执行结果。

        Raises:
            ToolError: 工具未注册时抛出。
        """
        tool = self._tools.get(name)
        if not tool:
            raise ToolError(f"工具 '{name}' 未注册")
        return await tool["fn"](arguments)
