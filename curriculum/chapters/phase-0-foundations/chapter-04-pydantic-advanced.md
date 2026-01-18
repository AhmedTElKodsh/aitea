# Chapter 4: Pydantic Advanced — The LLM Connector

<!--
METADATA
Phase: 0 - Shared Foundation
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Foundation
Prerequisites: Chapter 3
Builds Toward: LLM Structured Output (Ch 11), Validation Utils (Ch 5)
Correctness Properties: None (Foundation)
Project Thread: Data Architecture

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You ask an intern to "Write a summary of this report and give it a score from 0 to 1."
The intern hands you a sticky note: "It's pretty good! Score is maybe 75%?"

You ask again: "Please give me a decimal between 0 and 1."
Intern: "Okay, score: 0.75."

You ask again: "I need JSON."
Intern: `{"score": "0.75"}` (String instead of float). 🤦‍♂️

This is what working with LLMs is like. They are smart but chaotic.
To build reliable AI systems, we need a **Translator** that speaks "Strict Data" to our code and "Natural Language" to the LLM.

**Advanced Pydantic** is that translator. It doesn't just check types; it *fixes* messy data, validates complex logic (start_date < end_date), and generates the instructions (Schemas) that tell LLMs exactly what to do.

---

## Prerequisites Check

```bash
# Check if Pydantic is installed
python -c "import pydantic; print(f'Pydantic version: {pydantic.VERSION}')"
```

**Required**: Pydantic 2.5+

---

## The Story: Taming the Chaos

### The Problem (LLM Hallucinations)

You prompt GPT-4: "Extract the contract value."
GPT-4 replies: "The value is $50,000 (fifty thousand dollars)."

Your code: `float(response)` -> **CRASH**. 💥

### The Naive Solution (Regex)

> "I'll use Regex to find numbers!"

```python
import re
value = re.search(r"\d+", response).group()
```
It works until GPT-4 replies: "Contract ID 500, value $100."
Regex grabs "500". Wrong number. 😱

### The Elegant Solution (Validators)

We define a Pydantic model with a **Validator**.

```python
class ContractValue(BaseModel):
    amount: float

    @field_validator("amount", mode="before")
    def clean_currency(cls, v):
        if isinstance(v, str):
            return float(v.replace("$", "").replace(",", ""))
        return v
```

Now, when GPT-4 sends `"$50,000"`, Pydantic intercepts it, scrubs the symbols, converts it to `50000.0`, and hands you clean data.

---

## Part 1: Field Validators (The Cleaners)

Validators allow you to modify or check data *before* it gets assigned to your model.

### 🔬 Try This! (Hands-On Practice #1)

Let's build a `ComplianceScore` model that cleans up messy input.

**Challenge**: Create a model that accepts "85%", 0.85, or "0.85" and always stores `0.85`.

**Step 1: Create `test_validators.py`**

```python
from pydantic import BaseModel, field_validator, Field

class ComplianceScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)

    @field_validator("score", mode="before")
    @classmethod
    def normalize_score(cls, v):
        # Handle strings
        if isinstance(v, str):
            # Remove % and whitespace
            v = v.replace("%", "").strip()
            # If "85", convert to 0.85
            if float(v) > 1.0:
                return float(v) / 100.0
            return float(v)
        return v

# Test it
print(ComplianceScore(score="85%").score)  # 0.85
print(ComplianceScore(score=0.9).score)    # 0.9
print(ComplianceScore(score="0.75").score) # 0.75
```

**Run it**: `python test_validators.py`. It should print floats for all inputs.

---

## Part 2: Model Validators (The Logic Checkers)

Sometimes validation depends on *multiple* fields.
Example: `end_date` must be after `start_date`.

### 🔬 Try This! (Hands-On Practice #2)

**Challenge**: Validate a date range.

**Update `test_validators.py`**:

```python
from pydantic import model_validator
from datetime import date

class DateRange(BaseModel):
    start: date
    end: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.end < self.start:
            raise ValueError(f"End date {self.end} is before start {self.start}")
        return self

# Valid
print(DateRange(start="2025-01-01", end="2025-01-31"))

# Invalid (Should crash)
try:
    DateRange(start="2025-01-31", end="2025-01-01")
except ValueError as e:
    print(f"Caught expected error: {e}")
```

--- 

## Part 3: Nested Models for Compliance

We need a complex structure for our Compliance Agent (Phase 10). It needs to report issues, severity, and suggestions.

### 🔬 Try This! (Hands-On Practice #3)

Let's implement `shared/models/compliance.py`.

**Step 1: Create file**
`shared/models/compliance.py`

**Step 2: Add Imports & Enums**
```python
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from shared.models.enums import SeverityLevel

# Re-use our Enums from Chapter 2!
```

**Step 3: Define Models**

```python
class RewriteSuggestion(BaseModel):
    """Suggested text rewrite."""
    original_text: str
    suggested_text: str
    confidence: float = Field(ge=0.0, le=1.0)

class ComplianceIssue(BaseModel):
    """A specific problem found in the contract."""
    severity: SeverityLevel
    description: str
    suggestion: Optional[RewriteSuggestion] = None

class ComplianceReport(BaseModel):
    """The full report generated by the AI."""
    contract_id: str
    overall_score: float = Field(ge=0.0, le=1.0)
    issues: List[ComplianceIssue] = Field(default_factory=list)

    @field_validator("overall_score")
    @classmethod
    def round_score(cls, v: float) -> float:
        """Round score to 2 decimals."""
        return round(v, 2)
```

