# Chapter 12B: Type Hints & Type Checking — Building Type-Safe AI Systems

<!--
METADATA
Phase: Phase 1: LLM Fundamentals
Time: 1.5 hours (45 minutes reading + 45 minutes hands-on)
Difficulty: ⭐⭐
Type: Foundation / Implementation
Prerequisites: Chapter 8 (Multi-Provider Client), Chapter 12A (Async/Await), Chapter 3 (Pydantic)
Builds Toward: Chapter 11 (Structured Output), Chapter 17 (RAG System), Chapter 54 (Complete System)
Correctness Properties: [P13: Type Safety, P14: Static Analysis, P15: Interface Compliance]
Project Thread: TypeSafeDocumentSystem - connects to Ch 11, 17, 54

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification
→ What's Next: #whats-next

TEMPLATE VERSION: v2.1 (2026-01-17)
-->

---

## ☕ Coffee Shop Intro

Imagine you're building a document processor. Your colleague writes this function:

```python
def process_document(doc):
    return doc.process()
```

**You call it like this:**
```python
result = process_document("report.pdf")  # Crashes! Strings don't have .process()
```

😰 **The error only appears at runtime.** By then, it might be in production with angry users.

**With type hints:**

```python
def process_document(doc: DocumentProcessor) -> ProcessingResult:
    return doc.process()

# Your IDE immediately shows error:
result = process_document("report.pdf")  # ❌ Type error: Expected DocumentProcessor, got str
```

**The error is caught BEFORE you even run the code!** 🎯

**By the end of this chapter, you'll write type-safe code like this:**

```python
from typing import List, Dict, Optional, Union
from dataclasses import dataclass

@dataclass
class DocumentMetadata:
    project: str
    date: str
    engineer: str
    tags: List[str]
    custom_fields: Optional[Dict[str, str]] = None

async def process_batch(
    documents: List[DocumentProcessor],
    llm: BaseLLMClient,
    config: ProcessingConfig
) -> Tuple[List[ProcessingResult], List[ProcessingError]]:
    """Type hints make intent crystal clear!"""
    ...
```

Let's learn type hints and build bulletproof AI systems! 🚀

---

## Prerequisites Check

Before we proceed, make sure you're comfortable with:

✅ **Basic Python types**:
```python
name: str = "Ahmed"
age: int = 25
scores: list = [1, 2, 3]
```

✅ **Functions with parameters**:
```python
def greet(name, age):
    return f"Hello {name}, you are {age}"
```

✅ **Pydantic models** (Chapter 3):
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
```

✅ **Classes and inheritance** (Chapter 6C):
```python
class Child(Parent):
    pass
```

If any of these feel shaky, take 5 minutes to review! 🧩

---

## What You Already Know 🧩

You've been using type hints already without realizing it:

**In Pydantic models (Chapter 3):**
```python
from pydantic import BaseModel

class Document(BaseModel):
    title: str  # ← Type hint!
    pages: int  # ← Type hint!
```

**In function signatures:**
```python
def calculate_area(width: float, height: float) -> float:
    #                     ↑ type hints ↑        ↑ return type
    return width * height
```

**In your IDE:**
```python
# Your IDE already uses type hints for autocomplete:
text = "hello"
text.upper()  # IDE knows .upper() exists because text: str
#    ↑ autocomplete works!
```

You've been benefiting from type hints constantly. Now you'll learn to write them systematically! 💡

---

## The Story: Why Type Hints Matter

### The Problem

Ahmed's document processor has grown complex. Multiple developers contribute code:

```python
# developer1.py
def process_document(doc):
    """Process a document"""
    summary = summarize(doc)
    return {"summary": summary, "status": "complete"}

# developer2.py
def batch_process(documents, provider):
    """Process multiple documents"""
    results = []
    for doc in documents:
        result = process_document(doc)
        results.append(result)
    return results

# developer3.py (new junior dev)
# They call it wrong:
result = batch_process("report.pdf", "openai")  # CRASHES!
# Expected: list of DocumentProcessor objects
# Got: string!
```

😰 **Problems:**
1. **No documentation** — What types do functions expect?
2. **Runtime errors** — Bugs only discovered when code runs
3. **No IDE support** — No autocomplete, no warnings
4. **Hard to refactor** — Change one function, break 10 others
5. **Difficult onboarding** — New developers guess parameter types

### The Elegant Solution: Type Hints Everywhere

```python
from typing import List, Dict
from llm_client import BaseLLMClient
from document_processor import DocumentProcessor

