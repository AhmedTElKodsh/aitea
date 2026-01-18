# Chapter 6: Template System — The Configurable Engine

<!--
METADATA
Phase: 0 - Shared Foundation
Time: 2 hours (45 min reading + 75 min hands-on)
Difficulty: ⭐⭐
Type: Foundation
Prerequisites: Chapter 3, Chapter 5
Builds Toward: Contract Generation (Ch 14)
Correctness Properties: None (Foundation)
Project Thread: Configuration Architecture

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You work at a DMV (Department of Motor Vehicles).
Every time someone needs a driver's license, you take a blank sheet of paper and *hand-write* the entire form from memory. "Name: _____", "Address: ____", "Eye Color: ____".

If the law changes and you need to add "Blood Type", you have to re-memorize the form.
If you get sick, the temp has no idea what to write.

**This is what hardcoding data structures in Python feels like.**

Smart organizations use **Forms** (Templates).
- You print 1,000 copies.
- If the form changes, you print new ones.
- The clerks (your code) just fill in the blanks.

In this chapter, we will move our Contract definitions out of Python code and into **YAML Templates**. This means a non-programmer (like a lawyer) can update the wording of a contract without touching a single line of code. 🤯

---

## Prerequisites Check

```bash
# Check if you have the 'pyyaml' library
python -c "import yaml; print(f'PyYAML version: {yaml.__version__}')"
```

**If this errors**: Run `pip install pyyaml`.

---

## The Story: Code vs. Configuration

### The Problem (Hardcoded Structures)

You need to generate an "Engineering Contract".

```python
# ❌ Hardcoded in Python
def create_engineering_contract():
    return Contract(
        title="Engineering Services",
        sections=[...])
```

**Why this fails:**
1. **Updates**: To change "Services" to "Agreement", you must redeploy code.
2. **Access**: Lawyers can't edit Python files.
3. **Scale**: If you have 50 contract types, you have 50 functions.

### The Naive Solution (JSON Files)

> "I'll put it in JSON!"

```json
{
  "title": "Engineering Services",
  "sections": [...]
}
```
Better, but JSON doesn't support **comments**. You can't explain *why* a clause exists. Also, multi-line strings in JSON are painful (`"line 1\nline 2"`).

### The Elegant Solution (YAML + Pydantic)

**YAML** is human-readable, supports comments, and handles multi-line text beautifully.
**Pydantic** validates that the YAML is correct.

**The Workflow:**
1. Lawyer edits `engineering.yaml`.
2. Python loads it.
3. Pydantic validates it.
4. App generates contract.

---

## Part 1: The Template Models

We need Pydantic models that represent the *structure* of a template.

### 🔬 Try This! (Hands-On Practice #1)

Let's define the schema for our templates.

