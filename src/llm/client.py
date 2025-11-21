"""
LLM Client for OpenRouter
Simple client using Qwen via OpenRouter
"""

from langchain_openai import ChatOpenAI
from src.config.settings import settings


def get_llm(temperature: float = None, streaming: bool = False):
    """
    Get LLM instance for OpenRouter (Qwen).

    Args:
        temperature: Override the default temperature (0-1)
        streaming: Enable streaming mode for faster responses

    Returns:
        ChatOpenAI instance configured for OpenRouter

    Raises:
        ValueError: If OPENROUTER_API_KEY is missing
    """
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not set in .env file")

    temp = temperature if temperature is not None else settings.temperature

    # OpenRouter uses OpenAI-compatible API
    return ChatOpenAI(
        model=settings.openrouter_model,
        temperature=temp,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        streaming=streaming,
        request_timeout=30,  # 30 second timeout
        max_tokens=10000,  # Limit output tokens to control costs
    )


def get_translation_llm(temperature: float = 0.1, streaming: bool = False):
    """
    Get LLM instance for translation (Cohere).

    Args:
        temperature: Temperature for translation (default 0.1 for consistency)
        streaming: Enable streaming mode

    Returns:
        ChatOpenAI instance configured for Cohere translation model

    Raises:
        ValueError: If OPENROUTER_API_KEY is missing
    """
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not set in .env file")

    # Use Cohere model for translation via OpenRouter
    return ChatOpenAI(
        model=settings.translation_model,
        temperature=temperature,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        streaming=streaming,
        request_timeout=30,  # 30 second timeout
        max_tokens=10000,  # Translations are short
    )


# Singleton instances for different use cases
llm_router = get_llm(temperature=0.0)  # Router needs deterministic intent classification
llm_agent = get_llm()  # Default temperature for conversational agents
llm_translator = get_translation_llm()  # Translation model (Cohere)
