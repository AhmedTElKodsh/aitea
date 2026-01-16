# Chapter 2: Enums & Type Hints

## Header

- **Phase**: 0 - Shared Foundation
- **Time Estimate**: 1.5 hours
- **Difficulty**: Beginner
- **Prerequisites**: Chapter 1
- **Builds**: `shared/models/enums.py`
- **Requirements**: Req 2, 8, 8.1, 9

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. **Explain** why enums are better than string constants for representing fixed sets of values
2. **Implement** Python enums using the `Enum` class from the standard library
3. **Apply** type hints to function parameters and return values
4. **Debug** common enum-related errors (invalid values, comparison issues)
5. **Compare** enums with alternative approaches (strings, integers, constants)

---

## Key Concepts

### 1. The Problem with String Constants

**Concrete Example First:**

Imagine you're building a contract system that supports different template types. Here's the naive approach:

```python
# ❌ BAD: Using raw strings everywhere
def load_template(template_type: str):
    if template_type == "engineering":
        return load_engineering_template()
    elif template_type == "consulting":
        return load_consulting_template()
    # ... more types

# What happens with typos?
load_template("enginering")  # Typo! No error until runtime
load_template("ENGINEERING")  # Wrong case! Fails silently
load_template("software")     # Invalid type! No validation
```

**Problems with String Constants:**

1. **No validation** - Any string is accepted, even invalid ones
2. **Typos** - Easy to misspell, IDE can't help
3. **Case sensitivity** - "engineering" vs "Engineering" vs "ENGINEERING"
4. **No autocomplete** - IDE doesn't know valid values
5. **Hard to refactor** - Changing a value requires finding all string literals

**Intuition:**
Think of enums like a multiple-choice question. Instead of letting users type any answer (string), you give them a fixed set of options to choose from.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STRING vs ENUM                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Strings (Open-ended)          Enums (Fixed choices)                │
│  ┌──────────────────┐          ┌──────────────────┐                 │
│  │ "engineering"    │          │ ○ ENGINEERING    │                 │
│  │ "enginering"     │          │ ○ CONSULTING     │                 │
│  │ "ENGINEERING"    │          │ ○ MILITARY       │                 │
│  │ "software"       │          │ ○ GOVERNMENTAL   │                 │
│  │ "anything!"      │          └──────────────────┘                 │
│  └──────────────────┘                                               │
│  ❌ Any value accepted         ✅ Only valid choices                │
│  ❌ No IDE autocomplete        ✅ IDE shows options                 │
│  ❌ Typos cause bugs           ✅ Typos caught immediately          │
└─────────────────────────────────────────────────────────────────────┘
```

**Formal Definition:**
An **enumeration (enum)** is a set of symbolic names bound to unique, constant values. Enums provide type-safe representation of a fixed set of related constants.

---

### 2. Python Enums: The Solution

**Concrete Example First:**

```python
from enum import Enum

# ✅ GOOD: Define valid template types as an enum
class TemplateType(Enum):
    ENGINEERING = "engineering"
    CONSULTING = "consulting"
    MILITARY = "military"
    GOVERNMENTAL = "governmental"

# Now the function signature is type-safe
def load_template(template_type: TemplateType):
    if template_type == TemplateType.ENGINEERING:
        return load_engineering_template()
    elif template_type == TemplateType.CONSULTING:
        return load_consulting_template()
    # ... more types

# Usage - IDE autocompletes after typing "TemplateType."
load_template(TemplateType.ENGINEERING)  # ✅ Valid
load_template(TemplateType.CONSULTING)   # ✅ Valid

# These cause errors BEFORE running the code:
load_template("engineering")             # ❌ Type error (IDE catches)
load_template(TemplateType.ENGINERING)   # ❌ Attribute error (typo caught)
```

**Benefits of Enums:**

| Feature               | Strings | Enums |
| --------------------- | ------- | ----- |
| Type safety           | ❌      | ✅    |
| IDE autocomplete      | ❌      | ✅    |
| Typo detection        | ❌      | ✅    |
| Refactoring support   | ❌      | ✅    |
| Exhaustiveness checks | ❌      | ✅    |
| Documentation         | ❌      | ✅    |

---

### 3. Type Hints: Making Python Safer

**Concrete Example First:**

```python
# ❌ WITHOUT type hints - what does this function expect?
def calculate_score(report):
    return report.matched / report.total

# What is 'report'? A dict? An object? What fields does it have?
# You have to read the code or docs to know.

# ✅ WITH type hints - crystal clear
def calculate_score(report: ComplianceReport) -> float:
    return report.matched / report.total

# Now it's obvious:
# - Input: ComplianceReport object
# - Output: float (decimal number)
# - IDE can autocomplete report.matched, report.total
```

**Why Type Hints Matter for AI Projects:**

AI/ML code often involves complex data transformations:

```python
# Without type hints - what are these?
def embed_text(text):
    return model.encode(text)

