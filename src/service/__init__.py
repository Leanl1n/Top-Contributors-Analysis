"""
Service layer: external APIs (e.g. DeepSeek).
"""
from .deepseek import DeepSeekService, chat_completion

__all__ = ["DeepSeekService", "chat_completion"]