def process_document(doc: DocumentProcessor) -> Dict[str, str]:
    """
    Process a single document.

    Args:
        doc: DocumentProcessor instance to process

    Returns:
        Dictionary with 'summary' and 'status' keys
    """
    summary = summarize(doc)
    return {"summary": summary, "status": "complete"}

def batch_process(
    documents: List[DocumentProcessor],
    provider: BaseLLMClient
) -> List[Dict[str, str]]:
    """
    Process multiple documents with specified LLM provider.

    Args:
        documents: List of DocumentProcessor instances
        provider: LLM client instance (OpenAI, Anthropic, etc.)

    Returns:
        List of result dictionaries
    """
    results = []
    for doc in documents:
        result = process_document(doc)
        results.append(result)
    return results

# Now when junior dev makes mistake:
result = batch_process("report.pdf", "openai")
# ❌ IDE shows error IMMEDIATELY:
# "Expected List[DocumentProcessor], got str"
```

**🎉 Benefits:**
1. **Self-documenting code** — Types explain what functions expect
2. **Catch errors early** — Before running code
3. **Better IDE support** — Autocomplete, refactoring, navigation
4. **Safer refactoring** — Type checker catches breaking changes
5. **Easier collaboration** — Clear contracts between functions

This is why type hints are essential for production systems! Let's learn them systematically. 🚀

---

## Part 1: Basic Type Hints

### Variable Type Hints

```python
# Basic types
name: str = "Ahmed"
age: int = 25
height: float = 1.75
is_engineer: bool = True

# Collections
numbers: list = [1, 2, 3]  # Any list
scores: dict = {"math": 95}  # Any dict
tags: set = {"python", "ai"}  # Any set
position: tuple = (10, 20)  # Any tuple
```

**Note:** These are the Python 3.9+ style. For older Python, use `from typing import List, Dict, etc.`

---

### Function Type Hints

```python
def greet(name: str, age: int) -> str:
    """
    Greet a person.

    Args:
        name: Person's name
        age: Person's age

    Returns:
        Greeting message
    """
    return f"Hello {name}, you are {age} years old"

# Call it
message = greet("Ahmed", 25)  # ✅ Correct
message = greet(25, "Ahmed")  # ❌ IDE warns: Arguments swapped!
```

**Syntax:**
- Parameters: `parameter_name: Type`
- Return type: `-> ReturnType`
- No return value: `-> None`

---

### Multiple Return Values (Tuples)

```python
from typing import Tuple

def get_dimensions() -> Tuple[int, int]:
    """Return width and height"""
    return 1920, 1080

width, height = get_dimensions()
```

**For Python 3.9+, use lowercase:**
```python
def get_dimensions() -> tuple[int, int]:
    return 1920, 1080
```

---

## Part 2: Generic Types from `typing` Module

### List, Dict, Set with Specific Types

```python
from typing import List, Dict, Set, Tuple

# List of specific type
def process_names(names: List[str]) -> List[str]:
    return [name.upper() for name in names]

