# Chapter 12A: Async/Await Fundamentals — Making Concurrent LLM Calls

<!--
METADATA
Phase: Phase 1: LLM Fundamentals
Time: 1.5 hours (45 minutes reading + 45 minutes hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation / Foundation
Prerequisites: Chapter 8 (Multi-Provider Client), Chapter 6A (Decorators), Chapter 6B (Error Handling)
Builds Toward: Chapter 17 (RAG System), Chapter 54 (Complete System)
Correctness Properties: [P10: Concurrent Execution, P11: Error Resilience, P12: Performance Optimization]
Project Thread: AsyncDocumentProcessor - connects to Ch 17, 54

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification
→ What's Next: #whats-next

TEMPLATE VERSION: v2.1 (2026-01-17)
-->

---

## ☕ Coffee Shop Intro

Imagine you're at a coffee shop ordering drinks for your team of 5 engineers. ☕

**Synchronous approach (one at a time):**
1. Order drink 1 → Wait 3 minutes → Receive
2. Order drink 2 → Wait 3 minutes → Receive
3. Order drink 3 → Wait 3 minutes → Receive
4. Order drink 4 → Wait 3 minutes → Receive
5. Order drink 5 → Wait 3 minutes → Receive

**Total time: 15 minutes** ⏰

**Asynchronous approach (order all at once):**
1. Order drinks 1-5 simultaneously → Wait 3 minutes → Receive all

**Total time: 3 minutes** ⚡ (5x faster!)

**This is exactly what happens with LLM API calls.**

**Right now, your document processor does this:**
```python
# Synchronous - processes 10 documents in series
for doc in documents:
    summary = llm.chat(f"Summarize: {doc}")  # Wait 2 seconds per call
# Total: 20 seconds for 10 documents
```

**By the end of this chapter, you'll do this:**
```python
# Asynchronous - processes 10 documents concurrently
summaries = await asyncio.gather(*[
    llm.async_chat(f"Summarize: {doc}") for doc in documents
])
# Total: 2 seconds for 10 documents (10x faster!)
```

Let's learn async/await and supercharge your document processing! 🚀

---

## Prerequisites Check

Before we proceed, make sure you're comfortable with:

✅ **Making LLM API calls** (Chapter 7-8):
```python
llm = LLMClient.from_provider("openai")
response = llm.chat(messages)
```

✅ **List comprehensions**:
```python
results = [process(item) for item in items]
```

✅ **Error handling** (Chapter 6B):
```python
try:
    result = operation()
except Exception as e:
    handle_error(e)
```

✅ **Basic decorators** (Chapter 6A):
```python
@decorator
def function(): pass
```

If any of these feel shaky, take 5 minutes to review! 🧩

---

## What You Already Know 🧩

You've experienced async behavior in real life constantly:

**When you do laundry:**
```
❌ Synchronous: Wash clothes → Wait 1 hour doing nothing → Dry → Wait 1 hour doing nothing
✅ Asynchronous: Start washing → Go cook dinner → Check washer → Start dryer → Continue cooking
```

**When you send emails:**
```
❌ Synchronous: Write email → Hit send → Stare at screen until recipient responds
✅ Asynchronous: Write email → Hit send → Continue working → Get notified when reply arrives
```

**When you order food at a restaurant:**
```
❌ Synchronous: Order → Stand at kitchen door waiting → Get food
✅ Asynchronous: Order → Sit down and chat → Food arrives when ready
```

**In programming, async/await works the same way:**
- **Synchronous**: Your code waits (blocks) until operation completes
- **Asynchronous**: Your code continues working while waiting for I/O operations

You already understand the concept—now you'll learn the Python syntax! 💡

---

## The Story: Why Async Matters for LLM Applications

### The Problem

Ahmed's document processor needs to summarize 50 engineering reports for a client meeting tomorrow. Each summary takes 3 seconds (LLM API call).

**Current synchronous code:**

```python
import time
from llm_client import LLMClient

llm = LLMClient.from_provider("openai", model="gpt-3.5-turbo")

def process_documents(documents):
    summaries = []
    start = time.time()

    for doc in documents:
        print(f"Processing {doc['name']}...")
        summary = llm.chat([
            {"role": "user", "content": f"Summarize: {doc['text']}"}
        ])
        summaries.append(summary)

    elapsed = time.time() - start
    print(f"Processed {len(documents)} documents in {elapsed:.1f} seconds")
    return summaries


# Test with 50 documents
documents = [{"name": f"doc_{i}", "text": "..."} for i in range(50)]
summaries = process_documents(documents)
```

**Output:**
```
Processing doc_0...
Processing doc_1...
Processing doc_2...
...
Processing doc_49...
Processed 50 documents in 150.0 seconds  # 2.5 MINUTES! ⏰
```

😰 **Problems:**
1. **Extremely slow** — 2.5 minutes for 50 documents
2. **CPU is idle** — 95% of time spent waiting for API responses
3. **Doesn't scale** — 500 documents would take 25 minutes!
4. **Poor user experience** — Client meeting is in 10 minutes!

### The Breakthrough: Async/Await for Concurrent API Calls

**With async/await:**

```python
import asyncio
import time
from async_llm_client import AsyncLLMClient

llm = AsyncLLMClient.from_provider("openai", model="gpt-3.5-turbo")

async def process_documents_async(documents):
    summaries = []
    start = time.time()

    # Create all tasks at once
    tasks = [
        llm.async_chat([{"role": "user", "content": f"Summarize: {doc['text']}"}])
        for doc in documents
    ]

    # Run all tasks concurrently
    summaries = await asyncio.gather(*tasks)

    elapsed = time.time() - start
    print(f"Processed {len(documents)} documents in {elapsed:.1f} seconds")
    return summaries


# Run async function
documents = [{"name": f"doc_{i}", "text": "..."} for i in range(50)]
summaries = asyncio.run(process_documents_async(documents))
```

**Output:**
```
Processed 50 documents in 5.2 seconds  # 30x FASTER! ⚡
```

**🎉 From 150 seconds to 5 seconds!** The API calls run concurrently instead of sequentially. This is the power of async/await! 🚀

---

## Part 1: Understanding Synchronous vs Asynchronous

### Synchronous (Blocking) Code

```python
import time

def slow_operation():
    print("Starting operation...")
    time.sleep(2)  # Simulate API call
    print("Operation complete!")
    return "Result"

# Synchronous execution
result1 = slow_operation()  # Program stops here for 2 seconds
result2 = slow_operation()  # Program stops here for 2 seconds
result3 = slow_operation()  # Program stops here for 2 seconds

# Total: 6 seconds (2 + 2 + 2)
```

**Execution timeline:**
```
0s  ─────[Operation 1]─────  2s
2s  ─────[Operation 2]─────  4s
4s  ─────[Operation 3]─────  6s
                              ^
                         Total: 6s
```

---

### Asynchronous (Non-Blocking) Code

```python
import asyncio

async def slow_operation_async():
    print("Starting operation...")
    await asyncio.sleep(2)  # Simulate API call (async!)
    print("Operation complete!")
    return "Result"

# Asynchronous execution
async def main():
    # Create tasks (don't start yet)
    task1 = slow_operation_async()
    task2 = slow_operation_async()
    task3 = slow_operation_async()

    # Run all tasks concurrently
    results = await asyncio.gather(task1, task2, task3)
    return results

# Run the async function
results = asyncio.run(main())

# Total: 2 seconds (all run together!)
```

**Execution timeline:**
```
0s  ─────[Operation 1]─────  2s
0s  ─────[Operation 2]─────  2s
0s  ─────[Operation 3]─────  2s
                              ^
                         Total: 2s (3x faster!)
```

**Key difference:**
- **Synchronous**: Waits (blocks) at each `time.sleep()`
- **Asynchronous**: Releases control at each `await asyncio.sleep()`, allowing other operations to run

---

### When to Use Async vs Sync

| Scenario | Use | Why |
|----------|-----|-----|
| **I/O-bound operations** | Async | Lots of waiting (API calls, file I/O, database queries) |
| **Network requests** | Async | High latency, can run many concurrently |
| **LLM API calls** | Async | Each call takes seconds, perfect for concurrency |
| **CPU-intensive tasks** | Sync | No waiting, CPU is always busy (calculations, image processing) |
| **Simple scripts** | Sync | Async adds complexity, not worth it for simple tasks |

**Rule of thumb:** If your code spends most time *waiting* (I/O-bound), use async. If it spends most time *computing* (CPU-bound), use sync (or multiprocessing).

---

## Part 2: Async/Await Syntax Basics

### The `async` Keyword — Defining Async Functions

```python
# Regular synchronous function
def regular_function():
    return "I'm synchronous"

# Asynchronous function
async def async_function():
    return "I'm asynchronous"
```

**Key differences:**
- `async def` creates a **coroutine function**
- Calling it returns a **coroutine object** (not the result!)
- Must be `await`-ed or run with `asyncio.run()`

```python
# This doesn't work:
result = async_function()  # Returns coroutine object, NOT "I'm asynchronous"

# This works:
result = await async_function()  # ✅ (inside another async function)

# Or this (top-level):
result = asyncio.run(async_function())  # ✅
```

---

### The `await` Keyword — Waiting for Async Operations

```python
import asyncio

async def fetch_data():
    print("Fetching data...")
    await asyncio.sleep(1)  # Simulate API call
    print("Data received!")
    return {"data": "value"}

async def main():
    # await pauses this function until fetch_data() completes
    result = await fetch_data()
    print(f"Result: {result}")

asyncio.run(main())
```

**Output:**
```
Fetching data...
Data received!
Result: {'data': 'value'}
```

**What `await` does:**
1. **Pauses** the current async function
2. **Releases control** to the event loop (allows other tasks to run)
3. **Resumes** when the awaited operation completes
4. **Returns** the result

**Important:** You can only use `await` inside `async` functions!

```python
# ❌ WRONG - can't await in sync function
def sync_function():
    result = await async_function()  # SyntaxError!

# ✅ CORRECT - await in async function
async def async_function_wrapper():
    result = await async_function()
```

---

### Running Async Functions — `asyncio.run()`

```python
import asyncio

async def my_async_function():
    await asyncio.sleep(1)
    return "Done!"

# Entry point - run async function from synchronous code
result = asyncio.run(my_async_function())
print(result)  # "Done!"
```

**`asyncio.run()` does three things:**
1. Creates an event loop
2. Runs the async function
3. Closes the event loop

**Rule:** Use `asyncio.run()` once at the top level to enter the async world. After that, use `await` everywhere.

---

### 🔬 Try This! — Your First Async Function

**Challenge:** Create an async function that simulates downloading 3 files concurrently.

**Requirements:**
1. Create `async def download_file(filename, delay)` that:
   - Prints "Downloading {filename}..."
   - Awaits `asyncio.sleep(delay)` to simulate download time
   - Prints "Downloaded {filename}!"
   - Returns f"{filename} content"

2. Create `async def main()` that:
   - Downloads 3 files concurrently with different delays
   - Uses `asyncio.gather()` to run them together
   - Prints all results

3. Run with `asyncio.run(main())`

**Hints:**
- `asyncio.gather(*tasks)` runs multiple tasks concurrently
- Unpack a list with `*` operator: `asyncio.gather(*[task1, task2, task3])`

<details>
<summary>💡 <strong>Solution</strong></summary>

```python
import asyncio
import time

async def download_file(filename, delay):
    """Simulate downloading a file"""
    print(f"Downloading {filename}...")
    await asyncio.sleep(delay)  # Simulate network I/O
    print(f"Downloaded {filename}!")
    return f"{filename} content"

async def main():
    """Download multiple files concurrently"""
    start = time.time()

    # Create tasks for concurrent downloads
    tasks = [
        download_file("report1.pdf", 2),
        download_file("specs.docx", 3),
        download_file("drawings.dwg", 1)
    ]

    # Run all downloads concurrently
    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start
    print(f"\nAll downloads complete in {elapsed:.1f}s")
    print(f"Results: {results}")

# Run the async program
asyncio.run(main())
```

**Output:**
```
Downloading report1.pdf...
Downloading specs.docx...
Downloading drawings.dwg...
Downloaded drawings.dwg!
Downloaded report1.pdf!
Downloaded specs.docx!

All downloads complete in 3.0s
Results: ['report1.pdf content', 'specs.docx content', 'drawings.dwg content']
```

**Key takeaway:** All 3 downloads happened simultaneously! Total time = slowest download (3s), not sum of all (2+3+1=6s). This is the power of async! ⚡
</details>

---

## Part 3: Concurrent LLM API Calls

### Converting Sync LLM Client to Async

Let's upgrade our multi-provider client from Chapter 8 to support async:

```python
# async_llm_client.py

import asyncio
from abc import ABC, abstractmethod
from typing import List
from openai import AsyncOpenAI  # Async version!
import anthropic

from llm_client import ChatMessage, ChatResponse


class AsyncBaseLLMClient(ABC):
    """Async base class for LLM providers"""

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        self.total_tokens = 0
        self.total_cost = 0.0

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = None
    ) -> ChatResponse:
        """Async chat method - must be implemented by subclasses"""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Token counting (can remain synchronous)"""
        pass


class AsyncOpenAIClient(AsyncBaseLLMClient):
    """Async OpenAI client"""

    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
    }

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str = None):
        import os
        import tiktoken

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__(model, api_key)

        # Use async client!
        self.client = AsyncOpenAI(api_key=api_key)
        self.tokenizer = tiktoken.encoding_for_model(model)

    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = None
    ) -> ChatResponse:
        """Async chat with OpenAI"""

        # Convert to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Async API call - uses await!
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Extract and track
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        cost = self._calculate_cost(
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )

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
        """Count tokens (synchronous - no I/O)"""
        return len(self.tokenizer.encode(text))

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost (synchronous - just math)"""
        pricing = self.PRICING.get(self.model, self.PRICING["gpt-3.5-turbo"])
        return (input_tokens / 1000) * pricing["input"] + (output_tokens / 1000) * pricing["output"]
```

**Key changes:**
1. `AsyncOpenAI` instead of `OpenAI`
2. `async def chat()` instead of `def chat()`
3. `await self.client.chat.completions.create()` instead of `self.client.chat.completions.create()`

---

### Batch Processing Documents Concurrently

```python
# async_document_processor.py

import asyncio
import time
from typing import List, Dict
from async_llm_client import AsyncOpenAIClient
from llm_client import ChatMessage


class AsyncDocumentProcessor:
    """Process multiple documents concurrently"""

    def __init__(self, provider="openai", model="gpt-3.5-turbo"):
        if provider == "openai":
            self.llm = AsyncOpenAIClient(model=model)
        # Add other providers here

    async def summarize_one(self, document: Dict) -> Dict:
        """Summarize a single document"""
        messages = [
            ChatMessage(
                role="system",
                content="You are a Civil Engineering document summarizer."
            ),
            ChatMessage(
                role="user",
                content=f"Summarize this engineering report in 3 bullet points:\n\n{document['text']}"
            )
        ]

        response = await self.llm.chat(messages, temperature=0.3)

        return {
            "document_name": document["name"],
            "summary": response.content,
            "tokens": response.tokens_used,
            "cost": response.cost
        }

    async def summarize_batch(self, documents: List[Dict]) -> List[Dict]:
        """Summarize multiple documents concurrently"""
        start = time.time()

        # Create tasks for all documents
        tasks = [self.summarize_one(doc) for doc in documents]

        # Run all tasks concurrently
        summaries = await asyncio.gather(*tasks)

        elapsed = time.time() - start

        print(f"\n✅ Processed {len(documents)} documents in {elapsed:.1f}s")
        print(f"💰 Total cost: ${self.llm.total_cost:.4f}")
        print(f"🪙 Total tokens: {self.llm.total_tokens}")

        return summaries


# Usage example
async def main():
    # Load documents (simulated)
    documents = [
        {"name": f"report_{i}.pdf", "text": f"Engineering report {i} content..."}
        for i in range(20)
    ]

    # Process concurrently
    processor = AsyncDocumentProcessor()
    summaries = await processor.summarize_batch(documents)

    # Display results
    for summary in summaries[:3]:  # Show first 3
        print(f"\n{summary['document_name']}:")
        print(summary['summary'])


# Run it
if __name__ == "__main__":
    asyncio.run(main())
```

**Output:**
```
✅ Processed 20 documents in 4.2s
💰 Total cost: $0.0312
🪙 Total tokens: 15,620

report_0.pdf:
- Foundation analysis shows adequate bearing capacity
- Minor cracking detected, within acceptable limits
- Recommendations for regular monitoring included

report_1.pdf:
...
```

**Compare to synchronous version:**
- **Sync**: 20 documents × 3 seconds = 60 seconds
- **Async**: ~4 seconds (15x faster!)

---

## Part 4: Error Handling in Async Code

### Basic Try/Except with Async

```python
async def risky_api_call():
    """API call that might fail"""
    await asyncio.sleep(1)
    raise ValueError("API rate limit exceeded!")

async def main():
    try:
        result = await risky_api_call()
    except ValueError as e:
        print(f"Error caught: {e}")

asyncio.run(main())
```

**Output:**
```
Error caught: API rate limit exceeded!
```

**Same as synchronous error handling!** Just use `try`/`except` around `await`.

---

### Handling Errors in `asyncio.gather()`

When running multiple tasks concurrently, you need to handle failures gracefully:

```python
async def process_document(doc_id):
    """Simulate processing that might fail"""
    await asyncio.sleep(1)
    if doc_id == 3:
        raise ValueError(f"Document {doc_id} is corrupted!")
    return f"Processed doc {doc_id}"


async def main_with_errors():
    tasks = [process_document(i) for i in range(5)]

    try:
        # By default, gather() raises exception on first failure
        results = await asyncio.gather(*tasks)
    except ValueError as e:
        print(f"Error occurred: {e}")


asyncio.run(main_with_errors())
```

**Output:**
```
Error occurred: Document 3 is corrupted!
```

**Problem:** One failure stops everything! Documents 0, 1, 2, 4 didn't get processed.

---

### Using `return_exceptions=True` for Graceful Degradation

```python
async def process_document_safe(doc_id):
    """Process document with possible failures"""
    await asyncio.sleep(1)
    if doc_id == 3:
        raise ValueError(f"Document {doc_id} is corrupted!")
    return f"Processed doc {doc_id}"


async def main_safe():
    tasks = [process_document_safe(i) for i in range(5)]

    # return_exceptions=True: exceptions become results instead of raising
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results, handle exceptions individually
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ Document {i} failed: {result}")
        else:
            print(f"✅ Document {i}: {result}")


asyncio.run(main_safe())
```

**Output:**
```
✅ Document 0: Processed doc 0
✅ Document 1: Processed doc 1
✅ Document 2: Processed doc 2
❌ Document 3 failed: Document 3 is corrupted!
✅ Document 4: Processed doc 4
```

**Perfect!** All documents processed, failures logged individually. This is the pattern for production async code. 🎯

---

### Production-Ready Async Document Processor with Error Handling

```python
# production_async_processor.py

import asyncio
import time
from typing import List, Dict, Union
from dataclasses import dataclass
from async_llm_client import AsyncOpenAIClient
from llm_client import ChatMessage


@dataclass
class ProcessingResult:
    """Result of processing one document"""
    document_name: str
    success: bool
    summary: str = None
    error: str = None
    tokens: int = 0
    cost: float = 0.0


class ProductionAsyncProcessor:
    """Production-grade async document processor with error handling"""

    def __init__(self, provider="openai", model="gpt-3.5-turbo", max_retries=2):
        self.llm = AsyncOpenAIClient(model=model)
        self.max_retries = max_retries

    async def process_one_with_retry(self, document: Dict) -> ProcessingResult:
        """Process single document with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                messages = [
                    ChatMessage(role="system", content="You are a document summarizer."),
                    ChatMessage(role="user", content=f"Summarize:\n{document['text']}")
                ]

                response = await self.llm.chat(messages, temperature=0.3)

                return ProcessingResult(
                    document_name=document["name"],
                    success=True,
                    summary=response.content,
                    tokens=response.tokens_used,
                    cost=response.cost
                )

            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"⚠️  {document['name']} failed (attempt {attempt+1}), retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    # Final failure
                    return ProcessingResult(
                        document_name=document["name"],
                        success=False,
                        error=str(e)
                    )

    async def process_batch(self, documents: List[Dict]) -> Dict:
        """Process batch with comprehensive error handling"""
        start = time.time()

        # Create tasks
        tasks = [self.process_one_with_retry(doc) for doc in documents]

        # Run concurrently with exception handling
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Separate successes and failures
        successes = []
        failures = []

        for result in results:
            if isinstance(result, Exception):
                # Unexpected exception (shouldn't happen with our error handling)
                failures.append(ProcessingResult(
                    document_name="unknown",
                    success=False,
                    error=str(result)
                ))
            elif result.success:
                successes.append(result)
            else:
                failures.append(result)

        elapsed = time.time() - start

        # Summary statistics
        total_cost = sum(r.cost for r in successes)
        total_tokens = sum(r.tokens for r in successes)

        return {
            "total_documents": len(documents),
            "successful": len(successes),
            "failed": len(failures),
            "elapsed_time": elapsed,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "results": successes,
            "errors": failures
        }


# Usage
async def main():
    documents = [
        {"name": f"doc_{i}.pdf", "text": f"Engineering content {i}..."}
        for i in range(50)
    ]

    processor = ProductionAsyncProcessor(max_retries=2)
    summary = await processor.process_batch(documents)

    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successful: {summary['successful']}/{summary['total_documents']}")
    print(f"❌ Failed: {summary['failed']}/{summary['total_documents']}")
    print(f"⏱️  Time: {summary['elapsed_time']:.1f}s")
    print(f"💰 Cost: ${summary['total_cost']:.4f}")
    print(f"🪙 Tokens: {summary['total_tokens']}")

    if summary['errors']:
        print(f"\n❌ Errors:")
        for error in summary['errors']:
            print(f"   - {error.document_name}: {error.error}")


if __name__ == "__main__":
    asyncio.run(main())
```

**Features:**
1. ✅ **Retry logic** with exponential backoff
2. ✅ **Graceful degradation** (`return_exceptions=True`)
3. ✅ **Comprehensive reporting** (successes, failures, costs)
4. ✅ **Production-ready** error handling

---

## Common Mistakes and How to Avoid Them

### Mistake 1: Forgetting `await`

❌ **Wrong:**
```python
async def main():
    result = async_function()  # Forgot await!
    print(result)  # Prints: <coroutine object async_function at 0x...>
```

✅ **Correct:**
```python
async def main():
    result = await async_function()
    print(result)  # Prints actual result
```

---

### Mistake 2: Using `await` Outside Async Function

❌ **Wrong:**
```python
def sync_function():
    result = await async_function()  # SyntaxError!
```

✅ **Correct:**
```python
async def async_function_wrapper():
    result = await async_function()
    return result

# Or from top level:
result = asyncio.run(async_function())
```

---

### Mistake 3: Mixing Sync and Async Incorrectly

❌ **Wrong:**
```python
async def main():
    # Using synchronous sleep in async function - blocks event loop!
    time.sleep(2)  # BAD - blocks everything
```

✅ **Correct:**
```python
async def main():
    # Use async version
    await asyncio.sleep(2)  # GOOD - allows other tasks to run
```

**Rule:** In async functions, always use async versions of I/O operations:
- `await asyncio.sleep()` not `time.sleep()`
- `await client.get()` not `requests.get()`
- `async with open()` not `with open()`

---

## Quick Reference Card

### Basic Syntax

```python
# Define async function
async def my_function():
    await asyncio.sleep(1)
    return "Done"

# Call async function
result = await my_function()  # Inside async function

# Or from top level
result = asyncio.run(my_function())
```

### Concurrent Execution

```python
# Run multiple tasks concurrently
tasks = [async_func1(), async_func2(), async_func3()]
results = await asyncio.gather(*tasks)

# With error handling
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### Common Patterns

```python
# Retry with exponential backoff
for attempt in range(max_retries):
    try:
        return await operation()
    except Exception:
        await asyncio.sleep(2 ** attempt)

# Timeout
try:
    result = await asyncio.wait_for(slow_operation(), timeout=5.0)
except asyncio.TimeoutError:
    print("Operation timed out!")
```

---

## Assessment

### Quick Check Questions

1. **What's the difference between sync and async code execution?**
   <details>
   <summary>Answer</summary>

   - **Synchronous**: Code blocks (waits) during I/O operations. Tasks run one after another.
   - **Asynchronous**: Code releases control during I/O operations, allowing other tasks to run concurrently. Tasks run simultaneously.

   Async is beneficial for I/O-bound tasks (API calls, file I/O), not CPU-bound tasks (calculations).
   </details>

2. **Why can't you use `await` in a regular (non-async) function?**
   <details>
   <summary>Answer</summary>

   `await` can only be used inside `async` functions because it requires the async runtime (event loop) to manage task switching. Regular functions run synchronously and have no concept of yielding control to other tasks.
   </details>

3. **What does `return_exceptions=True` do in `asyncio.gather()`?**
   <details>
   <summary>Answer</summary>

   Instead of raising an exception on the first failure (default behavior), `return_exceptions=True` includes exceptions in the results list. This allows graceful degradation—you can process all tasks and handle failures individually instead of stopping on the first error.
   </details>

---

### Coding Challenge: Concurrent Document Metadata Extractor

**Your mission:** Build an async system that extracts metadata from 100 documents concurrently.

**Requirements:**

1. **Create `async def extract_metadata(document)`**:
   - Simulates API call with `await asyncio.sleep(random.uniform(0.5, 2.0))`
   - Randomly fails 10% of the time (raise `ValueError`)
   - Returns metadata dict on success

2. **Create `async def process_batch_with_stats(documents)`**:
   - Processes all documents concurrently using `asyncio.gather()`
   - Uses `return_exceptions=True` for error handling
   - Implements retry logic (max 2 retries with exponential backoff)
   - Returns summary statistics

3. **Test with 100 documents**

**Hints:**
- Use `random.uniform(0.5, 2.0)` for variable delays
- Use `random.random() < 0.1` for 10% failure rate
- Track start time and calculate elapsed time
- Count successes vs failures

<details>
<summary>💡 <strong>Solution</strong></summary>

```python
import asyncio
import random
import time
from typing import List, Dict


async def extract_metadata(document: Dict, max_retries=2) -> Dict:
    """Extract metadata from document with retry logic"""

    for attempt in range(max_retries + 1):
        try:
            # Simulate API call with variable delay
            delay = random.uniform(0.5, 2.0)
            await asyncio.sleep(delay)

            # Simulate 10% failure rate
            if random.random() < 0.1:
                raise ValueError(f"Failed to process {document['name']}")

            # Success - return metadata
            return {
                "document_name": document["name"],
                "success": True,
                "project": f"Project-{random.randint(1, 10)}",
                "date": "2024-01-15",
                "engineer": f"Engineer-{random.choice(['Smith', 'Chen', 'Garcia'])}"
            }

        except ValueError as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"⚠️  Retry {document['name']} in {wait}s...")
                await asyncio.sleep(wait)
            else:
                # Final failure
                return {
                    "document_name": document["name"],
                    "success": False,
                    "error": str(e)
                }


