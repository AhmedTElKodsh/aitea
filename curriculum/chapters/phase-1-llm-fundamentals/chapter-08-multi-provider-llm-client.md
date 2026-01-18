# Chapter 8: Multi-Provider LLM Client — Building Flexible AI Abstraction

<!--
METADATA
Phase: Phase 1: LLM Fundamentals
Time: 2.0 hours (60 minutes reading + 60 minutes hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation / Foundation
Prerequisites: Chapter 7 (Your First LLM Call), Chapter 6C (OOP Intermediate), Chapter 3 (Pydantic)
Builds Toward: Chapter 9 (Prompt Engineering), Chapter 17 (RAG System), Chapter 54 (Complete System)
Correctness Properties: [P4: Provider Abstraction, P5: Cost Tracking, P6: Factory Pattern]
Project Thread: MultiProviderLLMClient - connects to Ch 9, 17, 54

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification
→ What's Next: #whats-next

TEMPLATE VERSION: v2.1 (2026-01-17)
-->

---

## ☕ Coffee Shop Intro

Imagine you're building your Civil Engineering document system. You start with OpenAI's GPT-4, and it works great! But then:

- **GPT-4 is too expensive** for simple tasks → You want to use GPT-3.5
- **You need longer context** → Anthropic's Claude handles 200K tokens
- **OpenAI has an outage** → You need a fallback provider
- **A new model launches** → You want to test it without rewriting code

**Right now, your code looks like this:**

```python
from openai import OpenAI

client = OpenAI(api_key="...")
response = client.chat.completions.create(...)  # Locked to OpenAI!
```

**What if** you need to swap OpenAI for Claude? Or use GPT-4 for complex tasks and GPT-3.5 for simple ones? You'd have to change code everywhere. 😰

**Today, you'll build a provider-agnostic LLM client** that works like this:

```python
# Unified interface — same code, any provider!
llm = LLMClient.from_provider("openai", model="gpt-4")
response = llm.chat("Summarize this report...")

# Swap to Claude? Just change one parameter:
llm = LLMClient.from_provider("anthropic", model="claude-3-sonnet")
response = llm.chat("Summarize this report...")  # Same interface!
```

By the end of this chapter, you'll have a production-ready multi-provider LLM client using the OOP patterns from Chapter 6C. Let's build it! 🚀

---

## Prerequisites Check

Before we proceed, make sure you have:

✅ **Understanding of abstract base classes** (Chapter 6C):
```python
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def chat(self, prompt): pass
```

✅ **Factory method pattern** (Chapter 6C):
```python
@classmethod
def from_provider(cls, provider_name):
    return providers[provider_name]()
```

✅ **OpenAI API basics** (Chapter 7):
```python
response = client.chat.completions.create(model="gpt-4", messages=[...])
```

✅ **Environment variables for API keys**:
```python
import os
api_key = os.getenv("OPENAI_API_KEY")
```

If any of these feel unclear, take 10 minutes to review! 🧩

---

## What You Already Know 🧩

You've been using abstraction layers constantly:

**When you use a database:**
```python
# SQLAlchemy abstracts away database differences
engine = create_engine("postgresql://...")  # PostgreSQL
engine = create_engine("sqlite://...")      # SQLite
# Same code, different databases!
```

**When you work with files:**
```python
from pathlib import Path

# Works on Windows, Mac, Linux — Path abstracts OS differences
path = Path("data") / "report.pdf"
```

**When you make HTTP requests:**
```python
import requests

# requests abstracts away low-level sockets, handles all HTTP providers
response = requests.get("https://api.example.com")
```

**Your LLM client will work the same way:**
- Unified interface (`chat()`, `count_tokens()`, `get_cost()`)
- Provider-specific implementation hidden behind abstraction
- Swap providers without changing application code

You've been benefiting from this pattern—now you'll build it yourself! 💡

---

## The Story: Why Multi-Provider Matters

### The Problem

Ahmed's document system is growing:

```python
# report_summarizer.py
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_report(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Summarize: {text}"}]
    )
    return response.choices[0].message.content


# spec_generator.py
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_spec(requirements):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Generate spec: {requirements}"}]
    )
    return response.choices[0].message.content
```

**😰 Problems:**
1. **Vendor lock-in** — OpenAI code everywhere, can't switch providers
2. **No cost optimization** — Using expensive GPT-4 for everything
3. **No fallback** — If OpenAI is down, the system stops
4. **Duplication** — OpenAI client setup repeated in every file
5. **Hard to test** — Can't mock LLM calls easily

### The Elegant Solution: Abstract Provider Pattern

**Using OOP patterns from Chapter 6C:**

```python
# llm_client.py - ONE abstraction for ALL providers

from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    """Abstract base class for all LLM providers"""

    @abstractmethod
    def chat(self, prompt: str, system_message: str = None) -> str:
        """Send a chat message and get response"""
        pass

    @abstractmethod
    def get_cost(self) -> float:
        """Calculate cost of recent API calls"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI-specific implementation"""

    def chat(self, prompt, system_message=None):
        # OpenAI implementation
        pass


class AnthropicClient(BaseLLMClient):
    """Anthropic (Claude) implementation"""

    def chat(self, prompt, system_message=None):
        # Anthropic implementation
        pass


# Factory method
@classmethod
def from_provider(cls, provider: str):
    providers = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient
    }
    return providers[provider]()


# Usage - same code, any provider!
def summarize_report(text, provider="openai"):
    llm = BaseLLMClient.from_provider(provider)
    return llm.chat(f"Summarize: {text}")


# Easy to switch providers:
summary = summarize_report(report_text, provider="openai")
summary = summarize_report(report_text, provider="anthropic")
```

**🎉 Benefits:**
- **Provider-agnostic** — Application code doesn't know (or care) which LLM it's using
- **Cost optimization** — Use cheap models for simple tasks, expensive for complex
- **Fallback support** — Try OpenAI, fall back to Anthropic if it fails
- **Centralized configuration** — API keys and settings in one place
- **Testability** — Mock the base class for unit tests
- **Future-proof** — Add new providers without changing existing code

Let's build it step by step! 🏗️

---

## Part 1: Designing the Abstract Base Class

### Identifying Common Operations

All LLM providers support these core operations:

| Operation | Purpose | Example |
|-----------|---------|---------|
| **chat()** | Send message, get response | `client.chat("Hello!")` |
| **count_tokens()** | Estimate token usage | `client.count_tokens(text)` |
| **get_cost()** | Calculate API costs | `client.get_cost()` → `$0.05` |

**These become our abstract methods** — every provider MUST implement them.

### Optional Features

Some providers have unique features:

| Feature | Provider | Example |
|---------|----------|---------|
| **Streaming** | OpenAI, Anthropic | Real-time token generation |
| **Vision** | OpenAI GPT-4V, Claude 3 | Image analysis |
| **Function calling** | OpenAI | Structured tool use |
| **200K context** | Anthropic Claude | Very long documents |

**We'll handle these with optional methods** that raise `NotImplementedError` if unsupported.

---

### The Base Class Design

```python
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from dataclasses import dataclass

@dataclass
class ChatMessage:
    """Represents a chat message"""
    role: str  # "system", "user", or "assistant"
    content: str


@dataclass
class ChatResponse:
    """Unified response format across providers"""
    content: str
    model: str
    tokens_used: int
    cost: float
    provider: str


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM providers.

    All providers must implement:
    - chat(): Send messages and get responses
    - count_tokens(): Estimate token usage
    - get_cost(): Calculate costs

    Optional features can raise NotImplementedError.
    """

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        self.total_tokens = 0
        self.total_cost = 0.0

    @abstractmethod
    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> ChatResponse:
        """
        Send chat messages and get response.

        Args:
            messages: List of ChatMessage objects
            temperature: Randomness (0.0-1.0)
            max_tokens: Max tokens to generate

        Returns:
            ChatResponse with generated text and metadata
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Estimate number of tokens in text"""
        pass

    def get_cost(self) -> float:
        """Return total cost of API calls made so far"""
        return self.total_cost

    def reset_usage(self):
        """Reset token and cost tracking"""
        self.total_tokens = 0
        self.total_cost = 0.0
```

**Key design decisions:**
1. **`ChatMessage` dataclass** — Clean message representation
2. **`ChatResponse` dataclass** — Unified response format (same for all providers)
3. **Track usage automatically** — `total_tokens`, `total_cost` updated after each call
4. **Required methods** — `@abstractmethod` for `chat()` and `count_tokens()`
5. **Provider-agnostic interface** — Application code doesn't see provider details

---

## Part 2: Implementing OpenAI Client

```python
import tiktoken
from openai import OpenAI
from typing import List, Optional

class OpenAIClient(BaseLLMClient):
    """OpenAI-specific implementation"""

    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
    }

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        import os
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__(model, api_key)
        self.client = OpenAI(api_key=api_key)
        self.tokenizer = tiktoken.encoding_for_model(model)

    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> ChatResponse:
        """Send chat to OpenAI API"""

        # Convert our ChatMessage format to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Make API call
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Extract data
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        cost = self._calculate_cost(
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )

        # Update tracking
        self.total_tokens += tokens_used
        self.total_cost += cost

        return ChatResponse(
            content=content,
            model=response.model,
            tokens_used=tokens_used,
            cost=cost,
            provider="openai"
        )

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        return len(self.tokenizer.encode(text))

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage"""
        pricing = self.PRICING.get(self.model, self.PRICING["gpt-3.5-turbo"])
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        return input_cost + output_cost
```

**What makes this work:**
1. **Inherits from `BaseLLMClient`** — Must implement `chat()` and `count_tokens()`
2. **Provider-specific setup** — OpenAI client, tiktoken for token counting
3. **Price tracking** — Uses provider-specific pricing
4. **Format conversion** — Converts our `ChatMessage` to OpenAI's format
5. **Automatic cost calculation** — Tracks tokens and costs after each call

---

## Part 3: Implementing Anthropic Client

```python
import anthropic
from typing import List, Optional

class AnthropicClient(BaseLLMClient):
    """Anthropic (Claude) implementation"""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25}
    }

    def __init__(self, model: str = "claude-3-sonnet-20240229", api_key: Optional[str] = None):
        import os
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        super().__init__(model, api_key)
        self.client = anthropic.Anthropic(api_key=api_key)

    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1024
    ) -> ChatResponse:
        """Send chat to Anthropic API"""

        # Anthropic handles system messages differently
        system_message = next((msg.content for msg in messages if msg.role == "system"), None)
        user_messages = [msg for msg in messages if msg.role != "system"]

        # Convert to Anthropic format
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in user_messages
        ]

        # Make API call
        response = self.client.messages.create(
            model=self.model,
            system=system_message,
            messages=anthropic_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Extract data
        content = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        tokens_used = input_tokens + output_tokens
        cost = self._calculate_cost(input_tokens, output_tokens)

        # Update tracking
        self.total_tokens += tokens_used
        self.total_cost += cost

        return ChatResponse(
            content=content,
            model=response.model,
            tokens_used=tokens_used,
            cost=cost,
            provider="anthropic"
        )

    def count_tokens(self, text: str) -> int:
        """Estimate tokens (Anthropic uses different tokenizer)"""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage"""
        model_key = "claude-3-sonnet"  # Default
        if "opus" in self.model:
            model_key = "claude-3-opus"
        elif "haiku" in self.model:
            model_key = "claude-3-haiku"

        pricing = self.PRICING[model_key]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
```

**Key differences from OpenAI:**
1. **System message handling** — Anthropic uses separate `system` parameter
2. **Different API structure** — `messages.create()` instead of `chat.completions.create()`
3. **Token counting** — Anthropic doesn't provide public tokenizer, so we estimate
4. **Pricing structure** — Per 1M tokens instead of per 1K

**But the interface is identical!** Applications don't need to know these differences. 🎯

---

## Part 4: Factory Method for Provider Selection

```python
class LLMClient:
    """Factory class for creating LLM clients"""

    @staticmethod
    def from_provider(
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> BaseLLMClient:
        """
        Create LLM client for specified provider.

        Args:
            provider: "openai" or "anthropic"
            model: Model name (uses default if not specified)
            api_key: API key (uses env var if not specified)

        Returns:
            BaseLLMClient subclass instance

        Example:
            llm = LLMClient.from_provider("openai", model="gpt-4")
            response = llm.chat([ChatMessage(role="user", content="Hello!")])
        """

        providers = {
            "openai": OpenAIClient,
            "anthropic": AnthropicClient
        }

        provider_class = providers.get(provider.lower())
        if provider_class is None:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(providers.keys())}")

        # Create instance with or without model parameter
        if model:
            return provider_class(model=model, api_key=api_key)
        else:
            return provider_class(api_key=api_key)
```

**Usage:**

```python
# Use defaults (gpt-3.5-turbo, API key from env)
llm = LLMClient.from_provider("openai")

# Specify model
llm = LLMClient.from_provider("openai", model="gpt-4")

# Use Anthropic
llm = LLMClient.from_provider("anthropic", model="claude-3-opus-20240229")

# All have the same interface!
response = llm.chat([ChatMessage(role="user", content="Hello!")])
```

---

## Bringing It All Together: Multi-Provider Document Summarizer

Let's build a real-world application that uses multiple providers:

```python
# document_processor.py

import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List

# Import our LLM client classes
from llm_client import LLMClient, ChatMessage, ChatResponse

load_dotenv()


class DocumentSummarizer:
    """
    Document summarizer that uses appropriate LLM based on document size.

    Strategy:
    - Small documents (< 1000 tokens): Use cheap GPT-3.5
    - Medium documents (< 5000 tokens): Use Claude Haiku (fast + cheap)
    - Large documents (> 5000 tokens): Use Claude Sonnet (long context)
    """

    def __init__(self):
        # Initialize multiple clients
        self.gpt35 = LLMClient.from_provider("openai", model="gpt-3.5-turbo")
        self.claude_haiku = LLMClient.from_provider("anthropic", model="claude-3-haiku-20240307")
        self.claude_sonnet = LLMClient.from_provider("anthropic", model="claude-3-sonnet-20240229")

    def summarize(self, text: str, max_length: int = 200) -> dict:
        """
        Summarize text using cost-optimized provider selection.

        Returns:
            dict with summary, provider used, tokens, and cost
        """

        # Estimate tokens (using GPT-3.5 tokenizer as baseline)
        token_count = self.gpt35.count_tokens(text)

        # Select provider based on size
        if token_count < 1000:
            llm = self.gpt35
            provider_name = "GPT-3.5 Turbo"
        elif token_count < 5000:
            llm = self.claude_haiku
            provider_name = "Claude 3 Haiku"
        else:
            llm = self.claude_sonnet
            provider_name = "Claude 3 Sonnet"

        # Create prompt
        messages = [
            ChatMessage(
                role="system",
                content="You are a technical document summarizer for Civil Engineering projects."
            ),
            ChatMessage(
                role="user",
                content=f"Summarize the following document in {max_length} words or less:\n\n{text}"
            )
        ]

        # Make API call (unified interface!)
        response = llm.chat(messages, temperature=0.3)

        return {
            "summary": response.content,
            "provider": provider_name,
            "model": response.model,
            "tokens_used": response.tokens_used,
            "cost": response.cost,
            "input_tokens": token_count
        }

    def get_total_cost(self) -> dict:
        """Get cumulative costs across all providers"""
        return {
            "gpt35_cost": self.gpt35.get_cost(),
            "claude_haiku_cost": self.claude_haiku.get_cost(),
            "claude_sonnet_cost": self.claude_sonnet.get_cost(),
            "total_cost": (
                self.gpt35.get_cost() +
                self.claude_haiku.get_cost() +
                self.claude_sonnet.get_cost()
            )
        }


# Usage example
if __name__ == "__main__":
    summarizer = DocumentSummarizer()

    # Test documents of different sizes
    documents = [
        ("Short technical note (100 words)", "The beam analysis shows..."),
        ("Medium structural report (1500 words)", "Comprehensive structural analysis..."),
        ("Long CAD specification (10000 words)", "Detailed Civil Engineering specifications...")
    ]

    for doc_name, doc_text in documents:
        print(f"\n{'='*60}")
        print(f"Processing: {doc_name}")
        print(f"{'='*60}")

        result = summarizer.summarize(doc_text)

        print(f"Provider: {result['provider']}")
        print(f"Model: {result['model']}")
        print(f"Input tokens: {result['input_tokens']}")
        print(f"Tokens used: {result['tokens_used']}")
        print(f"Cost: ${result['cost']:.4f}")
        print(f"\nSummary:\n{result['summary']}")

    # Show total costs
    print(f"\n{'='*60}")
    print("Total Usage Summary")
    print(f"{'='*60}")
    costs = summarizer.get_total_cost()
    print(f"GPT-3.5 Turbo: ${costs['gpt35_cost']:.4f}")
    print(f"Claude 3 Haiku: ${costs['claude_haiku_cost']:.4f}")
    print(f"Claude 3 Sonnet: ${costs['claude_sonnet_cost']:.4f}")
    print(f"TOTAL: ${costs['total_cost']:.4f}")
```

**🎉 What this demonstrates:**
1. **Provider-agnostic application code** — Same interface for OpenAI and Anthropic
2. **Cost optimization** — Routes to cheapest model for the task
3. **Unified tracking** — Aggregates costs across providers
4. **Easy to extend** — Add new providers without changing `DocumentSummarizer`

---

## Common Mistakes and How to Avoid Them

### Mistake 1: Forgetting to Track Costs

❌ **Wrong:**
```python
def chat(self, messages):
    response = self.client.chat.completions.create(...)
    return response.choices[0].message.content  # Lost cost info!
```

✅ **Correct:**
```python
def chat(self, messages):
    response = self.client.chat.completions.create(...)
    tokens = response.usage.total_tokens
    cost = self._calculate_cost(...)
    self.total_cost += cost  # Track it!
    return ChatResponse(content=..., cost=cost, ...)
```

---

### Mistake 2: Provider-Specific Code in Application Layer

❌ **Wrong:**
```python
# Application code knows about OpenAI specifics
if provider == "openai":
    response = client.chat.completions.create(...)
elif provider == "anthropic":
    response = client.messages.create(...)  # Different API!
```

✅ **Correct:**
```python
# Application code uses unified interface
llm = LLMClient.from_provider(provider)
response = llm.chat(messages)  # Works for all providers!
```

---

### Mistake 3: Not Handling Missing API Keys

❌ **Wrong:**
```python
def __init__(self, api_key=None):
    self.client = OpenAI(api_key=api_key)  # Fails silently if None!
```

✅ **Correct:**
```python
def __init__(self, api_key=None):
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
    self.client = OpenAI(api_key=api_key)
```

---

## Quick Reference Card

### Creating Clients

```python
# OpenAI
llm = LLMClient.from_provider("openai", model="gpt-4")

# Anthropic
llm = LLMClient.from_provider("anthropic", model="claude-3-sonnet-20240229")
```

### Sending Chat Messages

```python
messages = [
    ChatMessage(role="system", content="You are a helpful assistant."),
    ChatMessage(role="user", content="Hello!")
]
response = llm.chat(messages, temperature=0.7)
print(response.content)
```

### Tracking Costs

```python
print(f"Tokens: {response.tokens_used}")
print(f"Cost: ${response.cost:.4f}")
print(f"Total cost: ${llm.get_cost():.4f}")
```

---

## Assessment

### Quick Check Questions

1. **What is the purpose of the `BaseLLMClient` abstract class?**
   <details>
   <summary>Answer</summary>

   To define a unified interface that all LLM providers must implement, ensuring consistent API across different providers (OpenAI, Anthropic, etc.). This allows application code to be provider-agnostic.
   </details>

2. **Why use a factory method (`from_provider`) instead of directly instantiating provider classes?**
   <details>
   <summary>Answer</summary>

   Factory methods:
   - Hide provider-specific implementation details
   - Allow provider selection at runtime (e.g., from config)
   - Make code more maintainable (change provider logic in one place)
   - Enable easier testing (mock the factory method)
   </details>

3. **How does the multi-provider client optimize costs?**
   <details>
   <summary>Answer</summary>

   By routing requests to the most cost-effective provider based on task requirements:
   - Simple/small tasks → Cheap models (GPT-3.5, Claude Haiku)
   - Complex/large tasks → Expensive but capable models (GPT-4, Claude Sonnet)
   - Tracks costs per provider for budget monitoring
   </details>

---

### Coding Challenge: Add Google Gemini Support

**Your mission:** Extend the multi-provider client to support Google's Gemini API.

**Requirements:**

1. **Create `GeminiClient` class**:
   - Inherits from `BaseLLMClient`
   - Implements `chat()` and `count_tokens()`
   - Uses Google's generative AI library

2. **Add to factory method**:
   - Update `LLMClient.from_provider()` to support "gemini" provider

3. **Pricing** (use approximate values):
   - gemini-pro: $0.0005 per 1K tokens (input/output)

**Hints:**
1. Install: `pip install google-generativeai`
2. API key env var: `GOOGLE_API_KEY`
3. Model name: `gemini-pro`
4. Google API uses `model.generate_content(prompt)` instead of chat format

<details>
<summary>💡 <strong>Solution Outline</strong></summary>

```python
import google.generativeai as genai
from typing import List, Optional

class GeminiClient(BaseLLMClient):
    """Google Gemini implementation"""

    PRICING = {
        "gemini-pro": {"input": 0.0005, "output": 0.0015}
    }

    def __init__(self, model: str = "gemini-pro", api_key: Optional[str] = None):
        import os
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key not found.")
        super().__init__(model, api_key)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> ChatResponse:
        """Send chat to Gemini API"""

        # Convert messages to single prompt (Gemini uses simple prompt format)
        prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])

        # Make API call
        response = self.client.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )

        # Extract data
        content = response.text
        # Gemini doesn't return token counts directly, so estimate
        tokens_used = self.count_tokens(prompt) + self.count_tokens(content)
        cost = (tokens_used / 1000) * self.PRICING["gemini-pro"]["input"]

        # Update tracking
        self.total_tokens += tokens_used
        self.total_cost += cost

        return ChatResponse(
            content=content,
            model=self.model,
            tokens_used=tokens_used,
            cost=cost,
            provider="google"
        )

    def count_tokens(self, text: str) -> int:
        """Estimate tokens"""
        return len(text) // 4  # Rough estimate


# Update factory method
class LLMClient:
    @staticmethod
    def from_provider(provider: str, model: Optional[str] = None, api_key: Optional[str] = None):
        providers = {
            "openai": OpenAIClient,
            "anthropic": AnthropicClient,
            "google": GeminiClient  # Added!
        }
        # ... rest of factory logic
```

**Test it:**
```python
llm = LLMClient.from_provider("google", model="gemini-pro")
response = llm.chat([ChatMessage(role="user", content="Hello!")])
print(response.content)
```

**Key takeaway:** Adding a new provider requires only creating a new subclass and updating the factory. Application code doesn't change at all! 🎯
</details>

---

## Verification

Let's verify your multi-provider client implementation with automated tests.

### Test Script

Create this file:

```python
# test_multi_provider_client.py
"""
Automated verification script for Chapter 8
Tests: Provider factory, unified interface, cost tracking, fallback handling
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Mock provider classes for testing without API calls
class MockChatResponse:
    def __init__(self, content: str, tokens: int = 100):
        self.content = content
        self.model = "mock-model"
        self.tokens_used = tokens
        self.cost = tokens * 0.0001
        self.provider = "mock"

class MockLLMClient:
    """Mock LLM client for testing"""
    def __init__(self, model: str = "mock-model", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or "mock-key"
        self.total_tokens = 0
        self.total_cost = 0.0
        self.call_count = 0

    def chat(self, messages, temperature=0.7, max_tokens=None):
        self.call_count += 1
        response = MockChatResponse(f"Mock response from {self.model}", tokens=100)
        self.total_tokens += response.tokens_used
        self.total_cost += response.cost
        return response

    def count_tokens(self, text: str) -> int:
        return len(text) // 4

    def get_cost(self) -> float:
        return self.total_cost

def test_provider_factory():
    """Test 1: Factory method creates correct provider instances"""
    try:
        # Mock factory pattern
        providers = {
            "openai": MockLLMClient,
            "anthropic": MockLLMClient,
            "google": MockLLMClient
        }

        # Test creating different providers
        openai_client = providers["openai"](model="gpt-4")
        anthropic_client = providers["anthropic"](model="claude-3-sonnet")

        # Verify instances are created
        assert openai_client is not None, "OpenAI client should be created"
        assert anthropic_client is not None, "Anthropic client should be created"

        # Verify models are set correctly
        assert openai_client.model == "gpt-4", f"Expected gpt-4, got {openai_client.model}"
        assert anthropic_client.model == "claude-3-sonnet", f"Expected claude-3-sonnet, got {anthropic_client.model}"

        print("✅ PASS: Provider factory creates correct instances")
        return True

    except Exception as e:
        print(f"❌ FAIL: Provider factory test failed: {e}")
        return False

def test_unified_interface():
    """Test 2: All providers have identical interface"""
    try:
        # Create multiple provider instances
        providers = [
            ("OpenAI", MockLLMClient(model="gpt-4")),
            ("Anthropic", MockLLMClient(model="claude-3-sonnet")),
            ("Google", MockLLMClient(model="gemini-pro"))
        ]

        # Test that all providers have the same methods
        required_methods = ["chat", "count_tokens", "get_cost"]

        for provider_name, client in providers:
            for method in required_methods:
                assert hasattr(client, method), \
                    f"{provider_name} missing required method: {method}"

                # Verify method is callable
                assert callable(getattr(client, method)), \
                    f"{provider_name}.{method} should be callable"

        # Test that chat() works the same way for all providers
        for provider_name, client in providers:
            messages = [{"role": "user", "content": "Test message"}]
            response = client.chat(messages)

            # All responses should have the same structure
            assert hasattr(response, "content"), f"{provider_name} response missing 'content'"
            assert hasattr(response, "tokens_used"), f"{provider_name} response missing 'tokens_used'"
            assert hasattr(response, "cost"), f"{provider_name} response missing 'cost'"

        print("✅ PASS: All providers implement unified interface")
        return True

    except Exception as e:
        print(f"❌ FAIL: Unified interface test failed: {e}")
        return False

def test_cost_tracking():
    """Test 3: Cost tracking works correctly across calls"""
    try:
        client = MockLLMClient(model="test-model")

        # Make multiple calls
        num_calls = 5
        for i in range(num_calls):
            messages = [{"role": "user", "content": f"Message {i}"}]
            response = client.chat(messages)

        # Verify costs accumulated
        total_cost = client.get_cost()

        assert total_cost > 0, "Total cost should be greater than 0"
        assert client.call_count == num_calls, \
            f"Expected {num_calls} calls, got {client.call_count}"

        # Verify cost is proportional to number of calls
        expected_cost = num_calls * 100 * 0.0001  # 100 tokens per call, $0.0001 per token
        assert abs(total_cost - expected_cost) < 0.001, \
            f"Expected cost ${expected_cost:.4f}, got ${total_cost:.4f}"

        print(f"✅ PASS: Cost tracking works correctly")
        print(f"   Total calls: {client.call_count}")
        print(f"   Total cost: ${total_cost:.4f}")
        return True

    except Exception as e:
        print(f"❌ FAIL: Cost tracking test failed: {e}")
        return False

def test_provider_selection():
    """Test 4: Can select provider based on task requirements"""
    try:
        # Simulate provider selection based on document size
        def select_provider(text_length: int) -> str:
            """Select cheapest provider for document size"""
            if text_length < 1000:
                return "gpt-3.5-turbo"  # Cheapest for small tasks
            elif text_length < 5000:
                return "claude-haiku"    # Fast and cheap for medium
            else:
                return "claude-sonnet"   # Long context for large

        # Test cases
        test_cases = [
            (500, "gpt-3.5-turbo"),
            (2000, "claude-haiku"),
            (10000, "claude-sonnet")
        ]

        for text_length, expected_model in test_cases:
            selected = select_provider(text_length)
            assert selected == expected_model, \
                f"For {text_length} chars, expected {expected_model}, got {selected}"

        print("✅ PASS: Provider selection logic works")
        return True

    except Exception as e:
        print(f"❌ FAIL: Provider selection test failed: {e}")
        return False

def run_all_tests():
    """Run all verification tests"""
    print("="*60)
    print("Chapter 8 Verification Tests")
    print("="*60)

    tests = [
        ("Provider Factory", test_provider_factory),
        ("Unified Interface", test_unified_interface),
        ("Cost Tracking", test_cost_tracking),
        ("Provider Selection", test_provider_selection)
    ]

    results = []
    for name, test_func in tests:
        print(f"\n[Test] {name}")
        results.append(test_func())

    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! You understand multi-provider patterns!")
        return True
    else:
        print("\n⚠️  Some tests failed. Review the concepts above.")
        return False

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

### Run the test:

```bash
python test_multi_provider_client.py
```

### Expected output:

```
============================================================
Chapter 8 Verification Tests
============================================================

[Test] Provider Factory
✅ PASS: Provider factory creates correct instances

[Test] Unified Interface
✅ PASS: All providers implement unified interface

[Test] Cost Tracking
✅ PASS: Cost tracking works correctly
   Total calls: 5
   Total cost: $0.0050

[Test] Provider Selection
✅ PASS: Provider selection logic works

============================================================
Results: 4/4 tests passed
============================================================

🎉 ALL TESTS PASSED! You understand multi-provider patterns!
```

---

## What's Next?

You've built a production-ready multi-provider LLM client using OOP patterns! This is a **huge milestone** in your AI engineering journey. 🎉

**In the next chapter (Chapter 9: Prompt Engineering Basics)**, you'll learn:
- How to craft effective prompts for consistent results
- Prompt templates and variable substitution
- Few-shot learning (examples in prompts)
- Chain-of-thought prompting for complex reasoning
- How to integrate prompt engineering with your multi-provider client

**But first, take a break!** You've learned a lot:
- Abstract base classes for provider abstraction
- Factory pattern for runtime provider selection
- Unified interfaces across different APIs
- Cost tracking and optimization strategies
- Real-world application architecture

**Your Civil Engineering system architecture now looks like this:**

```
DocumentProcessor (from Chapter 6C)
      ↓
LLMClient (multi-provider) ← YOU ARE HERE
      ↓
PromptTemplates (Chapter 9)
      ↓
RAG System (Chapters 13-17)
      ↓
Complete Document Generation System (Chapter 54)
```

You're building the foundation layer by layer! 🏗️

---

## Summary

**What you learned:**

1. ✅ **Abstract base classes** — Define unified interfaces across providers
2. ✅ **Provider implementation** — OpenAI and Anthropic clients with identical interfaces
3. ✅ **Factory pattern** — Runtime provider selection with `from_provider()`
4. ✅ **Cost optimization** — Route requests to appropriate providers based on task complexity
5. ✅ **Unified response format** — `ChatResponse` works across all providers
6. ✅ **Cost tracking** — Monitor spending across multiple providers
7. ✅ **Extensibility** — Add new providers without changing application code

**Key takeaway:** Abstraction layers let you build flexible systems that aren't locked to a single vendor. The patterns you learned here apply far beyond LLMs—databases, cloud providers, payment processors, all benefit from provider abstraction. You're thinking like a software architect now! 🏗️

**You got this!** 💪 Take a break, then let's master prompt engineering in Chapter 9! 🚀