# Dictionary with specific key/value types
def count_words(text: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1
    return counts

# Set of specific type
def get_unique_tags(documents: List[dict]) -> Set[str]:
    tags: Set[str] = set()
    for doc in documents:
        tags.update(doc.get("tags", []))
    return tags

# Tuple with specific types at each position
def parse_coordinates(text: str) -> Tuple[float, float, float]:
    """Return (x, y, z) coordinates"""
    x, y, z = map(float, text.split(","))
    return x, y, z
```

**Python 3.9+ shorthand:**
```python
def process_names(names: list[str]) -> list[str]:
    return [name.upper() for name in names]

def count_words(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    # ...
    return counts
```

---

### Optional — May Be None

```python
from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    """
    Find user by ID.

    Returns:
        Username if found, None if not found
    """
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)  # Returns str or None

# Usage
username = find_user(1)
if username is not None:
    print(f"Found: {username}")
else:
    print("User not found")
```

**`Optional[X]` is shorthand for `Union[X, None]`:**
```python
# These are equivalent:
def func() -> Optional[str]: ...
def func() -> Union[str, None]: ...
def func() -> str | None: ...  # Python 3.10+
```

---

### Union — One of Several Types

```python
from typing import Union

def process_input(value: Union[str, int, float]) -> str:
    """Accept string, int, or float"""
    return str(value)

# Python 3.10+ syntax (preferred):
def process_input(value: str | int | float) -> str:
    return str(value)
```

---

### Any — Disable Type Checking

```python
from typing import Any

def flexible_function(data: Any) -> Any:
    """Accept anything, return anything"""
    return data  # Type checker won't complain
```

**⚠️ Use sparingly!** `Any` defeats the purpose of type hints. Only use when absolutely necessary.

---

## Part 3: Advanced Type Hints for LLM Applications

### TypedDict — Structured Dictionaries

**Problem:** Plain `dict` doesn't specify structure:
```python
def process_metadata(meta: dict) -> None:
    # What keys does meta have? What are their types?
    pass
```

**Solution: TypedDict**
```python
from typing import TypedDict, List

class DocumentMetadata(TypedDict):
    """Structured metadata dictionary"""
    project: str
    date: str
    engineer: str
    tags: List[str]
    page_count: int

def process_metadata(meta: DocumentMetadata) -> str:
    """Now we know exact structure!"""
    return f"Project: {meta['project']}, Engineer: {meta['engineer']}"

# Usage
metadata: DocumentMetadata = {
    "project": "Bridge Analysis",
    "date": "2024-01-15",
    "engineer": "Sarah Chen",
    "tags": ["structural", "bridge"],
    "page_count": 50
}

process_metadata(metadata)  # ✅ Type safe!
```

**Optional fields:**
```python
from typing import TypedDict, NotRequired

class DocumentMetadata(TypedDict):
    project: str  # Required
    date: str  # Required
    engineer: str  # Required
    tags: NotRequired[List[str]]  # Optional
    notes: NotRequired[str]  # Optional
```

---

### Literal — Specific Values Only

```python
from typing import Literal

def set_log_level(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]) -> None:
    """Only accept these specific strings"""
    print(f"Log level set to {level}")

set_log_level("INFO")  # ✅ OK
set_log_level("TRACE")  # ❌ IDE error: Not a valid literal value
```

**Perfect for provider names:**
```python
from typing import Literal

LLMProvider = Literal["openai", "anthropic", "google"]

def create_client(provider: LLMProvider) -> BaseLLMClient:
    """Type-safe provider selection"""
    if provider == "openai":
        return OpenAIClient()
    elif provider == "anthropic":
        return AnthropicClient()
    else:
        return GoogleClient()
```

---

### Generic Types — Reusable Type Signatures

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')  # Generic type variable

class Container(Generic[T]):
    """Generic container that works with any type"""

    def __init__(self):
        self.items: List[T] = []

    def add(self, item: T) -> None:
        self.items.append(item)

    def get_all(self) -> List[T]:
        return self.items

# Usage with specific types
string_container = Container[str]()
string_container.add("hello")  # ✅ OK
string_container.add(42)  # ❌ Type error: Expected str

int_container = Container[int]()
int_container.add(42)  # ✅ OK
int_container.add("hello")  # ❌ Type error: Expected int
```

**Generic function:**
```python
from typing import TypeVar, List

T = TypeVar('T')

def first_item(items: List[T]) -> T:
    """Return first item, preserving type"""
    return items[0]

# Type is inferred:
numbers = [1, 2, 3]
first_num: int = first_item(numbers)  # Type: int

names = ["Alice", "Bob"]
first_name: str = first_item(names)  # Type: str
```

---

### Protocol — Duck Typing with Type Safety

**Duck typing:** "If it walks like a duck and quacks like a duck, it's a duck."

```python
from typing import Protocol

class Processable(Protocol):
    """Protocol: Any object with these methods can be processed"""

    def parse(self) -> str:
        ...

    def validate(self) -> bool:
        ...

def process_document(doc: Processable) -> str:
    """Accept ANY object that has parse() and validate()"""
    if doc.validate():
        return doc.parse()
    else:
        raise ValueError("Invalid document")

# Works with any class that implements the protocol:
class PDFDocument:
    def parse(self) -> str:
        return "PDF content"

    def validate(self) -> bool:
        return True

class WordDocument:
    def parse(self) -> str:
        return "Word content"

    def validate(self) -> bool:
        return True

# Both work!
process_document(PDFDocument())  # ✅ OK
process_document(WordDocument())  # ✅ OK
```

**Protocols are perfect for abstract interfaces** without requiring inheritance!

---

## Part 4: Type-Safe LLM Client

Let's add complete type hints to our multi-provider client:

