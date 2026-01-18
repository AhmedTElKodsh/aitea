# Chapter 12: Error Handling & Retries — The Safety Net

<!--
METADATA
Phase: 1 - LLM Fundamentals
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 8 (Client)
Builds Toward: Production Systems (Ch 41)
Correctness Properties: P9 (Retry Limits), P10 (Circuit Breaker)
Project Thread: Resilience

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You call your favorite pizza place.
Line is busy. *Beep.*
Do you:
A) Call back 0.1 seconds later? (Annoying)
B) Give up immediately and starve? (Defeatist)
C) Wait 5 seconds, then call? If busy, wait 10 seconds? (Smart)

Option C is called **Exponential Backoff**.
APIs are fragile. They timeout, they get overloaded, they crash. If your code assumes "Success or Crash," your app will be brittle.
If your code knows how to say, "Hold on, let me try that again," it becomes **Resilient**.

**By the end of this chapter**, you will build a self-healing system that survives network glitches and rate limits without the user even noticing. 🛡️

---

## Prerequisites Check

We need a new library. It's the industry standard for retrying code.

```bash
pip install tenacity
```

---

## The Story: The "Flaky" API

### The Problem (Random Failure)

You're processing 1,000 documents.
At document #99, the OpenAI API blips. `503 Service Unavailable`.
Your script crashes. You lose progress on the previous 98. You have to restart from zero. 😡

### The Naive Solution (While Loop)

> "I'll just wrap it in a while loop!"

```python
while True:
    try:
        response = client.generate(...)
        break
    except:
        pass # Try again forever
```
**Why this breaks**: If your API key is invalid (`401 Unauthorized`), this loop runs forever, spamming the server and maybe getting your IP banned.

### The Elegant Solution (Smart Retries)

We use **Tenacity**. We define rules:
1. Only retry **Transient** errors (Timeouts, 500s).
2. Never retry **Permanent** errors (401 Auth, 400 Bad Request).
3. Wait longer between each retry (Backoff).

---

## Part 1: Introducing `tenacity`

Tenacity is a decorator-based library. It wraps your function and handles the loop for you.

### 🔬 Try This! (Hands-On Practice #1)

Let's retry a function that fails 50% of the time.

**Create `test_tenacity.py`**:

```python
import random
from tenacity import retry, stop_after_attempt, wait_fixed

# 1. Define the Retry Logic
# Retry up to 3 times
# Wait 2 seconds between attempts
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def do_something_risky():
    print("🎲 Rolling the dice...")
    if random.random() < 0.5:
        print("❌ Failed!")
        raise ValueError("Bad luck")
    print("✅ Success!")
    return "Win"

# 2. Call it
try:
    do_something_risky()
except ValueError:
    print("💀 Gave up after 3 tries.")
```

**Run it**: `python test_tenacity.py`
You'll see it try, fail, wait, try again.

---

## Part 2: Exponential Backoff

Waiting 2 seconds is okay. But if the server is overloaded, spamming it every 2 seconds makes it *worse*.
**Exponential Backoff** waits: 1s, then 2s, then 4s, then 8s. It gives the server breathing room.

### 🔬 Try This! (Hands-On Practice #2)

Modify your script to use `wait_exponential`.

```python
from tenacity import wait_exponential

@retry(
    stop=stop_after_attempt(5), 
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def connect_to_server():
    print("🔌 Connecting...")
    raise ConnectionError("Server busy")

try:
    connect_to_server()
except ConnectionError:
    print("Stopped.")
```

**Run it**. Watch the timing. It slows down intelligently.

---

## Part 3: Selective Retrying

We must not retry errors that will never succeed (like a bad API key).

### 🔬 Try This! (Hands-On Practice #3)

We need to tell Tenacity *which* exceptions to catch.

```python
from tenacity import retry, retry_if_exception_type
import openai

# Only retry Timeout or RateLimit. Crash on AuthenticationError.
@retry(
    retry=retry_if_exception_type((
        openai.APITimeoutError,
        openai.RateLimitError,
        openai.InternalServerError
    )),
    stop=stop_after_attempt(3)
)
def call_api():
    print("Calling API...")
    # Simulate Auth Error
    raise openai.AuthenticationError("Bad Key", response=None, body=None)

# This should crash IMMEDIATELY (no retries)
try:
    call_api()
except Exception as e:
    print(f"Caught expected crash: {type(e).__name__}")
```

---

## Part 4: Updating the Client

Now, let's upgrade our `OpenAIProvider` to use this logic.

### 🔬 Try This! (Hands-On Practice #4)

**Update `shared/infrastructure/llm/openai_provider.py`**:

