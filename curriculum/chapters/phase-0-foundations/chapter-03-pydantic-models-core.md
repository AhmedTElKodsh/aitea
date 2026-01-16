# Chapter 3: Pydantic Models (Core)

## Header

- **Phase**: 0 - Foundation (Pydantic-First)
- **Time Estimate**: 2 hours
- **Difficulty**: Beginner
- **Prerequisites**: Chapter 2 (Type Hints & Enums)
- **Builds**: `shared/models/contract.py`
- **Requirements**: Req 2, 8, 8.1, 9

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. **Implement** Pydantic BaseModel classes for data validation
2. **Apply** Field constraints for declarative validation
3. **Create** nested Pydantic models for complex data structures
4. **Explain** why Pydantic is preferred over dataclasses for AI/LLM projects
5. **Debug** common Pydantic validation errors

---

## Key Concepts

### 1. Why Pydantic for AI Projects?

**Concrete Example First:**

Imagine you're building a contract system. Here's what happens without validation:

```python
# ❌ Without Pydantic - chaos!
contract = {
    "title": "",  # Empty title - should be invalid!
    "value": -1000,  # Negative value - nonsense!
    "sections": "not a list",  # Wrong type!
}

# No errors until you try to use it...
for section in contract["sections"]:  # TypeError at runtime!
    print(section)
```

With Pydantic, errors are caught immediately:

```python
# ✅ With Pydantic - safe!
from pydantic import BaseModel, Field

class Contract(BaseModel):
    title: str = Field(..., min_length=1)
    value: float = Field(..., gt=0)
    sections: list = Field(default_factory=list)

# Invalid data rejected immediately
contract = Contract(
    title="",  # ❌ ValidationError: min_length=1
    value=-1000,  # ❌ ValidationError: gt=0
    sections="not a list"  # ❌ ValidationError: wrong type
)
```

**Why Pydantic Matters for AI/LLM Projects:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PYDANTIC IN AI WORKFLOWS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User Input ──▶ [Pydantic Validation] ──▶ LLM ──▶ [Pydantic] ──▶ DB│
│                        │                              │              │
│                        ▼                              ▼              │
│                 ValidationError              Structured Output       │
│                 (Bad input!)                 (Reliable format!)      │
│                                                                      │
│  Benefits:                                                           │
│  ✅ Validate user input before sending to LLM                       │
│  ✅ Parse LLM responses into structured data                        │
│  ✅ Ensure data consistency across the system                       │
│  ✅ Generate JSON schemas for LLM function calling                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Industry Reality (December 2025):**

| Framework      | Uses Pydantic? | Why                                  |
| -------------- | -------------- | ------------------------------------ |
| **LangChain**  | ✅ Required    | Tools, structured output             |
| **LlamaIndex** | ✅ Required    | Data models, query engines           |
| **FastAPI**    | ✅ Required    | Request/response validation          |
| **OpenAI SDK** | ✅ Recommended | Structured outputs, function calling |

**Formal Definition:**
**Pydantic** is a data validation library that uses Python type hints to validate data at runtime, providing automatic type coercion, clear error messages, and JSON schema generation.

---

### 2. BaseModel: The Foundation

**Concrete Example First:**

```python
from pydantic import BaseModel

# WHY: BaseModel provides automatic validation and serialization
# WHAT: Define a data model with type hints
# HOW: Inherit from BaseModel, add typed attributes

class Clause(BaseModel):
    """
    A single clause in a contract section.

    Attributes:
        id: Unique identifier for the clause
        content: The actual text of the clause
    """
    id: str
    content: str

# Usage - automatic validation!
clause = Clause(id="clause_001", content="Payment terms...")
print(clause.model_dump())  # {'id': 'clause_001', 'content': 'Payment terms...'}

# Invalid data rejected
try:
    bad_clause = Clause(id=123, content="")  # id should be str
except ValidationError as e:
    print(e)  # Clear error message!
```

**What BaseModel Gives You:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BASEMODEL FEATURES                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Automatic Features:                                                 │
│  ✅ __init__() - Constructor with validation                        │
│  ✅ __repr__() - String representation                              │
│  ✅ __eq__() - Equality comparison                                  │
│  ✅ .model_dump() - Convert to dict                                 │
│  ✅ .model_dump_json() - Convert to JSON string                     │
│  ✅ .model_validate() - Validate dict data                          │
│  ✅ .model_json_schema() - Generate JSON schema                     │
│                                                                      │
│  Validation:                                                         │
│  ✅ Type checking (str, int, float, bool, etc.)                     │
│  ✅ Type coercion ("123" → 123 if field is int)                     │
│  ✅ Required vs optional fields                                     │
│  ✅ Clear error messages                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 3. Field Constraints: Declarative Validation

