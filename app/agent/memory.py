"""对话记忆"""

from typing import Optional

from app.schemas.chat import Message


DEFAULT_CONTEXT_LIMIT = 20


class Memory:
    def __init__(self, limit: int = DEFAULT_CONTEXT_LIMIT):
        self._messages: list[dict] = []
        self._limit = limit

    def add_messages(self, messages: list[Message]) -> None:
        for m in messages:
            self._messages.append({"role": m.role, "content": m.content})
        self._trim()

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        self._trim()

    def get_messages(self) -> list[dict]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def _trim(self) -> None:
        if len(self._messages) > self._limit:
            self._messages = self._messages[-self._limit:]
