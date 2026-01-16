# Chapter 4: Pydantic Advanced & Structured Output

## Header

- **Phase**: 0 - Foundation (Pydantic-First)
- **Time Estimate**: 1.5 hours
- **Difficulty**: Intermediate
- **Prerequisites**: Chapter 3 (Pydantic Models Core)
- **Builds**: `shared/models/compliance.py`, `shared/models/version.py`
- **Requirements**: Req 2, 8.1, 9, 13

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. **Implement** nested Pydantic models for complex data structures
2. **Apply** `@model_validator` for cross-field validation
3. **Use** `@field_validator` for custom transformation and validation
4. **Explain** how Pydantic integrates with LLM structured outputs
5. **Generate** JSON schemas from Pydantic models for LLM function calling

---

## Key Concepts

### 1. Why Advanced Pydantic for AI Projects?

**Concrete Example First:**

When an LLM analyzes a contract for compliance, it needs to return structured data:

```python
# ❌ Without structured output - unreliable!
llm_response = """
I found 2 issues:
1. Missing payment terms (high severity)
2. Unclear deliverables (medium severity)
The overall score is about 0.7
"""
# How do you parse this reliably? Regex? Hope?

# ✅ With Pydantic structured output - reliable!
from pydantic import BaseModel, Field
from typing import List

class ComplianceReport(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    issues: List[ComplianceIssue]

# LLM returns validated, typed data
report = llm.with_structured_output(ComplianceReport).invoke(prompt)
print(report.score)  # 0.7 - guaranteed to be a float between 0 and 1
```

**Why This Matters:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LLM + PYDANTIC WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Contract ──▶ LLM Analysis ──▶ [Pydantic Validation] ──▶ Report    │
│                    │                    │                            │
│                    ▼                    ▼                            │
│              Raw JSON            ComplianceReport                    │
│              (unreliable)        (validated, typed)                  │
│                                                                      │
│  Benefits:                                                           │
│  ✅ LLM output is automatically validated                           │
│  ✅ Type coercion handles minor format issues                       │
│  ✅ Clear errors when LLM returns invalid data                      │
│  ✅ IDE autocomplete on LLM responses                               │
└─────────────────────────────────────────────────────────────────────┘
```

**Formal Definition:**
**Structured output** is a technique where LLMs are constrained to return data matching a specific schema (like a Pydantic model), ensuring reliable, parseable responses.

---

### 2. Nested Models: Building Complex Structures

**Concrete Example First:**

Compliance reports have a hierarchical structure:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from shared.models.enums import SeverityLevel

# Level 1: Rewrite suggestion (innermost)
class RewriteSuggestion(BaseModel):
    """A suggested rewrite for problematic text."""
    original_text: str
    suggested_text: str
    confidence: float = Field(ge=0.0, le=1.0)

# Level 2: Compliance issue (contains suggestions)
class ComplianceIssue(BaseModel):
    """A single compliance issue found during review."""
    severity: SeverityLevel
    description: str = Field(min_length=1)
    clause_index: Optional[int] = None
    suggestions: List[RewriteSuggestion] = Field(default_factory=list)

# Level 3: Compliance report (contains issues)
class ComplianceReport(BaseModel):
    """Complete compliance report for a contract."""
    contract_id: str
    score: float = Field(ge=0.0, le=1.0)
    issues: List[ComplianceIssue] = Field(default_factory=list)
```

**Nested Validation Flow:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NESTED MODEL VALIDATION                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ComplianceReport                                                    │
│  ├── contract_id: str ✓                                             │
│  ├── score: float (0.0-1.0) ✓                                       │
│  └── issues: List[ComplianceIssue] ✓                                │
│      └── ComplianceIssue                                             │
│          ├── severity: SeverityLevel ✓                              │
│          ├── description: str (min_length=1) ✓                      │
│          ├── clause_index: Optional[int] ✓                          │
│          └── suggestions: List[RewriteSuggestion] ✓                 │
│              └── RewriteSuggestion                                   │
│                  ├── original_text: str ✓                           │
│                  ├── suggested_text: str ✓                          │
│                  └── confidence: float (0.0-1.0) ✓                  │
│                                                                      │
│  Pydantic validates EVERY level automatically!                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 3. Field Validators: Custom Transformation

**Concrete Example First:**

Sometimes you need to transform data during validation:

