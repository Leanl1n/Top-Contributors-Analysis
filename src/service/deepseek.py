"""
DeepSeek API client (OpenAI-compatible).
Uses DEEPSEEK_API_KEY from environment or myenv; base URL: https://api.deepseek.com
"""
import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv("myenv/.env")
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"


class DeepSeekService:
    """Service to call DeepSeek chat API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        self.base_url = base_url or DEFAULT_BASE_URL
        self.model = model or DEFAULT_MODEL
        self._client: Optional["OpenAI"] = None

    @property
    def client(self) -> "OpenAI":
        if OpenAI is None:
            raise ImportError("Install the openai package: pip install openai")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key is required. Set DEEPSEEK_API_KEY or pass api_key=..."
            )
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ):
        """
        Create a chat completion.

        Args:
            messages: List of {"role": "user"|"system"|"assistant", "content": "..."}
            model: Override default model (e.g. "deepseek-chat", "deepseek-reasoner")
            stream: Whether to stream the response.
            **kwargs: Extra args for client.chat.completions.create (e.g. temperature, max_tokens).

        Returns:
            Completion response (or stream iterator if stream=True).
        """
        return self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            stream=stream,
            **kwargs,
        )

    def complete(self, user_content: str, system_content: Optional[str] = None, **kwargs) -> str:
        """
        Simple completion: one user message, optional system message.
        Returns the assistant reply text.
        """
        messages = []
        if system_content:
            messages.append({"role": "system", "content": system_content})
        messages.append({"role": "user", "content": user_content})
        resp = self.chat(messages, **kwargs)
        return (resp.choices[0].message.content or "").strip()


def chat_completion(
    messages: list[dict[str, str]],
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> str:
    """
    One-off chat completion using default DeepSeek config.

    Args:
        messages: List of {"role": "...", "content": "..."}
        api_key: Optional override for DEEPSEEK_API_KEY
        model: Optional model override
        **kwargs: Passed to DeepSeekService.chat

    Returns:
        Assistant message content.
    """
    svc = DeepSeekService(api_key=api_key)
    resp = svc.chat(messages, model=model, **kwargs)
    return (resp.choices[0].message.content or "").strip()
