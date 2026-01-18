# Chapter 2: Enums & Type Hints — The Safety Net

<!--
METADATA
Phase: 0 - Shared Foundation
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐
Type: Foundation
Prerequisites: Chapter 1
Builds Toward: Data Models (Ch 3), All Future Code
Correctness Properties: None (Foundation)
Project Thread: Type System

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're at a coffee shop. You ask for a "Large Latte".
The barista stares at you blankly. "We only have *Venti*, *Grande*, and *Tall*."
You try again: "Okay, give me a *Big* one."
Barista: "Syntax Error." 🤖

This is exactly what happens when you use **Strings** in your code.
If you type `"engineering"` but your code expects `"ENGINEERING"`, everything breaks silently. Or worse, it works for 6 months until a typo takes down production.

**Enums** are like the coffee shop menu. You can ONLY choose from the valid options. No "Big", no "Large", just the exact choices defined on the menu.

By the end of this chapter, you'll banish "magic strings" from your code forever and write Python that catches bugs *before* you even run it. 🛡️

---

## Prerequisites Check

Let's make sure Chapter 1 stuck!

```bash
# Verify your virtual environment is active
# Windows:
where python
# Mac/Linux:
which python
```

**If this points to your `.venv` folder**, you're ready! ✅

**If it points to system Python**, run `source .venv/bin/activate` (or Windows equivalent) now.

---

## The Story: Why Strings Are Dangerous

### The Problem (Magic Strings)

Imagine you're building a contract generator. You need to support different template types.

```python
# ❌ The "Magic String" Approach
def generate_contract(template_type):
    if template_type == "engineering":
        return load_eng()
    elif template_type == "consulting":
        return load_cons()
```

**Why This is a Time Bomb:**
1. **Typos**: `generate_contract("enginering")` (missing 'e') -> Returns `None` silently.
2. **Case Sensitivity**: `"Engineering"` vs `"engineering"`.
3. **No Autocomplete**: You have to memorize every valid string.
4. **Refactoring Nightmare**: Changing `"consulting"` to `"advisory"` means finding-and-replacing text in 50 files.

### The Naive Solution

> "I'll just use constants!"

```python
ENGINEERING = "engineering"
CONSULTING = "consulting"

def generate_contract(template_type):
    if template_type == ENGINEERING: ...
```

Better... but `template_type` is still just a string. I can still pass `"random_garbage"` and Python won't complain until runtime.

### The Elegant Solution (Enums)

**Enumerations (Enums)** are a distinct data type that consists of a set of named values.

```python
from enum import Enum

class TemplateType(Enum):
    ENGINEERING = "engineering"
    CONSULTING = "consulting"

# Now I can ONLY pass TemplateType.ENGINEERING
```

If I try to pass `TemplateType.ENGINERRING`, the code **won't even start** because of the typo. That's power. 💪

---

## Part 1: Your First Enum

### What is an Enum?

**Analogy: The Radio Dial** 📻
A volume knob can be *any* number (0-100). That's like an **Integer**.
A radio channel selector clicks into specific stations (FM 98.5, FM 101.1). You can't be "kind of" on a station. That's an **Enum**.

### 🔬 Try This! (Hands-On Practice #1)

Let's build the `TemplateType` enum we'll use for the rest of the course.

**Challenge**: specific the core enum for our contract types.

**Step 1: Create folder structure**
```bash
# Make sure you're in the project root
mkdir -p shared/models
# Create empty __init__.py to make it a package
# Windows: type nul > shared/models/__init__.py
# Mac/Linux: touch shared/models/__init__.py
```

**Step 2: Create `shared/models/enums.py`**

```python
from enum import Enum

class TemplateType(Enum):
    """
    Supported contract template types.
    
    WHY: Prevents invalid template names
    WHAT: Maps business names to file paths/identifiers
    """
    ENGINEERING = "engineering"
    CONSULTING = "consulting"
    MILITARY = "military"
    GOVERNMENTAL = "governmental"

    def __str__(self) -> str:
        """Return human-readable name (e.g., 'Engineering')."""
        return self.name.capitalize()
```

**Step 3: Test it**
Create `test_enum.py` and run it:
```python
from shared.models.enums import TemplateType

t = TemplateType.ENGINEERING
print(f"Selected: {t}")
print(f"Value: {t.value}")
print(f"Is it engineering? {t == TemplateType.ENGINEERING}")
```

**Expected Output**:
```
Selected: Engineering
Value: engineering
Is it engineering? True
```

---

## Part 2: Type Hints (The map)

### The Problem with "Dynamic" Python

```python
def process_data(data):
    return data.strip()
```
Is `data` a string? A list? If I pass `10`, this crashes at runtime.

### The Solution: Type Hints

```python
def process_data(data: str) -> str:
    return data.strip()
```

Now your editor (VS Code) knows `data` is a string. It gives you autocomplete for `.strip()`, `.upper()`, etc.

### 🔬 Try This! (Hands-On Practice #2)

Let's add a second enum with rich methods and type hints.

**Challenge**: Add `SeverityLevel` to `shared/models/enums.py`.

**Add this code to `shared/models/enums.py`**:

```python
# ... inside shared/models/enums.py ...

class SeverityLevel(Enum):
    """
    Severity levels for compliance issues.
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    def __str__(self) -> str:
        return self.name.capitalize()

    def get_priority(self) -> int:
        """
        Get numeric priority (1=Highest). 
        
        Returns:
            int: Priority level
        """
        priority_map = {
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3
        }
        return priority_map[self]
```

**Test it**:
```python
# append to test_enum.py
from shared.models.enums import SeverityLevel

sev = SeverityLevel.HIGH
print(f"Severity: {sev}")
print(f"Priority: {sev.get_priority()}")
```