```python
from pydantic import BaseModel, Field, field_validator

class ComplianceReport(BaseModel):
    score: float = Field(ge=0.0, le=1.0)

    @field_validator('score')
    @classmethod
    def validate_score_precision(cls, v: float) -> float:
        """
        Round score to 2 decimal places for consistency.

        WHY: LLMs might return 0.7333333... we want 0.73
        WHAT: Rounds to 2 decimal places
        HOW: Uses Python's round() function
        """
        return round(v, 2)

# Usage
report = ComplianceReport(score=0.7333333)
print(report.score)  # 0.73 - automatically rounded!
```

**Key Points About Field Validators:**

| Aspect               | Description                                        |
| -------------------- | -------------------------------------------------- |
| **Decorator Order**  | `@field_validator` MUST come before `@classmethod` |
| **Return Value**     | Always return the (possibly transformed) value     |
| **Raise ValueError** | For validation failures                            |
| **Multiple Fields**  | Can validate multiple fields with one validator    |

```python
@field_validator('start_date', 'end_date')
@classmethod
def validate_date_format(cls, v: str) -> str:
    """Validate both date fields with the same logic."""
    # Validation logic here
    return v
```

---

### 4. Model Validators: Cross-Field Validation

**Concrete Example First:**

Sometimes validation depends on multiple fields:

```python
from pydantic import BaseModel, model_validator
from datetime import datetime

class Contract(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode='after')
    def validate_date_range(self) -> 'Contract':
        """
        Ensure end_date is after start_date.

        WHY: A contract can't end before it starts
        WHAT: Cross-field validation
        HOW: Compare dates after all fields are set
        """
        if self.end_date < self.start_date:
            raise ValueError('end_date must be after start_date')
        return self

# Usage
contract = Contract(start_date="2025-01-01", end_date="2025-12-31")  # ✅
contract = Contract(start_date="2025-12-31", end_date="2025-01-01")  # ❌ Error!
```

**Model Validator Modes:**

| Mode            | When It Runs               | Access To                |
| --------------- | -------------------------- | ------------------------ |
| `mode='before'` | Before field validation    | Raw input dict           |
| `mode='after'`  | After all field validators | Validated model instance |

```python
@model_validator(mode='before')
@classmethod
def preprocess_input(cls, data: dict) -> dict:
    """Transform input before field validation."""
    # Useful for normalizing input format
    if 'projectCode' in data:  # Handle camelCase input
        data['project_code'] = data.pop('projectCode')
    return data
```

---

### 5. LLM Structured Output Integration

**Concrete Example First:**

Here's how Pydantic integrates with LangChain for structured LLM outputs:

```python
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

# Define the output structure
class ExtractedTerms(BaseModel):
    """Terms extracted from a contract clause."""
    payment_amount: float = Field(description="Payment amount in USD")
    due_date: str = Field(description="Payment due date")
    penalties: list[str] = Field(description="List of penalty clauses")

# Create LLM with structured output
llm = ChatOpenAI(model="gpt-4o-mini")
structured_llm = llm.with_structured_output(ExtractedTerms)

# Invoke - returns a Pydantic model, not raw text!
result = structured_llm.invoke(
    "Extract terms from: Payment of $50,000 due Jan 15, 2025. "
    "Late fee of 5% after 30 days. Interest of 1% per month after 60 days."
)

print(result.payment_amount)  # 50000.0
print(result.due_date)        # "2025-01-15"
print(result.penalties)       # ["Late fee of 5% after 30 days", ...]
```

**How It Works:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STRUCTURED OUTPUT FLOW                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Pydantic Model ──▶ JSON Schema                                  │
│     class ExtractedTerms(BaseModel):                                │
│         payment_amount: float                                        │
│                                                                      │
│  2. JSON Schema ──▶ LLM System Prompt                               │
│     "Return JSON matching this schema: {...}"                        │
│                                                                      │
│  3. LLM Response ──▶ Pydantic Validation                            │
│     {"payment_amount": 50000} ──▶ ExtractedTerms(payment_amount=50000)│
│                                                                      │
│  4. Validated Model ──▶ Your Code                                   │
│     result.payment_amount  # Type-safe access!                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 6. JSON Schema Generation

**Concrete Example First:**

Pydantic can generate JSON schemas for LLM function calling:

```python
from pydantic import BaseModel, Field

class ComplianceIssue(BaseModel):
    """A compliance issue found in a contract."""
    severity: str = Field(description="Issue severity: high, medium, or low")
    description: str = Field(description="Detailed description of the issue")

# Generate JSON schema
schema = ComplianceIssue.model_json_schema()
print(schema)
```

**Output:**

```json
{
  "title": "ComplianceIssue",
  "description": "A compliance issue found in a contract.",
  "type": "object",
  "properties": {
    "severity": {
      "type": "string",
      "description": "Issue severity: high, medium, or low"
    },
    "description": {
      "type": "string",
      "description": "Detailed description of the issue"
    }
  },
  "required": ["severity", "description"]
}
```