**Concrete Example First:**

```python
from pydantic import BaseModel, Field

class Contract(BaseModel):
    """
    Contract with declarative validation constraints.
    """
    # WHY: Field() adds validation rules beyond type checking
    # WHAT: Constraints like min_length, max_length, gt (greater than)
    # HOW: Pydantic checks these rules during instantiation

    title: str = Field(
        ...,  # ... means required (no default)
        min_length=5,
        max_length=200,
        description="Contract title"
    )

    value: float = Field(
        ...,
        gt=0,  # Greater than 0
        description="Contract value in USD"
    )

    project_code: str = Field(
        ...,
        pattern=r'^PROJ-\d{4}-\d{4}$',  # Regex validation
        description="Project code in PROJ-YYYY-NNNN format"
    )

# Valid contract
contract = Contract(
    title="Software Development Agreement",
    value=50000.0,
    project_code="PROJ-2025-0001"
)

# Invalid - title too short
try:
    Contract(title="Hi", value=1000, project_code="PROJ-2025-0001")
except ValidationError as e:
    print(e)  # "String should have at least 5 characters"
```

**Common Field Constraints:**

| Constraint        | Type   | Example                       | Validates               |
| ----------------- | ------ | ----------------------------- | ----------------------- |
| `min_length`      | str    | `Field(min_length=1)`         | Non-empty string        |
| `max_length`      | str    | `Field(max_length=200)`       | String length limit     |
| `pattern`         | str    | `Field(pattern=r'^\d+$')`     | Regex match             |
| `gt`              | number | `Field(gt=0)`                 | Greater than            |
| `ge`              | number | `Field(ge=0)`                 | Greater than or equal   |
| `lt`              | number | `Field(lt=100)`               | Less than               |
| `le`              | number | `Field(le=100)`               | Less than or equal      |
| `default`         | any    | `Field(default="value")`      | Default if not provided |
| `default_factory` | any    | `Field(default_factory=list)` | Default from function   |

---

### 4. Nested Models: Building Complex Structures

**Concrete Example First:**

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from shared.models.enums import TemplateType

# WHY: Real contracts have hierarchical structure
# WHAT: Models can contain other models
# HOW: Use type hints with model classes

class Clause(BaseModel):
    """A single clause in a section."""
    text: str = Field(..., min_length=1)
    required: bool = True

class Section(BaseModel):
    """A section containing multiple clauses."""
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    clauses: List[Clause] = Field(default_factory=list)

class Contract(BaseModel):
    """Complete contract with nested sections."""
    project_code: str = Field(..., pattern=r"^PROJ-\d{4}-\d{4}$")
    template_type: TemplateType
    sections: List[Section] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def total_clauses(self) -> int:
        """Calculate total number of clauses across all sections."""
        return sum(len(section.clauses) for section in self.sections)

# Usage - nested validation works automatically!
contract = Contract(
    project_code="PROJ-2025-0001",
    template_type=TemplateType.ENGINEERING,
    sections=[
        Section(
            title="Payment Terms",
            clauses=[
                Clause(text="Payment due in 30 days"),
                Clause(text="Late fees apply after 60 days", required=False)
            ]
        ),
        Section(
            title="Deliverables",
            clauses=[
                Clause(text="Source code delivery")
            ]
        )
    ]
)

print(f"Total clauses: {contract.total_clauses}")  # 3
```

**Nested Model Benefits:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NESTED MODEL VALIDATION                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Contract                                                            │
│  ├── title: str ✓                                                   │
│  └── sections: List[Section] ✓                                      │
│      ├── Section                                                     │
│      │   ├── title: str ✓                                           │
│      │   └── clauses: List[Clause] ✓                                │
│      │       ├── Clause                                              │
│      │       │   ├── id: str ✓                                      │
│      │       │   └── content: str ✓                                 │
│      │       └── Clause                                              │
│      │           ├── id: str ✓                                      │
│      │           └── content: str ✓                                 │
│      └── Section                                                     │
│          └── ...                                                     │
│                                                                      │
│  Pydantic validates EVERY level automatically!                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Guide

### What You're Building

You'll implement the core contract data models in `shared/models/contract.py`:

```
Contract (top level)
├── project_code: str (PROJ-YYYY-NNNN format)
├── template_type: TemplateType (enum from Ch 2)
├── sections: List[Section]
│   └── Section
│       ├── title: str
│       ├── description: Optional[str]
│       └── clauses: List[Clause]
│           └── Clause
│               ├── text: str
│               └── required: bool
└── created_at: datetime
```

> **Note:** The actual implementation uses `text` and `required` for Clause fields (not `id` and `content`). This design focuses on clause content and whether it's mandatory.

---

### Example Pattern: Simple Model

Here's a pattern showing how to create a Pydantic model (NOT the exact solution):

```python
from pydantic import BaseModel, Field

