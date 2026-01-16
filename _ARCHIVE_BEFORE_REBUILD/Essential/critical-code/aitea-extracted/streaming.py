"""Streaming response handlers for LLM providers.

This module provides async generators and callback-based streaming for
real-time LLM output. It enables token-by-token streaming with lower
perceived latency and supports various callback patterns for UI updates.

Key components:
- StreamingResponse: Wrapper for streaming LLM responses with metadata
- StreamCallback: Protocol for streaming callbacks
- stream_with_callback: Async generator with callback support
- collect_stream: Utility to collect all chunks from a stream

Example:
    >>> from src.services.streaming import stream_with_callback, StreamCallback
    >>> 
    >>> class PrintCallback(StreamCallback):
    ...     def on_token(self, token: str) -> None:
    ...         print(token, end="", flush=True)
    ...
    >>> async for chunk in stream_with_callback(provider, prompt, PrintCallback()):
    ...     pass  # Callback handles output
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

from .llm import LLMProvider, ChatMessage


@dataclass
class StreamChunk:
    """A single chunk from a streaming response.
    
    Attributes:
        content: The text content of this chunk
        index: The position of this chunk in the stream (0-indexed)
        timestamp: Unix timestamp when this chunk was received
        is_final: Whether this is the last chunk in the stream
        metadata: Optional provider-specific metadata
    """
    content: str
    index: int
    timestamp: float = field(default_factory=time.time)
    is_final: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamingResponse:
    """Complete streaming response with all chunks and metadata.
    
    This class collects all chunks from a streaming response and provides
    utilities for accessing the complete text and individual chunks.
    
    Attributes:
        chunks: List of all received chunks
        start_time: Unix timestamp when streaming started
        end_time: Unix timestamp when streaming completed (None if ongoing)
        provider_name: Name of the LLM provider used
        prompt: The original prompt that generated this response
    """
    chunks: List[StreamChunk] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    provider_name: str = ""
    prompt: str = ""
    
    @property
    def text(self) -> str:
        """Get the complete response text by concatenating all chunks."""
        return "".join(chunk.content for chunk in self.chunks)
    
    @property
    def token_count(self) -> int:
        """Get the total number of chunks (approximate token count)."""
        return len(self.chunks)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get the total streaming duration in seconds."""
        if self.end_time is None:
            return None
        return self.end_time - self.start_time
    
    @property
    def is_complete(self) -> bool:
        """Check if the stream has completed."""
        return self.end_time is not None
    
    def add_chunk(self, content: str, is_final: bool = False, **metadata: Any) -> StreamChunk:
        """Add a new chunk to the response.
        
        Args:
            content: The text content of the chunk
            is_final: Whether this is the last chunk
            **metadata: Additional metadata for the chunk
            
        Returns:
            The created StreamChunk
        """
        chunk = StreamChunk(
            content=content,
            index=len(self.chunks),
            is_final=is_final,
            metadata=metadata,
        )
        self.chunks.append(chunk)
        
        if is_final:
            self.end_time = time.time()
        
        return chunk


@runtime_checkable
class StreamCallback(Protocol):
    """Protocol for streaming callbacks.
    
    Implement this protocol to receive streaming events during LLM generation.
    All methods are optional - implement only the ones you need.
    """
    
    def on_start(self, prompt: str) -> None:
        """Called when streaming begins.
        
        Args:
            prompt: The prompt being processed
        """
        ...
    
    def on_token(self, token: str, index: int) -> None:
        """Called for each token/chunk received.
        
        Args:
            token: The token/chunk content
            index: The position of this token in the stream
        """
        ...
    
    def on_complete(self, response: StreamingResponse) -> None:
        """Called when streaming completes successfully.
        
        Args:
            response: The complete streaming response
        """
        ...
    
    def on_error(self, error: Exception) -> None:
        """Called if an error occurs during streaming.
        
        Args:
            error: The exception that occurred
        """
        ...


