"""工具注册与调度"""

from typing import Any, Callable

from app.core.exceptions import ToolError


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, dict] = {}

    def register(self, name: str, fn: Callable, definition: dict) -> None:
        self._tools[name] = {"fn": fn, "definition": definition}

    def get_tool_definitions(self) -> list[dict]:
        return [t["definition"] for t in self._tools.values()]

    async def execute(self, name: str, arguments: str) -> Any:
        tool = self._tools.get(name)
        if not tool:
            raise ToolError(f"工具 '{name}' 未注册")
        return await tool["fn"](arguments)