async def process_batch_with_stats(documents: List[Dict]) -> Dict:
    """Process batch concurrently with statistics"""

    start = time.time()

    # Create tasks
    tasks = [extract_metadata(doc) for doc in documents]

    # Run concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Analyze results
    successes = [r for r in results if isinstance(r, dict) and r.get("success")]
    failures = [r for r in results if isinstance(r, dict) and not r.get("success")]
    unexpected_errors = [r for r in results if isinstance(r, Exception)]

    elapsed = time.time() - start

    return {
        "total": len(documents),
        "successful": len(successes),
        "failed": len(failures) + len(unexpected_errors),
        "elapsed_time": elapsed,
        "results": successes,
        "errors": failures + [{"error": str(e)} for e in unexpected_errors]
    }


async def main():
    # Create 100 test documents
    documents = [
        {"name": f"document_{i:03d}.pdf"}
        for i in range(100)
    ]

    print("Starting concurrent metadata extraction for 100 documents...")

    stats = await process_batch_with_stats(documents)

    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successful: {stats['successful']}/{stats['total']}")
    print(f"❌ Failed: {stats['failed']}/{stats['total']}")
    print(f"⏱️  Time: {stats['elapsed_time']:.1f}s")
    print(f"⚡ Speed: {stats['total'] / stats['elapsed_time']:.1f} docs/second")

    # Show first 5 successes
    print(f"\n📄 Sample successful extractions:")
    for result in stats['results'][:5]:
        print(f"   {result['document_name']}: {result['project']}, {result['engineer']}")


