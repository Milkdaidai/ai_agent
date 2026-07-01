"""自定义异常"""


class AgentError(Exception):
    """Agent 通用错误"""


class ConfigError(AgentError):
    """配置错误"""
