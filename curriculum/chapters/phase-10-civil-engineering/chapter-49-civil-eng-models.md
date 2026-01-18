# Chapter 49: Civil Engineering Document Models — The Blueprint

<!--
METADATA
Phase: 10 - Civil Engineering Application
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Application
Prerequisites: Chapter 3 (Pydantic)
Builds Toward: Contract Generation (Ch 50)
Correctness Properties: P70 (Contract Completeness), P71 (Proposal Validation)
Project Thread: Domain Modeling

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You are building a bridge.
You don't sketch it on a napkin. You have **Blueprints**.
You have codes: ASCE standards, ISO compliance, Local zoning.
If you miss a structural beam in the drawing, the bridge falls down.

AI usually generates "Napkin Sketches" (unstructured text).
For **Civil Engineering**, we need Blueprints.
We need strict Data Models that enforce: "This contract MUST have a budget," "This proposal MUST have a technical approach."

**By the end of this chapter**, you will translate the rigid world of Engineering Standards into flexible-yet-strict Python code. 🏗️

---

## Prerequisites Check

```bash
# Verify Pydantic
pip show pydantic
```

---

## The Story: The "Missing Clause" Lawsuit

### The Problem (Unstructured AI)

You ask GPT-4: "Write a contract for the Bridge Project."
It writes a beautiful contract. It looks great.
But it forgot the **Indemnification Clause**.
A year later, the bridge cracks. Your firm is sued for $10M.
The AI didn't know that clause was mandatory.

### The Solution (Domain Models)

We define a `CivilEngineeringContract` model.
It has a field `indemnification: str`.
If the AI tries to generate a contract without it, the code **Explodes** (raises ValidationError) *before* you send it to the client.

---

## Part 1: The Contract Model

Let's build the model for a standard engineering contract.

### 🔬 Try This! (Hands-On Practice #1)

**Create `domain_models.py`**:

```python
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from datetime import date
from enum import Enum

# 1. Enums (Standardization)
class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"

# 2. The Model
class EngineeringContract(BaseModel):
    """
    Standard Civil Engineering Services Contract.
    """
    project_id: str = Field(..., pattern=r"^ENG-\d{4}-\d{3}$")
    project_name: str
    client_name: str
    scope_of_work: str = Field(..., min_length=100, description="Detailed description")
    
    # Financials
    budget: float = Field(..., gt=0)
    currency: str = "USD"
    
    # Timeline
    start_date: date
    end_date: date
    
    # Required Clauses (The Safety Net)
    indemnification_clause: str
    termination_clause: str
    
    @model_validator(mode="after")
    def check_timeline(self):
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        return self

# 3. Test it
print("--- Validating Contract ---")
try:
    contract = EngineeringContract(
        project_id="ENG-2024-001",
        project_name="Bridge A",
        client_name="City Corp",
        scope_of_work="This is a very long scope of work that describes the bridge..." + "..."*20,
        budget=1000000,
        start_date="2024-01-01",
        end_date="2024-12-31",
        indemnification_clause="Client holds Engineer harmless...",
        termination_clause="Either party may terminate..."
    )
    print("✅ Contract Valid!")
except Exception as e:
    print(f"❌ Contract Invalid: {e}")
```

**Run it**.
Try removing `indemnification_clause`. See it fail. That failure saved your company $10M.

---

## Part 2: The Proposal Model

Before a contract, there is a **Proposal** (RFP Response).
It needs: Executive Summary, Technical Approach, Team, and Pricing.

### 🔬 Try This! (Hands-On Practice #2)

**Append to `domain_models.py`**:

```python
class TeamMember(BaseModel):
    name: str
    role: str
    license_number: Optional[str] = None # PE License

class TechnicalProposal(BaseModel):
    """
    Response to Request for Proposal (RFP).
    """
    rfp_reference: str
    executive_summary: str = Field(..., max_length=2000)
    technical_approach: List[str] # Steps 1, 2, 3...
    team: List[TeamMember]
    estimated_cost: float
    
    @model_validator(mode="after")
    def check_team(self):
        # Rule: Must have at least one PE (Professional Engineer)
        has_pe = any(m.license_number is not None for m in self.team)
        if not has_pe:
            raise ValueError("Proposal requires at least one Licensed PE.")
        return self

# Test
print("\n--- Validating Proposal ---")
try:
    prop = TechnicalProposal(
        rfp_reference="RFP-99",
        executive_summary="We will build it.",
        technical_approach=["Survey", "Design", "Build"],
        team=[TeamMember(name="Alice", role="Intern")], # No PE!
        estimated_cost=50000
    )
except ValueError as e:
    print(f"✅ Caught expected error: {e}")
```

