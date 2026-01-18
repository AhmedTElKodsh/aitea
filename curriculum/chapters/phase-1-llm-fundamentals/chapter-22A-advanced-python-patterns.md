# Chapter 22A: Advanced Python Patterns — Building Architectural Muscle 🏛️

<!--
METADATA
Phase: Python Bridge Module 3 (PBM-3)
Time: 2.5 hours (60 minutes reading + 90 minutes hands-on)
Difficulty: ⭐⭐⭐
Type: Concept / Implementation
Prerequisites: Chapter 6C (OOP), Chapter 8 (Multi-Provider Client), Chapter 12B (Type Hints)
Builds Toward: Chapter 31 (LangGraph), Chapter 43 (Multi-Agent Systems)
Correctness Properties: [P5, P9, P12]

NAVIGATION
→ Quick Reference: #quick-reference
→ Verification: #verification
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

Imagine you're building a custom home. 🏠 

In the beginning, you just needed a roof and some walls. But as you add more rooms—a kitchen, a home theater, a smart security system—things get complicated. If you wired the security system directly into the kitchen lights, and then decided to move the kitchen, everything would break. 💥

**Software is exactly the same.** When we started with simple LLM calls, we could put everything in one file. But as we build the **Civil Engineering Document System**, we'll have dozens of prompts, multiple LLM providers, and complex workflows.

**By the end of this chapter**, you'll stop writing "just code" and start writing **Architecture**. You'll learn the patterns that the pros use to build systems that don't crumble when you add new features.

Ready to become a software architect? Let's go! 🚀

---

## Prerequisites Check

Let's make sure your foundations are solid:

```bash
# You should be able to run mypy without errors on your current projects
mypy examples/mastery-check-project-pulse/src/main.py
```

**If this prints "Success"**, you're ready! ✅

**You should feel comfortable with**:
- **Abstract Base Classes** (Chapter 6C)
- **Type Hints & Protocols** (Chapter 12B)
- **Async/Await** (Chapter 12A)

*Don't worry if Design Patterns sound "scary" — they're actually just names for solutions to common problems we've already started solving!* 😊

---

## What You Already Know 🧩

Think of this chapter as the "Senior Engineer" upgrade to your existing skills:

<table>
<tr>
<th>Concept You Know</th>
<th>How We'll Level It Up</th>
</tr>
<tr>
<td>Inheritance (ABC)</td>
<td>**Dependency Inversion** (Coding to interfaces, not details)</td>
</tr>
<tr>
<td>`if/else` for LLMs</td>
<td>**Factory Pattern** (Standardizing object creation)</td>
</tr>
<tr>
<td>Switching Prompt logic</td>
<td>**Strategy Pattern** (Swapping algorithms at runtime)</td>
</tr>
</table>

### 🔮 Where This Leads

You'll use these patterns extensively in:
- **Chapter 31 (LangGraph)**: Managing complex state transitions.
- **Chapter 43 (Multi-Agent)**: Building flexible teams of agents that can swap roles.
- **Final Project**: Making the CE System easy to maintain as building codes change.

---

## The Story: Why Patterns Matter

### The Problem (The "Spaghetti" Nightmare) 🍝

Ahmed is expanding his Civil Engineering tool. He now has:
1. `StructuralAnalyzer` (OpenAI)
2. `ContractReviewer` (Anthropic)
3. `CostEstimator` (Llama 3)

His code looks like this:

```python
# 😫 START OF PAINFUL CODE
class CE_System:
    def process(self, doc_type, text):
        if doc_type == "structural":
            client = OpenAI(api_key=...)
            # 50 lines of OpenAI specific logic
        elif doc_type == "contract":
            client = Anthropic(api_key=...)
            # 50 lines of Anthropic specific logic
        # ... this goes on forever
# 😫 END OF PAINFUL CODE
```

**The Pain:**
- ❌ **Rigid**: Adding a new provider requires changing the core `CE_System` class.
- ❌ **Fragile**: A change in OpenAI's SDK might break the logic for Contracts.
- ❌ **Untestable**: You can't easily swap the "Real LLM" for a "Mock LLM" during tests.

### The Elegant Solution (The "Plug-and-Play" Architecture) 🔌

With Design Patterns, Ahmed's system becomes a set of **Interchangeable Parts**.

```python
# ✨ BEAUTIFUL CODE
system = CESystem(
    llm_factory=ProviderFactory(),
    strategy=SummaryStrategy()
)
result = await system.run(document)
```

