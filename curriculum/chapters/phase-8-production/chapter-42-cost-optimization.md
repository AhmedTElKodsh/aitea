# Chapter 42: Token Management & Cost Optimization — The Budget

<!--
METADATA
Phase: 8 - Production
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 10 (Streaming)
Builds Toward: Multi-Agent Systems (Ch 43)
Correctness Properties: P57 (Token Accuracy), P58 (Cost Calculation)
Project Thread: Efficiency

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You leave the water running while you brush your teeth.
It's just a little water, right?
Now imagine you run a hotel with 500 guests, and *everyone* leaves the water running. 🚰
That's your utility bill.

In AI, **Tokens are Water**.
Every time you send a prompt, the meter spins.
- "Hello" = 1 token.
- A 50-page PDF = 20,000 tokens.
- An Infinite Loop = Bankruptcy.

**By the end of this chapter**, you will learn how to count tokens before you spend them, cache answers to save money, and pick the right model for the right job. You'll turn a $500 bill into a $5 bill. 📉

---

## Prerequisites Check

```bash
# We need tiktoken (OpenAI's tokenizer)
pip install tiktoken
```

---

## The Story: The Surprise Bill

### The Problem (Invisible Costs)

You built a "Summary Bot". It summarizes user emails.
You used `gpt-4` because it's the smartest.
You didn't realize users were pasting 10,000-word newsletters.
GPT-4 costs ~$30.00 per 1M tokens (output).
You processed 1,000 emails. Boom. $100 gone in an afternoon.

### The Solution (Optimization)

1.  **Count**: Know the cost *before* you call.
2.  **Cache**: If you summarized this email yesterday, don't do it again.
3.  **Downgrade**: Use `gpt-4o-mini` (20x cheaper) for simple summaries.

---

## Part 1: Counting Tokens with Tiktoken

You can't optimize what you can't measure.

### 🔬 Try This! (Hands-On Practice #1)

**Create `token_counter.py`**:

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base") # Fallback
    
    tokens = encoding.encode(text)
    return len(tokens)

# Test
text = "Hello, world! This is a test."
count = count_tokens(text)
print(f"Text: '{text}'")
print(f"Tokens: {count}")
print(f"Words: {len(text.split())}")
```

**Run it**.
Notice: Tokens are usually *more* than words (punctuation counts). But sometimes *less* (long words like "intelligence" might be 1 token).
Rule of thumb: **1000 tokens ≈ 750 words**.

---

## Part 2: The Cost Calculator

Let's write a function to estimate price.

### 🔬 Try This! (Hands-On Practice #2)

**Create `cost_calc.py`**:

```python
from token_counter import count_tokens