def search_similar(query, store):
    embedding = embed_text(query)
    return store.search(embedding, k=5)

# With type hints - much clearer!
def embed_text(text: str) -> np.ndarray:
    """Convert text to embedding vector."""
    return model.encode(text)

def search_similar(
    query: str,
    store: HistoricalDataStore
) -> list[tuple[str, float]]:
    """Search for similar clauses, return (text, similarity) pairs."""
    embedding = embed_text(query)
    return store.search(embedding, k=5)
```

**Type Hints Flow:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TYPE HINTS IN ACTION                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  You Write Code          IDE Helps You           Type Checker        │
│  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐    │
│  │ def func(    │       │ Autocomplete │       │ mypy checks  │    │
│  │   x: str     │ ───▶  │ shows str    │ ───▶  │ all calls    │    │
│  │ ) -> int:    │       │ methods      │       │ match types  │    │
│  │   return...  │       └──────────────┘       └──────────────┘    │
│  └──────────────┘                                                   │
│                                                                      │
│  Benefits:                                                           │
│  ✅ Catch bugs before running code                                  │
│  ✅ Better IDE autocomplete                                         │
│  ✅ Self-documenting code                                           │
│  ✅ Easier refactoring                                              │
└─────────────────────────────────────────────────────────────────────┘
```

**Formal Definition:**
**Type hints** (also called type annotations) are optional syntax in Python 3.5+ that specify the expected types of variables, function parameters, and return values. They enable static type checking and improve code documentation.

---

### 4. Enum Anatomy

Let's break down how enums work in Python:

```python
from enum import Enum

class TemplateType(Enum):
    # NAME = value
    ENGINEERING = "engineering"
    CONSULTING = "consulting"
```

**Key Components:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENUM STRUCTURE                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  class TemplateType(Enum):                                          │
│        ↑            ↑                                                │
│        │            └─ Inherit from Enum base class                 │
│        └─ Your enum name (PascalCase by convention)                 │
│                                                                      │
│      ENGINEERING = "engineering"                                     │
│      ↑            ↑                                                  │
│      │            └─ Value (what gets stored/compared)               │
│      └─ Member name (UPPER_CASE by convention)                      │
│                                                                      │
│  Access:                                                             │
│  TemplateType.ENGINEERING        # The enum member                  │
│  TemplateType.ENGINEERING.name   # "ENGINEERING" (string)           │
│  TemplateType.ENGINEERING.value  # "engineering" (string)           │
└─────────────────────────────────────────────────────────────────────┘
```

**Important Properties:**

```python
# Member access
member = TemplateType.ENGINEERING

# Get the name (useful for display)
print(member.name)   # "ENGINEERING"

# Get the value (useful for storage/serialization)
print(member.value)  # "engineering"

# Comparison (use == or 'is')
if member == TemplateType.ENGINEERING:
    print("It's an engineering template!")

# Iteration (get all members)
for template_type in TemplateType:
    print(f"{template_type.name}: {template_type.value}")

# Lookup by value
template = TemplateType("engineering")  # Returns TemplateType.ENGINEERING
```

---

## Implementation

Now it's your turn to implement `shared/models/enums.py`! This file will define two enums used throughout the project.

### Step 1: Understand What You're Building

You'll create two enums:

1. **TemplateType** - Represents the four types of contract templates
2. **SeverityLevel** - Represents compliance issue severity (high, medium, low)

These enums will be used in:

- Chapter 3: Data models (Contract, ComplianceIssue)
- Chapter 5: Template loading system
- Chapter 14-16: Contract generation and review
- Chapter 32-36: Streamlit UI

---

### Step 2: Create the File Structure

```bash
# WHY: Organize code into logical modules
# WHAT: Create the shared/models directory
# HOW: Use mkdir to create nested directories

# Windows CMD
mkdir shared\models

# Windows PowerShell / macOS / Linux
mkdir -p shared/models
```

### Step 3: Implementation Guidance

**File: `shared/models/enums.py`**

Here's the structure you need to implement. I'll provide guidance and example patterns, but you'll write the actual code.

#### Example Pattern: Creating an Enum

Here's a generic example showing how to create an enum (NOT the exact solution):

```python
from enum import Enum

class Color(Enum):
    """
    Represents available colors.

    WHY: Type-safe color selection instead of strings
    WHAT: Fixed set of color options
    HOW: Each member maps name to hex value
    """
    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"

    def __str__(self) -> str:
        """Return the color name for display."""
        return self.name.lower()