```python
# typed_llm_client.py

from typing import List, Optional, Literal, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Type aliases for clarity
LLMProvider = Literal["openai", "anthropic", "google"]
MessageRole = Literal["system", "user", "assistant"]

@dataclass
class ChatMessage:
    """Type-safe chat message"""
    role: MessageRole
    content: str

@dataclass
class ChatResponse:
    """Type-safe chat response"""
    content: str
    model: str
    tokens_used: int
    cost: float
    provider: str

class BaseLLMClient(ABC):
    """Abstract base class with full type hints"""

    def __init__(self, model: str, api_key: str) -> None:
        self.model: str = model
        self.api_key: str = api_key
        self.total_tokens: int = 0
        self.total_cost: float = 0.0

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> ChatResponse:
        """Send chat messages and get response"""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Estimate token count"""
        pass

    def get_cost(self) -> float:
        """Get total cost"""
        return self.total_cost

    @staticmethod
    def from_provider(
        provider: LLMProvider,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> "BaseLLMClient":
        """Factory method with type-safe provider selection"""
        if provider == "openai":
            from openai_client import OpenAIClient
            return OpenAIClient(model=model or "gpt-3.5-turbo", api_key=api_key)
        elif provider == "anthropic":
            from anthropic_client import AnthropicClient
            return AnthropicClient(model=model or "claude-3-sonnet", api_key=api_key)
        elif provider == "google":
            from google_client import GoogleClient
            return GoogleClient(model=model or "gemini-pro", api_key=api_key)
        else:
            # This branch is unreachable due to Literal type, but helps runtime safety
            raise ValueError(f"Unknown provider: {provider}")

# Usage with full type safety:
def process_documents_typed(
    documents: List[str],
    provider: LLMProvider = "openai"
) -> List[ChatResponse]:
    """Fully type-hinted document processor"""

    client: BaseLLMClient = BaseLLMClient.from_provider(provider)
    results: List[ChatResponse] = []

    for doc_text in documents:
        messages: List[ChatMessage] = [
            ChatMessage(role="system", content="You are a document summarizer."),
            ChatMessage(role="user", content=f"Summarize: {doc_text}")
        ]

        response: ChatResponse = await client.chat(messages)
        results.append(response)

    return results
```

**Every type is explicit!** IDEs can:
- Autocomplete method names
- Show parameter types
- Warn about type mismatches
- Enable safe refactoring

---

## Part 5: Static Type Checking with mypy

### Installing mypy

```bash
pip install mypy
```

### Running mypy

```bash
# Check single file
mypy my_script.py

# Check entire project
mypy src/

# With strict mode (recommended for new projects)
mypy --strict src/
```

---

### Example: Catching Bugs Before Runtime

**Code with type error:**
```python
# document_processor.py
from typing import List

def summarize_documents(docs: List[str]) -> List[str]:
    summaries = []
    for doc in docs:
        summary = doc.upper()  # Simple transformation
        summaries.append(summary)
    return summaries

# Calling code with mistake:
documents = [123, 456, 789]  # ❌ Wrong! Should be strings
results = summarize_documents(documents)
```

**Run mypy:**
```bash
$ mypy document_processor.py
```

**Output:**
```
document_processor.py:11: error: Argument 1 to "summarize_documents" has incompatible type "List[int]"; expected "List[str]"
Found 1 error in 1 file (checked 1 source file)
```

**Bug caught before running!** Fix it:
```python
documents = ["doc1", "doc2", "doc3"]  # ✅ Correct type
results = summarize_documents(documents)
```

---

### Configuring mypy

Create `mypy.ini` or `pyproject.toml`:

```ini
# mypy.ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_generics = True
disallow_subclassing_any = True
disallow_untyped_calls = True
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

# Per-module configuration
[mypy-tests.*]
disallow_untyped_defs = False
```

**Or in `pyproject.toml`:**
```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
```

---

## Part 6: Type Hints in Practice

### Type-Safe Async Document Processor

