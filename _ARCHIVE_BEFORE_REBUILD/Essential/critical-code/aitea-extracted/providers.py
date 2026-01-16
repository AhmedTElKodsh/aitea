"""Multi-provider LLM implementations.

This module provides concrete LLM provider implementations for:
- OpenAI GPT models (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
- Anthropic Claude models (claude-3.5-sonnet, claude-3-haiku)
- AWS Bedrock models (Claude, Titan, Llama)

Each provider implements the LLMProvider interface with complete(),
stream(), chat(), and count_tokens() methods.

Example:
    >>> from src.services.providers import OpenAIProvider
    >>> provider = OpenAIProvider(model="gpt-4o-mini")
    >>> response = await provider.complete("Hello, world!")
"""

import os
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional

from .llm import LLMProvider, ChatMessage


@dataclass
class ProviderConfig:
    """Configuration for LLM providers.
    
    Attributes:
        model: The model identifier to use
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
    """
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 60.0


class OpenAIProvider(LLMProvider):
    """OpenAI GPT models provider.
    
    Supports GPT-4o, GPT-4o-mini, GPT-4-turbo, and GPT-3.5-turbo models.
    Requires OPENAI_API_KEY environment variable to be set.
    
    Attributes:
        model: The OpenAI model to use (default: gpt-4o-mini)
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 4096)
        
    Example:
        >>> provider = OpenAIProvider(model="gpt-4o-mini")
        >>> response = await provider.complete("Explain Python decorators")
        >>> print(response)
    """
    
    # Supported models and their context windows
    SUPPORTED_MODELS: Dict[str, int] = {
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gpt-4-turbo": 128000,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 16385,
        "gpt-3.5-turbo-16k": 16385,
    }
    
    # Approximate characters per token for OpenAI models
    CHARS_PER_TOKEN: float = 4.0
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the OpenAI provider.
        
        Args:
            model: The OpenAI model to use
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            
        Raises:
            ValueError: If the model is not supported or API key is missing
        """
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        self._client: Optional[Any] = None
        self._async_client: Optional[Any] = None
    
    def _get_client(self) -> Any:
        """Get or create the OpenAI client (lazy initialization)."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "openai package not installed. "
                    "Install with: pip install openai"
                )
        return self._client
    
    def _get_async_client(self) -> Any:
        """Get or create the async OpenAI client (lazy initialization)."""
        if self._async_client is None:
            try:
                from openai import AsyncOpenAI
                self._async_client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "openai package not installed. "
                    "Install with: pip install openai"
                )
        return self._async_client
    
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The generated completion text
        """
        client = self._get_async_client()
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.choices[0].message.content or ""
    
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a response for a chat conversation.
        
        Args:
            messages: List of chat messages in the conversation
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The generated response text
        """
        client = self._get_async_client()
        
        # Convert ChatMessage objects to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.choices[0].message.content or ""
    
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given prompt.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Yields:
            String chunks of the generated response
        """
        client = self._get_async_client()
        
        stream = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken if available, otherwise estimate.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The token count (exact if tiktoken available, estimated otherwise)
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except ImportError:
            # Fallback to estimation: ~4 characters per token
            return int(len(text) / self.CHARS_PER_TOKEN) + 1
        except KeyError:
            # Model not found in tiktoken, use estimation
            return int(len(text) / self.CHARS_PER_TOKEN) + 1
    
    @property
    def context_window(self) -> int:
        """Get the context window size for the current model."""
        return self.SUPPORTED_MODELS.get(self.model, 8192)



class AnthropicProvider(LLMProvider):
    """Anthropic Claude models provider.
    
    Supports Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Sonnet, and Claude 3 Haiku.
    Requires ANTHROPIC_API_KEY environment variable to be set.
    
    Attributes:
        model: The Anthropic model to use (default: claude-3-5-sonnet-20241022)
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 4096)
        
    Example:
        >>> provider = AnthropicProvider(model="claude-3-5-sonnet-20241022")
        >>> response = await provider.complete("Explain Python decorators")
        >>> print(response)
    """
    
    # Supported models and their context windows
    SUPPORTED_MODELS: Dict[str, int] = {
        "claude-3-5-sonnet-20241022": 200000,
        "claude-3-5-haiku-20241022": 200000,
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
    }
    
    # Approximate characters per token for Claude models
    CHARS_PER_TOKEN: float = 3.5
    
    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the Anthropic provider.
        
        Args:
            model: The Anthropic model to use
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            
        Raises:
            ValueError: If the model is not supported or API key is missing
        """
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )
        
        self._client: Optional[Any] = None
        self._async_client: Optional[Any] = None
    
    def _get_client(self) -> Any:
        """Get or create the Anthropic client (lazy initialization)."""
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. "
                    "Install with: pip install anthropic"
                )
        return self._client
    
    def _get_async_client(self) -> Any:
        """Get or create the async Anthropic client (lazy initialization)."""
        if self._async_client is None:
            try:
                from anthropic import AsyncAnthropic
                self._async_client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. "
                    "Install with: pip install anthropic"
                )
        return self._async_client
    
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The generated completion text
        """
        client = self._get_async_client()
        
        response = await client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        # Extract text from the response content blocks
        return "".join(
            block.text for block in response.content 
            if hasattr(block, "text")
        )
    
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a response for a chat conversation.
        
        Args:
            messages: List of chat messages in the conversation
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The generated response text
        """
        client = self._get_async_client()
        
        # Separate system message from conversation messages
        system_message = ""
        conversation_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Build request kwargs
        request_kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": conversation_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        if system_message:
            request_kwargs["system"] = system_message
        
        response = await client.messages.create(**request_kwargs)
        
        return "".join(
            block.text for block in response.content 
            if hasattr(block, "text")
        )
    
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given prompt.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Yields:
            String chunks of the generated response
        """
        client = self._get_async_client()
        
        async with client.messages.stream(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for Anthropic models.
        
        Anthropic doesn't provide a public tokenizer, so we estimate
        based on average characters per token (~3.5 for Claude).
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The estimated token count
        """
        return int(len(text) / self.CHARS_PER_TOKEN) + 1
    
    @property
    def context_window(self) -> int:
        """Get the context window size for the current model."""
        return self.SUPPORTED_MODELS.get(self.model, 200000)



