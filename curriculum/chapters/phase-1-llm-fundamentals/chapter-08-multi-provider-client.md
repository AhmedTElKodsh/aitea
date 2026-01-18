# Chapter 8: Multi-Provider LLM Client — The Universal Adapter

<!--
METADATA
Phase: 1 - LLM Fundamentals
Time: 2 hours (40 min reading + 80 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 7 (First LLM Call)
Builds Toward: Production Resilience (Ch 12), Cost Optimization (Ch 42)
Correctness Properties: P2 (Fallback), P3 (Response Consistency)
Project Thread: Core Infrastructure

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You travel to Europe. You plug your hairdryer into the wall. *ZAP!* Sparks fly. ⚡
Why? Because the plug shape and voltage are different.
So you buy a **Universal Travel Adapter**. Now you can plug anything (hairdryer, laptop, phone) into any wall (UK, EU, US) without blowing things up.

**LLM Providers** (OpenAI, Anthropic, Google, Ollama) are like those wall sockets.
They all provide "electricity" (intelligence), but their "plugs" (API formats) are slightly different.
- OpenAI wants `messages=[...]`
- Anthropic wants `system="..."` outside messages
- Google wants `contents=[...]`

If you hardcode OpenAI everywhere, you're locked in. When they have an outage (or raise prices), you're stuck in the dark. 🕯️

**By the end of this chapter**, you will build a **Universal LLM Client**. You'll be able to swap "brains" with a single line of config, and even automatically switch to a backup brain if the first one fails.

---

## Prerequisites Check

```bash
# Check if you have the basics
python --version
pip show openai python-dotenv
```

---

## The Story: The "Vendor Lock-In" Trap

### The Problem (Hardcoded Dependency)

You built your app using `openai.chat.completions.create`.
Suddenly, your boss runs in: "OpenAI is down! Switch to Claude (Anthropic) right now!"

You look at your code:
```python
# file_1.py
client.chat.completions.create(...)

# file_2.py
client.chat.completions.create(...)

# ... 50 other files ...
```
You have to rewrite 50 files. You have to learn Anthropic's API docs. You have to change how you parse the response (`response.content` vs `response.choices[0]...`).
It takes 3 days. The outage was over in 2 hours. 😭

### The Elegant Solution (The Strategy Pattern)

We define **One Interface** (The Adapter) that our app uses.
We write **Strategies** (Drivers) for each provider.

```python
# Our App only knows this:
client.generate("Hello")

# Behind the scenes, we swap the engine:
client = LLMClient(provider="openai")
# OR
client = LLMClient(provider="anthropic")
```

If OpenAI fails, the client automatically tries the next one. Seamless.

---

## Part 1: The Blueprint (Abstract Base Class)

We need a contract. Every provider MUST follow these rules:
1. Accept a standard list of messages.
2. Return a simple string.

### 🔬 Try This! (Hands-On Practice #1)

Let's define the interface.

**Step 1: Create directory**
`shared/infrastructure/llm/` (create `__init__.py` inside too).

**Step 2: Create `shared/infrastructure/llm/base.py`**

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel

# Standardize our input/output
class Message(BaseModel):
    role: str
    content: str

class LLMProvider(ABC):
    """The Abstract Base Class (The Blueprint)."""
    
    @abstractmethod
    def generate(self, messages: List[Message], **kwargs) -> str:
        """Every provider MUST implement this method."""
        pass
```

**What is `ABC`?**
It stands for **Abstract Base Class**. It prevents you from creating an `LLMProvider` directly. You *must* create a subclass (like `OpenAIProvider`) and implement the `generate` method. If you don't, Python yells at you.

---

## Part 2: The Adapters (Implementations)

Now let's build the actual connections.

### 🔬 Try This! (Hands-On Practice #2)

We'll build two providers: `OpenAI` and `Mock` (for testing).

**Step 1: Create `shared/infrastructure/llm/openai_provider.py`**

```python
from openai import OpenAI
from typing import List
from .base import LLMProvider, Message

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key) # Auto-loads from env if None

    def generate(self, messages: List[Message], **kwargs) -> str:
        # 1. Convert our standard Message objects to OpenAI dicts
        formatted_messages = [
            {"role": m.role, "content": m.content} 
            for m in messages
        ]
        
        # 2. Call API
        response = self.client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=formatted_messages,
            temperature=kwargs.get("temperature", 0.7)
        )
        
        # 3. Return standardized string
        return response.choices[0].message.content
```

**Step 2: Create `shared/infrastructure/llm/mock_provider.py`**
This is crucial for testing without spending money!

```python
from typing import List
from .base import LLMProvider, Message

class MockProvider(LLMProvider):
    def __init__(self, fixed_response: str = "This is a mock response."):
        self.fixed_response = fixed_response

    def generate(self, messages: List[Message], **kwargs) -> str:
        print(f"👻 [MOCK] Generating response for {len(messages)} messages")
        return self.fixed_response
```

---

## Part 3: The Universal Client (The Fallback Engine)

Now, the master controller. It holds a list of providers. If one fails, it calls the next.

### 🔬 Try This! (Hands-On Practice #3)

**Create `shared/infrastructure/llm/client.py`**

```python
from typing import List, Optional
from .base import LLMProvider, Message
from .openai_provider import OpenAIProvider
from .mock_provider import MockProvider