**Why this is magic:**
- ✅ **Flexible**: You can add "Gemini" support without touching the `CESystem` logic.
- ✅ **Clean**: Each class does exactly ONE thing (Single Responsibility).
- ✅ **Testable**: You can "Inject" a Mock provider effortlessly.

---

## Part 1: SOLID Principles (The Golden Rules)

Before we get to patterns, we need the "constitution" of good code: **SOLID**. We'll focus on the two most important ones for AI Engineering.

### 1. SRP: Single Responsibility Principle

**Analogy: The Swiss Army Knife vs. A Chef's Knife** 🔪

A Swiss Army knife does everything poorly. A Chef's knife does one thing perfectly. In code, a class should have **one reason to change**.

**❌ BAD**: A class that reads a PDF, calls OpenAI, AND saves to a database.
**✅ GOOD**: Three separate classes: `PDFLoader`, `LLMClient`, `DatabaseStorer`.


### 2. DIP: Dependency Inversion Principle

This is the big one! **High-level modules should not depend on low-level modules. Both should depend on abstractions.**

**Analogy: The Wall Outlet** 🔌
Your toaster doesn't care if the electricity comes from Solar, Coal, or Wind. It just care that the plug fits the outlet. The **Outlet is the Abstraction**.


### 🔬 Try This! (Hands-On Practice #1)

**Challenge**: Look at this code. How many "responsibilities" does it have?

```python
class DocumentManager:
    def process_and_save(self, path: str):
        # 1. Read file
        with open(path, 'r') as f:
            text = f.read()
        
        # 2. Call AI
        # (Imagine OpenAI code here)
        summary = "AI Summary"
        
        # 3. Print report
        print(f"REPORT: {summary}")
```

<details>
<summary>✅ Solution</summary>

It has **3 responsibilities**:
1. File I/O (Reading)
2. AI Logic (Processing)
3. UI/Output (Printing)

**How to fix it?** Break it into a `Reader` class, a `Processor` class, and a `Reporter` class.
</details>

---

## Part 2: The Factory Pattern (The Object Generator) 🏭

### What is a Factory?

Sometimes, you don't know which class you need until the program is actually running.

**Analogy: The Pizza Oven** 🍕
You don't build a new oven for every pizza. You tell the Oven (the Factory) "I want Pepperoni" or "I want Veggie," and it gives you the right pizza.

**In AI terms**: You tell the Factory "I want OpenAI" or "I want Anthropic," and it gives you a client that follows the same interface.

### Implementing a Factory

```python
from abc import ABC, abstractmethod

# 1. The Interface (The "Outlet")
class LLMClient(ABC):
    @abstractmethod
    async def chat(self, prompt: str) -> str:
        pass

# 2. The Concrete Products
class OpenAIClient(LLMClient):
    async def chat(self, prompt: str) -> str:
        return "OpenAI says: " + prompt

class AnthropicClient(LLMClient):
    async def chat(self, prompt: str) -> str:
        return "Anthropic says: " + prompt

# 3. The Factory (The "Pizza Oven")
class LLMFactory:
    @staticmethod
    def get_client(provider_name: str) -> LLMClient:
        if provider_name == "openai":
            return OpenAIClient()
        elif provider_name == "anthropic":
            return AnthropicClient()
        raise ValueError(f"Unknown provider: {provider_name}")
```

---

### 🔬 Try This! (Hands-On Practice #2)

**Challenge**: Extend the `LLMFactory` to support a `MockClient` for testing.

**Starter code**:
```python
class MockClient(LLMClient):
    async def chat(self, prompt: str) -> str:
        return "MOCK: I heard you!"

# Update LLMFactory.get_client to handle "mock"
```

<details>
<summary>✅ Solution</summary>

```python
class LLMFactory:
    @staticmethod
    def get_client(provider_name: str) -> LLMClient:
        providers = {
            "openai": OpenAIClient,
            "anthropic": AnthropicClient,
            "mock": MockClient
        }
        
        client_class = providers.get(provider_name.lower())
        if client_class:
            return client_class()
        raise ValueError(f"Unknown: {provider_name}")
```
</details>

---

## Part 3: The Strategy Pattern (The Swap-a-Brain) 🧠

### What is the Strategy Pattern?

The Strategy pattern lets you swap out the **Logic** or **Algorithm** inside an object without changing the object itself.

**Analogy: Navigation Apps** 🗺️
The Google Maps "Core" stays the same, but you can swap your **Strategy**:
- "Avoid Highways" Strategy
- "Fastest Route" Strategy
- "Walking" Strategy

