"""LLM provider configuration and factory."""

from typing import Optional
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel

from .settings import settings


def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> BaseChatModel:
    """
    Factory function to get LLM instance based on provider.
    
    Args:
        provider: LLM provider name (groq, openai, google). Defaults to settings.
        model: Model name. Defaults to settings.
        temperature: Temperature setting. Defaults to settings.
    
    Returns:
        BaseChatModel instance
    """
    provider = provider or settings.DEFAULT_LLM_PROVIDER
    model = model or settings.DEFAULT_MODEL
    temperature = temperature or settings.DEFAULT_TEMPERATURE
    
    provider_lower = provider.lower()
    
    if provider_lower == "groq":
        api_key = settings.get_api_key("groq")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        return ChatGroq(
            model_name=model,
            temperature=temperature,
            groq_api_key=api_key
        )
    
    elif provider_lower == "openai":
        api_key = settings.get_api_key("openai")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=api_key
        )
    
    elif provider_lower == "google":
        api_key = settings.get_api_key("google")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key
        )
    
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: groq, openai, google"
        )


def get_default_llm() -> BaseChatModel:
    """Get default LLM instance using settings."""
    return get_llm()