```python
# Add imports
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import openai

# Define the retry configuration
# We use a standalone decorator so we can reuse it
def openai_retry_decorator():
    return retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((
            openai.RateLimitError,
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.InternalServerError
        ))
    )

class OpenAIProvider(LLMProvider):
    # ... init ...

    # Apply the decorator to the generate method!
    @openai_retry_decorator()
    def generate(self, messages: List[Message], **kwargs) -> str:
        # ... existing code ...
```

Now, your client is bulletproof against network blips!

---

## Part 5: The Circuit Breaker (Advanced)

If the API fails 10 times in a row, it's probably dead. Retrying is pointless.
A **Circuit Breaker** "trips" and stops all requests for a while.

### 🔬 Try This! (Hands-On Practice #5)

We'll add a simple circuit breaker state to our Client.

**Update `shared/infrastructure/llm/client.py`**:

```python
import time

class MultiProviderClient:
    def __init__(self, provider: str = "openai"):
        # ... existing ...
        self.circuit_open = False
        self.circuit_open_time = 0
        self.COOLDOWN_SECONDS = 60

    def generate(self, prompt: str) -> str:
        # 1. Check Circuit
        if self.circuit_open:
            if time.time() - self.circuit_open_time > self.COOLDOWN_SECONDS:
                print("🔌 Circuit Breaker resetting...")
                self.circuit_open = False
            else:
                return "System is temporarily offline (Circuit Open)."

        # 2. Try Request
        try:
            return self.primary_provider.generate(...)
        except Exception as e:
            # 3. Fallback & Trip Circuit if needed
            print(f"⚠️ Error: {e}")
            # Logic: If fallback also fails, trip circuit?
            # Or trip after N primary failures?
            # For simplicity:
            # self.circuit_open = True 
            # self.circuit_open_time = time.time()
            return self.fallback_provider.generate(...)
```

*(Note: In production, you'd track error counts before tripping. For now, understanding the state flag is enough).*

---

## Common Mistakes

### Mistake #1: Retrying on 400 Bad Request
If you send an invalid prompt (too long), the server returns 400. Retrying won't shorten the prompt. You'll just get 400 again. **Never retry 4xx errors.**

### Mistake #2: Not Logging Retries
If your app is retrying, you need to know. Tenacity allows a `before` callback to log "Retrying attempt X...".

```python
from tenacity import before_log
import logging

@retry(before=before_log(logging.getLogger(), logging.INFO))
def ...
```

### Mistake #3: Hardcoding Wait Times
`time.sleep(5)` is bad. `wait_exponential` is good. Random Jitter (adding random ms) is even better to prevent "Thundering Herd" problems (where all clients retry at the exact same millisecond).

---

## Quick Reference Card

### Tenacity Pattern

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(IOError)
)
def network_call():
    ...
```

---

## Verification (REQUIRED SECTION)

We need to prove that we retry exactly N times and stop (Property P9).

**Create `verify_retries.py`**:

```python
"""
Verification script for Chapter 12.
"""
from tenacity import retry, stop_after_attempt
import sys

print("🧪 Running Retry Verification...\n")

# Counter to track attempts
attempts = 0

@retry(stop=stop_after_attempt(3), reraise=True)
def fail_always():
    global attempts
    attempts += 1
    print(f"  Attempt {attempts}...")
    raise ValueError("Fail")

# Test P9: Retry Limits
print("Test 1: Retry Limit Enforcement...")
try:
    fail_always()
except ValueError:
    print("  Caught expected error.")

print(f"Total attempts made: {attempts}")

if attempts == 3:
    print("✅ P9 Passed: Retried exactly 3 times.")
else:
    print(f"❌ Failed: Expected 3, got {attempts}")
    sys.exit(1)

print("\n🎉 Chapter 12 Complete! Your system is now resilient.")
```

**Run it:** `python verify_retries.py`

---

## Summary

**What you learned:**

1. ✅ **Transient vs Permanent**: Know which errors to retry.
2. ✅ **Exponential Backoff**: Don't spam the server.
3. ✅ **Tenacity**: The pythonic way to handle retries.
4. ✅ **Circuit Breaking**: Stopping the bleeding when things are truly broken.
5. ✅ **Decorator Injection**: How to apply retries cleanly to existing classes.

**Key Takeaway**: A system that fails gracefully is better than a perfect system that crashes once. Reliability is a feature.

**Skills unlocked**: 🎯
- Resilience Patterns
- Error Classification
- Decorator Usage

**Looking ahead**: We have covered the Core Fundamentals!
- Calls, Clients, Prompts, Streaming, Extraction, Error Handling.

In **Phase 2**, we will start dealing with **Memory and Knowledge**. We will learn about **Embeddings and Vector Databases** to let the AI "read" thousands of documents!

---

**Next**: [Phase 2: Embeddings & Vectors (Chapter 13) →](../phase-2-embeddings-vectors/chapter-13-understanding-embeddings.md)