```

**Key Points from This Pattern:**

1. Import `Enum` from the `enum` module
2. Class inherits from `Enum`
3. Docstring explains WHY/WHAT/HOW
4. Members use UPPER_CASE names
5. Values can be strings, integers, or any type
6. Optional: Add `__str__` method for custom string representation

---

#### Your Task: Implement TemplateType

**Requirements:**

1. Create a `TemplateType` enum with four members:

   - ENGINEERING (value: "engineering")
   - CONSULTING (value: "consulting")
   - MILITARY (value: "military")
   - GOVERNMENTAL (value: "governmental")

2. Add a comprehensive docstring explaining:

   - WHY: Why we use an enum instead of strings
   - WHAT: What this enum represents
   - HOW: How it's used in the system

3. Add a `__str__` method that returns a human-readable name:
   - ENGINEERING → "Engineering"
   - CONSULTING → "Consulting"
   - MILITARY → "Military"
   - GOVERNMENTAL → "Governmental"

**Starter Scaffold:**

```python
"""
Enumerations for the AI Contract Generator.

WHY: Enums provide type-safe alternatives to string constants
WHAT: Defines TemplateType and SeverityLevel enums
HOW: Used throughout the system for type checking and validation
"""

from enum import Enum


class TemplateType(Enum):
    """
    Contract template types supported by the system.

    WHY: [Your explanation - why enum instead of strings?]
    WHAT: [Your explanation - what does this represent?]
    HOW: [Your explanation - where is this used?]

    Example:
        >>> template_type = TemplateType.ENGINEERING
        >>> print(template_type.value)
        engineering
        >>> print(str(template_type))
        Engineering
    """
    # TODO: Add the four template type members here
    # Hint: MEMBER_NAME = "value"
    pass

    def __str__(self) -> str:
        """
        Return human-readable template type name.

        Returns:
            Capitalized template type name (e.g., "Engineering")

        WHY: [Your explanation]
        WHAT: [Your explanation]
        HOW: [Your explanation]
        """
        # TODO: Implement this method
        # Hint: self.name is "ENGINEERING", you want "Engineering"
        pass
```

---

#### Your Task: Implement SeverityLevel

**Requirements:**

1. Create a `SeverityLevel` enum with three members:

   - HIGH (value: "high")
   - MEDIUM (value: "medium")
   - LOW (value: "low")

2. Add a comprehensive docstring with WHY/WHAT/HOW

3. Add a `__str__` method that returns capitalized severity:

   - HIGH → "High"
   - MEDIUM → "Medium"
   - LOW → "Low"

4. Add a `get_priority` method that returns an integer priority:
   - HIGH → 1 (highest priority)
   - MEDIUM → 2
   - LOW → 3 (lowest priority)

**Why `get_priority`?**
This method will be used in Chapter 15 to sort compliance issues by severity. Higher severity issues should appear first in reports.

**Starter Scaffold:**

```python
class SeverityLevel(Enum):
    """
    Severity levels for compliance issues.

    WHY: [Your explanation - why enum for severity?]
    WHAT: [Your explanation - what does this represent?]
    HOW: [Your explanation - where is this used?]

    Example:
        >>> severity = SeverityLevel.HIGH
        >>> print(severity.value)
        high
        >>> print(str(severity))
        High
        >>> print(severity.get_priority())
        1
    """
    # TODO: Add the three severity level members here
    pass

    def __str__(self) -> str:
        """
        Return human-readable severity level.

        Returns:
            Capitalized severity level (e.g., "High")
        """
        # TODO: Implement this method
        pass

    def get_priority(self) -> int:
        """
        Get numeric priority for sorting (lower number = higher priority).

        Returns:
            Priority value (1=HIGH, 2=MEDIUM, 3=LOW)

        WHY: [Your explanation - why do we need numeric priority?]
        WHAT: [Your explanation - what does priority represent?]
        HOW: [Your explanation - how is this used for sorting?]

        Example:
            >>> issues = [issue1, issue2, issue3]
            >>> sorted_issues = sorted(issues, key=lambda i: i.severity.get_priority())
            >>> # Now issues are ordered: HIGH, MEDIUM, LOW
        """
        # TODO: Implement this method
        # Hint: Use a dictionary or if/elif to map self to priority
        pass
```

---

### Step 4: Implementation Hints

**Hint 1: String Manipulation**

```python
# To convert "ENGINEERING" to "Engineering":
name = "ENGINEERING"
capitalized = name.capitalize()  # "Engineering"

# Or use title() for multi-word names:
name = "MULTI_WORD"
title_case = name.replace("_", " ").title()  # "Multi Word"
```

**Hint 2: Mapping Enum Members to Values**

```python
# Option 1: Dictionary
def get_priority(self) -> int:
    priority_map = {
        SeverityLevel.HIGH: 1,
        SeverityLevel.MEDIUM: 2,
        SeverityLevel.LOW: 3,
    }
    return priority_map[self]

# Option 2: If/elif
def get_priority(self) -> int:
    if self == SeverityLevel.HIGH:
        return 1
    elif self == SeverityLevel.MEDIUM:
        return 2
    else:  # LOW
        return 3
```

**Hint 3: Type Hints**

```python
# Return type for __str__ is always str
def __str__(self) -> str:
    return "something"

# Return type for get_priority is int
def get_priority(self) -> int:
    return 1