**Why This Matters:**

- LLMs use JSON schemas to understand expected output format
- Field descriptions become instructions for the LLM
- Required fields are enforced by the LLM

---

## Implementation Guide

### What You're Building

You'll implement compliance-related models in `shared/models/compliance.py`:

```
ComplianceReport (top level)
├── contract_id: str
├── score: float (0.0-1.0)
├── issues: List[ComplianceIssue]
│   └── ComplianceIssue
│       ├── severity: SeverityLevel
│       ├── description: str
│       ├── clause_index: Optional[int]
│       └── suggestions: List[RewriteSuggestion]
│           └── RewriteSuggestion
│               ├── original_text: str
│               ├── suggested_text: str
│               └── confidence: float (0.0-1.0)
└── checked_at: datetime
```

---

### Example Pattern: Nested Model with Validation

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class InnerModel(BaseModel):
    """Innermost model with constraints."""
    value: float = Field(ge=0.0, le=1.0)

class OuterModel(BaseModel):
    """Outer model containing inner models."""
    items: List[InnerModel] = Field(default_factory=list)
    total: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator('total')
    @classmethod
    def round_total(cls, v: float) -> float:
        """Round to 2 decimal places."""
        return round(v, 2)
```

---

### Starter Scaffold

**File: `shared/models/compliance.py`**

```python
"""
Compliance report data models using Pydantic.

WHY: Compliance checking produces structured results that LLMs generate
WHAT: Models for issues, suggestions, and reports
HOW: Nested Pydantic models with validators for score constraints
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from shared.models.enums import SeverityLevel


class RewriteSuggestion(BaseModel):
    """
    Suggested rewrite for a compliance issue.

    WHY: [Your explanation - why suggest rewrites?]
    WHAT: [Your explanation - what does this represent?]
    HOW: [Your explanation - how is this used?]

    Attributes:
        original_text: The problematic text from the contract
        suggested_text: The recommended replacement text
        confidence: Confidence score (0.0 to 1.0)

    Example:
        >>> suggestion = RewriteSuggestion(
        ...     original_text="Payment due whenever",
        ...     suggested_text="Payment due within 30 days",
        ...     confidence=0.85
        ... )
    """
    # TODO: Implement fields
    # Hint: confidence should use Field(ge=0.0, le=1.0)
    pass


class ComplianceIssue(BaseModel):
    """
    A single compliance issue found during review.

    WHY: [Your explanation]
    WHAT: [Your explanation]
    HOW: [Your explanation]

    Attributes:
        severity: Issue severity level (HIGH, MEDIUM, LOW)
        description: Detailed description of the issue
        clause_index: Optional index of the affected clause
        suggestions: List of rewrite suggestions

    Example:
        >>> issue = ComplianceIssue(
        ...     severity=SeverityLevel.HIGH,
        ...     description="Missing payment terms"
        ... )
    """
    # TODO: Implement fields
    # Hint: description should have min_length=1
    # Hint: suggestions should use Field(default_factory=list)
    pass


class ComplianceReport(BaseModel):
    """
    Complete compliance report for a contract.

    WHY: [Your explanation]
    WHAT: [Your explanation]
    HOW: [Your explanation]

    Attributes:
        contract_id: ID of the reviewed contract
        score: Overall compliance score (0.0 to 1.0)
        issues: List of compliance issues found
        checked_at: Timestamp of the review

    Example:
        >>> report = ComplianceReport(
        ...     contract_id="PROJ-2025-0001",
        ...     score=0.85,
        ...     issues=[]
        ... )
    """
    # TODO: Implement fields
    # Hint: score should use Field(ge=0.0, le=1.0)
    # Hint: Add a field_validator to round score to 2 decimal places
    pass

    @field_validator('score')
    @classmethod
    def validate_score_precision(cls, v: float) -> float:
        """
        Round score to 2 decimal places for consistency.

        WHY: [Your explanation]
        WHAT: [Your explanation]
        HOW: [Your explanation]
        """
        # TODO: Implement rounding
        pass
```

---

### Acceptance Criteria

Your implementation is complete when:

- [ ] `RewriteSuggestion` has `original_text`, `suggested_text`, `confidence` fields
- [ ] `confidence` is constrained to 0.0-1.0 range
- [ ] `ComplianceIssue` has `severity`, `description`, `clause_index`, `suggestions` fields
- [ ] `severity` uses `SeverityLevel` enum
- [ ] `ComplianceReport` has `contract_id`, `score`, `issues`, `checked_at` fields
- [ ] `score` is constrained to 0.0-1.0 and rounded to 2 decimal places
- [ ] All models have comprehensive docstrings with WHY/WHAT/HOW

---

### Verification Commands

```bash
# Test 1: Import models
python -c "from shared.models.compliance import RewriteSuggestion, ComplianceIssue, ComplianceReport; print('✓ Imports work')"

# Test 2: Create RewriteSuggestion
python -c "
from shared.models.compliance import RewriteSuggestion
suggestion = RewriteSuggestion(
    original_text='Payment due whenever',
    suggested_text='Payment due within 30 days',
    confidence=0.85
)
assert suggestion.confidence == 0.85
print('✓ RewriteSuggestion works')
"

# Test 3: Test confidence bounds
python -c "
from shared.models.compliance import RewriteSuggestion
from pydantic import ValidationError
try:
    RewriteSuggestion(original_text='x', suggested_text='y', confidence=1.5)
    print('❌ Should have raised ValidationError')
except ValidationError:
    print('✓ Confidence bounds enforced')
"

# Test 4: Create ComplianceIssue with suggestions
python -c "
from shared.models.compliance import ComplianceIssue, RewriteSuggestion
from shared.models.enums import SeverityLevel
issue = ComplianceIssue(
    severity=SeverityLevel.HIGH,
    description='Missing payment terms',
    suggestions=[
        RewriteSuggestion(original_text='x', suggested_text='y', confidence=0.9)
    ]
)
assert len(issue.suggestions) == 1
print('✓ ComplianceIssue with nested suggestions works')
"

# Test 5: Create ComplianceReport with score rounding
python -c "
from shared.models.compliance import ComplianceReport
report = ComplianceReport(
    contract_id='PROJ-2025-0001',
    score=0.8567
)
assert report.score == 0.86  # Rounded to 2 decimal places
print('✓ Score rounding works')
"

# Test 6: Full nested structure
python -c "
from shared.models.compliance import ComplianceReport, ComplianceIssue, RewriteSuggestion
from shared.models.enums import SeverityLevel

report = ComplianceReport(
    contract_id='PROJ-2025-0001',
    score=0.75,
    issues=[
        ComplianceIssue(
            severity=SeverityLevel.HIGH,
            description='Missing payment terms',
            clause_index=3,
            suggestions=[
                RewriteSuggestion(
                    original_text='Payment due',
                    suggested_text='Payment due within 30 days',
                    confidence=0.92
                )
            ]
        )
    ]
)
assert len(report.issues) == 1
assert len(report.issues[0].suggestions) == 1
print('✓ Full nested structure works')
"
```

---

## Interactive Checkpoint Exercise

Create a complete compliance report with multiple issues:

```python
from shared.models.compliance import ComplianceReport, ComplianceIssue, RewriteSuggestion
from shared.models.enums import SeverityLevel

# Your task: Create a report with:
# - 2 issues (one HIGH, one MEDIUM severity)
# - Each issue has at least 1 suggestion
# - Overall score of 0.65

report = ComplianceReport(
    contract_id="PROJ-2025-0001",
    score=0.65,
    issues=[
        # TODO: Add issues with suggestions
    ]
)

# Verify
assert len(report.issues) == 2
assert report.issues[0].severity == SeverityLevel.HIGH
assert report.issues[1].severity == SeverityLevel.MEDIUM
print("✓ Checkpoint passed!")
```

---

## Debugging Challenge

**The Bug:**

A learner wrote this code:

```python
from pydantic import BaseModel, Field, field_validator

class Report(BaseModel):
    score: float = Field(ge=0.0, le=1.0)

    @classmethod  # Bug: Wrong order!
    @field_validator('score')
    def round_score(cls, v):
        return round(v, 2)

report = Report(score=0.8567)
print(report.score)  # Expected: 0.86, Got: ???
```

**Your Task:**

1. What's wrong with the decorator order?
2. What error or unexpected behavior occurs?
3. How do you fix it?

<details>
<summary>💡 Click to reveal answer</summary>

**Root Cause:**
The decorator order is wrong! `@field_validator` must come BEFORE `@classmethod`.

**What Happens:**
With wrong order, the validator may not be recognized by Pydantic, and the rounding won't happen.

**The Fix:**

```python
@field_validator('score')  # ✅ First!
@classmethod               # ✅ Second!
def round_score(cls, v: float) -> float:
    return round(v, 2)
```

**Key Lesson:** Decorator order matters! In Python, decorators are applied bottom-up, so `@field_validator` needs to wrap the `@classmethod` result.

</details>

---

## Quick Check Questions

### Question 1

What's the difference between `@field_validator` and `@model_validator`?

<details>
<summary>Answer</summary>

- **`@field_validator`**: Validates/transforms a single field (or multiple specified fields)
- **`@model_validator`**: Validates the entire model, useful for cross-field validation

```python
@field_validator('score')
def validate_score(cls, v):
    # Only has access to 'score' value
    return v

@model_validator(mode='after')
def validate_model(self):
    # Has access to ALL fields via self.field_name
    if self.end_date < self.start_date:
        raise ValueError("Invalid date range")
    return self
```

</details>

### Question 2

Why use `Field(ge=0.0, le=1.0)` instead of a custom validator?

<details>
<summary>Answer</summary>

**Prefer Field constraints when possible:**

- More declarative and readable
- Automatically included in JSON schema
- Less code to maintain
- Better error messages

```python
# ✅ GOOD: Declarative constraint
score: float = Field(ge=0.0, le=1.0)

# ❌ VERBOSE: Custom validator for same thing
score: float

@field_validator('score')
@classmethod
def validate_score(cls, v):
    if v < 0.0 or v > 1.0:
        raise ValueError("Score must be between 0 and 1")
    return v
```

**Use custom validators when:**

- You need transformation (like rounding)
- Validation logic is complex
- You need cross-field validation

</details>

### Question 3

How does `with_structured_output()` use Pydantic models?

<details>
<summary>Answer</summary>

1. **Schema Generation**: Pydantic model → JSON schema
2. **Prompt Injection**: Schema added to LLM system prompt
3. **Response Parsing**: LLM JSON → Pydantic model validation
4. **Type Safety**: Returns validated Pydantic instance

```python
# Behind the scenes:
schema = MyModel.model_json_schema()  # Step 1
# LLM receives: "Return JSON matching: {schema}"  # Step 2
response = llm.invoke(prompt)  # LLM returns JSON
result = MyModel.model_validate_json(response)  # Step 3 & 4
```

</details>

---

## Mini-Project

**Task:** Create a compliance analysis system

**Acceptance Criteria:**

- [ ] Create `RewriteSuggestion` with confidence validation
- [ ] Create `ComplianceIssue` with severity enum
- [ ] Create `ComplianceReport` with score rounding
- [ ] Generate JSON schema for `ComplianceReport`
- [ ] Create a sample report with 3 issues of different severities

**Verification:**

```bash
python -c "
from shared.models.compliance import ComplianceReport, ComplianceIssue, RewriteSuggestion
from shared.models.enums import SeverityLevel

# Create report with 3 issues
report = ComplianceReport(
    contract_id='PROJ-2025-0001',
    score=0.7234,  # Should round to 0.72
    issues=[
        ComplianceIssue(severity=SeverityLevel.HIGH, description='Issue 1'),
        ComplianceIssue(severity=SeverityLevel.MEDIUM, description='Issue 2'),
        ComplianceIssue(severity=SeverityLevel.LOW, description='Issue 3'),
    ]
)

# Verify
assert report.score == 0.72
assert len(report.issues) == 3

# Generate schema
schema = ComplianceReport.model_json_schema()
assert 'properties' in schema
assert 'score' in schema['properties']

print('✓ Mini-project complete!')
"
```

---

## Project Integration

**How This Connects:**

- **Chapter 3 (Core Models)**: Uses same patterns for Contract models
- **Chapter 11 (RAG Chain)**: ComplianceReport is the output of compliance checking
- **Chapter 12 (Structured Output)**: Uses `with_structured_output(ComplianceReport)`
- **Chapter 17 (Reviewer Agent)**: Agent returns ComplianceReport instances

**What's Next:**

Chapter 5 will teach validation utilities - reusable functions for validating project codes, form data, and extracting Pydantic errors for user-friendly display.

---

## From Scratch vs With Framework

### Manual Approach

```python
import json

def validate_report(data: dict) -> dict:
    errors = []
    if 'score' not in data:
        errors.append("Missing score")
    elif not (0 <= data['score'] <= 1):
        errors.append("Score must be 0-1")
    # ... 50 more lines of validation
    return {"valid": len(errors) == 0, "errors": errors}
```

**Cons:** Verbose, error-prone, no type safety, no JSON schema

### Framework Approach (Pydantic)

```python
from pydantic import BaseModel, Field

class ComplianceReport(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    # Done! Validation, serialization, schema all included
```

**Pros:** Declarative, type-safe, LLM integration, industry standard