--- 

## Bringing It All Together: AI Output Simulation

Let's simulate parsing a "messy" AI response into our clean structure.

**Create `simulate_ai.py`**:

```python
from shared.models.compliance import ComplianceReport
from shared.models.enums import SeverityLevel

# "Messy" JSON from an imaginary LLM
ai_response = {
    "contract_id": "CTR-2025-001",
    "overall_score": 0.87654321,  # Too many decimals!
    "issues": [
        {
            "severity": "high",   # Lowercase string (Enum expects value)
            "description": "Missing liability cap",
            "suggestion": {
                "original_text": "Unlimited liability...",
                "suggested_text": "Liability capped at...",
                "confidence": 0.95
            }
        }
    ]
}

# Pydantic magic happens here
report = ComplianceReport(**ai_response)

print(f"Score Rounded: {report.overall_score}")  # Should be 0.88
print(f"Severity Enum: {report.issues[0].severity}") # Should be SeverityLevel.HIGH
print(f"Nested Data: {report.issues[0].suggestion.confidence}")
```

**Run it**: `python simulate_ai.py`

**What just happened?**
1. `overall_score` was rounded by our validator.
2. `severity: "high"` was auto-converted to `SeverityLevel.HIGH`.
3. The nested dictionary became a `RewriteSuggestion` object.

This is the power of Pydantic. It cleans data at the boundaries. 🧼

---

## Common Mistakes

### Mistake #1: Decorator Order

```python
# ❌ WRONG
@classmethod
@field_validator("x")
def validate(cls, v): ...

# ✅ CORRECT
@field_validator("x")
@classmethod
def validate(cls, v): ...
```
`@field_validator` must be the **outermost** decorator (topmost).

### Mistake #2: Modifying `self` in Validators

In `@field_validator`, `self` doesn't exist yet (the model isn't created). You get the raw value `v`.
In `@model_validator(mode="after")`, you get `self` (the instance).

### Mistake #3: Infinite Recursion

Don't try to set fields inside a validator that triggers the validator again.

---

## Quick Reference Card

### Validator Cheatsheet

| Type | Syntax | Usage |
|------|--------|-------|
| **Field** | `@field_validator("field")` | Clean/Check single field |
| **Model** | `@model_validator(mode="after")` | Check relationships (A < B) |
| **Pre-process** | `@field_validator(..., mode="before")` | Parse strings/messy input |

### Schema Generation

```python
import json
print(json.dumps(ComplianceReport.model_json_schema(), indent=2))
```
This prints the JSON Schema you can paste into ChatGPT's "Functions" definition!

---

## Verification (REQUIRED SECTION)

Let's ensure your advanced models are working.

**Create `verify_advanced.py`**:

```python
"""
Verification script for Chapter 4.
"""
from shared.models.compliance import ComplianceReport, ComplianceIssue
from shared.models.enums import SeverityLevel
import sys

print("🧪 Running Advanced Pydantic Verification...\n")

# Test 1: Score Rounding
print("Test 1: Score Rounding...")
r = ComplianceReport(contract_id="TEST", overall_score=0.123456)
assert r.overall_score == 0.12
print("✅ Score rounded correctly to 0.12")

# Test 2: Enum Coercion
print("Test 2: Enum Coercion...")
i = ComplianceIssue(severity="high", description="Test")
assert i.severity == SeverityLevel.HIGH
print("✅ String 'high' converted to Enum")

# Test 3: Validation Error
print("Test 3: Bounds Checking...")
try:
    ComplianceReport(contract_id="TEST", overall_score=1.5)
    print("❌ Failed: Should have rejected 1.5")
    sys.exit(1)
except ValueError:
    print("✅ Rejected invalid score 1.5")

print("\n🎉 Chapter 4 Complete! You are ready to handle LLM outputs.")
```

**Run it:**
```bash
python verify_advanced.py
```

---

## Summary

**What you learned:**

1. ✅ **Validators**: How to clean data *before* it breaks your app.
2. ✅ **Cross-Field Logic**: Ensuring `start_date` < `end_date`.
3. ✅ **Nested Models**: Representing complex trees of data.
4. ✅ **LLM Preparation**: Pydantic models correspond 1:1 with LLM Structured Outputs.
5. ✅ **Type Coercion**: Handling the "stringy" nature of outside data automatically.

**Key Takeaway**: Don't write parsing code (Regex, `if/else`). Define **Models** and let Pydantic do the heavy lifting. This makes your code smaller, safer, and easier to read.

**Skills unlocked**: 🎯
- Advanced Data Validation
- Data Cleaning Pipelines
- LLM Interface Design

**Looking ahead**: In **Chapter 5**, we'll create a library of reusable validation utilities (email, phone, etc.) so we don't repeat ourselves!

---

**Next**: [Chapter 5: Validation Utilities →](chapter-05-validation-utilities.md)

```