if __name__ == "__main__":
    asyncio.run(main())
```

**Sample Output:**
```
Starting concurrent metadata extraction for 100 documents...
⚠️  Retry document_023.pdf in 1s...
⚠️  Retry document_067.pdf in 1s...

============================================================
BATCH PROCESSING COMPLETE
============================================================
✅ Successful: 94/100
❌ Failed: 6/100
⏱️  Time: 2.8s
⚡ Speed: 35.7 docs/second

📄 Sample successful extractions:
   document_000.pdf: Project-3, Engineer-Chen
   document_001.pdf: Project-7, Engineer-Garcia
   document_002.pdf: Project-5, Engineer-Smith
   document_003.pdf: Project-2, Engineer-Chen
   document_004.pdf: Project-9, Engineer-Garcia
```

**Key takeaway:** 100 documents processed in ~3 seconds instead of ~150 seconds (50x faster!). Async + proper error handling = production-ready system. 🚀
</details>

---

## Verification

Let's verify your async/await understanding with automated tests.

### Test Script

Create this file:

```python
# test_async_await.py
"""
Automated verification script for Chapter 12A
Tests: Async execution, concurrent speedup, error handling, gather behavior
"""

import asyncio
import time
from typing import List


async def simulated_api_call(delay: float, task_id: int) -> str:
    """Simulate an async API call with specified delay"""
    await asyncio.sleep(delay)
    return f"Result from task {task_id}"