**Step 1: Create `stores/template_store.py`**
(If `stores/` doesn't exist, create it).

```python
from pydantic import BaseModel, Field
from typing import List
from shared.models.enums import TemplateType

class ClauseTemplate(BaseModel):
    """Template for a single clause."""
    title: str
    placeholder: str  # e.g., "{{project_description}}"
    required: bool = True

class SectionTemplate(BaseModel):
    """Template for a section."""
    title: str
    required: bool = True
    clauses: List[ClauseTemplate] = Field(default_factory=list)

class ContractTemplate(BaseModel):
    """Definition of a contract type."""
    name: str
    type: TemplateType
    version: str = "1.0"
    description: str = ""
    required_sections: List[SectionTemplate]
```

**Step 2: Test the schema**
Create `test_schema.py`:

```python
from stores.template_store import ContractTemplate, TemplateType

data = {
    "name": "Test Contract",
    "type": "engineering",  # String will be coerced to Enum!
    "required_sections": [
        {
            "title": "Scope",
            "clauses": [{"title": "Desc", "placeholder": "{{desc}}"}]
        }
    ]
}

template = ContractTemplate(**data)
print(f"Loaded: {template.name} ({template.type})")
```

**Run it**: `python test_schema.py`

---

## Part 2: The Template Store (Loading YAML)

Now we need a class to load these files from disk.

### 🔬 Try This! (Hands-On Practice #2)

Implement the `TemplateStore`.

**Update `stores/template_store.py`**:

```python
import yaml
from pathlib import Path
from typing import Dict

class TemplateStore:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self._cache: Dict[TemplateType, ContractTemplate] = {}

    def get(self, template_type: TemplateType) -> ContractTemplate:
        # 1. Check cache
        if template_type in self._cache:
            return self._cache[template_type]

        # 2. Load file
        file_path = self.base_dir / f"{template_type.value}.yaml"
        if not file_path.exists():
            raise FileNotFoundError(f"Template {file_path} not found")

        # 3. Parse YAML
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        # 4. Validate with Pydantic
        template = ContractTemplate(**data)
        
        # 5. Cache and return
        self._cache[template_type] = template
        return template
```

--- 

## Part 3: Creating the YAML Files

Let's act like the Legal Team and create a template.

### 🔬 Try This! (Hands-On Practice #3)

**Step 1: Create directory**
`shared/data/templates/`

**Step 2: Create `shared/data/templates/engineering.yaml`**

```yaml
name: "Engineering Services Agreement"
type: engineering
version: "1.0"
description: >
  Standard agreement for software and hardware 
  engineering services.

required_sections:
  - title: "Scope of Work"
    required: true
    clauses:
      - title: "Project Description"
        placeholder: "The Contractor shall perform: {{project_description}}"
        required: true
      - title: "Deliverables"
        placeholder: "Key deliverables include: {{deliverables}}"  
  
  - title: "Payment"
    required: true
    clauses:
      - title: "Fees"
        placeholder: "Total fee: {{amount}} USD"
```

**Step 3: Verify Loading**
Create `verify_loading.py`:

```python
from pathlib import Path
from stores.template_store import TemplateStore
from shared.models.enums import TemplateType

base_dir = Path("shared/data/templates")
store = TemplateStore(base_dir)

template = store.get(TemplateType.ENGINEERING)
print(f"Successfully loaded: {template.name}")
print(f"Sections: {len(template.required_sections)}")
print(f"Clause 1 Placeholder: {template.required_sections[0].clauses[0].placeholder}")
```

**Run it**: `python verify_loading.py`

---

## Bringing It All Together: Filling the Template

Now, let's write a function to take a template + data and produce a contract text.

**Create `fill_template.py`**:

```python
from stores.template_store import ContractTemplate

def generate_text(template: ContractTemplate, data: dict) -> str:
    output = []
    output.append(f"# {template.name}\n")
    
    for section in template.required_sections:
        output.append(f"## {section.title}\n")
        for clause in section.clauses:
            text = clause.placeholder
            # Replace placeholders
            for key, val in data.items():
                text = text.replace(f"{{{{{key}}}}}", str(val))
            
            output.append(f"**{clause.title}**: {text}\n")
            
    return "\n".join(output)

# Mock Data
data = {
    "project_description": "Build a rocket ship",
    "deliverables": "1 Rocket, 2 Helmets",
    "amount": "1,000,000"
}

# Assume 'template' is loaded from Practice #3
# print(generate_text(template, data))
```

**Expected Output**:
A markdown-formatted contract with "Build a rocket ship" inserted correctly! 🚀

---

## Common Mistakes

### Mistake #1: YAML Indentation

YAML is sensitive to indentation (like Python). Use **2 spaces** or **4 spaces**. Do NOT use tabs.

```yaml
# ❌ BAD
sections:
	- title: "Tabbed"  # Crash!

# ✅ GOOD
sections:
  - title: "Spaced"
```

### Mistake #2: Unsafe Load

```python
# ❌ DANGEROUS
yaml.load(f)

# ✅ SAFE
yaml.safe_load(f)
```
`yaml.load` can execute arbitrary code embedded in YAML files. Never use it.

### Mistake #3: Missing Placeholders

If your YAML has `{{name}}` but your data dict doesn't have `"name"`, the user will see `{{name}}` in the final contract. We'll handle this validation in Chapter 14.

---

## Quick Reference Card

### YAML Cheatsheet

```yaml
key: "value"
number: 123
boolean: true
list:
  - item 1
  - item 2
nested:
  key: "value"
  # Multi-line string
  text: >
    This is a long
    paragraph.
```

### TemplateStore Pattern

```python
store = TemplateStore(path)
try:
    tmpl = store.get(TemplateType.ENGINEERING)
except FileNotFoundError:
    # Handle missing file
except ValidationError:
    # Handle invalid YAML structure
```

---

## Verification (REQUIRED SECTION)

Let's ensure your Template System is production-ready.

**Create `verify_templates.py`**:

```python
"""
Verification script for Chapter 6.
"""
from pathlib import Path
from stores.template_store import TemplateStore, ContractTemplate
from shared.models.enums import TemplateType
import sys

print("🧪 Running Template System Verification...\n")

# Setup
base_dir = Path("shared/data/templates")
if not base_dir.exists():
    print("❌ Error: shared/data/templates directory missing")
    sys.exit(1)

store = TemplateStore(base_dir)

# Test 1: Load Engineering Template
print("Test 1: Loading Engineering Template...")
try:
    tmpl = store.get(TemplateType.ENGINEERING)
    assert tmpl.type == TemplateType.ENGINEERING
    print("✅ Engineering template loaded & validated!")
except Exception as e:
    print(f"❌ Failed to load template: {e}")
    sys.exit(1)

# Test 2: Verify Structure
print("Test 2: Verifying Structure...")
assert len(tmpl.required_sections) > 0
first_section = tmpl.required_sections[0]
assert len(first_section.clauses) > 0
print("✅ Template has sections and clauses!")

# Test 3: Caching
print("Test 3: Testing Cache...")
tmpl2 = store.get(TemplateType.ENGINEERING)
assert tmpl is tmpl2  # Must be same object
print("✅ Caching works (Same object returned)")

print("\n🎉 Chapter 6 Complete! The engine is ready.")
```

**Run it:**
```bash
python verify_templates.py
```

---

## Summary

**What you learned:**

1. ✅ **Configuration vs Code**: Why moving logic to YAML makes systems flexible.
2. ✅ **YAML Syntax**: How to write structured data for humans.
3. ✅ **Pydantic Validation**: Ensuring YAML files match our application's expectations.
4. ✅ **Store Pattern**: Centralizing file access and caching.
5. ✅ **Placeholder Substitution**: The mechanics of "filling in the blanks".

**Key Takeaway**: You have successfully separated the *what* (Contract Content) from the *how* (Python Logic). This is the hallmark of a mature software architecture.

**Skills unlocked**: 🎯
- YAML Configuration
- Caching Strategies
- Template Engines

**Looking ahead**: You have completed **Phase 0: Foundations**! 🎓
Next, in **Phase 1**, we will start working with **LLMs** directly.

---

**Next**: [Phase 1: LLM Fundamentals (Chapter 7) →](../phase-1-llm-fundamentals/chapter-07-first-llm-call.md)