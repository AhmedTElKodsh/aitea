# Chapter 22B: Performance Optimization — Making Your AI Scream ⚡

<!--
METADATA
Phase: Python Bridge Module 3 (PBM-3)
Time: 2 hours (45 minutes reading + 75 minutes hands-on)
Difficulty: ⭐⭐⭐
Type: Concept / Implementation
Prerequisites: Chapter 12A (Async), Chapter 22A (Patterns)
Builds Toward: Chapter 13 (Embeddings), Chapter 54 (Final Project)
Correctness Properties: [P10, P15]

NAVIGATION
→ Quick Reference: #quick-reference
→ Verification: #verification
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

Imagine your coffee shop is a hit! ☕✨ 

But there's a problem: every time a customer orders a "Latte," the barista goes to the back, grinds one bean, boils one cup of water, and then comes back. Then they do it again for the next person. The line is out the door, and people are leaving.

**This is what slow code feels like.** 😫

In AI engineering, performance isn't just a "nice to have." If your system takes 30 seconds to summarize a document that a human could read in 60, nobody will use it. We need to find the bottlenecks, cache the answers, and stream the results.

**By the end of this chapter**, you'll know how to:
- Find exactly where your code is slow (Stop guessing!).
- Store answers so you never pay for the same LLM call twice.
- Handle massive files without crashing your computer.
- Control the "speed limit" of your API calls to avoid being banned.

Let's make your code production-fast! 🚀

---

## Prerequisites Check

Let's check your toolkit:

```bash
# We'll use a built-in tool called cProfile
python -m cProfile --version
```

**You should feel comfortable with**:
- **Async/Await** (Chapter 12A): This is already our biggest speed booster!
- **Decorators** (Chapter 6A): We'll use these for caching.

*Speed isn't about writing "clever" code; it's about writing "smart" architecture.* 😊

---

## What You Already Know 🧩

Performance is about managing resources:

<table>
<tr>
<th>Resource</th>
<th>How We Manage It Now</th>
<th>How We'll Optimize It</th>
</tr>
<tr>
<td>**Time**</td>
<td>Async (Wait in parallel)</td>
<td>**Caching** (Don't wait at all)</td>
</tr>
<tr>
<td>**Memory**</td>
<td>Lists (Load everything)</td>
<td>**Generators** (Process piece by piece)</td>
</tr>
<tr>
<td>**CPU**</td>
<td>Single Process</td>
<td>**Profiling** (Find the bottleneck)</td>
</tr>
</table>

---

## Part 1: Profiling (Find the "Wait") 🔍

Before you can fix the speed, you have to know what's slow.

**Analogy: The Leak in the Pipe** 🚰
If your water bill is high, you don't replace every pipe in the house. You find the leak. Profiling is the "leak detector" for your code.

### Using `cProfile`

Python has a built-in tool called `cProfile` that counts every function call and how long it took.

```bash
# Run your script through the profiler
python -m cProfile -s cumulative my_script.py
```

- `-s cumulative`: Sorts by the functions that took the most total time.

### 🔬 Try This! (Hands-On Practice #1)

**Challenge**: Run the profiler on our `ProjectPulse` tool.

```bash
python -m cProfile -s cumulative examples/mastery-check-project-pulse/src/main.py
```

**Look for**:
1. How much time was spent in `asyncio.run`?
2. How much time was spent in `MockLLMClient.generate`?
3. Is there any function taking a lot of time that *isn't* a network call?

---

## Part 2: Caching (The "Don't Repeat Yourself" Rule) 💾

LLM calls are **expensive** and **slow**. If you ask the same question twice, you shouldn't call the API twice.

**Analogy: The Cheat Sheet** 📝
If a teacher asks you "What is 15 x 15?" you might calculate it once (225). If they ask again 5 minutes later, you don't calculate it—you just remember it. That's caching.

### Using `@lru_cache`

Python's `functools` provides a decorator that does this automatically for sync functions.

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_calculation(n):
    print(f"Calculating for {n}...")
    return n * n

print(expensive_calculation(5)) # Prints "Calculating..." and 25
print(expensive_calculation(5)) # Just prints 25 (Instant!)
```

### Caching Async LLM Calls

Since LLM calls are async, we need a slightly different approach. 

```python
# Simple Async Cache (A Dictionary-based approach)
class CachedLLM:
    def __init__(self, real_client):
        self.client = real_client
        self.cache = {}

    async def generate(self, prompt: str) -> str:
        if prompt in self.cache:
            print("🎯 Cache Hit!")
            return self.cache[prompt]
        
        print("🌐 Calling API...")
        result = await self.client.generate(prompt)
        self.cache[prompt] = result
        return result
```

---


### 🔬 Try This! (Hands-On Practice #2)

**Challenge**: Wrap the `MockLLMClient` from Chapter 22A in a `CachedLLM` wrapper. Verify that the second call to the same prompt is instant (no `asyncio.sleep`).

<details>
<summary>✅ Solution</summary>

```python
# usage
real_client = MockLLMClient()
cached = CachedLLM(real_client)

await cached.generate("Hi") # Takes 0.5s
await cached.generate("Hi") # Takes 0.0s!
```
</details>

---

## Part 3: Generators (Memory Management) 🧠

When building the Civil Engineering system, we might process **thousands** of logs. If you load them all into a list at once, your program will crash.

**Analogy: The Buffet vs. The Conveyor Belt** 🍣
A buffet (List) puts all the food out at once. If the buffet is too big, the table breaks. A conveyor belt (Generator) brings you one piece of sushi at a time. The table never breaks!

### Using Generators

```python
# ❌ List Approach (Memory Heavy)
def get_all_logs(path):
    with open(path) as f:
        return f.readlines() # Loads EVERYTHING into RAM

# ✅ Generator Approach (Memory Efficient)
def stream_logs(path):
    with open(path) as f:
        for line in f:
            yield line # Yields ONE line at a time
```

---


### 🔬 Try This! (Hands-On Practice #3)

**Challenge**: Convert the log-reading logic in `ProjectPulse` to use a generator.

<details>
<summary>✅ Solution</summary>

```python
def log_generator(filepath: str):
    with open(filepath, 'r') as f:
        current_chunk = []
        for line in f:
            if line.strip() == "": # Split by double newline
                yield "\n".join(current_chunk)
                current_chunk = []
            else:
                current_chunk.append(line.strip())
        if current_chunk:
            yield "\n".join(current_chunk)
```
</details>

---

## Part 4: Semaphores (The Speed Limit) 🚦

If you send 100 API calls at once using `asyncio.gather`, the provider might block you (Rate Limiting).

**Analogy: The Bouncer** 🕺
A club has a maximum capacity. The Bouncer (Semaphore) only lets 5 people in at a time. As one person leaves, another can enter.

### Using `asyncio.Semaphore`

```python
import asyncio

async def call_ai(semaphore, i):
    async with semaphore: # Only N tasks can enter this block
        print(f"Task {i} running...")
        await asyncio.sleep(1)
        print(f"Task {i} done.")

async def main():
    sem = asyncio.Semaphore(3) # Max 3 at a time
    tasks = [call_ai(sem, i) for i in range(10)]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

---

## Bringing It All Together: The High-Performance Pulse

Let's update our mastery project with these optimizations.

```python
# src/optimized_pulse.py
import asyncio
from functools import lru_cache

class OptimizedOrchestrator:
    def __init__(self, client, limit=5):
        self.client = client
        self.sem = asyncio.Semaphore(limit)
        self.cache = {}

    async def process_one(self, chunk):
        # 1. Check Cache
        if chunk in self.cache:
            return self.cache[chunk]

        # 2. Respect Speed Limit
        async with self.sem:
            result = await self.client.generate(chunk)
            self.cache[chunk] = result
            return result

    async def run(self, log_generator):
        tasks = [self.process_one(chunk) for chunk in log_generator]
        return await asyncio.gather(*tasks)
```

---

## Common Mistakes 🚫

### Mistake #1: Premature Optimization
Don't optimize code that isn't slow. Use **Profiling** first. If the network call takes 2000ms and your logic takes 2ms, don't waste time optimizing the logic!

### Mistake #2: Caching Memory Leaks
If you cache everything and never clear it, your program will eventually run out of memory.
**Fix**: Use `maxsize` in `lru_cache` or a time-based expiration.

---

## Quick Reference Card 🃏

| Tool | Purpose | Syntax | 
|------|---------|--------|
| **cProfile** | Find slow functions | `python -m cProfile -s cumulative` | 
| **lru_cache** | Sync Caching | `@lru_cache(maxsize=128)` | 
| **yield** | Generators | `yield value` | 
| **Semaphore** | Rate Limiting | `async with asyncio.Semaphore(n):` | 

---

## Assessment

**1. What does "Cumulative Time" mean in a profiler report?**
a) How many times the function was called.
b) The total time spent in that function AND all the functions it called.
c) The time spent only inside that specific function.

**2. Why use a Generator instead of a List for 1GB of text?**
a) It makes the CPU faster.
b) It prevents a MemoryError by only loading what's needed.
c) It's required by the OpenAI API.

**3. What happens if you run 1000 tasks with a Semaphore of 5?**
a) Only 5 tasks will ever run.
b) 5 tasks run concurrently; as each finishes, a new one starts until all 1000 are done.
c) The program crashes.

<details>
<summary>💡 Answers</summary>
1. b
2. b
3. b
</details>

---

## What's Next?

You now have code that is **Clean** (Patterns) and **Fast** (Optimization). But is it **Correct**?

In **Chapter 22C: Testing Patterns**, we'll learn how to write tests that catch bugs automatically. We'll even learn how to "mock" the passage of time so we don't have to wait for real API calls during tests.

After that... we finally start **Milestone 3: RAG Fundamentals**! 🧠🚀

