"""自定义异常"""


class AgentError(Exception):
    """Agent 通用错误"""


class LLMError(AgentError):
    """LLM 调用错误"""


class ToolError(AgentError):
    """工具执行错误"""


class ConfigError(AgentError):
    """配置错误"""