```python
# async_typed_processor.py

import asyncio
from typing import List, Dict, Union, TypedDict
from dataclasses import dataclass

class DocumentData(TypedDict):
    """Type-safe document dictionary"""
    name: str
    text: str
    metadata: Dict[str, str]

@dataclass
class ProcessingResult:
    """Type-safe processing result"""
    document_name: str
    success: bool
    summary: str
    tokens: int
    cost: float
    error: Union[str, None] = None

class TypedAsyncProcessor:
    """Fully type-hinted async processor"""

    def __init__(self, provider: LLMProvider = "openai") -> None:
        self.client: BaseLLMClient = BaseLLMClient.from_provider(provider)

    async def process_one(self, doc: DocumentData) -> ProcessingResult:
        """Process single document with full type safety"""
        try:
            messages: List[ChatMessage] = [
                ChatMessage(role="system", content="You are a summarizer."),
                ChatMessage(role="user", content=f"Summarize: {doc['text']}")
            ]

            response: ChatResponse = await self.client.chat(messages)

            return ProcessingResult(
                document_name=doc["name"],
                success=True,
                summary=response.content,
                tokens=response.tokens_used,
                cost=response.cost
            )

        except Exception as e:
            return ProcessingResult(
                document_name=doc["name"],
                success=False,
                summary="",
                tokens=0,
                cost=0.0,
                error=str(e)
            )

    async def process_batch(
        self,
        documents: List[DocumentData]
    ) -> tuple[List[ProcessingResult], int, float]:
        """
        Process batch of documents.

        Returns:
            Tuple of (results, total_tokens, total_cost)
        """
        tasks: List[asyncio.Task[ProcessingResult]] = [
            asyncio.create_task(self.process_one(doc))
            for doc in documents
        ]

        results: List[ProcessingResult] = await asyncio.gather(*tasks)

        total_tokens: int = sum(r.tokens for r in results if r.success)
        total_cost: float = sum(r.cost for r in results if r.success)

        return results, total_tokens, total_cost

# Usage - fully type-safe:
async def main() -> None:
    documents: List[DocumentData] = [
        {
            "name": "doc1.pdf",
            "text": "Engineering report content...",
            "metadata": {"project": "Bridge", "date": "2024-01-15"}
        },
        {
            "name": "doc2.pdf",
            "text": "Structural analysis...",
            "metadata": {"project": "Tower", "date": "2024-01-16"}
        }
    ]

    processor: TypedAsyncProcessor = TypedAsyncProcessor(provider="openai")
    results, tokens, cost = await processor.process_batch(documents)

    print(f"Processed {len(results)} documents")
    print(f"Tokens: {tokens}, Cost: ${cost:.4f}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Every type is explicit!** mypy will catch:
- Wrong parameter types
- Missing return statements
- Incorrect dictionary keys
- Type mismatches in assignments

---

## Common Mistakes and How to Avoid Them

### Mistake 1: Forgetting Return Type

❌ **Wrong:**
```python
def process_document(doc: DocumentProcessor):  # Missing return type!
    return doc.parse()
```

✅ **Correct:**
```python
def process_document(doc: DocumentProcessor) -> str:
    return doc.parse()
```

---

### Mistake 2: Using `list` Instead of `List[T]`

❌ **Wrong:**
```python
def process_names(names: list) -> list:  # What type of items?
    return [n.upper() for n in names]
```

✅ **Correct:**
```python
def process_names(names: List[str]) -> List[str]:
    return [n.upper() for n in names]

# Or Python 3.9+:
def process_names(names: list[str]) -> list[str]:
    return [n.upper() for n in names]
```

---

### Mistake 3: Not Using Optional for None

❌ **Wrong:**
```python
def find_user(id: int) -> str:  # Can return None!
    return users.get(id)  # mypy error: Expected str, got Optional[str]
```

✅ **Correct:**
```python
def find_user(id: int) -> Optional[str]:
    return users.get(id)
```

---

### Mistake 4: Overusing `Any`

❌ **Wrong:**
```python
def process_data(data: Any) -> Any:  # Defeats purpose of type hints!
    return do_something(data)
```

✅ **Correct:**
```python
from typing import Union

def process_data(data: Union[str, int, dict]) -> ProcessingResult:
    return do_something(data)
```

---

## Quick Reference Card

### Basic Type Hints

```python
# Variables
name: str = "Ahmed"
age: int = 25

# Functions
def greet(name: str, age: int) -> str:
    return f"Hello {name}"

# Collections (Python 3.9+)
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"math": 95}
tags: set[str] = {"python", "ai"}

# Optional (may be None)
def find(id: int) -> Optional[str]:
    ...

# Union (one of several types)
def process(value: str | int | float) -> str:
    ...
```

### Advanced Types

```python
from typing import TypedDict, Literal, Protocol

# TypedDict - structured dict
class Config(TypedDict):
    host: str
    port: int

# Literal - specific values only
Provider = Literal["openai", "anthropic"]

# Protocol - duck typing
class Parseable(Protocol):
    def parse(self) -> str: ...
```

### Type Checking

```bash
# Install
pip install mypy