class BedrockProvider(LLMProvider):
    """AWS Bedrock models provider.
    
    Supports Claude, Titan, and Llama models through AWS Bedrock.
    Requires AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)
    or configured AWS profile.
    
    Attributes:
        model: The Bedrock model ID to use
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 4096)
        region: AWS region (default: us-east-1)
        
    Example:
        >>> provider = BedrockProvider(
        ...     model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        ...     region="us-east-1"
        ... )
        >>> response = await provider.complete("Explain Python decorators")
        >>> print(response)
    """
    
    # Supported models and their context windows
    SUPPORTED_MODELS: Dict[str, int] = {
        # Anthropic Claude models on Bedrock
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0": 200000,
        "us.anthropic.claude-3-5-haiku-20241022-v1:0": 200000,
        "anthropic.claude-3-opus-20240229-v1:0": 200000,
        "anthropic.claude-3-sonnet-20240229-v1:0": 200000,
        "anthropic.claude-3-haiku-20240307-v1:0": 200000,
        # Amazon Titan models
        "amazon.titan-text-express-v1": 8192,
        "amazon.titan-text-lite-v1": 4096,
        "amazon.titan-text-premier-v1:0": 32000,
        # Meta Llama models
        "meta.llama3-8b-instruct-v1:0": 8192,
        "meta.llama3-70b-instruct-v1:0": 8192,
        "meta.llama3-1-8b-instruct-v1:0": 128000,
        "meta.llama3-1-70b-instruct-v1:0": 128000,
        "meta.llama3-1-405b-instruct-v1:0": 128000,
    }
    
    # Model family detection for request formatting
    CLAUDE_MODELS = {"anthropic", "claude"}
    TITAN_MODELS = {"amazon", "titan"}
    LLAMA_MODELS = {"meta", "llama"}
    
    # Approximate characters per token
    CHARS_PER_TOKEN: float = 4.0
    
    def __init__(
        self,
        model: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        region: str = "us-east-1",
        profile_name: Optional[str] = None,
    ) -> None:
        """Initialize the Bedrock provider.
        
        Args:
            model: The Bedrock model ID to use
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            region: AWS region for Bedrock
            profile_name: AWS profile name (optional)
            
        Raises:
            ValueError: If the model is not supported
        """
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.region = region
        self.profile_name = profile_name
        
        self._client: Optional[Any] = None
        self._runtime_client: Optional[Any] = None
    
    def _get_model_family(self) -> str:
        """Detect the model family from the model ID."""
        model_lower = self.model.lower()
        if any(kw in model_lower for kw in self.CLAUDE_MODELS):
            return "claude"
        elif any(kw in model_lower for kw in self.TITAN_MODELS):
            return "titan"
        elif any(kw in model_lower for kw in self.LLAMA_MODELS):
            return "llama"
        return "unknown"
    
    def _get_runtime_client(self) -> Any:
        """Get or create the Bedrock runtime client (lazy initialization)."""
        if self._runtime_client is None:
            try:
                import boto3
                
                session_kwargs: Dict[str, Any] = {"region_name": self.region}
                if self.profile_name:
                    session_kwargs["profile_name"] = self.profile_name
                
                session = boto3.Session(**session_kwargs)
                self._runtime_client = session.client("bedrock-runtime")
            except ImportError:
                raise ImportError(
                    "boto3 package not installed. "
                    "Install with: pip install boto3"
                )
        return self._runtime_client
    
    def _format_request_body(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Format the request body based on model family.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters
            
        Returns:
            The formatted request body for the model
        """
        import json
        
        family = self._get_model_family()
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        if family == "claude":
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
        elif family == "titan":
            return {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens,
                    "temperature": temperature,
                    "topP": kwargs.get("top_p", 0.9),
                },
            }
        elif family == "llama":
            return {
                "prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                "max_gen_len": max_tokens,
                "temperature": temperature,
                "top_p": kwargs.get("top_p", 0.9),
            }
        else:
            # Default to Claude format
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
    
    def _parse_response(self, response_body: Dict[str, Any]) -> str:
        """Parse the response based on model family.
        
        Args:
            response_body: The response body from Bedrock
            
        Returns:
            The extracted text response
        """
        family = self._get_model_family()
        
        if family == "claude":
            content = response_body.get("content", [])
            return "".join(
                block.get("text", "") for block in content 
                if block.get("type") == "text"
            )
        elif family == "titan":
            results = response_body.get("results", [])
            if results:
                return results[0].get("outputText", "")
            return ""
        elif family == "llama":
            return response_body.get("generation", "")
        else:
            # Try common response formats
            if "content" in response_body:
                content = response_body["content"]
                if isinstance(content, list):
                    return "".join(
                        block.get("text", "") for block in content 
                        if isinstance(block, dict)
                    )
                return str(content)
            return str(response_body)
    
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The generated completion text
        """
        import json
        import asyncio
        
        client = self._get_runtime_client()
        request_body = self._format_request_body(prompt, **kwargs)
        
        # Run synchronous boto3 call in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.invoke_model(
                modelId=self.model,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json",
            )
        )
        
        response_body = json.loads(response["body"].read())
        return self._parse_response(response_body)
    
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a response for a chat conversation.
        
        Args:
            messages: List of chat messages in the conversation
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The generated response text
        """
        import json
        import asyncio
        
        client = self._get_runtime_client()
        family = self._get_model_family()
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        # Format messages based on model family
        if family == "claude":
            # Separate system message
            system_message = ""
            conversation_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    conversation_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            request_body: Dict[str, Any] = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": conversation_messages,
            }
            
            if system_message:
                request_body["system"] = system_message
        else:
            # For non-Claude models, concatenate messages into a prompt
            prompt_parts = []
            for msg in messages:
                if msg.role == "system":
                    prompt_parts.append(f"System: {msg.content}")
                elif msg.role == "user":
                    prompt_parts.append(f"User: {msg.content}")
                elif msg.role == "assistant":
                    prompt_parts.append(f"Assistant: {msg.content}")
            
            combined_prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
            request_body = self._format_request_body(combined_prompt, **kwargs)
        
        # Run synchronous boto3 call in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.invoke_model(
                modelId=self.model,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json",
            )
        )
        
        response_body = json.loads(response["body"].read())
        return self._parse_response(response_body)
    
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given prompt.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Yields:
            String chunks of the generated response
        """
        import json
        import asyncio
        
        client = self._get_runtime_client()
        request_body = self._format_request_body(prompt, **kwargs)
        family = self._get_model_family()
        
        # Run synchronous boto3 streaming call in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.invoke_model_with_response_stream(
                modelId=self.model,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json",
            )
        )
        
        # Process the event stream
        for event in response.get("body", []):
            chunk = event.get("chunk")
            if chunk:
                chunk_data = json.loads(chunk.get("bytes", b"{}").decode())
                
                if family == "claude":
                    # Claude streaming format
                    if chunk_data.get("type") == "content_block_delta":
                        delta = chunk_data.get("delta", {})
                        if delta.get("type") == "text_delta":
                            yield delta.get("text", "")
                elif family == "titan":
                    # Titan streaming format
                    yield chunk_data.get("outputText", "")
                elif family == "llama":
                    # Llama streaming format
                    yield chunk_data.get("generation", "")
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for Bedrock models.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The estimated token count
        """
        return int(len(text) / self.CHARS_PER_TOKEN) + 1
    
    @property
    def context_window(self) -> int:
        """Get the context window size for the current model."""
        return self.SUPPORTED_MODELS.get(self.model, 8192)



class CohereProvider(LLMProvider):
    """Cohere Command models provider.
    
    Supports Command R+, Command R, and Command models.
    Requires COHERE_API_KEY environment variable to be set.
    
    Attributes:
        model: The Cohere model to use (default: command-r-plus)
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 4096)
        
    Example:
        >>> provider = CohereProvider(model="command-r-plus")
        >>> response = await provider.complete("Explain Python decorators")
        >>> print(response)
    """
    
    SUPPORTED_MODELS: Dict[str, int] = {
        "command-r-plus": 128000,
        "command-r": 128000,
        "command": 4096,
        "command-light": 4096,
    }
    
    CHARS_PER_TOKEN: float = 4.0
    
    def __init__(
        self,
        model: str = "command-r-plus",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the Cohere provider."""
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.environ.get("COHERE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Cohere API key not provided. "
                "Set COHERE_API_KEY environment variable or pass api_key parameter."
            )
        
        self._client: Optional[Any] = None
    
    def _get_client(self) -> Any:
        """Get or create the Cohere client (lazy initialization)."""
        if self._client is None:
            try:
                import cohere
                self._client = cohere.AsyncClient(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "cohere package not installed. "
                    "Install with: pip install cohere"
                )
        return self._client
    
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt."""
        client = self._get_client()
        
        response = await client.chat(
            model=self.model,
            message=prompt,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.text
    
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a response for a chat conversation."""
        client = self._get_client()
        
        # Convert to Cohere chat history format
        chat_history = []
        user_message = ""
        
        for msg in messages:
            if msg.role == "user":
                user_message = msg.content
            elif msg.role == "assistant":
                chat_history.append({"role": "CHATBOT", "message": msg.content})
            elif msg.role == "system":
                # Cohere uses preamble for system messages
                kwargs["preamble"] = msg.content
        
        response = await client.chat(
            model=self.model,
            message=user_message,
            chat_history=chat_history if chat_history else None,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens"]}
        )
        
        return response.text
    
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given prompt."""
        client = self._get_client()
        
        stream = client.chat_stream(
            model=self.model,
            message=prompt,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        async for chunk in stream:
            if chunk.event_type == "text-generation":
                yield chunk.text
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for Cohere models."""
        return int(len(text) / self.CHARS_PER_TOKEN) + 1
    
    @property
    def context_window(self) -> int:
        """Get the context window size for the current model."""
        return self.SUPPORTED_MODELS.get(self.model, 4096)