```

---

### Step 5: Acceptance Criteria

Your implementation is complete when:

- [ ] `shared/models/enums.py` file exists
- [ ] `TemplateType` enum has all four members (ENGINEERING, CONSULTING, MILITARY, GOVERNMENTAL)
- [ ] `TemplateType.__str__()` returns capitalized names
- [ ] `SeverityLevel` enum has all three members (HIGH, MEDIUM, LOW)
- [ ] `SeverityLevel.__str__()` returns capitalized names
- [ ] `SeverityLevel.get_priority()` returns correct priorities (1, 2, 3)
- [ ] All docstrings include WHY/WHAT/HOW annotations
- [ ] Type hints are present on all methods

---

### Step 6: Verification Commands

After implementing, run these commands to verify your code works:

```bash
# Test 1: Import the enums
python -c "from shared.models.enums import TemplateType, SeverityLevel; print('✓ Imports work')"

# Test 2: Check TemplateType members
python -c "from shared.models.enums import TemplateType; print([t.value for t in TemplateType])"
# Expected: ['engineering', 'consulting', 'military', 'governmental']

# Test 3: Check TemplateType.__str__
python -c "from shared.models.enums import TemplateType; print(str(TemplateType.ENGINEERING))"
# Expected: Engineering

# Test 4: Check SeverityLevel members
python -c "from shared.models.enums import SeverityLevel; print([s.value for s in SeverityLevel])"
# Expected: ['high', 'medium', 'low']

# Test 5: Check SeverityLevel.__str__
python -c "from shared.models.enums import SeverityLevel; print(str(SeverityLevel.HIGH))"
# Expected: High

# Test 6: Check SeverityLevel.get_priority
python -c "from shared.models.enums import SeverityLevel; print(SeverityLevel.HIGH.get_priority(), SeverityLevel.MEDIUM.get_priority(), SeverityLevel.LOW.get_priority())"
# Expected: 1 2 3

# Test 7: Check sorting by priority
python -c "from shared.models.enums import SeverityLevel; levels = [SeverityLevel.LOW, SeverityLevel.HIGH, SeverityLevel.MEDIUM]; sorted_levels = sorted(levels, key=lambda s: s.get_priority()); print([str(s) for s in sorted_levels])"
# Expected: ['High', 'Medium', 'Low']
```

**All tests passing?** Great! You've successfully implemented the enums. 🎉

---

## From Scratch vs With Framework

### Manual Approach (What We're Doing)

```python
# Manual: Standard library Enum
from enum import Enum

class TemplateType(Enum):
    ENGINEERING = "engineering"
    CONSULTING = "consulting"
```

**Pros:**

- ✅ No extra dependencies
- ✅ Standard Python, works everywhere
- ✅ Simple and explicit
- ✅ Full control over behavior

**Cons:**

- ❌ Manual string conversion methods
- ❌ No automatic validation helpers
- ❌ More boilerplate for complex enums

---

### Framework Approach (Pydantic, StrEnum)

```python
# Python 3.11+ StrEnum (simpler for string enums)
from enum import StrEnum

class TemplateType(StrEnum):
    ENGINEERING = "engineering"
    CONSULTING = "consulting"
    # __str__ automatically returns the value!

# Or Pydantic for validation
from pydantic import BaseModel

class Contract(BaseModel):
    template_type: TemplateType  # Automatic validation!
```

**Pros:**

- ✅ Less boilerplate (StrEnum)
- ✅ Automatic validation (Pydantic)
- ✅ Better serialization support

**Cons:**

- ❌ Requires Python 3.11+ (StrEnum)
- ❌ Extra dependency (Pydantic)
- ❌ More "magic" behavior

**Why We Chose Manual:**
We're using standard `Enum` because:

1. Works with Python 3.8+ (broader compatibility)
2. Explicit behavior (educational)
3. Full control over behavior

**Note:** Pydantic is already used in Chapter 1 for configuration management (`config.py`). For enums specifically, standard library `Enum` is sufficient and keeps things simple. When you use enums with Pydantic models (like `Contract(BaseModel)`), Pydantic automatically validates enum values!

---

## Interactive Checkpoints

Complete these checkpoints to verify your understanding:

### ✅ Checkpoint 1: Enum Members Exist

```python
# Run this in Python REPL or as a script
from shared.models.enums import TemplateType, SeverityLevel

# Check TemplateType
print("TemplateType members:")
for template in TemplateType:
    print(f"  {template.name} = {template.value}")

# Check SeverityLevel
print("\nSeverityLevel members:")
for severity in SeverityLevel:
    print(f"  {severity.name} = {severity.value}")
```

**Expected Output:**

```
TemplateType members:
  ENGINEERING = engineering
  CONSULTING = consulting
  MILITARY = military
  GOVERNMENTAL = governmental

SeverityLevel members:
  HIGH = high
  MEDIUM = medium
  LOW = low