# Check files
mypy script.py
mypy --strict src/
```

---

## Assessment

### Quick Check Questions

1. **What's the difference between `List` and `list` in type hints?**
   <details>
   <summary>Answer</summary>

   - `List` (from `typing` module): Works in Python 3.5+, requires import
   - `list` (built-in): Works as type hint only in Python 3.9+, no import needed

   Both support generic syntax: `List[str]` or `list[str]`. Use lowercase `list` for Python 3.9+ projects.
   </details>

2. **When should you use `Optional[T]` vs `Union[T, None]`?**
   <details>
   <summary>Answer</summary>

   They're equivalent! `Optional[T]` is shorthand for `Union[T, None]`. Use `Optional` for readability:

   ```python
   # These are identical:
   def find_user(id: int) -> Optional[str]: ...
   def find_user(id: int) -> Union[str, None]: ...
   def find_user(id: int) -> str | None: ...  # Python 3.10+
   ```
   </details>

3. **What's the purpose of Protocol in type hints?**
   <details>
   <summary>Answer</summary>

   Protocol enables structural typing (duck typing with type safety). An object matches a Protocol if it has the required methods/attributes, without needing to inherit from the Protocol.

   This allows type-safe duck typing: "If it walks like a duck and quacks like a duck, it's a duck."
   </details>

---

### Coding Challenge: Add Type Hints to Document System

**Your mission:** Add complete type hints to a document processing system.

**Requirements:**

1. **Add type hints to all functions and variables**
2. **Create TypedDict for structured dictionaries**
3. **Use Protocol for document interface**
4. **Ensure mypy passes with `--strict` mode**

**Starter code (untyped):**

```python
# document_system.py (needs type hints!)

def load_documents(paths):
    documents = []
    for path in paths:
        with open(path) as f:
            content = f.read()
        documents.append({"path": path, "content": content})
    return documents

def summarize_document(doc, llm_client):
    messages = [
        {"role": "system", "content": "You are a summarizer."},
        {"role": "user", "content": f"Summarize: {doc['content']}"}
    ]
    response = llm_client.chat(messages)
    return response.content

def process_batch(document_paths, provider="openai"):
    documents = load_documents(document_paths)
    client = create_llm_client(provider)

    results = {}
    for doc in documents:
        summary = summarize_document(doc, client)
        results[doc["path"]] = summary

    return results
```

<details>
<summary>💡 <strong>Solution</strong></summary>

```python
# document_system.py (fully typed!)

from typing import List, Dict, TypedDict, Literal, Protocol
from pathlib import Path

# Type aliases
LLMProvider = Literal["openai", "anthropic", "google"]

# TypedDict for structured dictionaries
class DocumentData(TypedDict):
    """Structured document dictionary"""
    path: str
    content: str

# Protocol for LLM client interface
class LLMClientProtocol(Protocol):
    """Protocol for any LLM client"""
    def chat(self, messages: List[Dict[str, str]]) -> "ChatResponse":
        ...

class ChatResponse(Protocol):
    """Protocol for chat response"""
    @property
    def content(self) -> str:
        ...

def load_documents(paths: List[str]) -> List[DocumentData]:
    """
    Load documents from file paths.

    Args:
        paths: List of file paths to load

    Returns:
        List of document dictionaries
    """
    documents: List[DocumentData] = []

    for path in paths:
        with open(path, encoding='utf-8') as f:
            content: str = f.read()

        doc: DocumentData = {"path": path, "content": content}
        documents.append(doc)

    return documents

def summarize_document(
    doc: DocumentData,
    llm_client: LLMClientProtocol
) -> str:
    """
    Summarize a single document.

    Args:
        doc: Document dictionary with path and content
        llm_client: LLM client implementing chat interface

    Returns:
        Summary text
    """
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": "You are a summarizer."},
        {"role": "user", "content": f"Summarize: {doc['content']}"}
    ]

    response: ChatResponse = llm_client.chat(messages)
    return response.content

def create_llm_client(provider: LLMProvider) -> LLMClientProtocol:
    """
    Create LLM client for specified provider.

    Args:
        provider: One of "openai", "anthropic", "google"

    Returns:
        LLM client instance
    """
    if provider == "openai":
        from openai_client import OpenAIClient
        return OpenAIClient()
    elif provider == "anthropic":
        from anthropic_client import AnthropicClient
        return AnthropicClient()
    else:  # provider == "google"
        from google_client import GoogleClient
        return GoogleClient()

def process_batch(
    document_paths: List[str],
    provider: LLMProvider = "openai"
) -> Dict[str, str]:
    """
    Process batch of documents with specified provider.

    Args:
        document_paths: List of file paths
        provider: LLM provider to use

    Returns:
        Dictionary mapping file paths to summaries
    """
    documents: List[DocumentData] = load_documents(document_paths)
    client: LLMClientProtocol = create_llm_client(provider)

    results: Dict[str, str] = {}
    for doc in documents:
        summary: str = summarize_document(doc, client)
        results[doc["path"]] = summary

    return results

