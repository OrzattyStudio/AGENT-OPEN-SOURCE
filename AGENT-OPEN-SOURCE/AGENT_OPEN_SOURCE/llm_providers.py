"""
SYNTHESIS Open Source Agent Framework - LLM Provider Abstraction

Enterprise-grade LLM provider interface supporting:
- OpenAI (GPT-4o, GPT-4o-mini)
- Anthropic (Claude 3.5 Sonnet)
- Google (Gemini 2.0)
- Groq (Llama 3.3 70B)
- Ollama (Local models)
- LM Studio (Local models)

Usage:
    from llm_providers import get_provider, LLMMessage
    
    provider = get_provider("openai")
    response = await provider.chat([
        LLMMessage(role="user", content="Hello!")
    ])
"""

import os
import json
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger("SynthesisLLM")


class ProviderType(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"


@dataclass
class LLMMessage:
    """A message in the conversation"""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None


@dataclass
class LLMResponse:
    """Response from an LLM provider"""
    success: bool
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None
    raw_response: Optional[Dict] = None


@dataclass
class ToolDefinition:
    """Definition for a function/tool the LLM can call"""
    name: str
    description: str
    parameters: Dict[str, Any]


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = "gpt-4o-mini"
        self.provider_name = "base"
        self.timeout = 120
    
    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        tools: Optional[List[ToolDefinition]] = None,
        json_mode: bool = False
    ) -> LLMResponse:
        """Send a chat completion request"""
        pass
    
    async def chat_stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """Stream a chat completion response"""
        # Default implementation - most providers override this
        response = await self.chat(messages, model, temperature, max_tokens)
        yield response.content
    
    def _format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, str]]:
        """Format messages for API request"""
        return [{"role": m.role, "content": m.content} for m in messages]
    
    def is_available(self) -> bool:
        """Check if provider is properly configured"""
        return bool(self.api_key or self.base_url)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider (GPT-4o, GPT-4o-mini)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"))
        self.base_url = "https://api.openai.com/v1"
        self.default_model = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")
        self.provider_name = "openai"
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        tools: Optional[List[ToolDefinition]] = None,
        json_mode: bool = False
    ) -> LLMResponse:
        if not httpx:
            return LLMResponse(False, "", model or self.default_model, self.provider_name, 
                             error="httpx not installed. Run: pip install httpx")
        
        if not self.api_key:
            return LLMResponse(False, "", model or self.default_model, self.provider_name,
                             error="OPENAI_API_KEY not set")
        
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters
                    }
                }
                for t in tools
            ]
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"] or ""
                    usage = data.get("usage", {})
                    return LLMResponse(
                        success=True,
                        content=content,
                        model=model,
                        provider=self.provider_name,
                        usage={
                            "prompt_tokens": usage.get("prompt_tokens", 0),
                            "completion_tokens": usage.get("completion_tokens", 0),
                            "total_tokens": usage.get("total_tokens", 0)
                        },
                        raw_response=data
                    )
                else:
                    return LLMResponse(
                        success=False,
                        content="",
                        model=model,
                        provider=self.provider_name,
                        error=f"HTTP {response.status_code}: {response.text[:200]}"
                    )
        except Exception as e:
            return LLMResponse(False, "", model, self.provider_name, error=str(e))