class GeminiProvider(LLMProvider):
    """Google Gemini models provider.
    
    Supports Gemini 1.5 Pro and Gemini 1.5 Flash models.
    Requires GOOGLE_API_KEY environment variable to be set.
    
    Attributes:
        model: The Gemini model to use (default: gemini-1.5-pro)
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 4096)
        
    Example:
        >>> provider = GeminiProvider(model="gemini-1.5-pro")
        >>> response = await provider.complete("Explain Python decorators")
        >>> print(response)
    """
    
    SUPPORTED_MODELS: Dict[str, int] = {
        "gemini-1.5-pro": 2000000,
        "gemini-1.5-flash": 1000000,
        "gemini-1.0-pro": 32000,
    }
    
    CHARS_PER_TOKEN: float = 4.0
    
    def __init__(
        self,
        model: str = "gemini-1.5-pro",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the Gemini provider."""
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY_2")
        
        if not self.api_key:
            raise ValueError(
                "Google API key not provided. "
                "Set GOOGLE_API_KEY environment variable or pass api_key parameter."
            )
        
        self._model: Optional[Any] = None
    
    def _get_model(self) -> Any:
        """Get or create the Gemini model (lazy initialization)."""
        if self._model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. "
                    "Install with: pip install google-generativeai"
                )
        return self._model
    
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt."""
        model = self._get_model()
        
        generation_config = {
            "temperature": kwargs.get("temperature", self.temperature),
            "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        response = await model.generate_content_async(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a response for a chat conversation."""
        model = self._get_model()
        
        # Convert messages to Gemini format
        history = []
        user_message = ""
        
        for msg in messages:
            if msg.role == "system":
                # Gemini doesn't have system role, prepend to first user message
                continue
            elif msg.role == "user":
                user_message = msg.content
            elif msg.role == "assistant":
                history.append({"role": "model", "parts": [msg.content]})
        
        chat = model.start_chat(history=history if history else None)
        
        generation_config = {
            "temperature": kwargs.get("temperature", self.temperature),
            "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        response = await chat.send_message_async(
            user_message,
            generation_config=generation_config
        )
        
        return response.text
    
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given prompt."""
        model = self._get_model()
        
        generation_config = {
            "temperature": kwargs.get("temperature", self.temperature),
            "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        response = await model.generate_content_async(
            prompt,
            generation_config=generation_config,
            stream=True
        )
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for Gemini models."""
        return int(len(text) / self.CHARS_PER_TOKEN) + 1
    
    @property
    def context_window(self) -> int:
        """Get the context window size for the current model."""
        return self.SUPPORTED_MODELS.get(self.model, 32000)


class MistralProvider(LLMProvider):
    """Mistral AI models provider.
    
    Supports Mistral Large, Medium, and Small models.
    Requires MISTRAL_API_KEY environment variable to be set.
    
    Attributes:
        model: The Mistral model to use (default: mistral-large-latest)
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 4096)
        
    Example:
        >>> provider = MistralProvider(model="mistral-large-latest")
        >>> response = await provider.complete("Explain Python decorators")
        >>> print(response)
    """
    
    SUPPORTED_MODELS: Dict[str, int] = {
        "mistral-large-latest": 128000,
        "mistral-medium-latest": 32000,
        "mistral-small-latest": 32000,
        "open-mistral-7b": 32000,
        "open-mixtral-8x7b": 32000,
        "open-mixtral-8x22b": 64000,
    }
    
    CHARS_PER_TOKEN: float = 4.0
    
    def __init__(
        self,
        model: str = "mistral-large-latest",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the Mistral provider."""
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Mistral API key not provided. "
                "Set MISTRAL_API_KEY environment variable or pass api_key parameter."
            )
        
        self._client: Optional[Any] = None
    
    def _get_client(self) -> Any:
        """Get or create the Mistral client (lazy initialization)."""
        if self._client is None:
            try:
                from mistralai.async_client import MistralAsyncClient
                self._client = MistralAsyncClient(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "mistralai package not installed. "
                    "Install with: pip install mistralai"
                )
        return self._client
    
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt."""
        client = self._get_client()
        
        response = await client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.choices[0].message.content
    
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a response for a chat conversation."""
        client = self._get_client()
        
        # Convert to Mistral format
        mistral_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = await client.chat(
            model=self.model,
            messages=mistral_messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.choices[0].message.content
    
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given prompt."""
        client = self._get_client()
        
        stream = await client.chat_stream(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for Mistral models."""
        return int(len(text) / self.CHARS_PER_TOKEN) + 1
    
    @property
    def context_window(self) -> int:
        """Get the context window size for the current model."""
        return self.SUPPORTED_MODELS.get(self.model, 32000)


class HuggingFaceProvider(LLMProvider):
    """HuggingFace Inference API provider.
    
    Supports various models through HuggingFace Inference API.
    Requires HUGGINGFACE_API_KEY environment variable to be set.
    
    Attributes:
        model: The HuggingFace model to use
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 4096)
        
    Example:
        >>> provider = HuggingFaceProvider(model="meta-llama/Llama-2-70b-chat-hf")
        >>> response = await provider.complete("Explain Python decorators")
        >>> print(response)
    """
    
    CHARS_PER_TOKEN: float = 4.0
    
    def __init__(
        self,
        model: str = "meta-llama/Llama-2-70b-chat-hf",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the HuggingFace provider."""
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.environ.get("HUGGINGFACE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "HuggingFace API key not provided. "
                "Set HUGGINGFACE_API_KEY environment variable or pass api_key parameter."
            )
        
        self._client: Optional[Any] = None
    
    def _get_client(self) -> Any:
        """Get or create the HuggingFace client (lazy initialization)."""
        if self._client is None:
            try:
                from huggingface_hub import AsyncInferenceClient
                self._client = AsyncInferenceClient(token=self.api_key)
            except ImportError:
                raise ImportError(
                    "huggingface_hub package not installed. "
                    "Install with: pip install huggingface_hub"
                )
        return self._client
    
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt."""
        client = self._get_client()
        
        response = await client.text_generation(
            prompt,
            model=self.model,
            temperature=kwargs.get("temperature", self.temperature),
            max_new_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response
    
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a response for a chat conversation."""
        client = self._get_client()
        
        # Convert to HuggingFace chat format
        hf_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = await client.chat_completion(
            messages=hf_messages,
            model=self.model,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.choices[0].message.content
    
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given prompt."""
        client = self._get_client()
        
        stream = client.text_generation(
            prompt,
            model=self.model,
            temperature=kwargs.get("temperature", self.temperature),
            max_new_tokens=kwargs.get("max_tokens", self.max_tokens),
            stream=True,
        )
        
        async for chunk in stream:
            yield chunk
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for HuggingFace models."""
        return int(len(text) / self.CHARS_PER_TOKEN) + 1
    
    @property
    def context_window(self) -> int:
        """Get the context window size for the current model."""
        return 4096  # Default, varies by model


class OllamaProvider(LLMProvider):
    """Ollama local models provider.
    
    Supports locally running Ollama models.
    No API key required, but Ollama must be running locally.
    
    Attributes:
        model: The Ollama model to use (default: llama2)
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 4096)
        host: Ollama host URL (default: http://localhost:11434)
        
    Example:
        >>> provider = OllamaProvider(model="llama2")
        >>> response = await provider.complete("Explain Python decorators")
        >>> print(response)
    """
    
    CHARS_PER_TOKEN: float = 4.0
    
    def __init__(
        self,
        model: str = "llama2",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        host: str = "http://localhost:11434",
    ) -> None:
        """Initialize the Ollama provider."""
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        
        self._client: Optional[Any] = None
    
    def _get_client(self) -> Any:
        """Get or create the Ollama client (lazy initialization)."""
        if self._client is None:
            try:
                from ollama import AsyncClient
                self._client = AsyncClient(host=self.host)
            except ImportError:
                raise ImportError(
                    "ollama package not installed. "
                    "Install with: pip install ollama"
                )
        return self._client
    
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt."""
        client = self._get_client()
        
        response = await client.generate(
            model=self.model,
            prompt=prompt,
            options={
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", self.max_tokens),
            }
        )
        
        return response["response"]
    
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a response for a chat conversation."""
        client = self._get_client()
        
        # Convert to Ollama format
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = await client.chat(
            model=self.model,
            messages=ollama_messages,
            options={
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", self.max_tokens),
            }
        )
        
        return response["message"]["content"]
    
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given prompt."""
        client = self._get_client()
        
        stream = await client.generate(
            model=self.model,
            prompt=prompt,
            options={
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", self.max_tokens),
            },
            stream=True
        )
        
        async for chunk in stream:
            if "response" in chunk:
                yield chunk["response"]
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for Ollama models."""
        return int(len(text) / self.CHARS_PER_TOKEN) + 1
    
    @property
    def context_window(self) -> int:
        """Get the context window size for the current model."""
        return 4096  # Default, varies by model


# =============================================================================
# Multi-Provider Fallback Chain
# =============================================================================

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ProviderPriority(Enum):
    """Provider priority order for fallback chain."""
    OPENAI = 1
    COHERE = 2
    GEMINI = 3
    GROK = 4
    MISTRAL = 5
    HUGGINGFACE = 6
    OLLAMA = 7
    ANTHROPIC = 8
    BEDROCK = 9
    MOCK = 10


@dataclass
class FallbackResult:
    """Result from a fallback chain call.
    
    Attributes:
        response: The successful response text
        provider_used: Name of the provider that succeeded
        attempts: List of (provider_name, error) tuples for failed attempts
    """
    response: str
    provider_used: str
    attempts: List[tuple[str, str]] = field(default_factory=list)


class FallbackChain(LLMProvider):
    """Chain of fallback providers for LLM calls.
    
    Tries providers in priority order until one succeeds.
    Falls back to MockLLM if all real providers fail.
    
    Priority order:
    1. OpenAI → 2. Cohere → 3. Gemini → 4. Grok → 5. Mistral → 
    6. HuggingFace → 7. Ollama → 8. Anthropic → 9. Bedrock → 10. MockLLM
    
    Attributes:
        providers: List of (name, provider) tuples in priority order
        show_warnings: Whether to display warnings when falling back
        
    Example:
        >>> chain = FallbackChain.from_environment()
        >>> response = await chain.complete("Hello, world!")
        >>> print(f"Response from {chain.last_provider_used}: {response}")
    """
    
    def __init__(
        self,
        providers: Optional[List[tuple[str, LLMProvider]]] = None,
        show_warnings: bool = True,
    ) -> None:
        """Initialize the fallback chain.
        
        Args:
            providers: List of (name, provider) tuples in priority order.
                      If None, will be built from environment variables.
            show_warnings: Whether to display warnings when falling back
        """
        self.providers = providers or []
        self.show_warnings = show_warnings
        self._last_provider_used: Optional[str] = None
        self._last_attempts: List[tuple[str, str]] = []
    
    @classmethod
    def from_environment(
        cls,
        show_warnings: bool = True,
        **kwargs: Any
    ) -> "FallbackChain":
        """Create a fallback chain from environment variables.
        
        Checks for available API keys and creates providers in priority order.
        Always includes MockLLM as the final fallback.
        
        Args:
            show_warnings: Whether to display warnings when falling back
            **kwargs: Additional provider-specific parameters
            
        Returns:
            A FallbackChain instance with available providers
        """
        from .llm import MockLLM
        
        providers: List[tuple[str, LLMProvider]] = []
        
        # Check and add providers in priority order
        
        # 1. OpenAI
        if os.environ.get("OPENAI_API_KEY"):
            try:
                providers.append(("OpenAI", OpenAIProvider(**kwargs)))
                logger.debug("Added OpenAI provider to fallback chain")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI provider: {e}")
        
        # 2. Cohere
        if os.environ.get("COHERE_API_KEY"):
            try:
                providers.append(("Cohere", CohereProvider(**kwargs)))
                logger.debug("Added Cohere provider to fallback chain")
            except Exception as e:
                logger.warning(f"Failed to initialize Cohere provider: {e}")
        
        # 3. Gemini
        if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY_2"):
            try:
                providers.append(("Gemini", GeminiProvider(**kwargs)))
                logger.debug("Added Gemini provider to fallback chain")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini provider: {e}")
        
        # 4. Grok (uses OpenAI-compatible API)
        if os.environ.get("XAI_API_KEY"):
            try:
                grok_kwargs = {**kwargs, "api_key": os.environ.get("XAI_API_KEY")}
                providers.append(("Grok", OpenAIProvider(**grok_kwargs)))
                logger.debug("Added Grok provider to fallback chain")
            except Exception as e:
                logger.warning(f"Failed to initialize Grok provider: {e}")
        
        # 5. Mistral
        if os.environ.get("MISTRAL_API_KEY"):
            try:
                providers.append(("Mistral", MistralProvider(**kwargs)))
                logger.debug("Added Mistral provider to fallback chain")
            except Exception as e:
                logger.warning(f"Failed to initialize Mistral provider: {e}")
        
        # 6. HuggingFace
        if os.environ.get("HUGGINGFACE_API_KEY"):
            try:
                providers.append(("HuggingFace", HuggingFaceProvider(**kwargs)))
                logger.debug("Added HuggingFace provider to fallback chain")
            except Exception as e:
                logger.warning(f"Failed to initialize HuggingFace provider: {e}")
        
        # 7. Ollama (check if running)
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        try:
            import httpx
            response = httpx.get(ollama_host, timeout=2.0)
            if response.status_code == 200:
                providers.append(("Ollama", OllamaProvider(host=ollama_host, **kwargs)))
                logger.debug("Added Ollama provider to fallback chain")
        except Exception:
            pass  # Ollama not available
        
        # 8. Anthropic
        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                providers.append(("Anthropic", AnthropicProvider(**kwargs)))
                logger.debug("Added Anthropic provider to fallback chain")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic provider: {e}")
        
        # 9. Bedrock
        if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
            try:
                providers.append(("Bedrock", BedrockProvider(**kwargs)))
                logger.debug("Added Bedrock provider to fallback chain")
            except Exception as e:
                logger.warning(f"Failed to initialize Bedrock provider: {e}")
        
        # 10. MockLLM (always available as final fallback)
        providers.append(("MockLLM", MockLLM()))
        logger.debug("Added MockLLM as final fallback")
        
        return cls(providers=providers, show_warnings=show_warnings)
    
    @property
    def last_provider_used(self) -> Optional[str]:
        """Get the name of the last provider that successfully handled a request."""
        return self._last_provider_used
    
    @property
    def last_attempts(self) -> List[tuple[str, str]]:
        """Get the list of (provider_name, error) tuples from the last call."""
        return self._last_attempts
    
    @property
    def available_providers(self) -> List[str]:
        """Get list of available provider names in priority order."""
        return [name for name, _ in self.providers]
    
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion, trying providers in order until one succeeds.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The generated completion text
            
        Raises:
            RuntimeError: If all providers fail (should never happen with MockLLM)
        """
        self._last_attempts = []
        
        for name, provider in self.providers:
            try:
                response = await provider.complete(prompt, **kwargs)
                self._last_provider_used = name
                
                if name == "MockLLM" and self.show_warnings and len(self._last_attempts) > 0:
                    logger.warning(
                        f"All real providers failed, using MockLLM. "
                        f"Attempts: {self._last_attempts}"
                    )
                elif name != "MockLLM":
                    logger.info(f"Request handled by {name}")
                
                return response
                
            except Exception as e:
                error_msg = str(e)
                self._last_attempts.append((name, error_msg))
                logger.debug(f"Provider {name} failed: {error_msg}")
                
                if self.show_warnings and name != "MockLLM":
                    logger.warning(f"Provider {name} failed, trying next: {error_msg}")
        
        # This should never happen since MockLLM is always available
        raise RuntimeError("All providers failed, including MockLLM")
    
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> str:
        """Generate a chat response, trying providers in order until one succeeds.
        
        Args:
            messages: List of chat messages in the conversation
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The generated response text
        """
        self._last_attempts = []
        
        for name, provider in self.providers:
            try:
                response = await provider.chat(messages, **kwargs)
                self._last_provider_used = name
                
                if name == "MockLLM" and self.show_warnings and len(self._last_attempts) > 0:
                    logger.warning(
                        f"All real providers failed, using MockLLM. "
                        f"Attempts: {self._last_attempts}"
                    )
                elif name != "MockLLM":
                    logger.info(f"Chat request handled by {name}")
                
                return response
                
            except Exception as e:
                error_msg = str(e)
                self._last_attempts.append((name, error_msg))
                logger.debug(f"Provider {name} failed: {error_msg}")
        
        raise RuntimeError("All providers failed, including MockLLM")
    
    async def stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion, trying providers in order until one succeeds.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional provider-specific parameters
            
        Yields:
            String chunks of the generated response
        """
        self._last_attempts = []
        
        for name, provider in self.providers:
            try:
                async for chunk in provider.stream(prompt, **kwargs):
                    self._last_provider_used = name
                    yield chunk
                return  # Successfully streamed
                
            except Exception as e:
                error_msg = str(e)
                self._last_attempts.append((name, error_msg))
                logger.debug(f"Provider {name} failed: {error_msg}")
        
        raise RuntimeError("All providers failed, including MockLLM")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using the first available provider.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The token count
        """
        if self.providers:
            return self.providers[0][1].count_tokens(text)
        return len(text) // 4 + 1  # Fallback estimation
    
    async def complete_with_result(self, prompt: str, **kwargs: Any) -> FallbackResult:
        """Generate a completion and return detailed result information.
        
        Args:
            prompt: The input prompt to complete
            **kwargs: Additional provider-specific parameters
            
        Returns:
            FallbackResult with response, provider used, and attempt history
        """
        response = await self.complete(prompt, **kwargs)
        return FallbackResult(
            response=response,
            provider_used=self._last_provider_used or "Unknown",
            attempts=list(self._last_attempts)
        )
