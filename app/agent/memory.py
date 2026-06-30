"""对话记忆"""

from typing import Optional

from app.schemas.chat import Message


DEFAULT_CONTEXT_LIMIT = 20


class Memory:
    """对话记忆管理类，负责消息的存储和裁剪"""

    def __init__(self, limit: int = DEFAULT_CONTEXT_LIMIT):
        """初始化对话记忆

        Args:
            limit: 最大保留的消息轮数，默认为 20。
        """
        self._messages: list[dict] = []
        self._limit = limit

    def add_messages(self, messages: list[Message]) -> None:
        """批量添加消息

        将 Message 对象列表转换为内部格式并追加到记忆。

        Args:
            messages: Message 对象列表。
        """
        for m in messages:
            self._messages.append({"role": m.role, "content": m.content})
        self._trim()

    def add(self, role: str, content: str) -> None:
        """添加单条消息

        Args:
            role: 消息角色（user / assistant / tool）。
            content: 消息内容。
        """
        self._messages.append({"role": role, "content": content})
        self._trim()

    def get_messages(self) -> list[dict]:
        """获取所有消息

        Returns:
            消息字典列表。
        """
        return list(self._messages)

    def clear(self) -> None:
        """清空对话记忆"""
        self._messages.clear()

    def _trim(self) -> None:
        """裁剪超出限制的消息

        当消息数量超过上限时，移除最早的消息。
        """
        if len(self._messages) > self._limit:
            self._messages = self._messages[-self._limit:]
