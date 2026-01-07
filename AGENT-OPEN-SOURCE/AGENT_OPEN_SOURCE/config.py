"""
SYNTHESIS Open Source Agent Framework - Configuration

Manages environment configuration for the agent framework.

Usage:
    from config import Config
    
    print(Config.DEFAULT_PROVIDER)
    print(Config.is_configured())
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Configuration manager for SYNTHESIS agents"""
    
    # ==========================================================================
    # API Keys
    # ==========================================================================
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # ==========================================================================
    # Local LLM Configuration
    # ==========================================================================
    
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LMSTUDIO_BASE_URL: str = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
    
    # ==========================================================================
    # Default Provider & Model
    # ==========================================================================
    
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "openai")
    
    DEFAULT_OPENAI_MODEL: str = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")
    DEFAULT_ANTHROPIC_MODEL: str = os.getenv("DEFAULT_ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    DEFAULT_GOOGLE_MODEL: str = os.getenv("DEFAULT_GOOGLE_MODEL", "gemini-2.0-flash")
    DEFAULT_GROQ_MODEL: str = os.getenv("DEFAULT_GROQ_MODEL", "llama-3.3-70b-versatile")
    DEFAULT_OLLAMA_MODEL: str = os.getenv("DEFAULT_OLLAMA_MODEL", "llama3.2")
    
    # ==========================================================================
    # Agent Settings
    # ==========================================================================
    
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # ==========================================================================
    # Debug & Logging
    # ==========================================================================
    
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ==========================================================================
    # Helper Methods
    # ==========================================================================
    
    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """Get API key for a provider"""
        key_map = {
            "openai": cls.OPENAI_API_KEY,
            "anthropic": cls.ANTHROPIC_API_KEY,
            "google": cls.GOOGLE_API_KEY,
            "groq": cls.GROQ_API_KEY
        }
        return key_map.get(provider.lower())
    
    @classmethod
    def get_default_model(cls, provider: str) -> str:
        """Get default model for a provider"""
        model_map = {
            "openai": cls.DEFAULT_OPENAI_MODEL,
            "anthropic": cls.DEFAULT_ANTHROPIC_MODEL,
            "google": cls.DEFAULT_GOOGLE_MODEL,
            "groq": cls.DEFAULT_GROQ_MODEL,
            "ollama": cls.DEFAULT_OLLAMA_MODEL
        }
        return model_map.get(provider.lower(), "gpt-4o-mini")
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if at least one provider is configured"""
        return any([
            cls.OPENAI_API_KEY,
            cls.ANTHROPIC_API_KEY,
            cls.GOOGLE_API_KEY,
            cls.GROQ_API_KEY
        ])
    
    @classmethod
    def get_configured_providers(cls) -> List[str]:
        """Get list of configured providers"""
        providers = []
        if cls.OPENAI_API_KEY:
            providers.append("openai")
        if cls.ANTHROPIC_API_KEY:
            providers.append("anthropic")
        if cls.GOOGLE_API_KEY:
            providers.append("google")
        if cls.GROQ_API_KEY:
            providers.append("groq")
        # Ollama is always available if server is running
        providers.append("ollama")
        return providers
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary (masks secrets)"""
        def mask(value: str) -> str:
            if not value:
                return "(not set)"
            return value[:8] + "..." if len(value) > 8 else "***"
        
        return {
            "providers": {
                "openai": mask(cls.OPENAI_API_KEY),
                "anthropic": mask(cls.ANTHROPIC_API_KEY),
                "google": mask(cls.GOOGLE_API_KEY),
                "groq": mask(cls.GROQ_API_KEY)
            },
            "local": {
                "ollama_url": cls.OLLAMA_BASE_URL,
                "lmstudio_url": cls.LMSTUDIO_BASE_URL
            },
            "defaults": {
                "provider": cls.DEFAULT_PROVIDER,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_TOKENS
            },
            "debug": cls.DEBUG
        }
    
    @classmethod
    def print_status(cls):
        """Print configuration status"""
        print("\n📋 SYNTHESIS Agent Framework Configuration")
        print("=" * 50)
        
        providers = cls.get_configured_providers()
        print(f"\n✅ Configured Providers: {', '.join(providers)}")
        print(f"🎯 Default Provider: {cls.DEFAULT_PROVIDER}")
        print(f"🤖 Default Model: {cls.get_default_model(cls.DEFAULT_PROVIDER)}")
        
        print("\n🔑 API Keys:")
        for provider in ["openai", "anthropic", "google", "groq"]:
            key = cls.get_api_key(provider)
            status = "✅ Set" if key else "❌ Not set"
            print(f"   {provider.capitalize()}: {status}")
        
        print("\n🖥️  Local LLMs:")
        print(f"   Ollama: {cls.OLLAMA_BASE_URL}")
        print(f"   LM Studio: {cls.LMSTUDIO_BASE_URL}")
        
        print("\n⚙️  Settings:")
        print(f"   Temperature: {cls.TEMPERATURE}")
        print(f"   Max Tokens: {cls.MAX_TOKENS}")
        print(f"   Debug: {'Enabled' if cls.DEBUG else 'Disabled'}")
        print("=" * 50)


# Quick configuration check on import
if not Config.is_configured():
    import warnings
    warnings.warn(
        "No LLM API keys configured. Copy .env.example to .env and add your keys.",
        UserWarning
    )