class Person(BaseModel):
    """
    Example person model.

    WHY: Demonstrate Pydantic basics
    WHAT: Simple model with validation
    HOW: BaseModel + Field constraints
    """
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)
    email: str = Field(..., pattern=r'^[\w.+-]+@[\w.-]+\.\w+$')

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.name} ({self.age})"
```

**Key Points:**

- Import `BaseModel` and `Field` from `pydantic`
- Use `...` for required fields (no default)
- Add docstrings with WHY/WHAT/HOW
- Type hints on all attributes and methods

---

### Starter Scaffold

**File: `shared/models/contract.py`**

```python
"""
Core contract data models using Pydantic.

WHY: Type-safe data models with automatic validation
WHAT: Defines Clause, Section, and Contract models
HOW: Uses Pydantic BaseModel with Field constraints
"""

from pydantic import BaseModel, Field
from typing import List
from shared.models.enums import TemplateType


class Clause(BaseModel):
    """
    A single clause within a contract section.

    WHY: [Your explanation - why separate clause model?]
    WHAT: [Your explanation - what does a clause represent?]
    HOW: [Your explanation - how is this used?]

    Attributes:
        text: The clause content (required, non-empty)
        required: Whether this clause is mandatory (default: True)

    Example:
        >>> clause = Clause(
        ...     text="Payment due within 30 days",
        ...     required=True
        ... )
        >>> print(clause.text)
        Payment due within 30 days
    """
    # TODO: Implement Clause model
    # Hint: text is required string with min_length=1
    # Hint: required is bool with default=True
    pass


class Section(BaseModel):
    """
    A section of a contract containing multiple clauses.

    WHY: [Your explanation]
    WHAT: [Your explanation]
    HOW: [Your explanation]

    Attributes:
        title: Section title (e.g., "Payment Terms")
        description: Optional section description
        clauses: List of clauses in this section

    Example:
        >>> section = Section(
        ...     title="Payment Terms",
        ...     clauses=[
        ...         Clause(text="Payment due in 30 days")
        ...     ]
        ... )
        >>> print(len(section.clauses))
        1
    """
    # TODO: Implement Section model
    # Hint: title is required string with min_length=1
    # Hint: description is Optional[str] with default=None
    # Hint: clauses is List[Clause] with default_factory=list
    pass


class Contract(BaseModel):
    """
    Complete contract document with metadata and sections.

    WHY: [Your explanation]
    WHAT: [Your explanation]
    HOW: [Your explanation]

    Attributes:
        project_code: Unique project identifier (PROJ-YYYY-NNNN)
        template_type: Type of contract template
        sections: List of contract sections
        created_at: Timestamp of creation

    Example:
        >>> contract = Contract(
        ...     project_code="PROJ-2025-0001",
        ...     template_type=TemplateType.ENGINEERING
        ... )
        >>> print(contract.project_code)
        PROJ-2025-0001
    """
    # TODO: Implement Contract model
    # Hint: project_code should match pattern r'^PROJ-\d{4}-\d{4}$'
    # Hint: template_type is TemplateType enum
    # Hint: sections is List[Section] with default_factory=list
    # Hint: created_at is datetime with default_factory=datetime.now
    pass

    @property
    def total_clauses(self) -> int:
        """
        Calculate total number of clauses across all sections.

        Returns:
            Total count of clauses

        WHY: [Your explanation]
        WHAT: [Your explanation]
        HOW: [Your explanation]

        Example:
            >>> contract.total_clauses
            5
        """
        # TODO: Implement total_clauses property
        # Hint: Sum len(section.clauses) for all sections
        pass
```

---

### Implementation Hints

**Hint 1: Required vs Optional Fields**

```python
# Required field (no default)
name: str = Field(..., min_length=1)

