"""LLM provider abstraction and MockLLM implementation.

This module provides the LLM provider interface and a MockLLM implementation
for learning without API keys. The MockLLM provides deterministic responses
for feature extraction, estimation, and BRD parsing tasks.
"""

import os
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional


@dataclass
class ChatMessage:
    """A message in a chat conversation.
    
    Attributes:
        role: The role of the message sender (system, user, assistant)
        content: The message content
    """
    role: str
    content: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers.
    
    All LLM providers (OpenAI, Anthropic, Bedrock, Mock) must implement
    this interface to ensure consistent behavior across the system.
    
    This abstraction supports multiple providers (OpenAI, Anthropic, AWS Bedrock)
    with a unified interface for completion, streaming, and token counting.
    """
    
    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The generated completion text
        """
        ...
    
    @abstractmethod
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a response for a chat conversation.
        
        Args:
            messages: List of chat messages in the conversation
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The generated response text
        """
        ...
    
    @abstractmethod
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given prompt token by token.
        
        This method yields chunks of the response as they are generated,
        enabling real-time output display and lower perceived latency.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional provider-specific parameters
            
        Yields:
            String chunks of the generated response
            
        Example:
            >>> async for chunk in provider.stream("Tell me a story"):
            ...     print(chunk, end="", flush=True)
        """
        ...
        # This is needed to make the method a proper async generator
        # The actual implementation should yield strings
        if False:  # pragma: no cover
            yield ""
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in the given text.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The estimated token count
        """
        ...


class MockLLM(LLMProvider):
    """Deterministic LLM simulator for no-key learning.
    
    MockLLM provides predefined responses for common AITEA tasks,
    enabling learners to complete exercises without API keys.
    Responses are deterministic - the same input always produces
    the same output.
    
    Supported task types:
    - extract_features: Extract features from text descriptions
    - estimate_project: Generate project time estimates
    - parse_brd: Parse Business Requirements Documents
    
    Example:
        >>> mock = MockLLM()
        >>> response = await mock.complete("Extract features from: User login system")
        >>> print(response)  # Returns predefined feature extraction response
    """
    
    # Predefined responses for different task types
    RESPONSES: Dict[str, Dict[str, Any]] = {
        "extract_features": {
            "default": {
                "features": [
                    {"name": "User Authentication", "team": "backend", "estimated_hours": 8},
                    {"name": "User Registration", "team": "backend", "estimated_hours": 6},
                    {"name": "Password Reset", "team": "backend", "estimated_hours": 4},
                ]
            },
            "crud": {
                "features": [
                    {"name": "CRUD API", "team": "backend", "estimated_hours": 4},
                    {"name": "Data Validation", "team": "backend", "estimated_hours": 2},
                    {"name": "Database Schema", "team": "backend", "estimated_hours": 3},
                ]
            },
            "frontend": {
                "features": [
                    {"name": "UI Components", "team": "frontend", "estimated_hours": 6},
                    {"name": "Form Handling", "team": "frontend", "estimated_hours": 4},
                    {"name": "State Management", "team": "frontend", "estimated_hours": 5},
                ]
            },
        },
        "estimate_project": {
            "default": {
                "total_hours": 40,
                "confidence": "medium",
                "breakdown": [
                    {"feature": "Backend API", "hours": 16},
                    {"feature": "Frontend UI", "hours": 12},
                    {"feature": "Testing", "hours": 8},
                    {"feature": "Documentation", "hours": 4},
                ]
            },
            "small": {
                "total_hours": 16,
                "confidence": "high",
                "breakdown": [
                    {"feature": "Core Feature", "hours": 8},
                    {"feature": "Testing", "hours": 4},
                    {"feature": "Documentation", "hours": 4},
                ]
            },
            "large": {
                "total_hours": 120,
                "confidence": "low",
                "breakdown": [
                    {"feature": "Backend Services", "hours": 40},
                    {"feature": "Frontend Application", "hours": 32},
                    {"feature": "Integration", "hours": 24},
                    {"feature": "Testing", "hours": 16},
                    {"feature": "Documentation", "hours": 8},
                ]
            },
        },
        "parse_brd": {
            "default": {
                "title": "Sample Project",
                "description": "A sample business requirements document",
                "features": [
                    {
                        "id": "F001",
                        "name": "User Management",
                        "priority": "high",
                        "description": "Manage user accounts and permissions",
                    },
                    {
                        "id": "F002",
                        "name": "Data Dashboard",
                        "priority": "medium",
                        "description": "Display key metrics and analytics",
                    },
                ],
                "constraints": ["Must support 1000 concurrent users", "Response time < 200ms"],
            }
        },
    }

    
    def __init__(self) -> None:
        """Initialize the MockLLM."""
        self._call_count: int = 0
    
    def _detect_task_type(self, text: str) -> str:
        """Detect the task type from the input text.
        
        Args:
            text: The input prompt or message content
            
        Returns:
            The detected task type (extract_features, estimate_project, parse_brd)
        """
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["extract", "feature", "identify"]):
            return "extract_features"
        elif any(kw in text_lower for kw in ["estimate", "time", "hours", "project"]):
            return "estimate_project"
        elif any(kw in text_lower for kw in ["brd", "business requirement", "parse", "document"]):
            return "parse_brd"
        
        return "extract_features"  # Default task type
    
    def _detect_variant(self, text: str, task_type: str) -> str:
        """Detect the response variant based on input text.
        
        Args:
            text: The input prompt or message content
            task_type: The detected task type
            
        Returns:
            The variant key for the response
        """
        text_lower = text.lower()
        
        if task_type == "extract_features":
            if "crud" in text_lower or "create read update delete" in text_lower:
                return "crud"
            elif any(kw in text_lower for kw in ["frontend", "ui", "interface", "component"]):
                return "frontend"
        elif task_type == "estimate_project":
            if any(kw in text_lower for kw in ["small", "simple", "quick", "minor"]):
                return "small"
            elif any(kw in text_lower for kw in ["large", "complex", "enterprise", "major"]):
                return "large"
        
        return "default"
    
    def _get_response(self, text: str) -> Dict[str, Any]:
        """Get the appropriate response for the input text.
        
        Args:
            text: The input prompt or message content
            
        Returns:
            The response dictionary for the detected task and variant
        """
        task_type = self._detect_task_type(text)
        variant = self._detect_variant(text, task_type)
        
        task_responses = self.RESPONSES.get(task_type, {})
        return task_responses.get(variant, task_responses.get("default", {}))
    
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a deterministic completion for the given prompt.
        
        The response is determined by detecting the task type and variant
        from the prompt content.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Ignored (for API compatibility)
            
        Returns:
            A JSON string containing the predefined response
        """
        import json
        
        self._call_count += 1
        response = self._get_response(prompt)
        return json.dumps(response, indent=2)
    
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a deterministic response for a chat conversation.
        
        Uses the last user message to determine the response.
        
        Args:
            messages: List of chat messages in the conversation
            **kwargs: Ignored (for API compatibility)
            
        Returns:
            A JSON string containing the predefined response
        """
        import json
        
        self._call_count += 1
        
        # Find the last user message
        user_content = ""
        for msg in reversed(messages):
            if msg.role == "user":
                user_content = msg.content
                break
        
        response = self._get_response(user_content)
        return json.dumps(response, indent=2)
    
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a deterministic completion for the given prompt.
        
        Simulates streaming by yielding the response in small chunks.
        This allows learners to test streaming patterns without API keys.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Ignored (for API compatibility)
            
        Yields:
            String chunks of the predefined response
        """
        import json
        import asyncio
        
        self._call_count += 1
        response = self._get_response(prompt)
        response_str = json.dumps(response, indent=2)
        
        # Simulate streaming by yielding chunks of ~10 characters
        chunk_size = 10
        for i in range(0, len(response_str), chunk_size):
            yield response_str[i:i + chunk_size]
            # Small delay to simulate network latency
            await asyncio.sleep(0.01)
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count using a simple heuristic.
        
        Uses approximately 4 characters per token as a rough estimate.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The estimated token count
        """
        # Simple heuristic: ~4 characters per token on average
        return len(text) // 4 + 1
    
    @property
    def call_count(self) -> int:
        """Get the number of calls made to this MockLLM instance."""
        return self._call_count



# Warning message displayed when running in mock mode
MOCK_MODE_WARNING = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           ⚠️  MOCK LLM MODE ACTIVE                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  No API keys detected. Using MockLLM with predefined responses.              ║
║                                                                              ║
║  To use a real LLM provider, set one of these environment variables:         ║
║    • OPENAI_API_KEY       - For OpenAI GPT models                            ║
║    • COHERE_API_KEY       - For Cohere Command models                        ║
║    • GOOGLE_API_KEY       - For Google Gemini models                         ║
║    • XAI_API_KEY          - For xAI Grok models                              ║
║    • MISTRAL_API_KEY      - For Mistral AI models                            ║
║    • HUGGINGFACE_API_KEY  - For HuggingFace Inference API                    ║
║    • ANTHROPIC_API_KEY    - For Anthropic Claude models                      ║
║    • AWS_ACCESS_KEY_ID    - For AWS Bedrock models (with AWS_SECRET_ACCESS_KEY)║
║    • OLLAMA_HOST          - For local Ollama models (default: localhost:11434)║
║                                                                              ║
║  The system tries providers in priority order with automatic fallback.       ║
║  MockLLM provides deterministic responses for learning purposes.             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def _check_api_keys() -> Dict[str, bool]:
    """Check which API keys are available in the environment.
    
    Returns:
        Dictionary mapping provider names to availability status
    """
    return {
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "cohere": bool(os.environ.get("COHERE_API_KEY")),
        "gemini": bool(os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY_2")),
        "grok": bool(os.environ.get("XAI_API_KEY")),
        "mistral": bool(os.environ.get("MISTRAL_API_KEY")),
        "huggingface": bool(os.environ.get("HUGGINGFACE_API_KEY")),
        "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "bedrock": bool(
            os.environ.get("AWS_ACCESS_KEY_ID") and 
            os.environ.get("AWS_SECRET_ACCESS_KEY")
        ),
    }


def _check_ollama_available() -> bool:
    """Check if Ollama is running locally.
    
    Returns:
        True if Ollama is available, False otherwise
    """
    try:
        import httpx
        import asyncio
        
        async def check():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
                        timeout=2.0
                    )
                    return response.status_code == 200
            except:
                return False
        
        return asyncio.run(check())
    except:
        return False


def _display_mock_warning() -> None:
    """Display a warning message indicating mock mode is active."""
    warnings.warn(
        "No LLM API keys found. Using MockLLM with predefined responses.",
        UserWarning,
        stacklevel=3
    )
    print(MOCK_MODE_WARNING)


def get_llm_provider(
    provider: str = "auto",
    show_warning: bool = True,
    use_fallback_chain: bool = False,
    **kwargs: Any
) -> LLMProvider:
    """Get an LLM provider based on available API keys.
    
    When provider is "auto", this function checks for available API keys
    in the following priority order:
    1. OpenAI → 2. Cohere → 3. Gemini → 4. Grok → 5. Mistral → 
    6. HuggingFace → 7. Ollama → 8. Anthropic → 9. Bedrock → 10. MockLLM
    
    If no keys are found, it returns a MockLLM instance.
    
    Args:
        provider: The provider to use. Options:
            - "auto": Automatically select based on available API keys
            - "fallback": Use FallbackChain to try all providers in order
            - "mock": Always use MockLLM
            - "openai": Use OpenAI (requires OPENAI_API_KEY)
            - "cohere": Use Cohere (requires COHERE_API_KEY)
            - "gemini": Use Google Gemini (requires GOOGLE_API_KEY)
            - "grok": Use xAI Grok (requires XAI_API_KEY)
            - "mistral": Use Mistral AI (requires MISTRAL_API_KEY)
            - "huggingface": Use HuggingFace (requires HUGGINGFACE_API_KEY)
            - "ollama": Use Ollama (requires Ollama running locally)
            - "anthropic": Use Anthropic (requires ANTHROPIC_API_KEY)
            - "bedrock": Use AWS Bedrock (requires AWS credentials)
        show_warning: Whether to display a warning when using MockLLM
        use_fallback_chain: If True, returns a FallbackChain that tries all
                           available providers in order (same as provider="fallback")
        **kwargs: Additional provider-specific parameters (model, temperature, etc.)
            
    Returns:
        An LLMProvider instance (or FallbackChain if use_fallback_chain=True)
        
    Raises:
        ValueError: If the requested provider is not available
        
    Example:
        >>> # Auto-select provider based on available keys
        >>> llm = get_llm_provider()
        
        >>> # Use fallback chain to try all providers
        >>> llm = get_llm_provider("fallback")
        >>> # or
        >>> llm = get_llm_provider(use_fallback_chain=True)
        
        >>> # Explicitly use MockLLM for testing
        >>> llm = get_llm_provider("mock", show_warning=False)
        
        >>> # Use OpenAI with specific model
        >>> llm = get_llm_provider("openai", model="gpt-4o")
        
        >>> # Use Cohere with specific model
        >>> llm = get_llm_provider("cohere", model="command-r-plus")
    """
    # Import providers here to avoid circular imports
    from .providers import (
        OpenAIProvider, CohereProvider, GeminiProvider, MistralProvider,
        HuggingFaceProvider, OllamaProvider, AnthropicProvider, BedrockProvider,
        FallbackChain
    )
    
    available_keys = _check_api_keys()
    
    # Handle fallback chain request
    if provider == "fallback" or use_fallback_chain:
        chain = FallbackChain.from_environment(show_warnings=show_warning, **kwargs)
        
        # Show warning if only MockLLM is available
        if len(chain.providers) == 1 and chain.providers[0][0] == "MockLLM":
            if show_warning:
                _display_mock_warning()
        else:
            available = [name for name, _ in chain.providers if name != "MockLLM"]
            if available:
                print(f"🔗 Fallback chain initialized with providers: {' → '.join(available)} → MockLLM")
        
        return chain
    
    # Handle explicit mock request
    if provider == "mock":
        if show_warning:
            _display_mock_warning()
        return MockLLM()
    
    # Handle auto-selection with priority order
    if provider == "auto":
        # Priority order: OpenAI → Cohere → Gemini → Grok → Mistral → HuggingFace → Ollama → Anthropic → Bedrock
        if available_keys["openai"]:
            return OpenAIProvider(**kwargs)
        elif available_keys["cohere"]:
            return CohereProvider(**kwargs)
        elif available_keys["gemini"]:
            return GeminiProvider(**kwargs)
        elif available_keys["grok"]:
            # Grok uses OpenAI-compatible API
            return OpenAIProvider(api_key=os.environ.get("XAI_API_KEY"), **kwargs)
        elif available_keys["mistral"]:
            return MistralProvider(**kwargs)
        elif available_keys["huggingface"]:
            return HuggingFaceProvider(**kwargs)
        elif _check_ollama_available():
            return OllamaProvider(**kwargs)
        elif available_keys["anthropic"]:
            return AnthropicProvider(**kwargs)
        elif available_keys["bedrock"]:
            return BedrockProvider(**kwargs)
        
        # No API keys found - use MockLLM
        if show_warning:
            _display_mock_warning()
        return MockLLM()
    
    # Handle explicit provider requests
    if provider == "openai":
        if not available_keys["openai"]:
            raise ValueError(
                "OpenAI provider requested but OPENAI_API_KEY not set. "
                "Set the environment variable or use provider='mock'."
            )
        return OpenAIProvider(**kwargs)
    
    if provider == "cohere":
        if not available_keys["cohere"]:
            raise ValueError(
                "Cohere provider requested but COHERE_API_KEY not set. "
                "Set the environment variable or use provider='mock'."
            )
        return CohereProvider(**kwargs)
    
    if provider == "gemini":
        if not available_keys["gemini"]:
            raise ValueError(
                "Gemini provider requested but GOOGLE_API_KEY not set. "
                "Set the environment variable or use provider='mock'."
            )
        return GeminiProvider(**kwargs)
    
    if provider == "grok":
        if not available_keys["grok"]:
            raise ValueError(
                "Grok provider requested but XAI_API_KEY not set. "
                "Set the environment variable or use provider='mock'."
            )
        # Grok uses OpenAI-compatible API
        return OpenAIProvider(api_key=os.environ.get("XAI_API_KEY"), **kwargs)
    
    if provider == "mistral":
        if not available_keys["mistral"]:
            raise ValueError(
                "Mistral provider requested but MISTRAL_API_KEY not set. "
                "Set the environment variable or use provider='mock'."
            )
        return MistralProvider(**kwargs)
    
    if provider == "huggingface":
        if not available_keys["huggingface"]:
            raise ValueError(
                "HuggingFace provider requested but HUGGINGFACE_API_KEY not set. "
                "Set the environment variable or use provider='mock'."
            )
        return HuggingFaceProvider(**kwargs)
    
    if provider == "ollama":
        if not _check_ollama_available():
            raise ValueError(
                "Ollama provider requested but Ollama is not running. "
                "Start Ollama or use provider='mock'."
            )
        return OllamaProvider(**kwargs)
    
    if provider == "anthropic":
        if not available_keys["anthropic"]:
            raise ValueError(
                "Anthropic provider requested but ANTHROPIC_API_KEY not set. "
                "Set the environment variable or use provider='mock'."
            )
        return AnthropicProvider(**kwargs)
    
    if provider == "bedrock":
        if not available_keys["bedrock"]:
            raise ValueError(
                "Bedrock provider requested but AWS credentials not set. "
                "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or use provider='mock'."
            )
        return BedrockProvider(**kwargs)
    
    raise ValueError(
        f"Unknown provider: {provider}. "
        f"Valid options: auto, fallback, mock, openai, cohere, gemini, grok, mistral, "
        f"huggingface, ollama, anthropic, bedrock"
    )


def get_fallback_chain(show_warning: bool = True, **kwargs: Any) -> "FallbackChain":
    """Convenience function to get a FallbackChain directly.
    
    Creates a FallbackChain that tries all available providers in priority order:
    1. OpenAI → 2. Cohere → 3. Gemini → 4. Grok → 5. Mistral → 
    6. HuggingFace → 7. Ollama → 8. Anthropic → 9. Bedrock → 10. MockLLM
    
    Args:
        show_warning: Whether to display warnings when falling back
        **kwargs: Additional provider-specific parameters
        
    Returns:
        A FallbackChain instance
        
    Example:
        >>> chain = get_fallback_chain()
        >>> response = await chain.complete("Hello!")
        >>> print(f"Handled by: {chain.last_provider_used}")
    """
    from .providers import FallbackChain
    return FallbackChain.from_environment(show_warnings=show_warning, **kwargs)
