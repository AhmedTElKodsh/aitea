# Chapter 3: Pydantic Models (Core) — The Blueprint

<!--
METADATA
Phase: 0 - Shared Foundation
Time: 2 hours (40 min reading + 80 min hands-on)
Difficulty: ⭐⭐
Type: Foundation
Prerequisites: Chapter 2
Builds Toward: Data Models (Ch 4), All Future Code
Correctness Properties: None (Foundation)
Project Thread: Data Architecture

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're building a Lego castle. 🏰
But instead of hard plastic bricks, someone hands you... blocks made of Jell-O.
You try to stack them, and they wobble, squish, and collapse.

This is what programming with **Dictionaries** is like.
`{"name": "Alice", "age": "twenty"}` -> Wait, age is a string? Squish. Collapse.

**Pydantic Models** are the hard plastic bricks.
They have a rigid shape. If you try to jam a "square" piece into a "round" hole, it doesn't just squish—it yells at you immediately: *"ValidationError: Expected square, got round!"*

By the end of this chapter, you'll stop building with Jell-O and start building with high-precision engineering materials. 🏗️

---

## Prerequisites Check

Let's make sure you're ready.

```bash
# Check if Pydantic is installed (from Chapter 1)
python -c "import pydantic; print(f'Pydantic version: {pydantic.VERSION}')"
```

**If this prints a version number (like 2.5.2)**, you're good! ✅
**If it errors**, run `pip install pydantic` inside your virtual environment.

---

## The Story: Why Structure Matters

### The Problem (Dictionary Chaos)

You're building an AI that generates contracts. You represent a contract as a dictionary:

```python
contract = {
    "title": "Consulting Agreement",
    "value": 50000,
    "signed": False
}
```

Then, your new intern joins. They write:
```python
contract = {
    "title": "Bad Contract",
    "value": "$50,000",  # String instead of int!
    "is_signed": "no"    # Wrong key name! Wrong type!
}
```

Your code crashes 500 lines later when you try to do `contract["value"] * 0.1`. Good luck debugging that. 💥

### The Naive Solution (Manual Validation)

> "I'll just write `if` statements!"

```python
def process_contract(c):
    if not isinstance(c["value"], int):
        raise ValueError("Value must be int")
    if "signed" not in c:
        raise ValueError("Missing 'signed' key")
    # ... 50 more lines of checks ...
```

This is tedious, ugly, and you *will* forget something.

### The Elegant Solution (Pydantic)

Enter **Pydantic**. You define the *shape* of your data once, and Pydantic enforces it forever.

```python
from pydantic import BaseModel

class Contract(BaseModel):
    title: str
    value: int
    signed: bool

# Pydantic validates it automatically:
c = Contract(title="Good", value="50000", signed=False)
# It even converts the string "50000" to int 50000 for you! 🎩
```

---

## Part 1: Your First BaseModel

### What is a BaseModel?

It's a class that inherits from `pydantic.BaseModel`. It uses Python **Type Hints** (from Chapter 2) to define fields.

### 🔬 Try This! (Hands-On Practice #1)

Let's create a simple `Clause` model for our contracts.

**Challenge**: Create a class that represents a contract clause.

**Step 1: Create `shared/models/contract.py`**
If the file doesn't exist, create it.

```python
from pydantic import BaseModel

class Clause(BaseModel):
    """A single clause in a contract."""
    title: str
    text: str
    page_number: int
```

**Step 2: Test it**
Create `test_pydantic.py` and run:

```python
from shared.models.contract import Clause

# Valid data
c1 = Clause(title="Payment", text="Pay me", page_number=1)
print(f"Valid: {c1}")

# Data coercion (String "5" becomes Int 5)
c2 = Clause(title="Term", text="End date", page_number="5")
print(f"Coerced: {c2.page_number} is type {type(c2.page_number)}")

# Invalid data (this should crash)
try:
    c3 = Clause(title="Bad", text="No page", page_number="five")
except Exception as e:
    print(f"\nCaught Error:\n{e}")
```

**Expected Output**:
You should see that `c2.page_number` became an `int`, and `c3` raised a `ValidationError`.

---

## Part 2: Validation with `Field`

### The Problem with Basic Types

`title: str` allows empty strings `""`.
`value: int` allows negative numbers `-100`.
That's not good enough for a real contract.

### The Solution: `Field(...)`

We use `pydantic.Field` to add constraints.

```python
from pydantic import Field

class Item(BaseModel):
    name: str = Field(min_length=1)
    quantity: int = Field(gt=0)  # Greater Than 0
```

### 🔬 Try This! (Hands-On Practice #2)

Let's upgrade our `Clause` model with strict validation.

**Challenge**: Update `shared/models/contract.py`.

```python
from pydantic import BaseModel, Field

class Clause(BaseModel):
    """A single clause in a contract."""
    title: str = Field(..., min_length=1, max_length=100)
    text: str = Field(..., min_length=10)
    page_number: int = Field(..., gt=0)
```

**Test it**:
Try creating a clause with `page_number=0` or `text="short"`. Pydantic should reject it.

---

## Part 3: Nested Models (The Russian Doll)

Contracts aren't flat. They have Sections, and Sections have Clauses.
Pydantic handles this nesting beautifully.

### 🔬 Try This! (Hands-On Practice #3)

Let's build the full hierarchy.

**Challenge**: Implement `Section` and `Contract` models in `shared/models/contract.py`.

