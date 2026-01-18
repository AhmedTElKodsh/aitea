# Chapter 5: Validation Utilities — The Gatekeepers

<!--
METADATA
Phase: 0 - Shared Foundation
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Foundation
Prerequisites: Chapter 4
Builds Toward: Testing (Ch 39), UI (Ch 54)
Correctness Properties: None (Foundation)
Project Thread: Quality Assurance

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're running a nightclub. You hire 3 bouncers.
- Bouncer A lets anyone in who is "tall".
- Bouncer B checks ID but only for people wearing blue.
- Bouncer C uses a metal detector but ignores the VIP list.

Your club is going to have problems. 🚨

This is what happens when you scatter validation logic across 50 files.
`file_a.py` checks email with one Regex. `file_b.py` checks it with another. `file_c.py` doesn't check it at all.

**Validation Utilities** are your "Head of Security". You define the rules **once**, in **one place**, and everyone follows them. No exceptions. 🛡️

By the end of this chapter, you'll have a centralized library of validators that keep your data clean and your codebase DRY (Don't Repeat Yourself). 🛡️

---

## Prerequisites Check

```bash
# Check if your project structure is ready
# Windows:
if exist shared\models\contract.py (echo Ready) else (echo Missing Chapter 3)
# Mac/Linux:
[ -f shared/models/contract.py ] && echo Ready || echo Missing Chapter 3
```

---

## The Story: The "Copy-Paste" Trap

### The Problem (Inconsistency)

You need to validate Project Codes (`PROJ-2025-001`).

Developer A writes:
```python
if code.startswith("PROJ"): ...
```

Developer B writes:
```python
import re
if re.match(r"PROJ-\d{4}-\d{3}", code): ...
```

Two weeks later, the format changes to `PROJ-2025-ABCD`.
Developer B updates their regex. Developer A forgets.
Now half your system rejects valid codes. 💥

### The Naive Solution (Global Variables)

> "I'll put the Regex in a constants file!"

```python
# constants.py
PROJECT_REGEX = r"PROJ-..."
```

Better, but what about the logic? What if you need to check if the year is valid? You're still copying `if` statements everywhere.

### The Elegant Solution (Centralized Utilities)

We build a **Validation Library**.

```python
# shared/utils/validation.py
def validate_project_code(code: str) -> bool:
    # All logic lives here.
    # If rules change, we change ONE function.
    # The rest of the app updates instantly.
    return True
```

---

## Part 1: The Source of Truth

We start by defining our patterns. These are the DNA of our validation system.

### 🔬 Try This! (Hands-On Practice #1)

Let's start our utilities library.

**Step 1: Create `shared/utils/validation.py`**

```python
import re
from typing import Optional

# 1. Define Patterns Constants
PROJECT_CODE_PATTERN = r"^PROJ-\d{4}-\d{4}$"  # PROJ-2025-0001
EMAIL_PATTERN = r"^[WwVcRd_.+-]+@[WwVcRd_.+-]+\.WwVcRd$"

def validate_pattern(value: str, pattern: str) -> bool:
    """Generic regex validator."""
    return bool(re.match(pattern, value))
```

**Step 2: Test it**
Create `test_utils.py`:
```python
from shared.utils.validation import validate_pattern, PROJECT_CODE_PATTERN

print(validate_pattern("PROJ-2025-0001", PROJECT_CODE_PATTERN)) # True
print(validate_pattern("bad-code", PROJECT_CODE_PATTERN))       # False
```

---

## Part 2: Reusable Validators

Generic functions are okay, but specific ones are better. They tell a story.

### 🔬 Try This! (Hands-On Practice #2)

Add specific validators to `shared/utils/validation.py`.

```python
def validate_project_code(code: str) -> bool:
    """Check if string is a valid Project Code."""
    return validate_pattern(code, PROJECT_CODE_PATTERN)

def validate_email(email: str) -> bool:
    """Check if string is a valid email."""
    return validate_pattern(email, EMAIL_PATTERN)
```

**Why wrapper functions?**
If `validate_project_code` logic becomes complex (e.g., checking database for duplicates), you can add it inside the wrapper without changing any code that calls it.

---

## Part 3: The Pydantic Connection

Pydantic raises `ValidationError`, which contains a huge JSON object. Users don't want JSON; they want "Invalid Email".

Let's build a utility to format Pydantic errors.

### 🔬 Try This! (Hands-On Practice #3)

Add this error extraction utility to `shared/utils/validation.py`.

```python
from pydantic import ValidationError

def format_validation_error(e: ValidationError) -> str:
    """
    Convert Pydantic error to human-readable string. 
    
    Example:
        Input: [
            {'loc': ('email',), 'msg': 'value is not a valid email address'}
        ]
        Output: "email: value is not a valid email address"
    """
    errors = []
    for error in e.errors():
        field = ".".join(str(x) for x in error['loc'])
        msg = error['msg']
        errors.append(f"{field}: {msg}")
    return "\n".join(errors)
```