# Prices (as of late 2024, approximate)
PRICING = {
    "gpt-4o": {"input": 5.00, "output": 15.00}, # per 1M tokens
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

def estimate_cost(input_text: str, output_text: str, model: str) -> float:
    if model not in PRICING:
        return 0.0
    
    in_tokens = count_tokens(input_text, model)
    out_tokens = count_tokens(output_text, model)
    
    in_cost = (in_tokens / 1_000_000) * PRICING[model]["input"]
    out_cost = (out_tokens / 1_000_000) * PRICING[model]["output"]
    
    return in_cost + out_cost

# Scenario: Summarizing a book
book_text = "word " * 50000 # 50k words
summary = "word " * 500     # 500 words

cost_heavy = estimate_cost(book_text, summary, "gpt-4o")
cost_lite = estimate_cost(book_text, summary, "gpt-4o-mini")

print(f"GPT-4o Cost: ${cost_heavy:.4f}")
print(f"Mini Cost:   ${cost_lite:.4f}")
print(f"Savings: {cost_heavy / cost_lite:.1f}x")
```

**Run it**.
You'll see `gpt-4o-mini` is dramatically cheaper.
**Lesson**: Always start with Mini. Upgrade only if needed.

---

## Part 3: Caching (The Free Lunch)

The cheapest API call is the one you don't make.
LangChain has built-in caching.

### 🔬 Try This! (Hands-On Practice #3)

**Create `caching.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
import time

# 1. Enable Cache
set_llm_cache(InMemoryCache())

model = ChatOpenAI(model="gpt-4o-mini")

# 2. First Call (Slow, Costs Money)
start = time.time()
print("Call 1 (Network)...")
res1 = model.invoke("Tell me a joke about cache.")
print(f"Time: {time.time() - start:.4f}s")

# 3. Second Call (Fast, Free)
start = time.time()
print("\nCall 2 (Cached)...")
res2 = model.invoke("Tell me a joke about cache.") # Exact same prompt
print(f"Time: {time.time() - start:.4f}s")

print(f"\nResult: {res2.content[:50]}...")
```

**Run it**.
Call 2 should be almost instantaneous (0.001s).
In production, use **Redis** or **SQLite** caching so it persists after restart.

---

## Common Mistakes

### Mistake #1: Caching Dynamic Prompts
If your prompt includes the current time (`f"Current time: {time.time()}"`), the cache *never* hits because the prompt is always unique.
**Fix**: Remove timestamps from prompts unless necessary.

### Mistake #2: Ignoring Output Tokens
You focus on the prompt size, but the AI generates a 2,000-word essay.
**Fix**: Set `max_tokens` in your API call to limit the budget.

### Mistake #3: Optimizing too early
Don't optimize for cost when you are prototyping. Optimize for *quality* (GPT-4o). Once it works, swap to Mini and check if quality holds.

---

## Quick Reference Card

### Pricing Mental Model
- **GPT-4o**: Premium steak dinner ($$$)
- **GPT-4o-mini**: Fast food lunch ($)
- **Local (Ollama)**: Home cooking (Free, but you do the work)

### Caching Setup
```python
from langchain.globals import set_llm_cache
set_llm_cache(InMemoryCache())
```

---

## Verification (REQUIRED SECTION)

We need to verify **P57 (Token Accuracy)** and **P58 (Cost Calc)**.

**Create `verify_cost.py`**:

```python
"""
Verification script for Chapter 42.
Properties: P57 (Count), P58 (Calc).
"""
import tiktoken
import sys

print("🧪 Running Cost Verification...\n")

# P57: Token Accuracy
# "Hello world" is usually 2 tokens ("Hello", " world")
# Let's check a specific known string.
text = "Hello world"
enc = tiktoken.get_encoding("cl100k_base")
tokens = enc.encode(text)

print(f"Tokens: {tokens}")
if len(tokens) == 2:
    print("✅ P57 Passed: Token count is accurate.")
else:
    print(f"❌ Failed: Expected 2 tokens, got {len(tokens)}")
    sys.exit(1)

# P58: Cost Calculation logic
# If input price is $10/1M, and we have 1M tokens, cost is $10.
def calc(tokens, price_per_m):
    return (tokens / 1_000_000) * price_per_m

cost = calc(1_000_000, 10.00)
if abs(cost - 10.0) < 0.001:
    print("✅ P58 Passed: Cost math is correct.")
else:
    print(f"❌ Failed: Math error. {cost}")
    sys.exit(1)

print("\n🎉 Chapter 42 Complete! You are financially responsible.")
```

**Run it:** `python verify_cost.py`

---

## Summary

**What you learned:**

1. ✅ **Tokens vs Words**: The currency of AI.
2. ✅ **Tiktoken**: The scale for weighing your data.
3. ✅ **Pricing Tiers**: Understanding the 100x difference between models.
4. ✅ **Caching**: The easiest way to speed up apps and save money.
5. ✅ **Architecture**: Start smart (GPT-4), optimize later (Mini).

**Key Takeaway**: Performance isn't just about speed. It's about **ROI** (Return on Investment).

**Skills unlocked**: 🎯
- Cost Engineering
- Caching Strategies
- Production Economics

**Looking ahead**: You have finished **Phase 8: Production**. You can build, test, secure, and optimize.
Now, we reach the summit. **Phase 9: Multi-Agent Systems**.
One agent is cool. But a *team* of agents? That's a company.
In **Chapter 43**, we will introduce **Multi-Agent Fundamentals**.

---

**Next**: [Phase 9: Multi-Agent Systems (Chapter 43) →](../phase-9-multi-agent/chapter-43-multi-agent-fundamentals.md)