# Optional field with default
description: str = Field(default="", max_length=500)

# Optional field that's None by default
notes: str | None = Field(default=None)
```

**Hint 2: List Fields with default_factory**

```python
# ❌ WRONG - mutable default
clauses: List[Clause] = []  # Shared across instances!

# ✅ CORRECT - default_factory
clauses: List[Clause] = Field(default_factory=list)
```

**Hint 3: Regex Patterns**

```python
# Project code: PROJ-YYYY-NNNN
pattern=r'^PROJ-\d{4}-\d{4}$'

# Date: YYYY-MM-DD
pattern=r'^\d{4}-\d{2}-\d{2}$'
```

---

### Acceptance Criteria

Your implementation is complete when:

- [ ] `shared/models/contract.py` file exists
- [ ] `Clause` model has `text` and `required` fields with validation
- [ ] `Section` model has `title`, `description`, and `clauses` fields
- [ ] `Contract` model has `project_code`, `template_type`, `sections`, `created_at` fields
- [ ] `Contract.total_clauses` property works correctly (if implemented)
- [ ] All models have comprehensive docstrings with WHY/WHAT/HOW
- [ ] Type hints are present on all attributes and methods

---

### Verification Commands

```bash
# Test 1: Import models
python -c "from shared.models.contract import Clause, Section, Contract; print('✓ Imports work')"

# Test 2: Create a Clause
python -c "
from shared.models.contract import Clause
clause = Clause(text='Payment due within 30 days')
assert clause.text == 'Payment due within 30 days'
assert clause.required == True  # Default value
print('✓ Clause model works')
"

# Test 3: Create a Section with clauses
python -c "
from shared.models.contract import Clause, Section
section = Section(
    title='Test Section',
    clauses=[
        Clause(text='Content 1'),
        Clause(text='Content 2', required=False)
    ]
)
assert len(section.clauses) == 2
print('✓ Section model works')
"

# Test 4: Create a Contract
python -c "
from shared.models.contract import Contract
from shared.models.enums import TemplateType
contract = Contract(
    project_code='PROJ-2025-0001',
    template_type=TemplateType.ENGINEERING
)
assert contract.project_code == 'PROJ-2025-0001'
print('✓ Contract model works')
"

# Test 5: Test nested structure
python -c "
from shared.models.contract import Contract, Section, Clause
from shared.models.enums import TemplateType
contract = Contract(
    project_code='PROJ-2025-0001',
    template_type=TemplateType.ENGINEERING,
    sections=[
        Section(title='S1', clauses=[
            Clause(text='C1'),
            Clause(text='C2')
        ]),
        Section(title='S2', clauses=[
            Clause(text='C3')
        ])
    ]
)
total = sum(len(s.clauses) for s in contract.sections)
assert total == 3
print('✓ Nested structure works')
"

# Test 6: Test validation (should fail)
python -c "
from shared.models.contract import Contract
from shared.models.enums import TemplateType
from pydantic import ValidationError
try:
    Contract(
        project_code='invalid',  # Wrong format
        template_type=TemplateType.ENGINEERING
    )
    print('❌ Should have raised ValidationError')
except ValidationError:
    print('✓ Validation works correctly')
"
```

---

## Interactive Checkpoint Exercise

Create a complete contract with nested structure:

```python
from shared.models.contract import Contract, Section, Clause
from shared.models.enums import TemplateType

# Your task: Create a contract with 2 sections, 3 total clauses
contract = Contract(
    project_code="PROJ-2025-0001",
    template_type=TemplateType.ENGINEERING,
    sections=[
        # TODO: Add sections with clauses
    ]
)

# Verify
total_clauses = sum(len(s.clauses) for s in contract.sections)
assert total_clauses == 3
assert len(contract.sections) == 2
print("✓ Checkpoint passed!")
```

---

## Debugging Challenge

**The Bug:**

A learner wrote this code:

```python
from pydantic import BaseModel, Field
from typing import List

class Section(BaseModel):
    title: str
    clauses: List[str] = []  # Bug here!

# Create two sections
section1 = Section(title="Section 1")
section1.clauses.append("Clause 1")

section2 = Section(title="Section 2")
print(section2.clauses)  # Prints: ['Clause 1'] - WHY?!
```

**Your Task:**

1. Why does `section2` have a clause even though we didn't add one?
2. How do you fix this bug?

<details>
<summary>💡 Click to reveal answer</summary>

**Root Cause:**
Mutable default arguments (`[]`) are shared across all instances! When you append to `section1.clauses`, you're modifying the same list object that `section2.clauses` references.

**The Fix:**

```python
class Section(BaseModel):
    title: str
    clauses: List[str] = Field(default_factory=list)  # ✅ Correct!