# Type check passes!
if __name__ == "__main__":
    paths: List[str] = ["doc1.txt", "doc2.txt"]
    summaries: Dict[str, str] = process_batch(paths, provider="openai")
    print(summaries)
```

**Run mypy:**
```bash
$ mypy --strict document_system.py
Success: no issues found in 1 source file
```

**Key improvements:**
1. ✅ All functions have parameter and return type hints
2. ✅ TypedDict for structured dictionaries
3. ✅ Protocol for flexible LLM client interface
4. ✅ Literal type for provider safety
5. ✅ Passes mypy strict mode

**Key takeaway:** Type hints make code self-documenting and catch bugs early. The investment in adding types pays off immediately in better IDE support and safer refactoring! 🎯
</details>

---

## Verification

Let's verify your type hints understanding with automated tests.

### Test Script

Create this file:

```python
# test_type_hints.py
"""
Automated verification script for Chapter 12B
Tests: Type hint syntax, Optional handling, TypedDict, type compatibility
"""

from typing import List, Dict, Optional, Union, TypedDict, Literal
from dataclasses import dataclass


# Test TypedDict
class UserData(TypedDict):
    """Structured user dictionary"""
    name: str
    age: int
    email: Optional[str]


def test_basic_type_hints():
    """Test 1: Basic type hint syntax works"""
    try:
        # Function with type hints
        def greet(name: str, age: int) -> str:
            return f"Hello {name}, you are {age}"

        # Valid call
        result = greet("Ahmed", 25)
        assert isinstance(result, str), "Result should be string"
        assert "Ahmed" in result, "Name should be in result"
        assert "25" in result, "Age should be in result"

        print("✅ PASS: Basic type hint syntax works correctly")
        return True

    except Exception as e:
        print(f"❌ FAIL: Basic type hints test failed: {e}")
        return False


def test_optional_types():
    """Test 2: Optional types handle None correctly"""
    try:
        def find_user(user_id: int, users: Dict[int, str]) -> Optional[str]:
            """Find user by ID, return None if not found"""
            return users.get(user_id)

        # Test with existing user
        users = {1: "Alice", 2: "Bob"}
        result = find_user(1, users)
        assert result == "Alice", f"Expected 'Alice', got {result}"
        assert result is not None, "Result should not be None for existing user"

        # Test with non-existing user
        result_none = find_user(999, users)
        assert result_none is None, "Result should be None for non-existing user"

        print("✅ PASS: Optional types handle None correctly")
        return True

    except Exception as e:
        print(f"❌ FAIL: Optional types test failed: {e}")
        return False


def test_typed_dict():
    """Test 3: TypedDict enforces structure"""
    try:
        # Create valid TypedDict instance
        user: UserData = {
            "name": "Ahmed",
            "age": 25,
            "email": "ahmed@example.com"
        }

        # Verify structure
        assert "name" in user, "Should have 'name' key"
        assert "age" in user, "Should have 'age' key"
        assert "email" in user, "Should have 'email' key"

        # Verify types
        assert isinstance(user["name"], str), "Name should be string"
        assert isinstance(user["age"], int), "Age should be int"

        # Test with None email
        user_no_email: UserData = {
            "name": "Sarah",
            "age": 30,
            "email": None
        }
        assert user_no_email["email"] is None, "Email can be None"

        print("✅ PASS: TypedDict enforces structure correctly")
        return True

    except Exception as e:
        print(f"❌ FAIL: TypedDict test failed: {e}")
        return False


def test_list_dict_type_hints():
    """Test 4: Generic collection types work correctly"""
    try:
        def process_names(names: List[str]) -> List[str]:
            """Convert names to uppercase"""
            return [name.upper() for name in names]

        def count_words(text: str) -> Dict[str, int]:
            """Count word occurrences"""
            counts: Dict[str, int] = {}
            for word in text.split():
                counts[word] = counts.get(word, 0) + 1
            return counts

        # Test list processing
        names = ["ahmed", "sarah", "bob"]
        result = process_names(names)
        assert result == ["AHMED", "SARAH", "BOB"], \
            f"Expected uppercase names, got {result}"
        assert isinstance(result, list), "Result should be list"
        assert all(isinstance(n, str) for n in result), \
            "All items should be strings"

        # Test dict processing
        text = "hello world hello python"
        counts = count_words(text)
        assert counts["hello"] == 2, "Should count 'hello' twice"
        assert counts["world"] == 1, "Should count 'world' once"
        assert isinstance(counts, dict), "Result should be dict"

        print("✅ PASS: Generic collection types work correctly")
        return True

    except Exception as e:
        print(f"❌ FAIL: Collection types test failed: {e}")
        return False