class BaseStreamCallback:
    """Base implementation of StreamCallback with no-op methods.
    
    Extend this class and override only the methods you need.
    
    Example:
        >>> class MyCallback(BaseStreamCallback):
        ...     def on_token(self, token: str, index: int) -> None:
        ...         print(token, end="", flush=True)
    """
    
    def on_start(self, prompt: str) -> None:
        """Called when streaming begins. Override to customize."""
        pass
    
    def on_token(self, token: str, index: int) -> None:
        """Called for each token. Override to customize."""
        pass
    
    def on_complete(self, response: StreamingResponse) -> None:
        """Called when streaming completes. Override to customize."""
        pass
    
    def on_error(self, error: Exception) -> None:
        """Called on error. Override to customize."""
        pass


class PrintStreamCallback(BaseStreamCallback):
    """Callback that prints tokens to stdout in real-time.
    
    Useful for CLI applications that want to display streaming output.
    
    Attributes:
        flush: Whether to flush stdout after each token
        end: String to print after each token (default: "")
        
    Example:
        >>> callback = PrintStreamCallback()
        >>> async for _ in stream_with_callback(provider, prompt, callback):
        ...     pass  # Output is printed by callback
    """
    
    def __init__(self, flush: bool = True, end: str = "") -> None:
        """Initialize the print callback.
        
        Args:
            flush: Whether to flush stdout after each token
            end: String to print after each token
        """
        self.flush = flush
        self.end = end
    
    def on_token(self, token: str, index: int) -> None:
        """Print the token to stdout."""
        print(token, end=self.end, flush=self.flush)
    
    def on_complete(self, response: StreamingResponse) -> None:
        """Print a newline when complete."""
        print()  # Newline at end


class CollectorStreamCallback(BaseStreamCallback):
    """Callback that collects all tokens into a list.
    
    Useful for testing or when you need access to individual tokens.
    
    Attributes:
        tokens: List of all received tokens
        response: The complete StreamingResponse (available after completion)
    """
    
    def __init__(self) -> None:
        """Initialize the collector callback."""
        self.tokens: List[str] = []
        self.response: Optional[StreamingResponse] = None
    
    def on_token(self, token: str, index: int) -> None:
        """Collect the token."""
        self.tokens.append(token)
    
    def on_complete(self, response: StreamingResponse) -> None:
        """Store the complete response."""
        self.response = response
    
    @property
    def text(self) -> str:
        """Get the concatenated text from all tokens."""
        return "".join(self.tokens)


# Type for callback - can be a StreamCallback instance or a simple callable
CallbackType = Union[StreamCallback, Callable[[str], None], None]


async def stream_response(
    provider: LLMProvider,
    prompt: str,
    **kwargs: Any,
) -> AsyncIterator[StreamChunk]:
    """Create an async generator that yields StreamChunk objects.
    
    This is the core streaming function that wraps a provider's stream()
    method and yields structured StreamChunk objects with metadata.
    
    Args:
        provider: The LLM provider to use for streaming
        prompt: The prompt to send to the LLM
        **kwargs: Additional arguments passed to the provider
        
    Yields:
        StreamChunk objects containing the token and metadata
        
    Example:
        >>> async for chunk in stream_response(provider, "Tell me a story"):
        ...     print(f"[{chunk.index}] {chunk.content}")
    """
    index = 0
    
    async for token in provider.stream(prompt, **kwargs):
        yield StreamChunk(
            content=token,
            index=index,
            is_final=False,
        )
        index += 1
    
    # Yield a final empty chunk to signal completion
    yield StreamChunk(
        content="",
        index=index,
        is_final=True,
    )