async def failing_task(task_id: int) -> str:
    """Simulate a task that fails"""
    await asyncio.sleep(0.1)
    raise ValueError(f"Task {task_id} failed!")


def test_async_function_execution():
    """Test 1: Basic async function execution works"""
    try:
        async def simple_async():
            await asyncio.sleep(0.1)
            return "Success"

        # Run async function
        result = asyncio.run(simple_async())

        assert result == "Success", f"Expected 'Success', got {result}"

        print("✅ PASS: Async function execution works correctly")
        return True

    except Exception as e:
        print(f"❌ FAIL: Async function execution test failed: {e}")
        return False


def test_concurrent_execution_speedup():
    """Test 2: Concurrent execution is faster than sequential"""
    try:
        # Sequential execution
        async def sequential():
            start = time.time()
            results = []
            for i in range(5):
                result = await simulated_api_call(0.2, i)
                results.append(result)
            return time.time() - start, results

        # Concurrent execution
        async def concurrent():
            start = time.time()
            tasks = [simulated_api_call(0.2, i) for i in range(5)]
            results = await asyncio.gather(*tasks)
            return time.time() - start, results

        seq_time, seq_results = asyncio.run(sequential())
        conc_time, conc_results = asyncio.run(concurrent())

        # Verify results are the same
        assert len(seq_results) == len(conc_results), "Should process same number of tasks"

        # Verify concurrent is significantly faster (at least 3x faster)
        speedup = seq_time / conc_time
        assert speedup >= 3.0, \
            f"Concurrent should be at least 3x faster. Got {speedup:.1f}x speedup"

        print(f"✅ PASS: Concurrent execution is faster")
        print(f"   Sequential: {seq_time:.2f}s")
        print(f"   Concurrent: {conc_time:.2f}s")
        print(f"   Speedup: {speedup:.1f}x")
        return True

    except Exception as e:
        print(f"❌ FAIL: Concurrent execution test failed: {e}")
        return False