**Expected Output**:
```
Severity: High
Priority: 1
```

---

## Part 3: Advanced Enum Patterns

### Comparisons

Never compare Enums to strings!

```python
# ❌ BAD
if template == "engineering": ...

# ✅ GOOD
if template == TemplateType.ENGINEERING: ...
```

### Iteration

You can loop over enums like a list.

```python
for t in TemplateType:
    print(t.value)
```

---

## Bringing It All Together: The Contract Status Lifecycle

Let's implement a complex enum that manages state transitions.

**Challenge**: Implement `ContractStatus` with transition logic.

**Add to `shared/models/enums.py`**:

```python
class ContractStatus(Enum):
    """Lifecycle status of a contract."""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

    def __str__(self) -> str:
        # Replace underscore with space and Title Case
        return self.value.replace("_", " ").title()

    def can_transition_to(self, target: 'ContractStatus') -> bool:
        """
        Validate state transitions. 
        
        DRAFT -> UNDER_REVIEW
        UNDER_REVIEW -> APPROVED, REJECTED
        APPROVED -> ARCHIVED
        REJECTED -> ARCHIVED
        """
        valid_transitions = {
            ContractStatus.DRAFT: {ContractStatus.UNDER_REVIEW},
            ContractStatus.UNDER_REVIEW: {ContractStatus.APPROVED, ContractStatus.REJECTED},
            ContractStatus.APPROVED: {ContractStatus.ARCHIVED},
            ContractStatus.REJECTED: {ContractStatus.ARCHIVED},
            ContractStatus.ARCHIVED: set()
        }
        
        # Allow transition to self (no-op)
        if self == target:
            return True
            
        return target in valid_transitions.get(self, set())
```

<details>
<summary>💡 Hint: Type hints for forward references</summary>

Note the quotes in `target: 'ContractStatus'`. This is a "forward reference" because `ContractStatus` isn't fully defined when the method is read.
</details>

---

## Common Mistakes

### Mistake #1: Using `enums` without `value`

```python
# ❌ WRONG
class Color(Enum):
    RED  # Missing value assignment!
```

**The Fix**: Always assign a value (string or int).
```python
class Color(Enum):
    RED = 1
```

### Mistake #2: Comparing Enums with `is` vs `==`

Actually... `is` works for enums! But `==` is safer generally.
```python
# Both work
if type is TemplateType.ENGINEERING: ...
if type == TemplateType.ENGINEERING: ...
```
**Recommendation**: Use `==` for consistency, or `is` if you want to be strictly Pythonic with singletons.

---

## Quick Reference Card

### Standard Enum Template

```python
from enum import Enum

class MyEnum(Enum):
    OPTION_ONE = "one"
    OPTION_TWO = "two"
    
    def __str__(self) -> str:
        return self.name.lower()
```

### Type Hints Cheatsheet

| Hint | Meaning |
|------|---------|
| `x: str` | String |
| `x: int` | Integer |
| `x: Optional[str]` | String or None |
| `x: list[str]` | List of strings |
| `x: dict[str, int]` | Dict with string keys, int values |
| `def f() -> None:` | Function returns nothing |

---

## Verification (REQUIRED SECTION)

Let's ensure your `enums.py` is perfect.

**Create `verify_enums.py` and run it:**

```python
"""
Verification script for Chapter 2.
"""
from shared.models.enums import TemplateType, SeverityLevel, ContractStatus
import sys

print("🧪 Running Enum Verification...\n")

# Test 1: TemplateType
print("Test 1: TemplateType...")
assert TemplateType.ENGINEERING.value == "engineering"
assert str(TemplateType.ENGINEERING) == "Engineering"
assert len(TemplateType) == 4
print("✅ TemplateType looks good!")

# Test 2: SeverityLevel
print("Test 2: SeverityLevel...")
assert SeverityLevel.HIGH.get_priority() == 1
assert SeverityLevel.LOW.get_priority() == 3
assert str(SeverityLevel.HIGH) == "High"
print("✅ SeverityLevel looks good!")

# Test 3: ContractStatus Transitions
print("Test 3: ContractStatus Transitions...")
draft = ContractStatus.DRAFT
review = ContractStatus.UNDER_REVIEW
approved = ContractStatus.APPROVED

assert draft.can_transition_to(review) is True
assert draft.can_transition_to(approved) is False
assert str(ContractStatus.UNDER_REVIEW) == "Under Review"
print("✅ ContractStatus logic is perfect!")

print("\n🎉 Chapter 2 Complete! You are a master of Enums.")
```

**Run it:**
```bash
python verify_enums.py
```

---

## Summary

**What you learned:**

1. ✅ **Magic Strings are bad**: They cause silent bugs and are hard to maintain.
2. ✅ **Enums are the solution**: They enforce valid choices and give IDE superpowers.
3. ✅ **Type Hints**: They act as documentation that the computer can verify.
4. ✅ **Enum Methods**: Enums can have logic (like `get_priority` or `can_transition_to`).
5. ✅ **Refactoring**: Changing an enum name updates references everywhere automatically.
6. ✅ **State Machines**: You built a basic state machine using `ContractStatus`.
7. ✅ **Python Best Practices**: Using `__str__` and docstrings.

**Key Takeaway**: By restricting choices with Enums and documenting types with Hints, you shift bugs from "3 AM production crash" to "instant red squiggly line in editor". That is the path to sleeping well at night. 😴

**Skills unlocked**: 🎯
- Type Safety
- State Management
- Code Cleanliness

**Looking ahead**: In **Chapter 3**, we'll combine these Enums with Pydantic Models to build the actual data structures for our contracts!

---

**Next**: [Chapter 3: Pydantic Models (Core) →](chapter-03-pydantic-models-core.md)