```

- [ ] All enum members are present and have correct values

---

### ✅ Checkpoint 2: String Representation Works

```python
from shared.models.enums import TemplateType, SeverityLevel

# Test TemplateType.__str__
print(f"Template: {TemplateType.ENGINEERING}")
print(f"Template: {TemplateType.CONSULTING}")

# Test SeverityLevel.__str__
print(f"Severity: {SeverityLevel.HIGH}")
print(f"Severity: {SeverityLevel.MEDIUM}")
```

**Expected Output:**

```
Template: Engineering
Template: Consulting
Severity: High
Severity: Medium
```

- [ ] String representation is capitalized correctly

---

### ✅ Checkpoint 3: Priority Sorting Works

```python
from shared.models.enums import SeverityLevel

# Create a list of severities in random order
severities = [
    SeverityLevel.LOW,
    SeverityLevel.HIGH,
    SeverityLevel.MEDIUM,
    SeverityLevel.LOW,
    SeverityLevel.HIGH,
]

# Sort by priority (HIGH first, LOW last)
sorted_severities = sorted(severities, key=lambda s: s.get_priority())

# Print results
print("Sorted severities:")
for severity in sorted_severities:
    print(f"  {severity} (priority: {severity.get_priority()})")
```

**Expected Output:**

```
Sorted severities:
  High (priority: 1)
  High (priority: 1)
  Medium (priority: 2)
  Low (priority: 3)
  Low (priority: 3)
```

- [ ] Severities are sorted correctly (HIGH → MEDIUM → LOW)

---

### ✅ Checkpoint 4: Type Hints Enable IDE Features

Open `shared/models/enums.py` in your IDE and try these:

1. Type `TemplateType.` and press Ctrl+Space (or Cmd+Space on Mac)

   - [ ] IDE shows autocomplete with ENGINEERING, CONSULTING, MILITARY, GOVERNMENTAL

2. Type `severity = SeverityLevel.HIGH` then `severity.` and press Ctrl+Space

   - [ ] IDE shows autocomplete with `name`, `value`, `get_priority()`

3. Hover over `get_priority` method
   - [ ] IDE shows the docstring and return type `-> int`

---

## Debugging Scenario

### The Bug

A learner implemented `SeverityLevel.get_priority()` like this:

```python
def get_priority(self) -> int:
    if self.value == "high":
        return 1
    elif self.value == "medium":
        return 2
    else:
        return 3
```

When they run this code:

```python
from shared.models.enums import SeverityLevel

severities = [SeverityLevel.LOW, SeverityLevel.HIGH, SeverityLevel.MEDIUM]
sorted_severities = sorted(severities, key=lambda s: s.get_priority())
print([str(s) for s in sorted_severities])
```

They get: `['High', 'Medium', 'Low']` ✅ (correct!)

But their IDE shows a warning: "Comparing enum member to string is not recommended"

### Your Task

1. Why does the IDE show this warning?
2. What's a better way to implement `get_priority()`?
3. What could go wrong with the current implementation?

<details>
<summary>💡 Click to reveal the answer</summary>

**Root Cause:**
Comparing `self.value` (a string) to string literals works, but it's not type-safe. If someone changes the enum values, the comparisons break silently.

**Better Implementation:**
Compare enum members directly, not their values:

```python
def get_priority(self) -> int:
    # ✅ GOOD: Compare enum members
    if self == SeverityLevel.HIGH:
        return 1
    elif self == SeverityLevel.MEDIUM:
        return 2
    else:  # LOW
        return 3
```

**Or use a dictionary:**

```python
def get_priority(self) -> int:
    # ✅ EVEN BETTER: Dictionary mapping
    priority_map = {
        SeverityLevel.HIGH: 1,
        SeverityLevel.MEDIUM: 2,
        SeverityLevel.LOW: 3,
    }
    return priority_map[self]
```

**What Could Go Wrong:**

```python
# If someone changes the enum value:
class SeverityLevel(Enum):
    HIGH = "critical"  # Changed from "high"!
    MEDIUM = "medium"
    LOW = "low"

# The string comparison breaks:
if self.value == "high":  # Never true anymore!
    return 1

# But enum comparison still works:
if self == SeverityLevel.HIGH:  # Still works!
    return 1
```

**Key Lesson:** Always compare enum members directly (`self == SeverityLevel.HIGH`), not their values (`self.value == "high"`).

</details>

---

## Quick Check Questions

Test your understanding with these questions:

### Question 1

What's the difference between `TemplateType.ENGINEERING.name` and `TemplateType.ENGINEERING.value`?

<details>
<summary>Answer</summary>

**Answer:**

- **`.name`** returns the member name as a string: `"ENGINEERING"`
- **`.value`** returns the member's assigned value: `"engineering"`

```python
member = TemplateType.ENGINEERING
print(member.name)   # "ENGINEERING" (the Python identifier)
print(member.value)  # "engineering" (the assigned value)
```

**When to use each:**

- Use `.name` for display in UI (after formatting): `member.name.capitalize()` → "Engineering"
- Use `.value` for storage/serialization: Save "engineering" to database
- Use the member itself for comparisons: `if template_type == TemplateType.ENGINEERING:`

</details>

---

### Question 2

Why do we use `UPPER_CASE` for enum member names?

<details>
<summary>Answer</summary>

**Answer:** It's a Python convention (PEP 8) that constants should be named in `UPPER_CASE`. Since enum members are constants (they don't change), we follow this convention.

```python
# ✅ GOOD: Follows convention
class TemplateType(Enum):
    ENGINEERING = "engineering"
    CONSULTING = "consulting"