```

**Why This Works:**
`default_factory=list` calls `list()` for EACH new instance, creating a fresh list every time.

**Key Lesson:** Never use mutable defaults (`[]`, `{}`) in Pydantic models. Always use `Field(default_factory=...)`.

</details>

---

## Quick Check Questions

### Question 1

What's the difference between `Field(...)` and `Field(default="value")`?

<details>
<summary>Answer</summary>

- `Field(...)` means the field is **required** (no default value)
- `Field(default="value")` means the field is **optional** with a default

```python
class Example(BaseModel):
    required_field: str = Field(...)  # Must be provided
    optional_field: str = Field(default="default")  # Can be omitted

# Valid
Example(required_field="value")  # optional_field gets "default"

# Invalid
Example(optional_field="value")  # ❌ Missing required_field
```

</details>

### Question 2

Why use `@property` for `total_clauses` instead of a regular method?

<details>
<summary>Answer</summary>

**Properties** allow you to access computed values like attributes:

```python
# With @property
total = contract.total_clauses  # Clean, looks like an attribute

# Without @property (regular method)
total = contract.get_total_clauses()  # Verbose, looks like a method call
```

**When to use @property:**

- Computed values that don't take parameters
- Values that should feel like attributes
- Read-only access (no setter needed)

</details>

### Question 3

What happens if you try to modify a Pydantic model after creation?

<details>
<summary>Answer</summary>

By default, Pydantic models are **mutable** - you can change them:

```python
contract = Contract(...)
contract.title = "New Title"  # ✅ Works by default
```

To make them immutable, use `model_config`:

```python
from pydantic import ConfigDict

class ImmutableContract(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: str

contract = ImmutableContract(title="Original")
contract.title = "New"  # ❌ ValidationError: Instance is frozen
```

**When to use frozen=True:**

- Data that shouldn't change after creation
- When you want to use models as dict keys
- For thread-safety

</details>

---

## Mini-Project

**Task:** Create a complete contract with realistic data

**Acceptance Criteria:**

- [ ] Contract has project code "PROJ-2025-0001"
- [ ] Uses ENGINEERING template type
- [ ] Has title "Software Development Agreement"
- [ ] Has client name "Acme Corporation"
- [ ] Has effective date "2025-01-15"
- [ ] Has 3 sections: "Payment Terms", "Deliverables", "Warranties"
- [ ] Payment Terms has 2 clauses
- [ ] Deliverables has 3 clauses
- [ ] Warranties has 2 clauses
- [ ] Total clauses equals 7

**Verification:**

```bash
python -c "
from shared.models.contract import Contract, Section, Clause
from shared.models.enums import TemplateType

# Your implementation here
contract = Contract(...)

# Tests
assert contract.project_code == 'PROJ-2025-0001'
assert contract.template_type == TemplateType.ENGINEERING
assert len(contract.sections) == 3
assert contract.total_clauses == 7
print('✓ Mini-project complete!')
"
```

---

## Project Integration

**How This Connects:**

- **Chapter 2 (Enums)**: Uses `TemplateType` enum
- **Chapter 4 (Advanced Pydantic)**: Will add compliance models
- **Chapter 6 (Templates)**: Will load templates into these models
- **Chapter 14 (Generator)**: Will create Contract instances
- **Chapter 17 (Reviewer)**: Will analyze Contract instances

**What's Next:**

Chapter 4 will teach advanced Pydantic patterns including nested validation, model validators, and how these models integrate with LLM structured outputs.

---

## From Scratch vs With Framework

### Manual Approach (Dataclasses)

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Clause:
    id: str
    content: str

    def __post_init__(self):
        # Manual validation
        if not self.id:
            raise ValueError("id required")
        if not self.content:
            raise ValueError("content required")
```

**Pros:** No dependencies, simple
**Cons:** Manual validation, no JSON schema, verbose

### Framework Approach (Pydantic)

```python
from pydantic import BaseModel, Field

class Clause(BaseModel):
    id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
```

**Pros:** Automatic validation, JSON schema, LLM integration
**Cons:** Extra dependency

**Why Pydantic?** Required for LangChain, LlamaIndex, and modern AI frameworks.
