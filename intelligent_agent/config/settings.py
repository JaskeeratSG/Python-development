"""Application settings and configuration management."""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    SERPER_API_KEY: Optional[str] = os.getenv("SERPER_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "groq")
    # Updated: llama-3.1-70b-versatile was decommissioned
    # Common Groq models: llama-3.1-8b-instant, mixtral-8x7b-32768, gemma2-9b-it
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant")
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    
    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/intelligent_agent_db"
    )
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required API keys are set."""
        errors = []
        
        if not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is required. Get it from https://console.groq.com/")
        
        if not cls.TAVILY_API_KEY:
            errors.append("TAVILY_API_KEY is required. Get it from https://tavily.com/")
        
        if errors:
            raise ValueError("\n".join(errors))
        
        return True
    
    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        key_map = {
            "groq": cls.GROQ_API_KEY,
            "openai": cls.OPENAI_API_KEY,
            "google": cls.GOOGLE_API_KEY,
            "tavily": cls.TAVILY_API_KEY,
            "serper": cls.SERPER_API_KEY,
        }
        return key_map.get(provider.lower())


# Create a singleton instance
settings = Settings()