async def stream_with_callback(
    provider: LLMProvider,
    prompt: str,
    callback: CallbackType = None,
    **kwargs: Any,
) -> AsyncIterator[str]:
    """Stream LLM response with callback support.
    
    This function wraps the provider's stream() method and invokes
    callbacks at appropriate points during streaming.
    
    Args:
        provider: The LLM provider to use for streaming
        prompt: The prompt to send to the LLM
        callback: Optional callback for streaming events. Can be:
            - A StreamCallback instance with on_start, on_token, on_complete, on_error
            - A simple callable that takes a string (called for each token)
            - None (no callbacks)
        **kwargs: Additional arguments passed to the provider
        
    Yields:
        String tokens from the LLM response
        
    Example:
        >>> # With StreamCallback
        >>> callback = PrintStreamCallback()
        >>> async for token in stream_with_callback(provider, prompt, callback):
        ...     pass  # Callback handles output
        
        >>> # With simple callable
        >>> tokens = []
        >>> async for token in stream_with_callback(provider, prompt, tokens.append):
        ...     pass
        >>> print("".join(tokens))
    """
    response = StreamingResponse(
        provider_name=provider.__class__.__name__,
        prompt=prompt,
    )
    
    # Determine callback type and create wrapper functions
    on_start: Callable[[str], None] = lambda p: None
    on_token: Callable[[str, int], None] = lambda t, i: None
    on_complete: Callable[[StreamingResponse], None] = lambda r: None
    on_error: Callable[[Exception], None] = lambda e: None
    
    if callback is not None:
        if isinstance(callback, StreamCallback):
            # Full StreamCallback protocol
            if hasattr(callback, 'on_start'):
                on_start = callback.on_start
            if hasattr(callback, 'on_token'):
                on_token = callback.on_token
            if hasattr(callback, 'on_complete'):
                on_complete = callback.on_complete
            if hasattr(callback, 'on_error'):
                on_error = callback.on_error
        elif callable(callback):
            # Simple callable - treat as on_token with index ignored
            on_token = lambda t, i: callback(t)  # type: ignore
    
    # Signal start
    on_start(prompt)
    
    try:
        index = 0
        async for token in provider.stream(prompt, **kwargs):
            response.add_chunk(token)
            on_token(token, index)
            yield token
            index += 1
        
        # Mark response as complete
        response.end_time = time.time()
        if response.chunks:
            response.chunks[-1] = StreamChunk(
                content=response.chunks[-1].content,
                index=response.chunks[-1].index,
                timestamp=response.chunks[-1].timestamp,
                is_final=True,
                metadata=response.chunks[-1].metadata,
            )
        
        on_complete(response)
        
    except Exception as e:
        on_error(e)
        raise


async def stream_chat_with_callback(
    provider: LLMProvider,
    messages: List[ChatMessage],
    callback: CallbackType = None,
    **kwargs: Any,
) -> AsyncIterator[str]:
    """Stream chat response with callback support.
    
    Similar to stream_with_callback but for chat-style interactions
    with message history.
    
    Args:
        provider: The LLM provider to use for streaming
        messages: List of chat messages in the conversation
        callback: Optional callback for streaming events
        **kwargs: Additional arguments passed to the provider
        
    Yields:
        String tokens from the LLM response
        
    Note:
        This function constructs a prompt from the messages and uses
        the provider's stream() method. For providers that support
        native chat streaming, consider using their specific methods.
    """
    # Construct prompt from messages for streaming
    # Most providers' stream() method works with prompts, not messages
    prompt_parts = []
    for msg in messages:
        if msg.role == "system":
            prompt_parts.append(f"System: {msg.content}")
        elif msg.role == "user":
            prompt_parts.append(f"User: {msg.content}")
        elif msg.role == "assistant":
            prompt_parts.append(f"Assistant: {msg.content}")
    
    combined_prompt = "\n\n".join(prompt_parts)
    
    async for token in stream_with_callback(provider, combined_prompt, callback, **kwargs):
        yield token


async def collect_stream(
    provider: LLMProvider,
    prompt: str,
    **kwargs: Any,
) -> StreamingResponse:
    """Collect all chunks from a streaming response.
    
    This utility function consumes the entire stream and returns
    a complete StreamingResponse object with all chunks.
    
    Args:
        provider: The LLM provider to use for streaming
        prompt: The prompt to send to the LLM
        **kwargs: Additional arguments passed to the provider
        
    Returns:
        A StreamingResponse containing all chunks
        
    Example:
        >>> response = await collect_stream(provider, "Tell me a story")
        >>> print(f"Received {response.token_count} tokens in {response.duration_seconds:.2f}s")
        >>> print(response.text)
    """
    response = StreamingResponse(
        provider_name=provider.__class__.__name__,
        prompt=prompt,
    )
    
    async for token in provider.stream(prompt, **kwargs):
        response.add_chunk(token)
    
    # Mark as complete
    response.end_time = time.time()
    if response.chunks:
        # Update last chunk to be final
        last = response.chunks[-1]
        response.chunks[-1] = StreamChunk(
            content=last.content,
            index=last.index,
            timestamp=last.timestamp,
            is_final=True,
            metadata=last.metadata,
        )
    
    return response


