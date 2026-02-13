"""
POLYMARKET ALPHA MODE - LLM Integration
======================================
Unified interface for LLM providers (Anthropic Claude, OpenAI GPT).
Agents use this to get AI-powered analysis.
"""

import asyncio
import json
from typing import Dict, Any, Optional, Literal
from abc import ABC, abstractmethod
from loguru import logger

from config.settings import settings


# ============================================
# ABSTRACT LLM PROVIDER
# ============================================

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        response_format: Optional[Literal["json", "text"]] = None
    ) -> str:
        """Generate a completion."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and available."""
        pass


# ============================================
# ANTHROPIC CLAUDE PROVIDER
# ============================================

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self):
        self._client = None
        self._api_key = settings.anthropic_api_key
    
    def is_available(self) -> bool:
        return bool(self._api_key)
    
    async def _ensure_client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None and self._api_key:
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self._api_key)
            except ImportError:
                logger.warning("anthropic package not installed")
                return False
        return self._client is not None
    
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        response_format: Optional[Literal["json", "text"]] = None
    ) -> str:
        if not await self._ensure_client():
            raise RuntimeError("Anthropic client not available")
        
        try:
            # Add JSON instruction if needed
            if response_format == "json":
                system_prompt += "\n\nRespond ONLY with valid JSON. No markdown, no explanation."
            
            message = await self._client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


# ============================================
# OPENAI GPT PROVIDER
# ============================================

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT API provider."""
    
    def __init__(self):
        self._client = None
        self._api_key = settings.openai_api_key
    
    def is_available(self) -> bool:
        return bool(self._api_key)
    
    async def _ensure_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None and self._api_key:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self._api_key)
            except ImportError:
                logger.warning("openai package not installed")
                return False
        return self._client is not None
    
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        response_format: Optional[Literal["json", "text"]] = None
    ) -> str:
        if not await self._ensure_client():
            raise RuntimeError("OpenAI client not available")
        
        try:
            kwargs = {
                "model": "gpt-4o",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}
            
            response = await self._client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


# ============================================
# LLM MANAGER (UNIFIED INTERFACE)
# ============================================

class LLMManager:
    """
    Unified LLM interface with automatic fallback.
    Priority: Anthropic > OpenAI > Rule-based fallback
    """
    
    def __init__(self):
        self._providers: list[BaseLLMProvider] = [
            AnthropicProvider(),
            OpenAIProvider(),
        ]
        self._active_provider: Optional[BaseLLMProvider] = None
        self._select_provider()
    
    def _select_provider(self):
        """Select the first available provider."""
        for provider in self._providers:
            if provider.is_available():
                self._active_provider = provider
                provider_name = provider.__class__.__name__
                logger.info(f"LLM Provider selected: {provider_name}")
                return
        
        logger.warning("No LLM provider available - using rule-based fallback")
        self._active_provider = None
    
    @property
    def has_llm(self) -> bool:
        """Check if an LLM provider is available."""
        return self._active_provider is not None
    
    @property
    def provider_name(self) -> str:
        """Get the name of the active provider."""
        if self._active_provider:
            return self._active_provider.__class__.__name__
        return "None (Rule-based)"
    
    async def analyze(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.5,
        max_tokens: int = 1024
    ) -> Optional[Dict[str, Any]]:
        """
        Get LLM analysis as parsed JSON.
        
        Returns None if no LLM available or parsing fails.
        """
        if not self._active_provider:
            return None
        
        try:
            response = await self._active_provider.complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format="json"
            )
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            return json.loads(response.strip())
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return None
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Optional[str]:
        """
        Get LLM text generation (non-JSON).
        
        Returns None if no LLM available.
        """
        if not self._active_provider:
            return None
        
        try:
            return await self._active_provider.complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format="text"
            )
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None


# ============================================
# SINGLETON INSTANCE
# ============================================

llm_manager = LLMManager()