**In AI terms**:
- "Summarization" Strategy (one prompt)
- "Extraction" Strategy (another prompt)
- "Critique" Strategy (a third prompt)

### Implementing Strategy

```python
from typing import Protocol

# 1. The Strategy Protocol (Ch 12B skill!)
class ProcessingStrategy(Protocol):
    def get_prompt(self, text: str) -> str:
        ...

# 2. Concrete Strategies
class SummaryStrategy:
    def get_prompt(self, text: str) -> str:
        return f"Summarize this: {text}"

class CritiqueStrategy:
    def get_prompt(self, text: str) -> str:
        return f"Critique the logic in this: {text}"

# 3. The Context (The Navigation App)
class DocumentProcessor:
    def __init__(self, strategy: ProcessingStrategy):
        self.strategy = strategy

    async def process(self, client: LLMClient, text: str):
        prompt = self.strategy.get_prompt(text)
        return await client.chat(prompt)

# Usage:
# summarizer = DocumentProcessor(SummaryStrategy())
# await summarizer.process(openai_client, "The sky is blue.")
```

---

### 🔬 Try This! (Hands-On Practice #3)

**Challenge**: Create a `PirateStrategy` that translates any text into pirate-speak. Apply it to the `DocumentProcessor`.

<details>
<summary>✅ Solution</summary>

```python
class PirateStrategy:
    def get_prompt(self, text: str) -> str:
        return f"Translate this into pirate-speak: {text}. Arrr!"

# Usage
# pirate_bot = DocumentProcessor(PirateStrategy())
# print(await pirate_bot.process(mock_client, "I would like a coffee."))
```
</details>

---

## Bringing It All Together: The "Architect" Version of ProjectPulse

Let's refactor our `ProjectPulse` tool using everything we learned today. We'll use a **Factory** for providers and a **Strategy** for different report types (Executive vs. Technical).

---

### Step 1: Define the Interfaces (`src/interfaces.py`)

```python
from typing import Protocol, List
from pydantic import BaseModel

class LLMClient(Protocol):
    async def generate(self, prompt: str) -> str: ...

class ReportStrategy(Protocol):
    def format_report(self, data: List[dict]) -> str: ...
```

### Step 2: Implement the Factory & Logic (`src/core.py`)

```python
class ProviderFactory:
    @staticmethod
    def create(provider: str) -> LLMClient:
        # Returns OpenAI, Anthropic, or Mock based on input
        ...

class TechnicalStrategy:
    def format_report(self, data):
        return "## TECHNICAL LOG\n" + str(data)

class PulseOrchestrator:
    def __init__(self, client: LLMClient, strategy: ReportStrategy):
        self.client = client
        self.strategy = strategy

    async def run(self, logs: List[str]):
        # 1. Process logs using self.client
        # 2. Format using self.strategy
        pass
```

---

## Common Mistakes (Learn from Others!)

### Mistake #1: Over-Engineering 🏗️
Don't use a Factory if you only have ONE provider and it will never change.
**Rule**: Use patterns only when you have **at least two** versions of something or high probability of future expansion.

### Mistake #2: Forgetting Type Hints
If you use the Factory pattern but don't type hint the return as the `Interface`, your IDE won't help you!
❌ `client = Factory.get("openai")`
✅ `client: LLMClient = Factory.get("openai")`

---

## Quick Reference Card

### Factory Template
```python
def factory(type: str) -> Interface:
    mapping = {"a": ConcreteA, "b": ConcreteB}
    return mapping[type]()
```

### Strategy Template
```python
class Strategy(Protocol):
    def execute(self, data): ...

class Context:
    def __init__(self, strat: Strategy):
        self.strat = strat
```

---

## Assessment

**1. What does the "D" in SOLID stand for?**
a) Data Integrity
b) Dependency Inversion
c) Document Induction

**2. When should you use the Factory pattern?**
a) When you want to hide the complexity of creating an object.
b) When you want to make your code run faster.
c) When you want to use global variables.

**3. What is the main difference between Strategy and Inheritance?**
a) Strategy is slower.
b) Strategy allows you to swap behavior at **runtime**, inheritance is fixed at **coding time**.

<details>
<summary>💡 Answers</summary>
1. b
2. a
3. b
</details>

---

## What's Next?

You've built the **Structure** of a professional system. But even a well-built house can be slow. 

In **Chapter 22B: Performance Optimization**, you'll learn how to make your Python code scream by using **Caching, Profiling, and Generator efficiency**.

Then, in **22C**, we'll learn how to **Test** these patterns so they never break.

Ready to optimize? Let's go! 🚀