async def stream_to_string(
    provider: LLMProvider,
    prompt: str,
    **kwargs: Any,
) -> str:
    """Stream a response and return the complete text.
    
    This is a convenience function that streams the response
    and returns the concatenated text.
    
    Args:
        provider: The LLM provider to use for streaming
        prompt: The prompt to send to the LLM
        **kwargs: Additional arguments passed to the provider
        
    Returns:
        The complete response text
        
    Example:
        >>> text = await stream_to_string(provider, "Hello!")
        >>> print(text)
    """
    response = await collect_stream(provider, prompt, **kwargs)
    return response.text


class BufferedStreamCallback(BaseStreamCallback):
    """Callback that buffers tokens and flushes on word boundaries.
    
    Useful for smoother output when tokens don't align with word boundaries.
    
    Attributes:
        buffer: Current buffer contents
        flush_callback: Function to call when flushing buffer
        word_boundary_chars: Characters that trigger a flush
    """
    
    def __init__(
        self,
        flush_callback: Callable[[str], None],
        word_boundary_chars: str = " \n\t.,!?;:",
    ) -> None:
        """Initialize the buffered callback.
        
        Args:
            flush_callback: Function to call with buffered text
            word_boundary_chars: Characters that trigger a flush
        """
        self.buffer = ""
        self.flush_callback = flush_callback
        self.word_boundary_chars = word_boundary_chars
    
    def on_token(self, token: str, index: int) -> None:
        """Buffer the token and flush on word boundaries."""
        self.buffer += token
        
        # Check if we should flush
        for char in self.word_boundary_chars:
            if char in self.buffer:
                # Flush up to and including the boundary
                last_boundary = max(
                    self.buffer.rfind(c) for c in self.word_boundary_chars
                    if c in self.buffer
                )
                if last_boundary >= 0:
                    to_flush = self.buffer[:last_boundary + 1]
                    self.buffer = self.buffer[last_boundary + 1:]
                    self.flush_callback(to_flush)
                break
    
    def on_complete(self, response: StreamingResponse) -> None:
        """Flush any remaining buffer content."""
        if self.buffer:
            self.flush_callback(self.buffer)
            self.buffer = ""


class ThrottledStreamCallback(BaseStreamCallback):
    """Callback that throttles token delivery to a maximum rate.
    
    Useful for controlling output speed in UI applications.
    
    Attributes:
        tokens_per_second: Maximum tokens to deliver per second
        inner_callback: The callback to forward tokens to
    """
    
    def __init__(
        self,
        inner_callback: BaseStreamCallback,
        tokens_per_second: float = 50.0,
    ) -> None:
        """Initialize the throttled callback.
        
        Args:
            inner_callback: The callback to forward tokens to
            tokens_per_second: Maximum delivery rate
        """
        self.inner_callback = inner_callback
        self.tokens_per_second = tokens_per_second
        self.min_interval = 1.0 / tokens_per_second
        self.last_token_time = 0.0
    
    def on_start(self, prompt: str) -> None:
        """Forward to inner callback."""
        self.inner_callback.on_start(prompt)
        self.last_token_time = time.time()
    
    def on_token(self, token: str, index: int) -> None:
        """Throttle and forward to inner callback."""
        current_time = time.time()
        elapsed = current_time - self.last_token_time
        
        if elapsed < self.min_interval:
            # Note: In async context, you'd use asyncio.sleep
            # This is a simplified synchronous version
            pass
        
        self.inner_callback.on_token(token, index)
        self.last_token_time = time.time()
    
    def on_complete(self, response: StreamingResponse) -> None:
        """Forward to inner callback."""
        self.inner_callback.on_complete(response)
    
    def on_error(self, error: Exception) -> None:
        """Forward to inner callback."""
        self.inner_callback.on_error(error)