**Test it:**
Update `test_utils.py`:
```python
from pydantic import BaseModel, Field, ValidationError
from shared.utils.validation import format_validation_error

class User(BaseModel):
    name: str = Field(min_length=3)

try:
    User(name="Jo")
except ValidationError as e:
    print("\nFormatted Error:")
    print(format_validation_error(e))
```

**Expected Output:**
```
Formatted Error:
name: String should have at least 3 characters
```

---

## Bringing It All Together: The Form Validator

Let's simulate a web form submission (like you'd see in Streamlit later).

**Challenge**: Create a function that takes a dict, validates it against a Model, and returns clean errors.

**Add to `shared/utils/validation.py`**:

```python
from typing import Dict, Any, Tuple, Type, TypeVar

T = TypeVar("T", bound=BaseModel)

def validate_model(model: Type[T], data: Dict[str, Any]) -> Tuple[Optional[T], Optional[str]]:
    """
    Validate dict against model. Returns (instance, error_message).
    
    Usage:
        user, error = validate_model(User, data)
        if error:
            print(error)
    """
    try:
        instance = model(**data)
        return instance, None
    except ValidationError as e:
        return None, format_validation_error(e)
```

**Test it:**
```python
# test_utils.py
user, error = validate_model(User, {"name": "Jo"})
if error:
    print(f"Validation Failed: {error}")
else:
    print(f"Success! {user}")
```

---

## Common Mistakes

### Mistake #1: Over-Engineering Regex

```python
# ❌ BAD: Attempting to validate every email RFC edge case
REGEX = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|...)"
```
**Why**: You will fail. The only way to truly validate an email is to send an email to it. Use a simple regex for sanity checks (has `@`, has `.`).

### Mistake #2: Raising Errors vs Returning False

- **Validators (`validate_email`)**: Should usually return `bool` (Simple check).
- **Parsers (`parse_email`)**: Should return value or raise Exception.
- **Model Validation**: Pydantic raises `ValidationError`.

Consistency is key. Decide if your utilities throw or return `False`. Our `validate_pattern` returns `bool`.

---

## Quick Reference Card

### Regex Cheatsheet

| Pattern | Matches |
|---------|---------|
| `^` | Start of string |
| `$` | End of string |
| `\d{4}` | Exactly 4 digits |
| `\w` | Word char (a-z, 0-9, _) |
| `\.` | Literal dot |

### Validation Utilities Template

```python
def validate_thing(value: str) -> bool:
    if not value: return False
    return bool(re.match(PATTERN, value))
```

---

## Verification (REQUIRED SECTION)

Let's ensure your utilities are robust.

**Create `verify_utils.py`**:

```python
"""
Verification script for Chapter 5.
"""
from shared.utils.validation import (
    validate_project_code,
    validate_email,
    validate_model,
    PROJECT_CODE_PATTERN
)
from pydantic import BaseModel, Field
import sys

print("🧪 Running Validation Utilities Verification...\n")

# Test 1: Project Code
print("Test 1: Project Code...")
assert validate_project_code("PROJ-2025-0001") is True
assert validate_project_code("PROJ-25-1") is False
assert validate_project_code("PROJECT-2025-0001") is False
print("✅ Project Code validation works!")

# Test 2: Email
print("Test 2: Email...")
assert validate_email("test@example.com") is True
assert validate_email("invalid-email") is False
print("✅ Email validation works!")

# Test 3: Model Helper
print("Test 3: Model Helper...")
class TestModel(BaseModel):
    val: int = Field(gt=10)

inst, err = validate_model(TestModel, {"val": 5})
assert inst is None
assert "val: Input should be greater than 10" in err
print("✅ Pydantic helper captures errors!")

print("\n🎉 Chapter 5 Complete! Your codebase is secure.")
```

**Run it:**
```bash
python verify_utils.py
```

---

## Summary

**What you learned:**

1. ✅ **Centralization**: Why putting logic in one place saves headaches later.
2. ✅ **Regex Patterns**: Defining `PROJ-\d{4}-\d{4}` once.
3. ✅ **Wrapper Functions**: Creating readable names like `validate_email`.
4. ✅ **Pydantic Translators**: Turning raw `ValidationError` into human text.
5. ✅ **Generic Validators**: Using `TypeVar` to make a universal model validator.

**Key Takeaway**: "Don't Repeat Yourself" (DRY) isn't just about saving keystrokes. It's about safety. When you fix a bug in `validate_email`, you fix it for the *entire application* instantly. ⚡

**Skills unlocked**: 🎯
- Regular Expressions
- Utility Library Design
- Error Handling

**Looking ahead**: In **Chapter 6**, we'll build the **Template System** using everything we've learned: Enums, Models, and Validation!

---

**Next**: [Chapter 6: Template System →](chapter-06-template-system.md)