# ❌ BAD: Doesn't follow convention (but technically works)
class TemplateType(Enum):
    engineering = "engineering"
    consulting = "consulting"
```

**Benefits of following convention:**

1. **Readability** - Immediately recognizable as constants
2. **Consistency** - Matches other Python code
3. **IDE support** - Some IDEs highlight constants differently

</details>

---

### Question 3

Can you create an enum member from its value? How?

<details>
<summary>Answer</summary>

**Answer:** Yes! Use the enum class as a callable with the value:

```python
# Create enum member from value
template = TemplateType("engineering")
print(template)  # TemplateType.ENGINEERING

# This is useful for deserialization
def load_template_from_db(value: str) -> TemplateType:
    return TemplateType(value)

# If the value doesn't exist, raises ValueError
try:
    invalid = TemplateType("invalid")
except ValueError as e:
    print(f"Error: {e}")
    # Error: 'invalid' is not a valid TemplateType
```

**Common use cases:**

- Loading from database: `TemplateType(row["template_type"])`
- Parsing API requests: `TemplateType(request.json["type"])`
- Reading config files: `TemplateType(config["template"])`

</details>

---

### Question 4

What happens if you try to compare an enum member to a string?

<details>
<summary>Answer</summary>

**Answer:** It returns `False` (they're different types), but it's not recommended:

```python
template = TemplateType.ENGINEERING

# ❌ BAD: Comparing enum to string
if template == "engineering":  # False! Different types
    print("This won't print")

# ✅ GOOD: Compare to enum member
if template == TemplateType.ENGINEERING:  # True!
    print("This will print")

# ✅ ALSO GOOD: Compare values if needed
if template.value == "engineering":  # True!
    print("This will print")
```

**Why it matters:**

```python
# This bug is silent - no error, just wrong behavior
def process_template(template_type: TemplateType):
    if template_type == "engineering":  # Always False!
        return "Engineering template"
    else:
        return "Other template"

result = process_template(TemplateType.ENGINEERING)
print(result)  # "Other template" - WRONG!
```

**Key Lesson:** Always compare enum members to enum members, not strings.

</details>

---

### Question 5

Why do we add type hints to the `__str__` and `get_priority` methods?

<details>
<summary>Answer</summary>

**Answer:** Type hints serve multiple purposes:

1. **Documentation** - Shows what the method returns without reading code
2. **IDE support** - Enables autocomplete and type checking
3. **Static analysis** - Tools like `mypy` can catch type errors
4. **Runtime validation** - Libraries like Pydantic can enforce types

```python
# Without type hint - unclear what this returns
def get_priority(self):
    return 1

# With type hint - crystal clear
def get_priority(self) -> int:
    return 1