class AnthropicProvider(BaseLLMProvider):
    """Anthropic API provider (Claude 3.5 Sonnet)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.base_url = "https://api.anthropic.com/v1"
        self.default_model = os.getenv("DEFAULT_ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.provider_name = "anthropic"
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        tools: Optional[List[ToolDefinition]] = None,
        json_mode: bool = False
    ) -> LLMResponse:
        if not httpx:
            return LLMResponse(False, "", model or self.default_model, self.provider_name,
                             error="httpx not installed")
        
        if not self.api_key:
            return LLMResponse(False, "", model or self.default_model, self.provider_name,
                             error="ANTHROPIC_API_KEY not set")
        
        model = model or self.default_model
        
        # Anthropic uses a different message format
        system_msg = None
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system_msg = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})
        
        payload = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if system_msg:
            payload["system"] = system_msg
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["content"][0]["text"] if data.get("content") else ""
                    usage = data.get("usage", {})
                    return LLMResponse(
                        success=True,
                        content=content,
                        model=model,
                        provider=self.provider_name,
                        usage={
                            "prompt_tokens": usage.get("input_tokens", 0),
                            "completion_tokens": usage.get("output_tokens", 0),
                            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                        },
                        raw_response=data
                    )
                else:
                    return LLMResponse(False, "", model, self.provider_name,
                                     error=f"HTTP {response.status_code}: {response.text[:200]}")
        except Exception as e:
            return LLMResponse(False, "", model, self.provider_name, error=str(e))


class GoogleProvider(BaseLLMProvider):
    """Google AI Studio provider (Gemini 2.0)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("GOOGLE_API_KEY"))
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.default_model = os.getenv("DEFAULT_GOOGLE_MODEL", "gemini-2.0-flash")
        self.provider_name = "google"
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        tools: Optional[List[ToolDefinition]] = None,
        json_mode: bool = False
    ) -> LLMResponse:
        if not httpx:
            return LLMResponse(False, "", model or self.default_model, self.provider_name,
                             error="httpx not installed")
        
        if not self.api_key:
            return LLMResponse(False, "", model or self.default_model, self.provider_name,
                             error="GOOGLE_API_KEY not set")
        
        model = model or self.default_model
        
        # Convert messages to Gemini format
        contents = []
        system_instruction = None
        
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
            elif m.role == "user":
                contents.append({"role": "user", "parts": [{"text": m.content}]})
            elif m.role == "assistant":
                contents.append({"role": "model", "parts": [{"text": m.content}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"
        
        try:
            url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    content = ""
                    if data.get("candidates"):
                        parts = data["candidates"][0].get("content", {}).get("parts", [])
                        content = parts[0].get("text", "") if parts else ""
                    
                    usage = data.get("usageMetadata", {})
                    return LLMResponse(
                        success=True,
                        content=content,
                        model=model,
                        provider=self.provider_name,
                        usage={
                            "prompt_tokens": usage.get("promptTokenCount", 0),
                            "completion_tokens": usage.get("candidatesTokenCount", 0),
                            "total_tokens": usage.get("totalTokenCount", 0)
                        },
                        raw_response=data
                    )
                else:
                    return LLMResponse(False, "", model, self.provider_name,
                                     error=f"HTTP {response.status_code}: {response.text[:200]}")
        except Exception as e:
            return LLMResponse(False, "", model, self.provider_name, error=str(e))


class GroqProvider(BaseLLMProvider):
    """Groq API provider (Llama 3.3, ultra-fast inference)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("GROQ_API_KEY"))
        self.base_url = "https://api.groq.com/openai/v1"
        self.default_model = os.getenv("DEFAULT_GROQ_MODEL", "llama-3.3-70b-versatile")
        self.provider_name = "groq"
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        tools: Optional[List[ToolDefinition]] = None,
        json_mode: bool = False
    ) -> LLMResponse:
        if not httpx:
            return LLMResponse(False, "", model or self.default_model, self.provider_name,
                             error="httpx not installed")
        
        if not self.api_key:
            return LLMResponse(False, "", model or self.default_model, self.provider_name,
                             error="GROQ_API_KEY not set")
        
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"] or ""
                    usage = data.get("usage", {})
                    return LLMResponse(
                        success=True,
                        content=content,
                        model=model,
                        provider=self.provider_name,
                        usage={
                            "prompt_tokens": usage.get("prompt_tokens", 0),
                            "completion_tokens": usage.get("completion_tokens", 0),
                            "total_tokens": usage.get("total_tokens", 0)
                        },
                        raw_response=data
                    )
                else:
                    return LLMResponse(False, "", model, self.provider_name,
                                     error=f"HTTP {response.status_code}: {response.text[:200]}")
        except Exception as e:
            return LLMResponse(False, "", model, self.provider_name, error=str(e))


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, base_url: Optional[str] = None):
        super().__init__(base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
        self.default_model = os.getenv("DEFAULT_OLLAMA_MODEL", "llama3.2")
        self.provider_name = "ollama"
    
    def is_available(self) -> bool:
        return bool(self.base_url)
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        tools: Optional[List[ToolDefinition]] = None,
        json_mode: bool = False
    ) -> LLMResponse:
        if not httpx:
            return LLMResponse(False, "", model or self.default_model, self.provider_name,
                             error="httpx not installed")
        
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": self._format_messages(messages),
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if json_mode:
            payload["format"] = "json"
        
        try:
            async with httpx.AsyncClient(timeout=300) as client:  # Longer timeout for local
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("message", {}).get("content", "")
                    return LLMResponse(
                        success=True,
                        content=content,
                        model=model,
                        provider=self.provider_name,
                        usage={
                            "prompt_tokens": data.get("prompt_eval_count", 0),
                            "completion_tokens": data.get("eval_count", 0),
                            "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                        },
                        raw_response=data
                    )
                else:
                    return LLMResponse(False, "", model, self.provider_name,
                                     error=f"HTTP {response.status_code}: {response.text[:200]}")
        except Exception as e:
            return LLMResponse(False, "", model, self.provider_name, error=str(e))


# Provider registry
_PROVIDERS: Dict[str, type] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
    "groq": GroqProvider,
    "ollama": OllamaProvider
}

_provider_instances: Dict[str, BaseLLMProvider] = {}


def get_provider(name: str = None) -> BaseLLMProvider:
    """Get an LLM provider instance by name
    
    Args:
        name: Provider name (openai, anthropic, google, groq, ollama)
              If None, uses DEFAULT_PROVIDER env var or "openai"
    
    Returns:
        BaseLLMProvider instance
    """
    name = name or os.getenv("DEFAULT_PROVIDER", "openai")
    name = name.lower()
    
    if name not in _provider_instances:
        if name not in _PROVIDERS:
            raise ValueError(f"Unknown provider: {name}. Available: {list(_PROVIDERS.keys())}")
        _provider_instances[name] = _PROVIDERS[name]()
    
    return _provider_instances[name]


def get_available_providers() -> List[str]:
    """Get list of properly configured providers"""
    available = []
    for name, cls in _PROVIDERS.items():
        try:
            provider = cls()
            if provider.is_available():
                available.append(name)
        except:
            pass
    return available


async def chat_with_fallback(
    messages: List[LLMMessage],
    providers: Optional[List[str]] = None,
    **kwargs
) -> LLMResponse:
    """Try multiple providers in sequence until one succeeds
    
    Args:
        messages: List of messages
        providers: List of provider names to try in order
        **kwargs: Additional arguments for chat()
    
    Returns:
        LLMResponse from the first successful provider
    """
    if providers is None:
        providers = get_available_providers()
    
    if not providers:
        return LLMResponse(False, "", "", "", error="No providers available")
    
    errors = []
    for provider_name in providers:
        try:
            provider = get_provider(provider_name)
            response = await provider.chat(messages, **kwargs)
            if response.success:
                return response
            errors.append(f"{provider_name}: {response.error}")
        except Exception as e:
            errors.append(f"{provider_name}: {str(e)}")
    
    return LLMResponse(
        success=False,
        content="",
        model="",
        provider="",
        error=f"All providers failed: {'; '.join(errors)}"
    )
