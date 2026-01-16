"""Token management utilities for LLM providers.

This module provides token counting, context window management, and token
budget tracking for different model families. It supports:
- Accurate token counting using tiktoken for OpenAI models
- Estimation-based counting for Anthropic and other models
- Context window management with truncation strategies
- Token budget tracking for cost management

Key components:
- TokenCounter: Abstract base for token counting
- OpenAITokenCounter: Tiktoken-based counting for OpenAI models
- AnthropicTokenCounter: Estimation-based counting for Claude models
- BedrockTokenCounter: Estimation-based counting for Bedrock models
- ContextWindowManager: Manages context with truncation strategies
- TokenBudget: Tracks token usage against budgets

Example:
    >>> from src.services.tokens import get_token_counter, ContextWindowManager
    >>> 
    >>> counter = get_token_counter("openai", model="gpt-4o")
    >>> tokens = counter.count("Hello, world!")
    >>> print(f"Token count: {tokens}")
    
    >>> manager = ContextWindowManager(max_tokens=4096, counter=counter)
    >>> truncated = manager.truncate("Very long text...", max_tokens=100)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import time


class ModelFamily(str, Enum):
    """Supported model families for token counting."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    MOCK = "mock"


class TruncationStrategy(str, Enum):
    """Strategies for truncating text to fit context windows."""
    HEAD = "head"  # Keep the beginning, truncate the end
    TAIL = "tail"  # Keep the end, truncate the beginning
    MIDDLE = "middle"  # Keep beginning and end, truncate middle
    SMART = "smart"  # Truncate at sentence/paragraph boundaries


# Model context window sizes
MODEL_CONTEXT_WINDOWS: Dict[str, int] = {
    # OpenAI models
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4": 8192,
    "gpt-3.5-turbo": 16385,
    "gpt-3.5-turbo-16k": 16385,
    # Anthropic models
    "claude-3-5-sonnet-20241022": 200000,
    "claude-3-5-haiku-20241022": 200000,
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 200000,
    "claude-3-haiku-20240307": 200000,
    # Bedrock models
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0": 200000,
    "us.anthropic.claude-3-5-haiku-20241022-v1:0": 200000,
    "amazon.titan-text-express-v1": 8192,
    "amazon.titan-text-lite-v1": 4096,
    "amazon.titan-text-premier-v1:0": 32000,
    "meta.llama3-8b-instruct-v1:0": 8192,
    "meta.llama3-70b-instruct-v1:0": 8192,
    "meta.llama3-1-8b-instruct-v1:0": 128000,
    "meta.llama3-1-70b-instruct-v1:0": 128000,
    "meta.llama3-1-405b-instruct-v1:0": 128000,
}

# Model pricing per 1K tokens (input/output)
MODEL_PRICING: Dict[str, Tuple[float, float]] = {
    # OpenAI models (input, output per 1K tokens)
    "gpt-4o": (0.0025, 0.01),
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-4": (0.03, 0.06),
    "gpt-3.5-turbo": (0.0005, 0.0015),
    # Anthropic models
    "claude-3-5-sonnet-20241022": (0.003, 0.015),
    "claude-3-5-haiku-20241022": (0.00025, 0.00125),
    "claude-3-opus-20240229": (0.015, 0.075),
    "claude-3-sonnet-20240229": (0.003, 0.015),
    "claude-3-haiku-20240307": (0.00025, 0.00125),
}