# Now the IDE knows:
severity = SeverityLevel.HIGH
priority = severity.get_priority()  # IDE knows this is an int
result = priority + 10  # IDE knows this is valid (int + int)
result = priority + "10"  # IDE warns: can't add int + str
```

**Type hints are especially valuable in AI/ML projects** where data flows through many transformations:

```python
# Clear data flow with type hints
def embed_text(text: str) -> np.ndarray: ...
def search_similar(embedding: np.ndarray) -> list[tuple[str, float]]: ...
def rank_results(results: list[tuple[str, float]]) -> list[str]: ...
```

</details>

---

## Mini-Project

### Challenge: Add a ContractStatus Enum

Extend `shared/models/enums.py` with a new enum for tracking contract lifecycle status.

**Requirements:**

1. Create a `ContractStatus` enum with these members:

   - DRAFT (value: "draft")
   - UNDER_REVIEW (value: "under_review")
   - APPROVED (value: "approved")
   - REJECTED (value: "rejected")
   - ARCHIVED (value: "archived")

2. Add a `__str__` method that returns human-readable status:

   - DRAFT → "Draft"
   - UNDER_REVIEW → "Under Review"
   - APPROVED → "Approved"
   - REJECTED → "Rejected"
   - ARCHIVED → "Archived"

3. Add a `is_final()` method that returns `True` for terminal states:

   - APPROVED, REJECTED, ARCHIVED → `True`
   - DRAFT, UNDER_REVIEW → `False`

4. Add a `can_transition_to(target: 'ContractStatus')` method that validates state transitions:
   - DRAFT can transition to: UNDER_REVIEW, ARCHIVED
   - UNDER_REVIEW can transition to: APPROVED, REJECTED, DRAFT
   - APPROVED can transition to: ARCHIVED
   - REJECTED can transition to: ARCHIVED, DRAFT
   - ARCHIVED cannot transition to anything

**Starter Scaffold:**

```python
class ContractStatus(Enum):
    """
    Contract lifecycle status.

    WHY: [Your explanation - why track contract status?]
    WHAT: [Your explanation - what do these statuses represent?]
    HOW: [Your explanation - how is this used in the workflow?]

    Example:
        >>> status = ContractStatus.DRAFT
        >>> print(str(status))
        Draft
        >>> print(status.is_final())
        False
        >>> print(status.can_transition_to(ContractStatus.UNDER_REVIEW))
        True
    """
    # TODO: Add the five status members here
    pass

    def __str__(self) -> str:
        """Return human-readable status name."""
        # TODO: Implement this
        # Hint: Handle UNDER_REVIEW specially (two words)
        pass

    def is_final(self) -> bool:
        """
        Check if this is a terminal state.

        Returns:
            True if status is final (APPROVED, REJECTED, ARCHIVED)

        WHY: [Your explanation]
        WHAT: [Your explanation]
        HOW: [Your explanation]
        """
        # TODO: Implement this
        pass

    def can_transition_to(self, target: 'ContractStatus') -> bool:
        """
        Check if transition to target status is valid.

        Args:
            target: The status to transition to

        Returns:
            True if transition is allowed

        WHY: [Your explanation - why validate transitions?]
        WHAT: [Your explanation - what makes a transition valid?]
        HOW: [Your explanation - how is this used?]

        Example:
            >>> draft = ContractStatus.DRAFT
            >>> draft.can_transition_to(ContractStatus.UNDER_REVIEW)
            True
            >>> draft.can_transition_to(ContractStatus.APPROVED)
            False
        """
        # TODO: Implement this
        # Hint: Use a dictionary mapping each status to allowed targets
        pass
```

**Acceptance Criteria:**

- [ ] `ContractStatus` enum exists with all five members
- [ ] `__str__()` returns properly formatted names (including "Under Review")
- [ ] `is_final()` returns `True` only for APPROVED, REJECTED, ARCHIVED
- [ ] `can_transition_to()` enforces the transition rules correctly
- [ ] All methods have comprehensive docstrings with WHY/WHAT/HOW
- [ ] Type hints are present on all methods

**Verification Commands:**

```bash
# Test 1: Check members
python -c "from shared.models.enums import ContractStatus; print([s.value for s in ContractStatus])"
# Expected: ['draft', 'under_review', 'approved', 'rejected', 'archived']

# Test 2: Check string representation
python -c "from shared.models.enums import ContractStatus; print(str(ContractStatus.UNDER_REVIEW))"
# Expected: Under Review

# Test 3: Check is_final
python -c "from shared.models.enums import ContractStatus; print(ContractStatus.DRAFT.is_final(), ContractStatus.APPROVED.is_final())"
# Expected: False True

# Test 4: Check valid transition
python -c "from shared.models.enums import ContractStatus; print(ContractStatus.DRAFT.can_transition_to(ContractStatus.UNDER_REVIEW))"
# Expected: True

# Test 5: Check invalid transition
python -c "from shared.models.enums import ContractStatus; print(ContractStatus.DRAFT.can_transition_to(ContractStatus.APPROVED))"
# Expected: False

# Test 6: Check archived cannot transition
python -c "from shared.models.enums import ContractStatus; print(ContractStatus.ARCHIVED.can_transition_to(ContractStatus.DRAFT))"
# Expected: False
```

**Suggested Extensions:**

1. Add a `get_next_statuses()` method that returns a list of valid next statuses
2. Add a `get_color()` method that returns a color for UI display (e.g., APPROVED → "green")
3. Add a `requires_approval()` method that returns `True` for UNDER_REVIEW
4. Create a state transition diagram using ASCII art or Mermaid

**Hint for `__str__` with UNDER_REVIEW:**

```python
# Option 1: Special case
if self == ContractStatus.UNDER_REVIEW:
    return "Under Review"
else:
    return self.name.capitalize()

# Option 2: Replace underscores
return self.name.replace("_", " ").title()
# "UNDER_REVIEW" → "Under Review"
```

---

## Project Integration Notes

### What We Built

In this chapter, we created the foundational enums that will be used throughout the entire project:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CHAPTER 2 DELIVERABLES                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ✅ shared/models/enums.py                                          │
│     ├── TemplateType (4 members)                                    │
│     │   └── Used for contract template selection                    │
│     └── SeverityLevel (3 members)                                   │
│         └── Used for compliance issue prioritization                │
│                                                                      │
│  These enums provide type-safe alternatives to string constants!    │
└─────────────────────────────────────────────────────────────────────┘
```