def test_error_handling_with_gather():
    """Test 3: return_exceptions=True handles failures gracefully"""
    try:
        async def test_with_exceptions():
            tasks = [
                simulated_api_call(0.1, 0),
                failing_task(1),
                simulated_api_call(0.1, 2),
                failing_task(3),
                simulated_api_call(0.1, 4)
            ]

            # With return_exceptions=True
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results

        results = asyncio.run(test_with_exceptions())

        # Verify all tasks completed (5 results total)
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"

        # Count successes and failures
        successes = [r for r in results if isinstance(r, str)]
        failures = [r for r in results if isinstance(r, Exception)]

        assert len(successes) == 3, f"Expected 3 successes, got {len(successes)}"
        assert len(failures) == 2, f"Expected 2 failures, got {len(failures)}"

        # Verify failure messages
        for failure in failures:
            assert "failed" in str(failure).lower(), \
                "Exception should contain 'failed' message"

        print("✅ PASS: Error handling with gather works correctly")
        print(f"   Successes: {len(successes)}")
        print(f"   Failures: {len(failures)}")
        return True

    except Exception as e:
        print(f"❌ FAIL: Error handling test failed: {e}")
        return False


def test_gather_vs_sequential_behavior():
    """Test 4: asyncio.gather() executes tasks concurrently"""
    try:
        async def measure_execution():
            # Create 4 tasks, each taking 0.2 seconds
            tasks = [simulated_api_call(0.2, i) for i in range(4)]

            start = time.time()
            results = await asyncio.gather(*tasks)
            elapsed = time.time() - start

            return elapsed, results

        elapsed, results = asyncio.run(measure_execution())

        # Verify all results returned
        assert len(results) == 4, f"Expected 4 results, got {len(results)}"

        # Verify concurrent execution (total time should be ~0.2s, not 0.8s)
        # Allow some overhead, so check if < 0.5s
        assert elapsed < 0.5, \
            f"Expected ~0.2s (concurrent), got {elapsed:.2f}s (seems sequential)"

        print("✅ PASS: asyncio.gather() executes concurrently")
        print(f"   4 tasks (0.2s each) completed in {elapsed:.2f}s")
        return True

    except Exception as e:
        print(f"❌ FAIL: Gather behavior test failed: {e}")
        return False