class MultiProviderClient:
    def __init__(self, provider: str = "openai"):
        self.primary_provider = self._get_provider(provider)
        self.fallback_provider = MockProvider("System is currently offline (Fallback).")

    def _get_provider(self, name: str) -> LLMProvider:
        if name == "openai":
            return OpenAIProvider()
        elif name == "mock":
            return MockProvider()
        else:
            raise ValueError(f"Unknown provider: {name}")

    def generate(self, prompt: str) -> str:
        """The main entry point for the app."""
        # Convert simple string to Message format
        messages = [Message(role="user", content=prompt)]
        
        try:
            return self.primary_provider.generate(messages)
        except Exception as e:
            print(f"⚠️ Primary provider failed: {e}")
            print("🔄 Switching to fallback...")
            return self.fallback_provider.generate(messages)
```

---

## Bringing It All Together: Resilience Test

Let's simulate a disaster (OpenAI "failing") and watch our system survive.

**Create `simulate_outage.py`**:

```python
from shared.infrastructure.llm.client import MultiProviderClient
from shared.infrastructure.llm.base import LLMProvider, Message
from typing import List

# 1. Create a "Broken" Provider that always fails
class BrokenProvider(LLMProvider):
    def generate(self, messages: List[Message], **kwargs) -> str:
        raise ConnectionError("500 Internal Server Error")

# 2. Hack our client to use the broken provider
client = MultiProviderClient(provider="mock") # Initialize
client.primary_provider = BrokenProvider()    # Break it on purpose

# 3. Try to generate text
print("🚀 Sending request...")
response = client.generate("Hello!")

print(f"\n📝 Final Result: {response}")
```

**Run it**: `python simulate_outage.py`

**Expected Output**:
```
🚀 Sending request...
⚠️ Primary provider failed: 500 Internal Server Error
🔄 Switching to fallback...
👻 [MOCK] Generating response...
📝 Final Result: System is currently offline (Fallback).
```

**Victory!** Your app didn't crash. It degraded gracefully. 🛡️

---

## Common Mistakes

### Mistake #1: Leaking Provider Details
Don't let provider-specific objects (like `openai.types.completion`) leak out of your `generate` method. Always return standard Python types (`str`, `dict`, or your own Pydantic models).

### Mistake #2: Infinite Retry Loops
If you add retry logic inside the provider AND fallback logic in the client, you might end up waiting minutes for a failure. Keep retries tight (e.g., 2 attempts).

### Mistake #3: Hardcoding Models
Don't hardcode `gpt-4` deep inside the provider class. Pass it via `**kwargs` or config, so you can change models easily.

---

## Quick Reference Card

### The Pattern (Strategy)

```python
class Client:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def run(self):
        return self.strategy.execute()
```

### Adding New Providers (e.g., Ollama)

```python
# Just inherit and implement!
class OllamaProvider(LLMProvider):
    def generate(self, messages, **kwargs):
        # Call Ollama API
        return result
```

---

## Verification (REQUIRED SECTION)

Let's ensure your Multi-Provider Client is production-ready.

**Create `verify_client.py`**:

```python
"""
Verification script for Chapter 8.
"""
from shared.infrastructure.llm.client import MultiProviderClient
from shared.infrastructure.llm.mock_provider import MockProvider
import sys

print("🧪 Running Multi-Provider Verification...\n")

# Test 1: Mock Provider Direct
print("Test 1: Mock Provider...")
mock = MockProvider(fixed_response="Test Success")
res = mock.generate([])
assert res == "Test Success"
print("✅ Mock provider works")

# Test 2: Client with Mock
print("Test 2: Client instantiation...")
client = MultiProviderClient(provider="mock")
res = client.generate("Hello")
assert "mock response" in res.lower() or "test" in res.lower()
print("✅ Client connects to provider")

# Test 3: Fallback Logic (Mocking a failure)
print("Test 3: Fallback Mechanism...")
class CrashingProvider(MockProvider):
    def generate(self, *args, **kwargs):
        raise ValueError("Boom")

client.primary_provider = CrashingProvider()
res = client.generate("Help")
assert "Fallback" in res or "mock" in res.lower()
print("✅ Fallback successfully activated")

print("\n🎉 Chapter 8 Complete! You have a resilient LLM infrastructure.")
```

**Run it:** `python verify_client.py`

---

## Summary

**What you learned:**

1. ✅ **Vendor Lock-In is real**: And avoiding it is a key architectural decision.
2. **Strategy Pattern**: Swapping algorithms (providers) at runtime.
3. **Abstraction**: Creating a `base.py` contract that enforces consistency.
4. **Resilience**: Implementing fallback logic to handle outages.
5. **Testing**: Using `MockProvider` to test logic without API costs.

**Key Takeaway**: By wrapping the API call in your own class, you own the interface. You control the defaults, the logging, and the error handling. You are the captain now. 👩‍✈️

**Skills unlocked**: 🎯
- Software Architecture (Adapter Pattern)
- Resilience Engineering
- Abstract Base Classes (ABC)

**Looking ahead**: Now that we can call LLMs safely, we need to talk about **Prompts**. In **Chapter 9**, we'll build a system to manage prompts as engineering assets, not just magic strings.

---

**Next**: [Chapter 9: Prompt Engineering Basics →](chapter-09-prompt-engineering-basics.md)