### How It Connects to Other Chapters

| Chapter                        | Uses From Chapter 2                      |
| ------------------------------ | ---------------------------------------- |
| Ch 3 (Dataclasses)             | `TemplateType` in Contract model         |
|                                | `SeverityLevel` in ComplianceIssue model |
| Ch 5 (Template System)         | `TemplateType` for template lookup       |
| Ch 6 (Property Testing)        | Enum validation properties (P11, P12)    |
| Ch 14 (Contract Generator)     | `TemplateType` for template selection    |
| Ch 15-16 (Compliance Reviewer) | `SeverityLevel` for issue prioritization |
| Ch 32-36 (Streamlit UI)        | Both enums for dropdowns and display     |

### Enum Usage Pattern

Here's how these enums will be used in future chapters:

```python
# Chapter 3: Dataclasses will use these enums
@dataclass
class Contract:
    template_type: TemplateType  # Type-safe template selection
    # ... other fields

@dataclass
class ComplianceIssue:
    severity: SeverityLevel  # Type-safe severity levels
    # ... other fields

# Chapter 5: Template loading
def load_template(template_type: TemplateType) -> dict:
    template_path = f"templates/{template_type.value}.yaml"
    # ...

# Chapter 15: Sorting compliance issues
def sort_issues(issues: list[ComplianceIssue]) -> list[ComplianceIssue]:
    return sorted(issues, key=lambda i: i.severity.get_priority())

# Chapter 32: Streamlit UI
template_type = st.selectbox(
    "Template Type",
    options=list(TemplateType),
    format_func=str  # Uses our __str__ method!
)
```

---

### What's Next

**Chapter 3: Dataclasses & Data Models** will build on these enums by:

- Creating `Contract` dataclass with `template_type: TemplateType` field
- Creating `ComplianceIssue` dataclass with `severity: SeverityLevel` field
- Learning how dataclasses + enums = type-safe data models
- Understanding automatic validation and serialization

**Preview of Chapter 3:**

```python
from dataclasses import dataclass
from shared.models.enums import TemplateType, SeverityLevel

@dataclass
class Contract:
    project_code: str
    template_type: TemplateType  # ← Using our enum!
    sections: list[Section]

@dataclass
class ComplianceIssue:
    clause_id: str
    severity: SeverityLevel  # ← Using our enum!
    description: str
```

---

## Summary

In this chapter, you learned:

1. **Why Enums** - Type-safe alternatives to string constants
2. **Python Enum Class** - How to create and use enums
3. **Type Hints** - Annotating functions for better IDE support
4. **Enum Methods** - Adding behavior to enum members
5. **Best Practices** - Comparing members, not values

**Key Takeaways:**

- Enums prevent typos and invalid values at development time
- Type hints enable IDE autocomplete and static type checking
- Always compare enum members directly (`==`), not their values
- Add methods to enums for domain-specific behavior (like `get_priority()`)
- Follow Python conventions: `UPPER_CASE` for enum members

**Design Patterns Learned:**

- **Enum Pattern** - Fixed set of related constants
- **Priority Pattern** - Numeric ordering for sorting
- **String Representation** - Custom `__str__` for display

**Next Chapter:** [Chapter 3: Dataclasses & Data Models](./chapter-03-dataclasses-models.md)

---

## Additional Resources

### Official Documentation

- [Python Enum Documentation](https://docs.python.org/3/library/enum.html)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)

### Further Reading

- [Real Python: Python Enums](https://realpython.com/python-enum/)
- [Real Python: Type Checking](https://realpython.com/python-type-checking/)
- [mypy Documentation](https://mypy.readthedocs.io/)

### Common Pitfalls

1. **Comparing to strings instead of enum members**

   ```python
   # ❌ BAD
   if template == "engineering":

   # ✅ GOOD
   if template == TemplateType.ENGINEERING:
   ```

2. **Forgetting to import Enum**

   ```python
   # ❌ BAD
   class TemplateType:  # Missing (Enum)

   # ✅ GOOD
   from enum import Enum
   class TemplateType(Enum):
   ```

3. **Using lowercase enum member names**

   ```python
   # ❌ BAD (works but violates convention)
   class TemplateType(Enum):
       engineering = "engineering"

   # ✅ GOOD (follows PEP 8)
   class TemplateType(Enum):
       ENGINEERING = "engineering"
   ```

4. **Not adding type hints to methods**

   ```python
   # ❌ BAD (no type hints)
   def get_priority(self):
       return 1

   # ✅ GOOD (with type hints)
   def get_priority(self) -> int:
       return 1
   ```

---

**Congratulations!** You've completed Chapter 2 and built the foundational enums for the AI Contract Generator. These type-safe enums will be used throughout the entire project. 🎉

Ready to continue? Move on to [Chapter 3: Dataclasses & Data Models](./chapter-03-dataclasses-models.md) to build the core data structures!