def test_literal_types():
    """Test 5: Literal types restrict to specific values"""
    try:
        Provider = Literal["openai", "anthropic", "google"]

        def get_provider_info(provider: Provider) -> str:
            """Get info for specific provider"""
            if provider == "openai":
                return "OpenAI GPT models"
            elif provider == "anthropic":
                return "Anthropic Claude models"
            else:  # provider == "google"
                return "Google Gemini models"

        # Test valid providers
        info_openai = get_provider_info("openai")
        assert "OpenAI" in info_openai, "Should return OpenAI info"

        info_claude = get_provider_info("anthropic")
        assert "Claude" in info_claude, "Should return Claude info"

        info_gemini = get_provider_info("google")
        assert "Gemini" in info_gemini, "Should return Gemini info"

        print("✅ PASS: Literal types work correctly")
        return True

    except Exception as e:
        print(f"❌ FAIL: Literal types test failed: {e}")
        return False


def run_all_tests():
    """Run all verification tests"""
    print("="*60)
    print("Chapter 12B Verification Tests")
    print("="*60)

    tests = [
        ("Basic Type Hints", test_basic_type_hints),
        ("Optional Types", test_optional_types),
        ("TypedDict", test_typed_dict),
        ("Generic Collection Types", test_list_dict_type_hints),
        ("Literal Types", test_literal_types)
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
        print("\n🎉 ALL TESTS PASSED! You understand type hints!")
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
python test_type_hints.py
```

### Expected output:

```
============================================================
Chapter 12B Verification Tests
============================================================

[Test] Basic Type Hints
✅ PASS: Basic type hint syntax works correctly

[Test] Optional Types
✅ PASS: Optional types handle None correctly

[Test] TypedDict
✅ PASS: TypedDict enforces structure correctly

[Test] Generic Collection Types
✅ PASS: Generic collection types work correctly

[Test] Literal Types
✅ PASS: Literal types work correctly

============================================================
Results: 5/5 tests passed
============================================================

🎉 ALL TESTS PASSED! You understand type hints!
```

### Optional: Type Checking with mypy

After the tests pass, run mypy to verify your code:

```bash
pip install mypy
mypy test_type_hints.py
```

Expected output:
```
Success: no issues found in 1 source file
```

---

## What's Next?

Congratulations! You've mastered type hints and static type checking. Your code is now safer, more maintainable, and self-documenting! 🎉

**PBM-2 (Python Bridge Module 2) is now complete!** ✅
- Chapter 12A: Async/Await ✅
- Chapter 12B: Type Hints & Type Checking ✅

**Next:** Complete Chapter 7 (Your First LLM Call) remaining sections, then move to PBM-3 or Milestone 3 (RAG Fundamentals).

**Your enhanced toolchain:**

```python
# You can now write production-grade code like this:

from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class DocumentMetadata:
    project: str
    engineer: str
    date: str

async def process_documents_production(
    files: List[str],
    provider: Literal["openai", "anthropic"] = "openai",
    config: Optional[Dict[str, Any]] = None
) -> tuple[List[ProcessingResult], float]:
    """
    Fully type-safe, async, production-ready document processing.

    - Type hints everywhere
    - Async for concurrency
    - Error handling
    - Cost tracking
    """
    # Implementation...
    pass
```

This is professional-grade Python! 🏗️

---

## Summary

**What you learned:**

1. ✅ **Basic type hints** — Variables, functions, return types
2. ✅ **Generic types** — List, Dict, Set, Tuple with specific types
3. ✅ **Optional and Union** — Handling None and multiple types
4. ✅ **TypedDict** — Structured dictionaries with type safety
5. ✅ **Literal types** — Restrict to specific values
6. ✅ **Protocols** — Duck typing with type safety
7. ✅ **mypy** — Static type checking to catch bugs early
8. ✅ **Production patterns** — Type-safe async LLM clients

**Key takeaway:** Type hints are documentation that your tools can verify. They catch bugs before runtime, enable better IDE support, and make code self-documenting. Every production Python project should use type hints! 🎯

**You got this!** 💪 Next: Complete Chapter 7, then on to RAG! 🚀