class TokenCounter(ABC):
    """Abstract base class for token counting.
    
    Different model families use different tokenization schemes.
    This abstract class defines the interface for token counting
    implementations.
    """
    
    @abstractmethod
    def count(self, text: str) -> int:
        """Count the number of tokens in the given text.
        
        Args:
            text: The text to count tokens for.
            
        Returns:
            The number of tokens in the text.
        """
        ...
    
    @abstractmethod
    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in a list of chat messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            
        Returns:
            The total number of tokens including message overhead.
        """
        ...
    
    @property
    @abstractmethod
    def chars_per_token(self) -> float:
        """Average characters per token for this model family."""
        ...


class OpenAITokenCounter(TokenCounter):
    """Token counter for OpenAI models using tiktoken.
    
    Uses the tiktoken library for accurate token counting when available,
    falls back to estimation otherwise.
    
    Attributes:
        model: The OpenAI model name for encoding selection.
        
    Example:
        >>> counter = OpenAITokenCounter(model="gpt-4o")
        >>> tokens = counter.count("Hello, world!")
        >>> print(f"Tokens: {tokens}")
    """
    
    # Tokens per message overhead for chat models
    TOKENS_PER_MESSAGE = 3  # <|start|>role<|sep|>content<|end|>
    TOKENS_PER_NAME = 1  # If name is provided
    
    def __init__(self, model: str = "gpt-4o") -> None:
        """Initialize the OpenAI token counter.
        
        Args:
            model: The OpenAI model name for encoding selection.
        """
        self.model = model
        self._encoding: Optional[Any] = None
        self._tiktoken_available: Optional[bool] = None
    
    def _get_encoding(self) -> Optional[Any]:
        """Get or create the tiktoken encoding (lazy initialization)."""
        if self._tiktoken_available is False:
            return None
        
        if self._encoding is None:
            try:
                import tiktoken
                try:
                    self._encoding = tiktoken.encoding_for_model(self.model)
                except KeyError:
                    # Model not found, use cl100k_base as default
                    self._encoding = tiktoken.get_encoding("cl100k_base")
                self._tiktoken_available = True
            except ImportError:
                self._tiktoken_available = False
                return None
        
        return self._encoding
    
    @property
    def chars_per_token(self) -> float:
        """Average characters per token for OpenAI models (~4)."""
        return 4.0
    
    def count(self, text: str) -> int:
        """Count tokens using tiktoken if available, otherwise estimate.
        
        Args:
            text: The text to count tokens for.
            
        Returns:
            The token count (exact if tiktoken available, estimated otherwise).
        """
        encoding = self._get_encoding()
        if encoding is not None:
            return len(encoding.encode(text))
        
        # Fallback to estimation
        return int(len(text) / self.chars_per_token) + 1
    
    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in chat messages including overhead.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            
        Returns:
            Total tokens including message formatting overhead.
        """
        total = 0
        for message in messages:
            total += self.TOKENS_PER_MESSAGE
            total += self.count(message.get("role", ""))
            total += self.count(message.get("content", ""))
            if "name" in message:
                total += self.count(message["name"])
                total += self.TOKENS_PER_NAME
        
        # Every reply is primed with <|start|>assistant<|message|>
        total += 3
        
        return total


class AnthropicTokenCounter(TokenCounter):
    """Token counter for Anthropic Claude models.
    
    Anthropic doesn't provide a public tokenizer, so this uses
    estimation based on average characters per token (~3.5 for Claude).
    
    Attributes:
        model: The Anthropic model name.
        
    Example:
        >>> counter = AnthropicTokenCounter(model="claude-3-5-sonnet-20241022")
        >>> tokens = counter.count("Hello, world!")
    """
    
    # Estimated tokens per message overhead for Claude
    TOKENS_PER_MESSAGE = 4
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022") -> None:
        """Initialize the Anthropic token counter.
        
        Args:
            model: The Anthropic model name.
        """
        self.model = model
    
    @property
    def chars_per_token(self) -> float:
        """Average characters per token for Claude models (~3.5)."""
        return 3.5
    
    def count(self, text: str) -> int:
        """Estimate token count for Anthropic models.
        
        Args:
            text: The text to count tokens for.
            
        Returns:
            The estimated token count.
        """
        return int(len(text) / self.chars_per_token) + 1
    
    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        """Estimate tokens in chat messages including overhead.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            
        Returns:
            Estimated total tokens including message overhead.
        """
        total = 0
        for message in messages:
            total += self.TOKENS_PER_MESSAGE
            total += self.count(message.get("role", ""))
            total += self.count(message.get("content", ""))
        
        return total