def run_all_tests():
    """Run all verification tests"""
    print("="*60)
    print("Chapter 12A Verification Tests")
    print("="*60)

    tests = [
        ("Async Function Execution", test_async_function_execution),
        ("Concurrent Execution Speedup", test_concurrent_execution_speedup),
        ("Error Handling with Gather", test_error_handling_with_gather),
        ("Gather Concurrent Behavior", test_gather_vs_sequential_behavior)
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
        print("\n🎉 ALL TESTS PASSED! You understand async/await!")
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
python test_async_await.py
```

### Expected output:

```
============================================================
Chapter 12A Verification Tests
============================================================

[Test] Async Function Execution
✅ PASS: Async function execution works correctly

[Test] Concurrent Execution Speedup
✅ PASS: Concurrent execution is faster
   Sequential: 1.01s
   Concurrent: 0.21s
   Speedup: 4.8x

[Test] Error Handling with Gather
✅ PASS: Error handling with gather works correctly
   Successes: 3
   Failures: 2

[Test] Gather Concurrent Behavior
✅ PASS: asyncio.gather() executes concurrently
   4 tasks (0.2s each) completed in 0.20s

============================================================
Results: 4/4 tests passed
============================================================

🎉 ALL TESTS PASSED! You understand async/await!
```

---

## What's Next?

Congratulations! You've mastered async/await for concurrent LLM API calls. This is a game-changer for building scalable AI applications! 🎉

**In the next chapter (Chapter 12B: Type Hints & Type Checking)**, you'll learn:
- Type hints syntax (`str`, `List[str]`, `Dict[str, Any]`)
- Optional and Union types
- Generic types for reusable functions
- Using `mypy` for static type checking
- TypedDict for structured dictionaries
- Protocols for duck typing

**But first, take a break!** You've learned a lot:
- Sync vs async execution models
- `async`/`await` syntax
- `asyncio.gather()` for concurrency
- Error handling with `return_exceptions=True`
- Retry logic with exponential backoff
- Production-ready async document processing

**Your async toolchain:**

```
Async Foundations ← YOU ARE HERE
├── async/await syntax
├── Concurrent LLM API calls
├── asyncio.gather() for parallel execution
└── Production error handling with retries

Next: Type Hints & Type Checking (Ch 12B)
Then: Structured Output with Pydantic (Ch 11)
Then: RAG Systems (Ch 13-17)
```

You're building production-grade AI systems! 🏗️

---

## Summary

**What you learned:**

1. ✅ **Sync vs Async** — Blocking vs non-blocking execution
2. ✅ **async/await syntax** — Defining and calling async functions
3. ✅ **asyncio.gather()** — Running multiple tasks concurrently
4. ✅ **Error handling** — `return_exceptions=True` for graceful degradation
5. ✅ **Retry logic** — Exponential backoff for transient failures
6. ✅ **Async LLM clients** — Converting sync to async API calls
7. ✅ **Batch processing** — Processing 100s of documents in seconds

**Key takeaway:** Async/await transforms I/O-bound operations from sequential bottlenecks into concurrent powerhouses. For LLM applications, this means 10-50x speedups with minimal code changes. Master async, and you'll build systems that scale! ⚡

**You got this!** 💪 Take a break, then let's add type safety with type hints in Chapter 12B! 🚀