**Run it**.
It enforces the requirement for a Professional Engineer (PE).

---

## Part 3: The Technical Report Model

Engineers produce calculations and reports.

### 🔬 Try This! (Hands-On Practice #3)

**Append to `domain_models.py`**:

```python
class Calculation(BaseModel):
    name: str
    formula: str
    result: float
    units: str

class TechnicalReport(BaseModel):
    report_id: str
    title: str
    calculations: List[Calculation]
    conclusion: str
    approved_by: str

# Test
calc = Calculation(name="Load", formula="mass * gravity", result=9800, units="N")
print(f"\nCalculation: {calc.result} {calc.units}")
```

---

## Common Mistakes

### Mistake #1: Vague Fields
Field `data: str`. What data?
**Fix**: `Field(description="Geotechnical survey data in CSV format")`.

### Mistake #2: Ignoring Units
`length: float`. Is it meters? Feet? Inches?
**Fix**: Use `Annotated` types or explicit fields `length_meters: float`. Or a `Measurement` model.

### Mistake #3: Regex Overkill
Trying to validate complex engineering codes with one Regex.
**Fix**: Use a custom `@field_validator` with Python logic.

---

## Quick Reference Card

### Engineering Fields

| Field | Constraint | Example |
|-------|------------|---------|
| Project ID | Regex | `ENG-2024-001` |
| Budget | `gt=0` | 50000.00 |
| Timeline | Start < End | 2024-01 to 2024-06 |
| PE License | Custom | "PE-12345" |

---

## Verification (REQUIRED SECTION)

We need to verify **P70 (Contract Completeness)** and **P71 (Proposal Validation)**.

**Create `verify_civil_models.py`**:

```python
"""
Verification script for Chapter 49.
Properties: P70 (Contract), P71 (Proposal).
"""
from domain_models import EngineeringContract, TechnicalProposal, TeamMember
import sys
from pydantic import ValidationError

print("🧪 Running Domain Model Verification...\n")

# P70: Contract Completeness
# Try creating a contract without a mandatory clause
print("Test 1: Contract Completeness...")
try:
    EngineeringContract(
        project_id="ENG-2024-001",
        project_name="X",
        client_name="Y",
        scope_of_work="Valid scope..." * 10,
        budget=100,
        start_date="2024-01-01",
        end_date="2024-02-01",
        # Missing indemnification_clause
        termination_clause="Valid"
    )
    print("❌ Failed: Created incomplete contract.")
    sys.exit(1)
except ValidationError as e:
    if "indemnification_clause" in str(e):
        print("✅ P70 Passed: Detected missing indemnification.")
    else:
        print(f"❌ Failed: Wrong error {e}")

# P71: Proposal Validation
# Try creating proposal without PE
print("Test 2: Proposal Logic...")
try:
    TechnicalProposal(
        rfp_reference="X",
        executive_summary="Summary",
        technical_approach=["Step 1"],
        team=[TeamMember(name="Bob", role="Drafter")], # No PE
        estimated_cost=100
    )
    print("❌ Failed: Created proposal without PE.")
    sys.exit(1)
except ValueError as e:
    if "Licensed PE" in str(e):
        print("✅ P71 Passed: Enforced Professional Engineer requirement.")
    else:
        print(f"❌ Failed: Wrong error {e}")

print("\n🎉 Chapter 49 Complete! The blueprints are solid.")
```

**Run it:** `python verify_civil_models.py`

---

## Summary

**What you learned:**

1. ✅ **Domain Modeling**: Translating real-world rules into code.
2. ✅ **Mandatory Fields**: Preventing legal liability via Validation.
3. ✅ **Logical Constraints**: Timelines and Team Composition.
4. ✅ **Structure**: Organizing data for Contracts, Proposals, and Reports.
5. ✅ **Safety**: Using code to police the AI.

**Key Takeaway**: Before you let an AI write a contract, you must define what a contract *is*.

**Skills unlocked**: 🎯
- Domain-Driven Design (DDD)
- Regulatory Compliance Engineering
- Data Schemas

**Looking ahead**: We have the models. Now let's build the machine that fills them.
In **Chapter 50**, we will build the **Contract Generation System**. We'll combine RAG (to read the RFP) and Agents (to write the clauses).

---

**Next**: [Chapter 50: Contract Generation System →](chapter-50-contract-generation.md)