class BedrockTokenCounter(TokenCounter):
    """Token counter for AWS Bedrock models.
    
    Supports Claude, Titan, and Llama models on Bedrock.
    Uses model-specific estimation based on the model family.
    
    Attributes:
        model: The Bedrock model ID.
        
    Example:
        >>> counter = BedrockTokenCounter(
        ...     model="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        ... )
        >>> tokens = counter.count("Hello, world!")
    """
    
    TOKENS_PER_MESSAGE = 4
    
    def __init__(self, model: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0") -> None:
        """Initialize the Bedrock token counter.
        
        Args:
            model: The Bedrock model ID.
        """
        self.model = model
        self._model_family = self._detect_model_family()
    
    def _detect_model_family(self) -> str:
        """Detect the model family from the model ID."""
        model_lower = self.model.lower()
        if "claude" in model_lower or "anthropic" in model_lower:
            return "claude"
        elif "titan" in model_lower or "amazon" in model_lower:
            return "titan"
        elif "llama" in model_lower or "meta" in model_lower:
            return "llama"
        return "unknown"
    
    @property
    def chars_per_token(self) -> float:
        """Average characters per token based on model family."""
        if self._model_family == "claude":
            return 3.5
        elif self._model_family == "titan":
            return 4.0
        elif self._model_family == "llama":
            return 4.0
        return 4.0  # Default
    
    def count(self, text: str) -> int:
        """Estimate token count for Bedrock models.
        
        Args:
            text: The text to count tokens for.
            
        Returns:
            The estimated token count.
        """
        return int(len(text) / self.chars_per_token) + 1
    
    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        """Estimate tokens in chat messages including overhead.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            
        Returns:
            Estimated total tokens including message overhead.
        """
        total = 0
        for message in messages:
            total += self.TOKENS_PER_MESSAGE
            total += self.count(message.get("role", ""))
            total += self.count(message.get("content", ""))
        
        return total


class MockTokenCounter(TokenCounter):
    """Token counter for MockLLM.
    
    Uses simple character-based estimation for testing purposes.
    """
    
    def __init__(self) -> None:
        """Initialize the mock token counter."""
        pass
    
    @property
    def chars_per_token(self) -> float:
        """Average characters per token for mock (~4)."""
        return 4.0
    
    def count(self, text: str) -> int:
        """Estimate token count using simple heuristic.
        
        Args:
            text: The text to count tokens for.
            
        Returns:
            The estimated token count.
        """
        return len(text) // 4 + 1
    
    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        """Estimate tokens in chat messages.
        
        Args:
            messages: List of message dicts.
            
        Returns:
            Estimated total tokens.
        """
        total = 0
        for message in messages:
            total += 3  # Message overhead
            total += self.count(message.get("role", ""))
            total += self.count(message.get("content", ""))
        return total


def get_token_counter(
    family: Union[str, ModelFamily],
    model: Optional[str] = None,
) -> TokenCounter:
    """Get a token counter for the specified model family.
    
    Args:
        family: The model family ("openai", "anthropic", "bedrock", "mock")
                or a ModelFamily enum value.
        model: Optional model name for family-specific configuration.
        
    Returns:
        A TokenCounter instance for the specified family.
        
    Raises:
        ValueError: If the family is not supported.
        
    Example:
        >>> counter = get_token_counter("openai", model="gpt-4o")
        >>> tokens = counter.count("Hello!")
    """
    if isinstance(family, str):
        family = family.lower()
    else:
        family = family.value
    
    if family == "openai":
        return OpenAITokenCounter(model=model or "gpt-4o")
    elif family == "anthropic":
        return AnthropicTokenCounter(model=model or "claude-3-5-sonnet-20241022")
    elif family == "bedrock":
        return BedrockTokenCounter(model=model or "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    elif family == "mock":
        return MockTokenCounter()
    else:
        raise ValueError(
            f"Unsupported model family: {family}. "
            f"Supported families: openai, anthropic, bedrock, mock"
        )


def get_context_window(model: str) -> int:
    """Get the context window size for a model.
    
    Args:
        model: The model name or ID.
        
    Returns:
        The context window size in tokens.
        Returns 8192 as default if model is not found.
    """
    return MODEL_CONTEXT_WINDOWS.get(model, 8192)


def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Estimate the cost for a model call.
    
    Args:
        model: The model name.
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.
        
    Returns:
        Estimated cost in USD.
        Returns 0.0 if pricing is not available.
    """
    pricing = MODEL_PRICING.get(model)
    if pricing is None:
        return 0.0
    
    input_price, output_price = pricing
    return (input_tokens / 1000 * input_price) + (output_tokens / 1000 * output_price)



@dataclass
class ContextWindowManager:
    """Manages context window with truncation strategies.
    
    This class helps manage text content to fit within model context
    windows, supporting various truncation strategies.
    
    Attributes:
        max_tokens: Maximum tokens allowed in the context window.
        counter: TokenCounter instance for counting tokens.
        reserve_tokens: Tokens to reserve for output (default: 1024).
        
    Example:
        >>> counter = get_token_counter("openai", model="gpt-4o")
        >>> manager = ContextWindowManager(max_tokens=4096, counter=counter)
        >>> truncated = manager.truncate(long_text, max_tokens=2000)
    """
    max_tokens: int
    counter: TokenCounter
    reserve_tokens: int = 1024
    
    @property
    def available_tokens(self) -> int:
        """Get the number of tokens available for input."""
        return self.max_tokens - self.reserve_tokens
    
    def fits(self, text: str) -> bool:
        """Check if text fits within available tokens.
        
        Args:
            text: The text to check.
            
        Returns:
            True if the text fits, False otherwise.
        """
        return self.counter.count(text) <= self.available_tokens
    
    def truncate(
        self,
        text: str,
        max_tokens: Optional[int] = None,
        strategy: TruncationStrategy = TruncationStrategy.TAIL,
    ) -> str:
        """Truncate text to fit within token limit.
        
        Args:
            text: The text to truncate.
            max_tokens: Maximum tokens (defaults to available_tokens).
            strategy: The truncation strategy to use.
            
        Returns:
            The truncated text.
        """
        if max_tokens is None:
            max_tokens = self.available_tokens
        
        current_tokens = self.counter.count(text)
        if current_tokens <= max_tokens:
            return text
        
        if strategy == TruncationStrategy.HEAD:
            return self._truncate_head(text, max_tokens)
        elif strategy == TruncationStrategy.TAIL:
            return self._truncate_tail(text, max_tokens)
        elif strategy == TruncationStrategy.MIDDLE:
            return self._truncate_middle(text, max_tokens)
        elif strategy == TruncationStrategy.SMART:
            return self._truncate_smart(text, max_tokens)
        else:
            return self._truncate_tail(text, max_tokens)
    
    def _truncate_head(self, text: str, max_tokens: int) -> str:
        """Keep the beginning, truncate the end."""
        chars_per_token = self.counter.chars_per_token
        # Estimate character limit with some buffer
        estimated_chars = int(max_tokens * chars_per_token * 0.9)
        
        truncated = text[:estimated_chars]
        
        # Fine-tune by checking actual token count
        while self.counter.count(truncated) > max_tokens and len(truncated) > 0:
            truncated = truncated[:-100] if len(truncated) > 100 else truncated[:-10]
        
        if truncated != text:
            truncated = truncated.rstrip() + "..."
        
        return truncated
    
    def _truncate_tail(self, text: str, max_tokens: int) -> str:
        """Keep the end, truncate the beginning."""
        chars_per_token = self.counter.chars_per_token
        estimated_chars = int(max_tokens * chars_per_token * 0.9)
        
        truncated = text[-estimated_chars:]
        
        while self.counter.count(truncated) > max_tokens and len(truncated) > 0:
            truncated = truncated[100:] if len(truncated) > 100 else truncated[10:]
        
        if truncated != text:
            truncated = "..." + truncated.lstrip()
        
        return truncated
    
    def _truncate_middle(self, text: str, max_tokens: int) -> str:
        """Keep beginning and end, truncate middle."""
        chars_per_token = self.counter.chars_per_token
        estimated_chars = int(max_tokens * chars_per_token * 0.9)
        
        # Split roughly in half
        half_chars = estimated_chars // 2
        
        start = text[:half_chars]
        end = text[-half_chars:]
        
        truncated = start.rstrip() + "\n\n[...truncated...]\n\n" + end.lstrip()
        
        # Fine-tune
        while self.counter.count(truncated) > max_tokens:
            half_chars = int(half_chars * 0.9)
            start = text[:half_chars]
            end = text[-half_chars:]
            truncated = start.rstrip() + "\n\n[...truncated...]\n\n" + end.lstrip()
            if half_chars < 10:
                break
        
        return truncated
    
    def _truncate_smart(self, text: str, max_tokens: int) -> str:
        """Truncate at sentence/paragraph boundaries."""
        chars_per_token = self.counter.chars_per_token
        estimated_chars = int(max_tokens * chars_per_token * 0.9)
        
        if len(text) <= estimated_chars:
            return text
        
        # Try to find a good break point
        truncated = text[:estimated_chars]
        
        # Look for paragraph break
        last_para = truncated.rfind("\n\n")
        if last_para > estimated_chars * 0.5:
            truncated = truncated[:last_para]
        else:
            # Look for sentence break
            for sep in [". ", "! ", "? ", ".\n", "!\n", "?\n"]:
                last_sentence = truncated.rfind(sep)
                if last_sentence > estimated_chars * 0.5:
                    truncated = truncated[:last_sentence + 1]
                    break
        
        # Fine-tune
        while self.counter.count(truncated) > max_tokens and len(truncated) > 0:
            truncated = truncated[:-50] if len(truncated) > 50 else truncated[:-5]
        
        if truncated != text:
            truncated = truncated.rstrip() + "\n\n[...content truncated...]"
        
        return truncated
    
    def truncate_messages(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        preserve_system: bool = True,
        preserve_last_n: int = 2,
    ) -> List[Dict[str, str]]:
        """Truncate a list of messages to fit within token limit.
        
        Removes older messages while preserving system message and
        recent messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'.
            max_tokens: Maximum tokens (defaults to available_tokens).
            preserve_system: Whether to always keep system messages.
            preserve_last_n: Number of recent messages to always keep.
            
        Returns:
            Truncated list of messages.
        """
        if max_tokens is None:
            max_tokens = self.available_tokens
        
        if not messages:
            return messages
        
        # Separate system messages and conversation
        system_messages = []
        conversation = []
        
        for msg in messages:
            if msg.get("role") == "system" and preserve_system:
                system_messages.append(msg)
            else:
                conversation.append(msg)
        
        # Calculate tokens for preserved messages
        preserved = system_messages + conversation[-preserve_last_n:] if preserve_last_n > 0 else system_messages
        preserved_tokens = self.counter.count_messages(preserved)
        
        if preserved_tokens >= max_tokens:
            # Even preserved messages exceed limit - truncate content
            return self._truncate_message_content(preserved, max_tokens)
        
        # Add older messages until we hit the limit
        remaining_tokens = max_tokens - preserved_tokens
        middle_messages = conversation[:-preserve_last_n] if preserve_last_n > 0 else conversation
        
        included_middle: List[Dict[str, str]] = []
        for msg in reversed(middle_messages):
            msg_tokens = self.counter.count_messages([msg])
            if msg_tokens <= remaining_tokens:
                included_middle.insert(0, msg)
                remaining_tokens -= msg_tokens
            else:
                break
        
        # Reconstruct message list
        result = system_messages + included_middle
        if preserve_last_n > 0:
            result.extend(conversation[-preserve_last_n:])
        
        return result
    
    def _truncate_message_content(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
    ) -> List[Dict[str, str]]:
        """Truncate individual message content to fit."""
        result = []
        remaining = max_tokens
        
        for msg in messages:
            msg_copy = msg.copy()
            content = msg_copy.get("content", "")
            
            # Reserve some tokens for this message's overhead
            content_budget = remaining - 10
            if content_budget <= 0:
                break
            
            content_tokens = self.counter.count(content)
            if content_tokens > content_budget:
                # Truncate content
                msg_copy["content"] = self._truncate_head(content, content_budget)
            
            result.append(msg_copy)
            remaining -= self.counter.count_messages([msg_copy])
            
            if remaining <= 0:
                break
        
        return result


@dataclass
class TokenUsage:
    """Record of token usage for a single operation.
    
    Attributes:
        input_tokens: Number of input/prompt tokens.
        output_tokens: Number of output/completion tokens.
        total_tokens: Total tokens used.
        model: The model used.
        timestamp: Unix timestamp of the operation.
        operation: Description of the operation.
        cost: Estimated cost in USD.
    """
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    timestamp: float = field(default_factory=time.time)
    operation: str = ""
    cost: float = 0.0
    
    @classmethod
    def create(
        cls,
        input_tokens: int,
        output_tokens: int,
        model: str,
        operation: str = "",
    ) -> "TokenUsage":
        """Create a TokenUsage record with calculated cost.
        
        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            model: The model used.
            operation: Description of the operation.
            
        Returns:
            A TokenUsage instance with calculated cost.
        """
        total = input_tokens + output_tokens
        cost = estimate_cost(model, input_tokens, output_tokens)
        
        return cls(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total,
            model=model,
            operation=operation,
            cost=cost,
        )


@dataclass
class TokenBudget:
    """Tracks token usage against a budget.
    
    This class helps manage token consumption for cost control,
    tracking usage over time and enforcing limits.
    
    Attributes:
        max_tokens: Maximum tokens allowed in the budget period.
        max_cost: Maximum cost allowed in USD (optional).
        period_seconds: Budget period in seconds (default: 3600 = 1 hour).
        
    Example:
        >>> budget = TokenBudget(max_tokens=100000, max_cost=1.0)
        >>> budget.record_usage(TokenUsage.create(1000, 500, "gpt-4o"))
        >>> print(f"Remaining: {budget.remaining_tokens} tokens")
        >>> if budget.can_spend(2000):
        ...     # Make API call
        ...     pass
    """
    max_tokens: int
    max_cost: Optional[float] = None
    period_seconds: float = 3600.0  # 1 hour default
    _usage_history: List[TokenUsage] = field(default_factory=list)
    _period_start: float = field(default_factory=time.time)
    
    def _cleanup_old_usage(self) -> None:
        """Remove usage records outside the current period."""
        current_time = time.time()
        cutoff = current_time - self.period_seconds
        
        # Reset period if needed
        if current_time - self._period_start >= self.period_seconds:
            self._period_start = current_time
            self._usage_history = []
        else:
            self._usage_history = [
                u for u in self._usage_history
                if u.timestamp >= cutoff
            ]
    
    @property
    def used_tokens(self) -> int:
        """Get total tokens used in current period."""
        self._cleanup_old_usage()
        return sum(u.total_tokens for u in self._usage_history)
    
    @property
    def used_cost(self) -> float:
        """Get total cost in current period."""
        self._cleanup_old_usage()
        return sum(u.cost for u in self._usage_history)
    
    @property
    def remaining_tokens(self) -> int:
        """Get remaining tokens in budget."""
        return max(0, self.max_tokens - self.used_tokens)
    
    @property
    def remaining_cost(self) -> Optional[float]:
        """Get remaining cost budget."""
        if self.max_cost is None:
            return None
        return max(0.0, self.max_cost - self.used_cost)
    
    def can_spend(self, tokens: int, estimated_cost: float = 0.0) -> bool:
        """Check if spending tokens would exceed budget.
        
        Args:
            tokens: Number of tokens to spend.
            estimated_cost: Estimated cost of the operation.
            
        Returns:
            True if the operation is within budget.
        """
        if self.used_tokens + tokens > self.max_tokens:
            return False
        
        if self.max_cost is not None and self.used_cost + estimated_cost > self.max_cost:
            return False
        
        return True
    
    def record_usage(self, usage: TokenUsage) -> None:
        """Record token usage.
        
        Args:
            usage: The TokenUsage record to add.
        """
        self._cleanup_old_usage()
        self._usage_history.append(usage)
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get a summary of current usage.
        
        Returns:
            Dictionary with usage statistics.
        """
        self._cleanup_old_usage()
        
        return {
            "period_seconds": self.period_seconds,
            "max_tokens": self.max_tokens,
            "max_cost": self.max_cost,
            "used_tokens": self.used_tokens,
            "used_cost": self.used_cost,
            "remaining_tokens": self.remaining_tokens,
            "remaining_cost": self.remaining_cost,
            "usage_count": len(self._usage_history),
            "utilization_percent": (self.used_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0,
        }
    
    def reset(self) -> None:
        """Reset the budget period and clear usage history."""
        self._period_start = time.time()
        self._usage_history = []


class TokenBudgetExceededError(Exception):
    """Raised when an operation would exceed the token budget."""
    
    def __init__(
        self,
        requested_tokens: int,
        remaining_tokens: int,
        message: Optional[str] = None,
    ) -> None:
        """Initialize the error.
        
        Args:
            requested_tokens: Tokens requested for the operation.
            remaining_tokens: Tokens remaining in budget.
            message: Optional custom message.
        """
        self.requested_tokens = requested_tokens
        self.remaining_tokens = remaining_tokens
        
        if message is None:
            message = (
                f"Token budget exceeded: requested {requested_tokens} tokens, "
                f"but only {remaining_tokens} remaining"
            )
        
        super().__init__(message)