**Update `shared/models/contract.py`**:

```python
from typing import List, Optional
from pydantic import BaseModel, Field
from shared.models.enums import TemplateType, ContractStatus # From Ch 2

class Clause(BaseModel):
    title: str = Field(..., min_length=1)
    text: str = Field(..., min_length=10)

class Section(BaseModel):
    """A group of clauses."""
    title: str = Field(..., min_length=1)
    clauses: List[Clause] = Field(default_factory=list)

class Contract(BaseModel):
    """The complete document."""
    title: str
    template_type: TemplateType
    status: ContractStatus = Field(default=ContractStatus.DRAFT)
    sections: List[Section] = Field(default_factory=list)
```

**Why `default_factory=list`?**
Never use `clauses: List[Clause] = []`. In Python, that list is *shared* between all instances. `default_factory` creates a new list for every new object.

---

## Bringing It All Together: The Builder

Let's create a script that builds a complex contract using all our models.

**Create `build_contract.py`**:

```python
from shared.models.contract import Contract, Section, Clause
from shared.models.enums import TemplateType, ContractStatus

# 1. Create Clauses
c1 = Clause(title="Payment", text="Pay me", page_number=1)
c2 = Clause(title="Term", text="End date", page_number="5")

# 2. Create Sections
section_payment = Section(title="Financials", clauses=[c1])
section_legal = Section(title="Legal", clauses=[c2])

# 3. Create Contract
contract = Contract(
    title="Web Dev Agreement",
    template_type=TemplateType.ENGINEERING,
    sections=[section_payment, section_legal]
)

# 4. Serialize to JSON (this is what we'd send to an API)
print(contract.model_dump_json(indent=2))
```

**Run it**:
```bash
python build_contract.py
```

**Expected Output**:
A beautifully formatted JSON string representing your entire contract tree. 🌳

---

## Common Mistakes

### Mistake #1: Mutable Defaults

```python
# ❌ WRONG
class BadModel(BaseModel):
    items: list = []

# ✅ CORRECT
class GoodModel(BaseModel):
    items: list = Field(default_factory=list)
```

### Mistake #2: Forgetting `model_dump()`

When you want a dictionary from your model, don't use `dict(model)`.
Use `model.model_dump()`.

### Mistake #3: Validation Confusion

Validation happens *at creation*. If you modify a field *after* creation, Pydantic (by default) won't check it unless you enable `validate_assignment`.

```python
c = Clause(...)
c.page_number = -5  # This might succeed by default!
```
(We'll learn how to fix this in Chapter 4).

---

## Quick Reference Card

### Basic Model Template

```python
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    required_field: str
    optional_field: int = 10
    constrained_field: str = Field(..., min_length=5)
```

### Common Field Constraints

| Constraint | Meaning | Example |
|------------|---------|---------|
| `min_length` | Min string chars | `min_length=1` |
| `max_length` | Max string chars | `max_length=50` |
| `gt` / `lt` | Greater/Less than | `gt=0` |
| `ge` / `le` | Greater/Less or Equal | `ge=18` |
| `pattern` | Regex validation | `pattern=r"^\d+$"` |

---

## Verification (REQUIRED SECTION)

Let's verify your models structure.

**Create `verify_models.py`**:

```python
"""
Verification script for Chapter 3.
"""
from shared.models.contract import Contract, Section, Clause
from shared.models.enums import TemplateType
import sys

print("🧪 Running Pydantic Verification...\n")

# Test 1: Clause Validation
print("Test 1: Clause Validation...")
try:
    Clause(title="A", text="Short")
    print("❌ Failed: Should have rejected short text")
    sys.exit(1)
except ValueError:
    print("✅ Clause validation caught short text!")

# Test 2: Nested Structure
print("Test 2: Nested Structure...")
try:
    c = Contract(
        title="Test",
        template_type=TemplateType.CONSULTING,
        sections=[
            Section(title="S1", clauses=[
                Clause(title="C1", text="Long enough text here")
            ])
        ]
    )
    assert len(c.sections) == 1
    assert c.sections[0].clauses[0].title == "C1"
    print("✅ Nested structure verified!")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 3: JSON Serialization
print("Test 3: JSON Serialization...")
try:
    json_out = c.model_dump_json()
    assert "Long enough text here" in json_out
    print("✅ JSON serialization works!")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

print("\n🎉 Chapter 3 Complete! You have built the data backbone.")
```

**Run it:**
```bash
python verify_models.py
```

---

## Summary

**What you learned:**

1. ✅ **BaseModel**: The foundation of all Pydantic models.
2. ✅ **Validation**: Using `Field(...)` to enforce rules like `min_length` and `gt`.
3. ✅ **Type Coercion**: Pydantic creates data from messy inputs (str -> int).
4. ✅ **Nesting**: Models can contain lists of other models.
5. ✅ **Serialization**: `model_dump_json()` makes it easy to save/send data.
6. ✅ **Best Practices**: Using `default_factory=list` to avoid mutable default bugs.

**Key Takeaway**: Pydantic is the "Gatekeeper" of your application. It stops bad data at the door, so the rest of your code can assume everything is perfect. 🛡️

**Skills unlocked**: 🎯
- Data Modeling
- Declarative Validation
- JSON Schema Design

**Looking ahead**: In **Chapter 4**, we'll go deeper with custom validators and computed fields!

---

**Next**: [Chapter 4: Pydantic Advanced →](chapter-04-pydantic-advanced.md)