# Chapter 6: Template System — Building a Flexible Contract Template Architecture

<!--
NAVIGATION: → [Jump to Quick Reference](#quick-reference-card) | [Jump to Verification](#verification-commands)
-->

## Header

- **Phase**: 0 - Foundation (Pydantic-First)
- **Time Estimate**: 45 min reading + 75 min hands-on (2 hours total)
- **Difficulty**: Intermediate
- **Prerequisites**: Chapter 3 (Pydantic Models Core), Chapter 5 (Validation Utilities)
- **Builds**: `stores/template_store.py`, `shared/data/templates/*.yaml`
- **Requirements**: Req 2 (Template-based generation), Req 8.1 (Configuration management)

---

## Prerequisites Check

Before starting, verify you have the prerequisites from previous chapters:

```bash
# Quick check: Can you import what you need from previous chapters?
python -c "
from shared.models.enums import TemplateType, SeverityLevel
from shared.models.contract import Contract, Section, Clause
print('✓ Prerequisites verified - you are ready to start!')
"
```

**If this fails:** Go back to Chapter 3 (Pydantic Models) and Chapter 2 (Enums) and complete the verification commands there first.

---

## What You Already Know

📌 **Recall from Chapter 3:** Pydantic models validate data at construction time—if the data doesn't match the schema, you get a `ValidationError` immediately with a clear message explaining exactly what went wrong and where.

🔮 **You'll use this again in Chapter 14:** The Contract Generator Engine will use `TemplateStore` to load templates and fill placeholders with user-provided form data, producing complete contracts.

---

## The Story: Why Templates Matter

### The Problem You're Solving

Picture this scenario: You're an engineer at AIECon, and your team needs to generate contracts for different types of projects—engineering services, consulting agreements, military contracts, and governmental agreements. Each contract type has its own required sections, specific clauses, and legal language that must be included.

**The naive approach** would be to hardcode each contract type directly in Python:

```python
# ❌ THE PAINFUL WAY: Hardcoded contract structures
def create_engineering_contract(client_name: str, project_desc: str, amount: float):
    """
    This function creates an engineering contract.

    PROBLEMS WITH THIS APPROACH:
    1. Every contract type needs its own function
    2. Changing a clause requires code changes and redeployment
    3. Non-developers (legal team) can't modify templates
    4. No separation between structure and logic
    5. Testing is difficult - you're testing code, not configuration
    6. Duplication everywhere - same patterns repeated
    """
    return {
        "title": "Engineering Services Agreement",
        "sections": [
            {
                "title": "Scope of Work",
                "clauses": [
                    {"title": "Project Description", "content": project_desc},
                    {"title": "Deliverables", "content": "..."},
                ]
            },
            {
                "title": "Payment Terms",
                "clauses": [
                    {"title": "Total Amount", "content": f"${amount}"},
                ]
            },
        ]
    }

def create_consulting_contract(client_name: str, hourly_rate: float):
    """Another function with duplicated structure..."""
    return {
        "title": "Consulting Agreement",
        "sections": [
            # ... same pattern, different content
        ]
    }

def create_military_contract(contract_number: str, clearance_level: str):
    """Yet another function with the same pattern..."""
    return {
        "title": "Military Services Contract",
        "sections": [
            # ... and again...
        ]
    }
```

**Let's break this down line by line:**

```python
def create_engineering_contract(client_name: str, project_desc: str, amount: float):
    return {
        "title": "Engineering Services Agreement",
        "sections": [
            {"title": "Scope of Work", "clauses": [...]},
        ]
    }
```

| Line                                        | What It Does                             | The Problem                                                |
| ------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------- |
| `def create_engineering_contract(...)`      | Creates a function for ONE contract type | Need a new function for every contract type                |
| `"title": "Engineering Services Agreement"` | Hardcodes the contract title             | Can't change without code modification                     |
| `"sections": [...]`                         | Defines sections inline                  | Structure is buried in code, not visible to non-developers |
| `{"title": "Scope of Work", ...}`           | Hardcodes section structure              | Same structure duplicated across all contract functions    |

**See the pattern?** Every contract type requires its own function with the same structural code repeated. That's not just tedious—it's a maintenance nightmare waiting to happen.

**What happens when the legal team says**: "We need to add a new 'Data Protection' section to ALL contract types"?

You'd have to:

1. Find all contract creation functions (hope you didn't miss any!)
2. Modify each one manually (copy-paste the new section)
3. Write tests for each modified function
4. Get code review approval
5. Redeploy the entire application
6. Pray nothing broke in the process

**This is a maintenance nightmare.**

### The Elegant Solution: Template-Driven Architecture

What if instead of hardcoding contract structures in Python, we stored them in **human-readable configuration files** that anyone could edit?

```yaml
# ✅ THE ELEGANT WAY: engineering.yaml
# A template file that ANYONE can read and modify - no Python required!
name: "Engineering Services Agreement"
type: engineering
version: "1.0"
description: "Standard template for engineering service contracts"

required_sections:
  - title: "Scope of Work"
    required: true
    clauses:
      - title: "Project Description"
        placeholder: "{{project_description}}"
        required: true
      - title: "Deliverables"
        placeholder: "{{deliverables}}"
        required: true

  - title: "Payment Terms"
    required: true
    clauses:
      - title: "Total Amount"
        placeholder: "{{total_amount}}"
        required: true
```

Now:

- **Legal team can modify templates without touching code** — They edit YAML files, not Python
- **Adding a new section means editing a YAML file** — No code changes, no redeployment
- **New contract types = new YAML file** — Zero code changes required
- **Version control tracks template changes separately from code** — Clear audit trail
- **Testing becomes straightforward** — Validate YAML against schema, test generation separately

**This is the Template-Driven Architecture pattern**, and it's what we're building in this chapter.

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. **Explain** why template-driven architecture is superior to hardcoded structures for document generation
2. **Design** a hierarchical template system using YAML files and Pydantic models that mirror each other
3. **Implement** a `TemplateStore` class that loads, validates, and caches templates efficiently
4. **Create** contract templates with required sections, clauses, and placeholder variables using proper YAML syntax
5. **Apply** the Repository/Store pattern for efficient data access with in-memory caching
6. **Debug** common YAML parsing errors and Pydantic validation issues when templates don't load correctly
7. **Understand** security considerations when loading external configuration files (path traversal, code injection)

---

## Key Concepts Deep Dive

### Concept 1: The Template-Driven Architecture Pattern

#### What Is It?

A **template-driven architecture** separates the **structure** of documents from the **logic** that generates them. Instead of embedding document structure in code, you define it in external configuration files that can be modified independently.

**Real-World Analogy:** Think of a template like a form at the DMV. The form (template) defines what information is needed and where it goes. The clerk (your code) fills in the blanks with your specific information. If the DMV needs to add a new field, they print new forms—they don't retrain every clerk.

#### Visual Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TEMPLATE-DRIVEN ARCHITECTURE                              │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     TEMPLATE LAYER (YAML Files)                      │    │
│  │                                                                      │    │
│  │   shared/data/templates/                                             │    │
│  │   ├── engineering.yaml      ← Legal team can edit directly          │    │
│  │   ├── consulting.yaml       ← No code changes needed                │    │
│  │   ├── military.yaml         ← Version controlled separately         │    │
│  │   └── governmental.yaml     ← Easy to add new types                 │    │
│  │                                                                      │    │
│  │   Each file defines:                                                 │    │
│  │   • Template metadata (name, version, description)                   │    │
│  │   • Required sections with their clauses                             │    │
│  │   • Placeholder variables ({{variable_name}})                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     STORE LAYER (Python)                             │    │
│  │                                                                      │    │
│  │   TemplateStore                                                      │    │
│  │   ┌──────────────────────────────────────────────────────────────┐  │    │
│  │   │  Responsibilities:                                            │  │    │
│  │   │  • Load YAML files from disk                                  │  │    │
│  │   │  • Validate against Pydantic schemas                          │  │    │
│  │   │  • Cache loaded templates for performance                     │  │    │
│  │   │  • Provide type-safe access to templates                      │  │    │
│  │   │                                                               │  │    │
│  │   │  Methods:                                                     │  │    │
│  │   │  • load(template_type) → ContractTemplate (fresh from disk)   │  │    │
│  │   │  • get(template_type) → ContractTemplate (cached)             │  │    │
│  │   │  • list_available() → list[TemplateType]                      │  │    │
│  │   │  • clear_cache() → None                                       │  │    │
│  │   └──────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     ENGINE LAYER (Chapter 14)                        │    │
│  │                                                                      │    │
│  │   ContractGeneratorEngine                                            │    │
│  │   • Receives template from TemplateStore                             │    │
│  │   • Fills placeholders with form data                                │    │
│  │   • Validates completeness                                           │    │
│  │   • Generates final contract document                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### The "Aha!" Moment

The key insight is that **templates are data, not code**. By treating contract structures as configuration data:

1. **Changes don't require deployments** — Edit YAML, reload templates, done
2. **Domain experts can contribute** — Legal team edits templates directly without developer involvement
3. **Testing is simpler** — Validate YAML against schema separately from testing generation logic
4. **Scaling is easier** — 100 contract types = 100 YAML files, same codebase

This is the same pattern used by:

- **Email systems** (email templates in HTML/Jinja)
- **CMS platforms** (page templates in themes)
- **CI/CD systems** (pipeline templates in YAML - GitHub Actions, GitLab CI)
- **Infrastructure as Code** (Terraform modules, Kubernetes manifests)

> **🤔 Common Confusion: "Why not just use a database for templates?"**
>
> You could, but YAML files have advantages for this use case:
>
> - **Version control** — Git tracks every change with full history
> - **Code review** — Template changes go through the same review process as code
> - **No database dependency** — Simpler deployment, works offline
> - **Human readable** — Legal team can read and edit without special tools
>
> For high-volume, frequently-changing templates, a database might make sense. For our contract system with ~4-10 template types that change rarely, files are simpler.

---

### Concept 2: Why YAML for Templates?

#### What Is It?

YAML (YAML Ain't Markup Language) is a human-readable data serialization format. It's designed to be easy for humans to read and write while still being parseable by machines.

#### Comparison Table

| Aspect                      | YAML                                 | JSON                                   | TOML                              | Python Dict                  |
| --------------------------- | ------------------------------------ | -------------------------------------- | --------------------------------- | ---------------------------- |
| **Human Readability**       | ✅ Excellent - clean, minimal syntax | ⚠️ Verbose - lots of quotes and braces | ✅ Good - INI-like sections       | ⚠️ Requires Python knowledge |
| **Comments**                | ✅ Supported with `#`                | ❌ Not supported at all                | ✅ Supported with `#`             | ✅ Supported                 |
| **Multi-line Strings**      | ✅ Easy with `\|` or `>`             | ❌ Requires `\n` escaping              | ⚠️ Verbose triple quotes          | ✅ Triple quotes             |
| **Non-developer Editing**   | ✅ Easy to learn                     | ⚠️ Error-prone (missing commas)        | ✅ Easy for simple configs        | ❌ Requires Python           |
| **Indentation Sensitivity** | ⚠️ Yes - spaces matter               | ❌ No - braces define structure        | ❌ No - sections define structure | ❌ No                        |
| **Python Integration**      | ✅ `yaml.safe_load()`                | ✅ `json.load()`                       | ✅ `tomllib` (3.11+)              | ✅ Native                    |

#### Why We Choose YAML

For **contract templates** specifically, YAML wins because:

1. **Legal teams can read and edit it** — No programming knowledge required, syntax is intuitive
2. **Comments document intent** — Explain WHY a clause exists, not just what it contains
3. **Multi-line text is natural** — Contract clauses are often paragraphs, YAML handles this elegantly
4. **Hierarchical structure is clear** — Sections contain clauses, visually obvious through indentation

#### YAML Syntax Essentials

Before we dive into implementation, let's ensure you understand YAML syntax. This is critical because YAML parsing errors are common and can be frustrating:

```yaml
# This is a comment - YAML supports comments (JSON doesn't!)
# Use comments to explain WHY something exists

# ═══════════════════════════════════════════════════════════════════════════
# BASIC KEY-VALUE PAIRS
# ═══════════════════════════════════════════════════════════════════════════
name: "Engineering Services Agreement" # Strings can be quoted
version: "1.0" # Quotes are optional for simple strings
is_active: true # Booleans: true/false (lowercase)
max_amount: 1000000.00 # Numbers: integers or floats

# ═══════════════════════════════════════════════════════════════════════════
# LISTS (ARRAYS) - Use dashes with consistent indentation
# ═══════════════════════════════════════════════════════════════════════════
required_sections:
  - title: "Scope of Work" # First item
    required: true
  - title: "Payment Terms" # Second item
    required: true

# ═══════════════════════════════════════════════════════════════════════════
# NESTED STRUCTURES - Use indentation (2 spaces is standard)
# ═══════════════════════════════════════════════════════════════════════════
metadata:
  author: "Legal Team"
  last_updated: "2025-01-06"
  tags:
    - engineering
    - services
    - standard

# ═══════════════════════════════════════════════════════════════════════════
# MULTI-LINE STRINGS
# ═══════════════════════════════════════════════════════════════════════════

# Use | for LITERAL (preserves newlines exactly as written)
description: |
  This is a multi-line description.
  Each line break is preserved.
  Great for contract clause text that needs
  specific formatting.

# Use > for FOLDED (joins lines with spaces, like a paragraph)
summary: >
  This text will be joined
  into a single line with
  spaces between words.
```

> **🤔 Common Confusion: "Why does my YAML fail to parse?"**
>
> The most common YAML errors are:
>
> 1. **Inconsistent indentation** — Mix of tabs and spaces (use spaces only, 2 per level!)
> 2. **Missing quotes around special characters** — `title: Section: Overview` fails because of the colon
> 3. **Incorrect list syntax** — Forgetting the dash `-` before list items
> 4. **Trailing spaces** — Invisible but can cause issues
>
> **Pro tip**: Use a YAML validator (VS Code extension, online tool) when editing templates. Most IDEs highlight YAML syntax errors in real-time.

---

### Concept 3: Pydantic Models for Template Validation

#### What Is It?

Pydantic models define the **exact structure** that valid template data must have. When you load YAML and pass it to a Pydantic model, you get either a validated object or a clear error explaining what's wrong.

#### The Problem with Unvalidated YAML

Loading YAML gives you a plain Python dictionary. What happens if someone makes a typo in the template file?

```yaml
# Typo: "requred_sections" instead of "required_sections"
name: "Engineering Agreement"
type: engineering
requred_sections: # ← TYPO! Missing 'i' - but YAML doesn't care
  - title: "Scope"
```

```python
# Without Pydantic validation - error happens LATER, far from the source
data = yaml.safe_load(file)
print(data)  # {'name': '...', 'requred_sections': [...]}  # Looks fine!

# ... 100 lines later, in a completely different function ...
sections = data["required_sections"]  # KeyError! But WHY? WHERE?
```

The error only appears when you try to USE the template—possibly in production, possibly affecting a customer. The error message doesn't tell you the template file had a typo.

#### The Solution: Pydantic Schema Validation

With Pydantic, we define **exactly what a valid template looks like**:

```python
from pydantic import BaseModel, Field

class ContractTemplate(BaseModel):
    """
    Pydantic model that defines the EXACT structure of a valid template.

    If the YAML doesn't match this schema, Pydantic raises a ValidationError
    IMMEDIATELY when loading—not later when you try to use it.
    """
    name: str = Field(..., min_length=1)
    type: TemplateType
    required_sections: list[SectionTemplate]  # Note: correct spelling enforced!
```

Now the typo is caught immediately:

```python
# With Pydantic validation - error happens IMMEDIATELY with clear message
data = yaml.safe_load(file)
template = ContractTemplate(**data)
# ValidationError: Field required [type=missing, input_value={'name': '...', 'requred_sections': [...]}, input_type=dict]
#   For further information visit https://errors.pydantic.dev/2.6/v/missing
```

The error tells you:

- **What's wrong**: Field `required_sections` is missing
- **What you provided**: Shows the actual input with the typo visible
- **Where to learn more**: Link to documentation

#### The Template Model Hierarchy

Our template system has three levels of models, like Russian nesting dolls:

```
ContractTemplate (the whole contract template)
├── name: str                              # "Engineering Services Agreement"
├── type: TemplateType                     # TemplateType.ENGINEERING
├── version: str                           # "1.0"
├── description: str                       # "Standard template for..."
└── required_sections: list[SectionTemplate]
    ├── title: str                         # "Scope of Work"
    ├── required: bool                     # True
    └── clauses: list[ClauseTemplate]
        ├── title: str                     # "Project Description"
        ├── placeholder: str               # "{{project_description}}"
        └── required: bool                 # True
```

Each level validates its own fields, and Pydantic validates the entire hierarchy when you create a `ContractTemplate`.

> **⚡ Performance Note:** Pydantic validation is fast—typically microseconds for our template sizes. The validation cost is negligible compared to the debugging time saved by catching errors early.

---

### Concept 4: The Store Pattern (Repository Pattern)

#### What Is It?

The **Store pattern** (also called Repository pattern) provides a **clean abstraction** for data access. Instead of scattering file I/O code throughout your application, you centralize it in a dedicated class that handles all the details.

**Real-World Analogy:** Think of a library. You don't go into the stacks and search for books yourself—you ask the librarian (the Store). The librarian knows where everything is, can find things quickly, and handles all the organizational details. You just say "I need the engineering template" and get it back.

#### Without Store Pattern (Scattered Code)

```python
# ❌ File I/O scattered throughout codebase - hard to maintain

def generate_contract(template_type: str):
    file_path = f"templates/{template_type}.yaml"
    with open(file_path) as f:
        data = yaml.safe_load(f)
    template = ContractTemplate(**data)
    # ... generate contract

def check_compliance(template_type: str, contract_text: str):
    file_path = f"templates/{template_type}.yaml"  # Duplicated!
    with open(file_path) as f:                      # Duplicated!
        data = yaml.safe_load(f)                    # Duplicated!
    template = ContractTemplate(**data)             # Duplicated!
    # ... check compliance

def list_template_options():
    templates = []
    for file in Path("templates").glob("*.yaml"):   # Different path handling!
        with open(file) as f:
            data = yaml.safe_load(f)
        templates.append(data["name"])
    return templates
```

**Problems:**

- Same file loading code duplicated everywhere
- Path handling inconsistent across functions
- No caching—same file loaded repeatedly
- Hard to test—each function does its own I/O
- If file location changes, must update everywhere

#### With Store Pattern (Centralized)

```python
# ✅ Centralized in TemplateStore - clean and maintainable

class TemplateStore:
    """All file I/O logic in one place."""

    def get(self, template_type: TemplateType) -> ContractTemplate:
        # Handles: path resolution, file reading, parsing, validation, caching
        ...

# Usage throughout codebase - clean and consistent
def generate_contract(template_type: TemplateType, store: TemplateStore):
    template = store.get(template_type)  # One line!
    # ... generate contract

def check_compliance(template_type: TemplateType, contract_text: str, store: TemplateStore):
    template = store.get(template_type)  # Same pattern!
    # ... check compliance

def list_template_options(store: TemplateStore):
    return store.list_available()  # Store handles the details
```

#### Benefits of the Store Pattern

| Benefit                   | Explanation                                                                          |
| ------------------------- | ------------------------------------------------------------------------------------ |
| **Single Responsibility** | File I/O logic is in one place—TemplateStore does ONE thing well                     |
| **Easy Testing**          | Mock the store in tests, not file operations. `store.get()` can return test fixtures |
| **Caching**               | Add caching in one place, benefit everywhere. No duplicate cache implementations     |
| **Flexibility**           | Change storage (files → database → API) without changing any consumers               |
| **Type Safety**           | Store returns typed `ContractTemplate` objects, not raw dicts                        |
| **Error Handling**        | Consistent error handling and messages across all template access                    |

#### Caching Strategy

Our `TemplateStore` implements a simple but effective caching strategy:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CACHING FLOW                                         │
│                                                                              │
│  First call: store.get(TemplateType.ENGINEERING)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  1. Check cache: Is ENGINEERING in _cache?  → NO                    │    │
│  │  2. Load from disk: Read engineering.yaml                           │    │
│  │  3. Parse YAML: yaml.safe_load()                                    │    │
│  │  4. Validate: ContractTemplate(**data)                              │    │
│  │  5. Store in cache: _cache[ENGINEERING] = template                  │    │
│  │  6. Return template                                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Second call: store.get(TemplateType.ENGINEERING)                           │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  1. Check cache: Is ENGINEERING in _cache?  → YES                   │    │
│  │  2. Return cached template immediately (no disk I/O!)               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Performance Impact:                                                         │
│  • First call: ~5-10ms (disk I/O + parsing + validation)                    │
│  • Subsequent calls: ~0.001ms (dictionary lookup)                           │
│  • That's 5000-10000x faster for cached access!                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **🤔 Common Confusion: "When should I use `load()` vs `get()`?"**
>
> | Method          | Use When                                                              | Example                                  |
> | --------------- | --------------------------------------------------------------------- | ---------------------------------------- |
> | `get()`         | Normal usage—you want the template and caching is fine                | Contract generation, compliance checking |
> | `load()`        | Testing, or when you need a fresh copy after template modification    | Unit tests, development iteration        |
> | `clear_cache()` | After modifying templates at runtime, to force reload on next `get()` | Hot-reload scenarios, admin interfaces   |

---

### Concept 5: Placeholder Variables

#### What Is It?

Placeholders are **markers in template text** that get replaced with actual values during contract generation. We use the `{{variable_name}}` syntax (double curly braces), which is a common convention used by many templating systems like Jinja2, Mustache, and Handlebars.

#### How Placeholders Work

```yaml
# In template YAML - placeholders mark where dynamic content goes
clauses:
  - title: "Project Description"
    placeholder: "{{project_description}}"
  - title: "Contract Value"
    placeholder: "The total contract value is {{total_amount}} {{currency}}."
  - title: "Timeline"
    placeholder: "Work shall commence on {{start_date}} and complete by {{end_date}}."
```

```python
# During generation - placeholders are replaced with actual values
form_data = {
    "project_description": "Design and implement a cloud migration strategy",
    "total_amount": "$150,000",
    "currency": "USD",
    "start_date": "January 15, 2026",
    "end_date": "June 30, 2026"
}

# Result after placeholder substitution:
# "The total contract value is $150,000 USD."
# "Work shall commence on January 15, 2026 and complete by June 30, 2026."
```

#### Placeholder Substitution Logic

```python
def fill_placeholders(template_text: str, data: dict[str, str]) -> str:
    """
    Replace {{placeholders}} with actual values from data dictionary.

    WHY: Enable dynamic content in templates without hardcoding values.
         The same template can generate thousands of different contracts.

    WHAT: String substitution for each placeholder variable found in text.

    HOW: Iterate through data dict, replace each {{key}} with its value.

    Args:
        template_text: Text containing {{placeholder}} markers
        data: Dictionary mapping placeholder names to values

    Returns:
        Text with all placeholders replaced by their values

    Example:
        >>> fill_placeholders(
        ...     "Hello {{name}}, your balance is {{amount}}.",
        ...     {"name": "Alice", "amount": "$1,000"}
        ... )
        'Hello Alice, your balance is $1,000.'
    """
    result = template_text
    for key, value in data.items():
        placeholder = f"{{{{{key}}}}}"  # Creates "{{key}}" - note the escaping!
        result = result.replace(placeholder, str(value))
    return result
```

#### Placeholder Naming Conventions

| Convention    | Example                   | Use For                            |
| ------------- | ------------------------- | ---------------------------------- |
| `snake_case`  | `{{project_description}}` | Multi-word variables (recommended) |
| `lowercase`   | `{{amount}}`              | Single-word variables              |
| `descriptive` | `{{client_legal_name}}`   | Clarity over brevity               |

**Naming Rules:**

- Use lowercase letters, numbers, and underscores only
- Start with a letter, not a number
- Be descriptive—`{{client_legal_name}}` is better than `{{cln}}`
- Match the form field names you'll use in the UI

**Avoid:**

- `{{ProjectDescription}}` — Inconsistent with Python conventions
- `{{pd}}` — Too cryptic, hard to understand
- `{{project description}}` — Spaces cause parsing issues
- `{{123_field}}` — Don't start with numbers

> **🤔 Common Confusion: "What if a placeholder isn't in the data dictionary?"**
>
> With our simple `replace()` approach, unfilled placeholders remain in the text as `{{placeholder_name}}`. This is actually useful—you can see what's missing! In Chapter 14, we'll add validation to ensure all required placeholders are filled before generating the final contract.

---

## Implementation Guide (What You Build)

### What You're Building

Alright, let's get our hands dirty. By the end of this section, you'll have created these files for our AI Contract Generator:

```
ai-contract-generator/
├── stores/
│   ├── __init__.py              # Exports TemplateStore and models
│   └── template_store.py        # TemplateStore class + Pydantic models
└── shared/
    └── data/
        └── templates/
            ├── engineering.yaml     # Engineering services template
            ├── consulting.yaml      # Consulting agreement template
            ├── military.yaml        # Military contract template
            └── governmental.yaml    # Governmental contract template
```

> **🤔 Common Confusion: "Why `stores/` and not `shared/stores/`?"**
>
> We're placing `TemplateStore` in the top-level `stores/` directory because it's an infrastructure component that will be used across the entire application. The `shared/` directory is for domain models and utilities. This separation keeps concerns clear: `shared/` = domain logic, `stores/` = data access.

---

### Step-by-Step Plan (Do This in Order)

1. **Create the Pydantic models** — `ClauseTemplate`, `SectionTemplate`, `ContractTemplate`

   - These define the schema that YAML files must match
   - Build from innermost (Clause) to outermost (Contract)

2. **Implement TemplateStore class** — Loading, validation, caching

   - `load()` for fresh reads from disk
   - `get()` for cached access
   - `list_available()` for discovering templates

3. **Create template YAML files** — One for each contract type

   - Engineering, Consulting, Military, Governmental
   - Each with appropriate sections and clauses

4. **Verify everything works** — Run the verification commands
   - Test loading, caching, and validation

---

### Example Pattern (Learn From This)

**Purpose:** Show you the pattern you'll use—not the exact solution.
**Key ideas:** Pydantic model hierarchy, Field definitions, docstring patterns

```python
"""
Example: Hierarchical Pydantic models for configuration

WHY: When you have nested configuration (like templates with sections with clauses),
     you build Pydantic models from the inside out. The innermost model is defined
     first, then models that contain it.

WHAT: Three-level model hierarchy demonstrating the pattern
HOW: Define leaf models first, then container models that reference them
"""

from pydantic import BaseModel, Field
from enum import Enum


class ItemType(str, Enum):
    """Example enum for type safety."""
    STANDARD = "standard"
    PREMIUM = "premium"


class LeafModel(BaseModel):
    """
    The innermost model - no nested models inside.

    WHY: Start with the simplest, most atomic unit of your data structure.
         This model has no dependencies on other custom models.

    Attributes:
        name: Identifier for this item
        value: The actual content or data
        required: Whether this item must be present
    """
    name: str = Field(..., min_length=1, description="Item identifier")
    value: str = Field(default="", description="Item content")
    required: bool = Field(default=True, description="Is this item mandatory?")


class ContainerModel(BaseModel):
    """
    Middle-level model - contains a list of LeafModels.

    WHY: Group related leaf items together. This creates the hierarchy.

    Attributes:
        title: Name of this container
        items: List of LeafModel instances
    """
    title: str = Field(..., min_length=1)
    items: list[LeafModel] = Field(default_factory=list)


class RootModel(BaseModel):
    """
    Top-level model - the entry point for your configuration.

    WHY: This is what you instantiate when loading configuration.
         It contains all the nested structure.

    Attributes:
        name: Configuration name
        type: Type enum for categorization
        containers: List of ContainerModel instances
    """
    name: str = Field(..., min_length=1)
    type: ItemType
    containers: list[ContainerModel] = Field(default_factory=list)


# Usage example - this is how you'd load from a dict (like parsed YAML)
config_data = {
    "name": "Example Config",
    "type": "standard",
    "containers": [
        {
            "title": "First Container",
            "items": [
                {"name": "Item 1", "value": "Content 1"},
                {"name": "Item 2", "value": "Content 2", "required": False}
            ]
        }
    ]
}

config = RootModel(**config_data)  # Validates entire hierarchy!
print(config.containers[0].items[0].name)  # "Item 1"
```

**What just happened (key points):**

1. **Inside-out definition** — `LeafModel` defined before `ContainerModel` before `RootModel`
2. **Field with defaults** — `Field(default=...)` for optional fields, `Field(...)` for required
3. **Type safety** — Enum ensures only valid types are accepted
4. **Automatic validation** — Creating `RootModel(**data)` validates the entire nested structure

---

### Starter Scaffold (Structure Only — You Fill the TODOs)

**Purpose:** Give you the file shape and hints.
**Why:** You learn by writing the implementation yourself.

**File: `stores/__init__.py`**

```python
"""
Store modules for the AI Contract Generator.

WHY: Centralize data access patterns in dedicated store classes.
     Instead of scattering file I/O throughout the codebase, we have
     specialized stores that handle loading, validation, and caching.

WHAT: Provides store classes for templates (and later: versions, vectors)

HOW: Each store manages a specific data type with:
     - Loading from source (files, database, etc.)
     - Validation against Pydantic schemas
     - Caching for performance

This module exports:
- TemplateStore: Loads and caches contract templates from YAML files
- ContractTemplate: Pydantic model for complete contract templates
- SectionTemplate: Pydantic model for template sections
- ClauseTemplate: Pydantic model for template clauses

Usage:
    from stores import TemplateStore
    from shared.models.enums import TemplateType

    store = TemplateStore()
    template = store.get(TemplateType.ENGINEERING)
    print(template.name)  # "Engineering Services Agreement"
"""

from .template_store import (
    TemplateStore,
    ContractTemplate,
    SectionTemplate,
    ClauseTemplate,
)

__all__ = [
    "TemplateStore",
    "ContractTemplate",
    "SectionTemplate",
    "ClauseTemplate",
]
```

**File: `stores/template_store.py`**

```python
"""
Template store for loading and managing contract templates.

WHY: Centralize template access with validation and caching.
     Without this class, every part of the application would need to:
     1. Know where template files are located
     2. Handle file I/O correctly
     3. Parse YAML safely
     4. Validate against the schema
     5. Implement their own caching

WHAT: Loads YAML templates, validates with Pydantic, caches results.
      Provides a clean interface for the rest of the application.

HOW: Uses Path for cross-platform file operations, yaml.safe_load for
     secure parsing, and a simple dict for caching.

ARCHITECTURE:
    YAML Files (engineering.yaml, consulting.yaml, etc.)
         ↓
    TemplateStore.load() - reads file, parses YAML
         ↓
    Pydantic Models - validate the data structure
         ↓
    Cache - store for fast repeated access
         ↓
    Your Application - uses validated templates

MODEL HIERARCHY (like Russian nesting dolls):
    ContractTemplate (the whole contract)
        └── contains list[SectionTemplate] (chapters)
                └── each contains list[ClauseTemplate] (paragraphs)
"""

from pathlib import Path
from typing import Dict, List, Optional
import yaml

from pydantic import BaseModel, Field
from shared.models.enums import TemplateType


# ============================================================================
# PYDANTIC MODELS FOR TEMPLATES
# ============================================================================

class ClauseTemplate(BaseModel):
    """
    Template for a single clause within a section.

    WHY: Define clause structure with placeholders for dynamic content.
         Clauses are the atomic units of contracts—each represents a single
         legal provision or requirement that can be filled with specific data.

    WHAT: Contains title, placeholder text, and required flag.
          The placeholder uses {{variable_name}} syntax for substitution.

    HOW: Loaded from YAML, validated by Pydantic, used by generator engine.

    Attributes:
        title: The clause heading (e.g., "Project Description")
        placeholder: Template text with {{placeholders}} for substitution
        required: Whether this clause must be included in generated contracts

    Example YAML:
        - title: "Project Description"
          placeholder: "{{project_description}}"
          required: true

    Example Usage:
        >>> clause = ClauseTemplate(
        ...     title="Project Description",
        ...     placeholder="{{project_description}}"
        ... )
        >>> clause.title
        'Project Description'
    """
    # TODO: Add 'title' field
    # Hint: str type, use Field(...) to make it required, add min_length=1
    # Hint: Add description parameter to Field for documentation

    # TODO: Add 'placeholder' field
    # Hint: str type, default to empty string "", this is the template text

    # TODO: Add 'required' field
    # Hint: bool type, default to True (most clauses are required)

    ...


class SectionTemplate(BaseModel):
    """
    Template for a contract section containing multiple clauses.

    WHY: Group related clauses into logical sections for organization.
         Contracts are structured documents—sections provide hierarchy
         and make navigation easier for readers.

    WHAT: Contains section title, required flag, and list of clauses.
          Each section represents a major topic (e.g., "Payment Terms").

    HOW: Sections are loaded from YAML and contain nested ClauseTemplates.
         The generator iterates through sections to build the contract.

    Attributes:
        title: The section heading (e.g., "Scope of Work")
        required: Whether this section must be included
        clauses: List of ClauseTemplate objects in this section

    Example YAML:
        - title: "Payment Terms"
          required: true
          clauses:
            - title: "Total Amount"
              placeholder: "{{total_amount}}"
            - title: "Payment Schedule"
              placeholder: "{{payment_schedule}}"
    """
    # TODO: Add 'title' field (required, non-empty string)

    # TODO: Add 'required' field (bool, default True)

    # TODO: Add 'clauses' field
    # Hint: list[ClauseTemplate] type
    # Hint: Use Field(default_factory=list) for mutable default

    ...


class ContractTemplate(BaseModel):
    """
    Complete contract template loaded from YAML.

    WHY: Provide the full template structure for contract generation.
         This is the top-level model that represents an entire contract type
         (engineering, consulting, military, governmental).

    WHAT: Contains metadata (name, type, version) and all required sections.
          This model is what the generator engine uses to create contracts.

    HOW: Loaded from YAML files by TemplateStore, validated by Pydantic.
         The generator iterates through required_sections to build output.

    Attributes:
        name: Human-readable template name (e.g., "Engineering Services Agreement")
        type: TemplateType enum value identifying the contract category
        version: Semantic version string for template versioning
        description: Optional description of when to use this template
        required_sections: List of SectionTemplate objects

    Example YAML (engineering.yaml):
        name: "Engineering Services Agreement"
        type: engineering
        version: "1.0"
        description: "Standard template for engineering service contracts"
        required_sections:
          - title: "Scope of Work"
            clauses: [...]
    """
    # TODO: Add 'name' field (required, non-empty string)

    # TODO: Add 'type' field (TemplateType enum)

    # TODO: Add 'version' field (string, default "1.0")

    # TODO: Add 'description' field (string, default empty)

    # TODO: Add 'required_sections' field (list of SectionTemplate)

    ...


# ============================================================================
# TEMPLATE STORE CLASS
# ============================================================================

class TemplateStore:
    """
    Manages contract template loading and caching.

    WHY: Centralize template access with efficient caching.
         Without this class, every part of the application would need to
         handle file I/O, parsing, and validation independently.

    WHAT: Loads YAML templates, validates with Pydantic, caches results.

    HOW: Uses Path for file operations, yaml.safe_load for parsing,
         dict for caching.

    Attributes:
        _templates_dir: Path to directory containing template YAML files
        _cache: Dict mapping TemplateType to loaded ContractTemplate

    Example Usage:
        >>> store = TemplateStore()
        >>> template = store.get(TemplateType.ENGINEERING)
        >>> template.name
        'Engineering Services Agreement'

        >>> # Caching in action
        >>> t1 = store.get(TemplateType.ENGINEERING)
        >>> t2 = store.get(TemplateType.ENGINEERING)
        >>> t1 is t2  # Same object from cache
        True
    """

    def __init__(self, templates_dir: Path | None = None):
        """
        Initialize the template store.

        WHY: Allow custom template directory for testing flexibility.
             In production, we use the default location. In tests, we can
             point to a temporary directory with test fixtures.

        Args:
            templates_dir: Directory containing template YAML files.
                          If None, defaults to shared/data/templates/
        """
        # TODO: Set default templates_dir if None
        # Hint: Use Path(__file__).parent.parent / "shared" / "data" / "templates"
        # Hint: This navigates from stores/ up to project root, then into shared/data/templates

        # TODO: Store templates_dir in self._templates_dir

        # TODO: Initialize empty cache dict: self._cache = {}

        ...

    def load(self, template_type: TemplateType) -> ContractTemplate:
        """
        Load a template from YAML file (bypasses cache).

        WHY: Provide fresh template loading for updates and testing.

        Args:
            template_type: The type of template to load

        Returns:
            ContractTemplate validated from YAML file

        Raises:
            FileNotFoundError: If template file doesn't exist
            yaml.YAMLError: If YAML is malformed
            pydantic.ValidationError: If YAML doesn't match schema
        """
        # TODO: Construct file path from template_type
        # Hint: file_path = self._templates_dir / f"{template_type.value}.yaml"

        # TODO: Check if file exists, raise FileNotFoundError with helpful message if not

        # TODO: Open file and parse with yaml.safe_load()
        # Hint: Use 'with open(file_path, 'r', encoding='utf-8') as f:'

        # TODO: Create and return ContractTemplate from parsed data
        # Hint: return ContractTemplate(**data)

        ...

    def get(self, template_type: TemplateType) -> ContractTemplate:
        """
        Get a template with caching.

        WHY: Avoid repeated file I/O for frequently used templates.

        Args:
            template_type: The type of template to get

        Returns:
            ContractTemplate (cached if previously loaded)
        """
        # TODO: Check if template_type is in cache
        # TODO: If not in cache, call load() and store result
        # TODO: Return cached template

        ...

    def list_available(self) -> list[TemplateType]:
        """
        List all available template types.

        WHY: Allow UI to show available options dynamically.

        Returns:
            List of TemplateType values that have corresponding template files
        """
        # TODO: Iterate through all TemplateType values
        # TODO: Check if corresponding file exists
        # TODO: Return list of types that have files

        ...

    def clear_cache(self) -> None:
        """
        Clear the template cache.

        WHY: Allow cache refresh when templates are updated at runtime.
        """
        # TODO: Reset self._cache to empty dict

        ...
```

---

### Template YAML Files (Create These)

Create these four template files in `shared/data/templates/`:

**File: `shared/data/templates/engineering.yaml`**

```yaml
# Engineering Services Agreement Template
# ========================================
# WHY: Standard template for engineering and technical service contracts
# WHAT: Defines required sections for engineering projects at AIECon
# HOW: YAML structure validated by ContractTemplate Pydantic model
#
# Usage: This template is loaded by TemplateStore and used by
#        ContractGeneratorEngine to create engineering contracts.
#
# Placeholders: Use {{variable_name}} syntax for dynamic content.
#               These are replaced with actual values during generation.

name: "Engineering Services Agreement"
type: engineering
version: "1.0"
description: |
  Standard template for engineering and technical service contracts.
  Use this template for projects involving technical deliverables,
  software development, system integration, or engineering consulting.

required_sections:
  # -------------------------------------------------------------------------
  # SCOPE OF WORK SECTION
  # WHY: Defines what work will be performed - the core of any contract
  # -------------------------------------------------------------------------
  - title: "Scope of Work"
    required: true
    clauses:
      - title: "Project Description"
        placeholder: "{{project_description}}"
        required: true
      - title: "Deliverables"
        placeholder: "{{deliverables}}"
        required: true
      - title: "Timeline"
        placeholder: "{{timeline}}"
        required: true
      - title: "Acceptance Criteria"
        placeholder: "{{acceptance_criteria}}"
        required: false

  # -------------------------------------------------------------------------
  # PAYMENT TERMS SECTION
  # WHY: Defines compensation - critical for both parties
  # -------------------------------------------------------------------------
  - title: "Payment Terms"
    required: true
    clauses:
      - title: "Total Contract Value"
        placeholder: "{{total_amount}}"
        required: true
      - title: "Payment Schedule"
        placeholder: "{{payment_schedule}}"
        required: true
      - title: "Late Payment Penalties"
        placeholder: "{{late_payment_terms}}"
        required: false

  # -------------------------------------------------------------------------
  # TECHNICAL REQUIREMENTS SECTION
  # WHY: Engineering contracts need clear technical specifications
  # -------------------------------------------------------------------------
  - title: "Technical Requirements"
    required: true
    clauses:
      - title: "Technical Specifications"
        placeholder: "{{technical_specs}}"
        required: true
      - title: "Quality Standards"
        placeholder: "{{quality_standards}}"
        required: true

  # -------------------------------------------------------------------------
  # INTELLECTUAL PROPERTY SECTION
  # WHY: Engineering work often creates IP - ownership must be clear
  # -------------------------------------------------------------------------
  - title: "Intellectual Property"
    required: true
    clauses:
      - title: "IP Ownership"
        placeholder: "{{ip_ownership}}"
        required: true
      - title: "License Terms"
        placeholder: "{{license_terms}}"
        required: false
```

**File: `shared/data/templates/consulting.yaml`**

```yaml
# Consulting Agreement Template
# =============================
# WHY: Template for professional consulting and advisory services
# WHAT: Defines sections for consulting engagements
# HOW: Focuses on services, rates, and confidentiality

name: "Consulting Agreement"
type: consulting
version: "1.0"
description: |
  Template for professional consulting and advisory services.
  Use for engagements focused on expertise, advice, and guidance
  rather than specific deliverables.

required_sections:
  - title: "Services"
    required: true
    clauses:
      - title: "Service Description"
        placeholder: "{{service_description}}"
        required: true
      - title: "Service Level Agreement"
        placeholder: "{{sla}}"
        required: false

  - title: "Compensation"
    required: true
    clauses:
      - title: "Hourly Rate"
        placeholder: "{{hourly_rate}}"
        required: true
      - title: "Expense Reimbursement"
        placeholder: "{{expense_policy}}"
        required: false

  - title: "Confidentiality"
    required: true
    clauses:
      - title: "Confidential Information"
        placeholder: "{{confidentiality_terms}}"
        required: true
      - title: "Non-Disclosure Period"
        placeholder: "{{nda_period}}"
        required: true
```

**File: `shared/data/templates/military.yaml`**

```yaml
# Military Contract Template
# ==========================
# WHY: Defense contracts have specific compliance requirements
# WHAT: Includes security clearance and DFARS compliance sections
# HOW: Adds government-specific clauses to standard structure

name: "Military Services Contract"
type: military
version: "1.0"
description: |
  Template for defense and military service contracts.
  Includes required compliance sections for government contracting.

required_sections:
  - title: "Contract Overview"
    required: true
    clauses:
      - title: "Contract Number"
        placeholder: "{{contract_number}}"
        required: true
      - title: "Program Description"
        placeholder: "{{program_description}}"
        required: true

  - title: "Security Requirements"
    required: true
    clauses:
      - title: "Security Clearance Level"
        placeholder: "{{clearance_level}}"
        required: true
      - title: "Facility Clearance"
        placeholder: "{{facility_clearance}}"
        required: true
      - title: "ITAR Compliance"
        placeholder: "{{itar_compliance}}"
        required: true

  - title: "DFARS Compliance"
    required: true
    clauses:
      - title: "DFARS Clauses"
        placeholder: "{{dfars_clauses}}"
        required: true
      - title: "Cybersecurity Requirements"
        placeholder: "{{cybersecurity_requirements}}"
        required: true

  - title: "Deliverables and Payment"
    required: true
    clauses:
      - title: "Contract Line Items"
        placeholder: "{{contract_line_items}}"
        required: true
      - title: "Payment Terms"
        placeholder: "{{payment_terms}}"
        required: true
```

**File: `shared/data/templates/governmental.yaml`**

```yaml
# Governmental Contract Template
# ==============================
# WHY: Government contracts require specific regulatory compliance
# WHAT: Includes FAR compliance and public accountability sections
# HOW: Structured for federal, state, or local government contracts

name: "Governmental Services Agreement"
type: governmental
version: "1.0"
description: |
  Template for federal, state, or local government contracts.
  Includes required compliance and accountability sections.

required_sections:
  - title: "Contract Identification"
    required: true
    clauses:
      - title: "Solicitation Number"
        placeholder: "{{solicitation_number}}"
        required: true
      - title: "Agency Name"
        placeholder: "{{agency_name}}"
        required: true
      - title: "Contract Type"
        placeholder: "{{contract_type}}"
        required: true

  - title: "Scope of Services"
    required: true
    clauses:
      - title: "Statement of Work"
        placeholder: "{{statement_of_work}}"
        required: true
      - title: "Performance Standards"
        placeholder: "{{performance_standards}}"
        required: true

  - title: "FAR Compliance"
    required: true
    clauses:
      - title: "Applicable FAR Clauses"
        placeholder: "{{far_clauses}}"
        required: true
      - title: "Small Business Subcontracting"
        placeholder: "{{small_business_plan}}"
        required: false

  - title: "Pricing and Payment"
    required: true
    clauses:
      - title: "Contract Value"
        placeholder: "{{contract_value}}"
        required: true
      - title: "Billing Instructions"
        placeholder: "{{billing_instructions}}"
        required: true
      - title: "Prompt Payment Terms"
        placeholder: "{{prompt_payment}}"
        required: true
```

---

### How to Debug ValidationError (Fast)

When you see a `ValidationError`, read it like this:

1. **Where?** Which field path failed (e.g., `required_sections.0.clauses.1.title`)
2. **What rule?** Type mismatch, missing field, constraint violation
3. **What did you provide?** Compare input vs expected type/constraint

**Mini example:**

```python
# This will fail - let's see how to read the error
from stores import ClauseTemplate

try:
    clause = ClauseTemplate(title="", placeholder="test")  # Empty title!
except ValidationError as e:
    print(e)

# Output:
# 1 validation error for ClauseTemplate
# title
#   String should have at least 1 character [type=string_too_short, input_value='', input_type=str]
#     For further information visit https://errors.pydantic.dev/2.6/v/string_too_short

# Reading this error:
# - Field: "title"
# - Rule: "String should have at least 1 character" (min_length=1 constraint)
# - Input: '' (empty string)
# - Fix: Provide a non-empty title
```

> **Tip:** The error message includes a URL to Pydantic's documentation explaining that specific error type. Click it when you're confused!

---

## Acceptance Criteria

How do you know you're done? Here's the checklist. If all of these are true, you've nailed it:

| ✓   | Criterion                                                | How to Verify                            | Quality Level |
| --- | -------------------------------------------------------- | ---------------------------------------- | ------------- |
| ☐   | `stores/__init__.py` exports TemplateStore and models    | `from stores import TemplateStore` works | Acceptable    |
| ☐   | `ClauseTemplate` has title, placeholder, required fields | Create instance, check attributes        | Acceptable    |
| ☐   | `SectionTemplate` has title, required, clauses fields    | Create instance with nested clauses      | Acceptable    |
| ☐   | `ContractTemplate` has all 5 fields                      | Create instance with full structure      | Acceptable    |
| ☐   | `TemplateStore.load()` reads and validates YAML          | Loading returns ContractTemplate         | Acceptable    |
| ☐   | `TemplateStore.get()` caches templates                   | `t1 is t2` returns True                  | Excellent     |
| ☐   | `TemplateStore.list_available()` returns types           | Returns list of TemplateType enums       | Acceptable    |
| ☐   | All 4 template YAML files exist and are valid            | Each loads without ValidationError       | Acceptable    |
| ☐   | Invalid YAML raises clear ValidationError                | Test with typo in template               | Excellent     |
| ☐   | All code has WHY/WHAT/HOW docstrings                     | Review docstrings                        | Excellent     |

### Quality Rubric

| Level          | Description                                                                      |
| -------------- | -------------------------------------------------------------------------------- |
| **Needs Work** | Code runs but has issues: missing edge cases, poor naming, no error handling     |
| **Acceptable** | Code works correctly, handles basic errors, follows patterns from examples       |
| **Excellent**  | Clean code, comprehensive error handling, good documentation, handles edge cases |

> **Pro tip:** Don't skip the verification. It's tempting to eyeball it and move on, but these checks catch the subtle bugs that bite you three chapters later.

---

## Verification Commands

⏱️ **Time checkpoint:** You should reach here in ~90 minutes. If you're significantly over, check the Troubleshooting FAQ below.

Time to prove it works. Run these commands and make sure you see the success messages:

```bash
# Test 1: Import template store
# This checks that your __init__.py exports are correct
python -c "
from stores import TemplateStore, ContractTemplate, SectionTemplate, ClauseTemplate
print('✓ All imports work correctly')
"

# Test 2: Load engineering template
# This verifies YAML loading and Pydantic validation
python -c "
from stores import TemplateStore
from shared.models.enums import TemplateType

store = TemplateStore()
template = store.get(TemplateType.ENGINEERING)
print(f'Template: {template.name}')
print(f'Type: {template.type.value}')
print(f'Sections: {len(template.required_sections)}')
for section in template.required_sections:
    print(f'  - {section.title}: {len(section.clauses)} clauses')
print('✓ Template loading works')
"

# Test 3: Verify caching works
# Same object should be returned on repeated calls
python -c "
from stores import TemplateStore
from shared.models.enums import TemplateType

store = TemplateStore()
t1 = store.get(TemplateType.ENGINEERING)
t2 = store.get(TemplateType.ENGINEERING)
assert t1 is t2, 'Caching not working - objects should be identical'
print(f'First call returned: {id(t1)}')
print(f'Second call returned: {id(t2)}')
print('✓ Caching works correctly (same object returned)')
"

# Test 4: List available templates
# Should find all 4 template files
python -c "
from stores import TemplateStore

store = TemplateStore()
available = store.list_available()
print(f'Available templates: {[t.value for t in available]}')
assert len(available) >= 4, f'Expected 4 templates, found {len(available)}'
print('✓ All templates available')
"

# Test 5: Validate all template structures
# Each template should have valid structure
python -c "
from stores import TemplateStore
from shared.models.enums import TemplateType

store = TemplateStore()

for template_type in TemplateType:
    try:
        template = store.get(template_type)
        assert template.name, f'{template_type}: Missing name'
        assert template.type == template_type, f'{template_type}: Type mismatch'
        assert len(template.required_sections) > 0, f'{template_type}: No sections'

        for section in template.required_sections:
            assert section.title, f'{template_type}: Section missing title'
            assert len(section.clauses) > 0, f'{template_type}/{section.title}: No clauses'

        print(f'✓ {template_type.value}: Valid ({len(template.required_sections)} sections)')
    except FileNotFoundError:
        print(f'⚠ {template_type.value}: File not found')

print('✓ All template structures valid')
"
```

**If something fails:** Don't panic. Check the error message, compare your code to the examples above, and look at the Troubleshooting FAQ section. 90% of issues are typos or missing imports.

---

## Troubleshooting FAQ

Common environment and setup issues (not code logic errors):

| Problem                                            | Likely Cause                              | Solution                                              |
| -------------------------------------------------- | ----------------------------------------- | ----------------------------------------------------- |
| `ModuleNotFoundError: No module named 'yaml'`      | PyYAML not installed                      | `pip install pyyaml`                                  |
| `ModuleNotFoundError: No module named 'stores'`    | Not running from project root             | `cd` to project root directory                        |
| `ImportError: cannot import name 'TemplateType'`   | Missing enums module                      | Complete Chapter 2 first                              |
| `FileNotFoundError: ...templates/engineering.yaml` | Templates directory missing or wrong path | Check `shared/data/templates/` exists with YAML files |
| `ValidationError` on valid-looking YAML            | Type mismatch or typo in field name       | Check exact field names match model (case-sensitive)  |
| `yaml.scanner.ScannerError`                        | YAML syntax error (tabs, indentation)     | Use spaces only, 2 per indent level                   |

**Still stuck?** Check these common issues:

1. Are you running Python from the project root directory?
2. Did you create all 4 template YAML files?
3. Are the YAML files using spaces (not tabs) for indentation?
4. Do field names in YAML exactly match Pydantic model field names?

---

## What to Tell Me Next

When you finish implementing, send me:

1. Your `stores/template_store.py` — I'll review your implementation
2. One sample `ContractTemplate` you loaded successfully — show me it works with output
3. One `ValidationError` you intentionally triggered — paste the error message to show you understand validation

This helps me verify you've got the pattern down and can debug issues yourself.

---

## Self-Assessment

Before moving on, rate your confidence (be honest—it helps identify gaps):

| Concept                              | 1 (Lost) | 2 (Shaky) | 3 (Okay) | 4 (Solid) | 5 (Could teach it) |
| ------------------------------------ | -------- | --------- | -------- | --------- | ------------------ |
| Template-driven architecture pattern | ☐        | ☐         | ☐        | ☐         | ☐                  |
| YAML syntax and structure            | ☐        | ☐         | ☐        | ☐         | ☐                  |
| Pydantic model hierarchy             | ☐        | ☐         | ☐        | ☐         | ☐                  |
| Store pattern with caching           | ☐        | ☐         | ☐        | ☐         | ☐                  |
| Placeholder variable syntax          | ☐        | ☐         | ☐        | ☐         | ☐                  |

**If any are 1-2:** Re-read that concept section, try the examples again, or ask for help before continuing.

---

## Interactive Checkpoint Exercise

**Purpose:** Verify you understand the concepts by applying them to a guided exercise.

**Task**: Create and test a custom template programmatically (without YAML files)

```python
"""
Interactive Checkpoint: Creating Templates Programmatically

This exercise verifies you understand:
1. How the Pydantic models relate to each other (hierarchy)
2. How to create templates in code (useful for testing)
3. How serialization works for templates (model_dump)
"""

from stores import (
    TemplateStore,
    ContractTemplate,
    SectionTemplate,
    ClauseTemplate
)
from shared.models.enums import TemplateType

# Step 1: Create a template programmatically
# WHY: Sometimes you need to create templates in code for testing
# WHAT: Build a ContractTemplate from nested Pydantic models
# HOW: Create from innermost (Clause) to outermost (Contract)

custom_template = ContractTemplate(
    name="Custom Test Agreement",
    type=TemplateType.CONSULTING,  # Reusing existing enum
    version="1.0",
    description="A custom template created for testing purposes",
    required_sections=[
        SectionTemplate(
            title="Services",
            required=True,
            clauses=[
                ClauseTemplate(
                    title="Service Description",
                    placeholder="{{services}}",
                    required=True
                ),
                ClauseTemplate(
                    title="Service Level",
                    placeholder="{{sla}}",
                    required=False
                )
            ]
        ),
        SectionTemplate(
            title="Compensation",
            required=True,
            clauses=[
                ClauseTemplate(
                    title="Rate",
                    placeholder="{{hourly_rate}} per hour",
                    required=True
                )
            ]
        )
    ]
)

# Step 2: Verify the structure
print(f"Template: {custom_template.name}")
print(f"Type: {custom_template.type.value}")
print(f"Sections: {len(custom_template.required_sections)}")

for section in custom_template.required_sections:
    print(f"\n  Section: {section.title}")
    print(f"  Required: {section.required}")
    print(f"  Clauses:")
    for clause in section.clauses:
        print(f"    - {clause.title}: {clause.placeholder}")

# Step 3: Test serialization (useful for saving templates)
yaml_data = custom_template.model_dump()
print(f"\nSerialized keys: {list(yaml_data.keys())}")

# Step 4: Verify round-trip (dict → model → dict)
reconstructed = ContractTemplate(**yaml_data)
assert reconstructed.name == custom_template.name
assert len(reconstructed.required_sections) == len(custom_template.required_sections)

print("\n✓ Checkpoint passed! You understand template creation.")
```

**Expected Output:**

```
Template: Custom Test Agreement
Type: consulting
Sections: 2

  Section: Services
  Required: True
  Clauses:
    - Service Description: {{services}}
    - Service Level: {{sla}}

  Section: Compensation
  Required: True
  Clauses:
    - Rate: {{hourly_rate}} per hour

Serialized keys: ['name', 'type', 'version', 'description', 'required_sections']

✓ Checkpoint passed! You understand template creation.
```

---

## Debugging Challenge

**Purpose:** Apply your knowledge to diagnose and fix a real-world bug (different from the checkpoint—this tests debugging skills, not just understanding).

Real-world debugging scenario: A junior developer wrote this template loading code and it's not working correctly. Users are reporting security concerns and random crashes.

**The Buggy Code:**

```python
import yaml

def load_template(template_type: str) -> dict:
    """Load a template - but this code has multiple bugs!"""
    file_path = f"templates/{template_type}.yaml"
    with open(file_path) as f:
        return yaml.load(f)  # Bug 1: Unsafe!
```

**The Problems:**

When they test it:

```python
# These calls reveal the bugs:
load_template("engineering")
# FileNotFoundError: [Errno 2] No such file or directory: 'templates/engineering.yaml'

load_template("../../../etc/passwd")
# Security risk - could read system files!

load_template("ENGINEERING")
# Fails because case doesn't match file name
```

**Your Task:**

Answer these questions before looking at the solution:

1. What are the **security issues** with this code? (Hint: there are at least 2)
2. Why does `yaml.load()` without a Loader cause a warning/security issue?
3. How would you fix the **path handling** to be robust?
4. What's missing for **type safety** and **validation**?

<details>
<summary>💡 Click to reveal the analysis and fix</summary>

**Issue 1: Path Traversal Attack**

The code accepts arbitrary strings and uses them directly in file paths:

```python
load_template("../../../etc/passwd")  # Could read ANY file on the system!
```

**Fix**: Use an enum to restrict input to valid values only. The enum acts as a whitelist.

**Issue 2: Unsafe YAML Loading**

`yaml.load()` can execute arbitrary Python code embedded in YAML:

```yaml
# Malicious YAML that yaml.load() would execute!
malicious: !!python/object/apply:os.system ["rm -rf /"]
```

**Fix**: Always use `yaml.safe_load()` for untrusted or external input.

**Issue 3: Relative Path Problems**

`"templates/{template_type}.yaml"` is relative to the current working directory, which varies depending on how/where the script is run.

**Fix**: Use `Path(__file__)` to get paths relative to the code file location.

**Issue 4: No Validation**

The function returns a raw dict with no validation. Typos and missing fields aren't caught until much later.

**Fix**: Validate with Pydantic immediately after loading.

**The Corrected Code:**

```python
from pathlib import Path
import yaml

from pydantic import ValidationError
from shared.models.enums import TemplateType
from stores import ContractTemplate


def load_template(template_type: TemplateType) -> ContractTemplate:
    """
    Safely load a template with all security issues fixed.

    WHY: Secure template loading with validation
    WHAT: Loads YAML, validates with Pydantic
    HOW: Enum restricts input, safe_load prevents code execution,
         Path(__file__) ensures consistent paths, Pydantic validates
    """
    # Fix 1: Enum parameter prevents arbitrary file access
    # Only predefined template types are allowed - no path traversal possible

    # Fix 2: Use Path relative to this file, not working directory
    base_dir = Path(__file__).parent / "shared" / "data" / "templates"
    file_path = base_dir / f"{template_type.value}.yaml"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Template not found: {template_type.value}. "
            f"Expected at: {file_path}"
        )

    with open(file_path, 'r', encoding='utf-8') as f:
        # Fix 3: Use safe_load to prevent code execution
        data = yaml.safe_load(f)

    # Fix 4: Validate with Pydantic immediately
    return ContractTemplate(**data)
```

**Key Lessons:**

| Problem        | Solution            | Principle                                  |
| -------------- | ------------------- | ------------------------------------------ |
| Path traversal | Use enums for input | Restrict input to valid values (whitelist) |
| Code execution | `yaml.safe_load()`  | Never trust external data                  |
| Relative paths | `Path(__file__)`    | Paths relative to code, not CWD            |
| No validation  | Pydantic models     | Validate early, fail fast                  |

</details>

---

## Common Mistakes and How to Avoid Them

Look, we've all been there. Here are the traps that catch almost everyone—and how to sidestep them.

### Mistake 1: Using `yaml.load()` Instead of `yaml.safe_load()`

```python
# ❌ BAD: Can execute arbitrary Python code from YAML
data = yaml.load(file)

# ✅ GOOD: Only loads data types, no code execution
data = yaml.safe_load(file)
```

**Here's the thing:** YAML has a feature that lets you embed Python objects, and `yaml.load()` will happily execute them. This is a serious security vulnerability—imagine someone uploading a malicious template that deletes files or steals data. I've seen this break production systems. Always use `safe_load()`.

### Mistake 2: Hardcoding Template Paths

```python
# ❌ BAD: Breaks when run from different directories
file_path = "shared/data/templates/engineering.yaml"

# ✅ GOOD: Works regardless of working directory
file_path = Path(__file__).parent / "shared" / "data" / "templates" / "engineering.yaml"
```

**Real talk:** Relative paths are relative to where you RUN the script, not where the script IS. So `python app.py` and `python src/app.py` resolve paths differently. Using `Path(__file__)` anchors paths to the code file's location, which is consistent.

### Mistake 3: Not Validating After Loading YAML

```python
# ❌ BAD: Returns unvalidated dict - errors happen later, far from source
def load_template(name):
    with open(f"templates/{name}.yaml") as f:
        return yaml.safe_load(f)  # Just a dict, no validation!

# ✅ GOOD: Returns validated Pydantic model - errors happen immediately
def load_template(template_type: TemplateType) -> ContractTemplate:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return ContractTemplate(**data)  # Validated!
```

**Why this trips people up:** The dict looks fine when you print it. The error only appears when you try to ACCESS a field that's misspelled or missing—possibly in production, possibly affecting customers. Validate immediately.

### Mistake 4: Mixing Tabs and Spaces in YAML

```yaml
# ❌ BAD: Tabs cause parsing errors (invisible but deadly)
sections:
	- title: "Scope"  # This is a TAB character!

# ✅ GOOD: Consistent 2-space indentation
sections:
  - title: "Scope"  # Two spaces
```

**The sneaky part:** Tabs and spaces look identical in most editors, but YAML treats them differently. Configure your editor to show whitespace characters, or use "Convert Indentation to Spaces" command.

---

## Security Considerations

### Path Traversal Prevention

```python
# ❌ INSECURE: Accepts arbitrary strings, allows path traversal
def load_template(name: str):
    return yaml.safe_load(open(f"templates/{name}.yaml"))

# Attack: load_template("../../../etc/passwd")
# Could read ANY file the process has access to!

# ✅ SECURE: Enum restricts to predefined values only
def load_template(template_type: TemplateType):
    # TemplateType enum only has: ENGINEERING, CONSULTING, MILITARY, GOVERNMENTAL
    # No way to pass "../../../etc/passwd" - it's not in the enum!
    file_path = templates_dir / f"{template_type.value}.yaml"
    return yaml.safe_load(open(file_path))
```

**Why it matters:** Path traversal is a common attack vector. By using an enum, you create a whitelist of allowed values. The type system itself prevents the attack.

### YAML Code Injection Prevention

```python
# ❌ INSECURE: yaml.load() executes embedded Python
data = yaml.load(file)  # DANGEROUS!

# Malicious YAML could contain:
# !!python/object/apply:os.system ["rm -rf /"]

# ✅ SECURE: yaml.safe_load() only loads data
data = yaml.safe_load(file)  # Safe - only loads strings, numbers, lists, dicts
```

**Why it matters:** In 2013, Ruby on Rails had a critical vulnerability (CVE-2013-0156) caused by unsafe YAML parsing that allowed remote code execution. The same vulnerability exists in Python's `yaml.load()`.

> **⚠️ Security Rule:** Always use `yaml.safe_load()` for any YAML that could come from external sources—user uploads, API responses, configuration files that users can edit.

---

## Quick Check Questions

Before you move on, let's make sure the key concepts clicked. Try answering these without peeking—it's the best way to know if you really got it.

### Question 1: Why do we use `yaml.safe_load()` instead of `yaml.load()`?

<details>
<summary>Click to reveal answer</summary>

`yaml.load()` can execute arbitrary Python code embedded in YAML files using special YAML tags like `!!python/object/apply:`. This is a serious security vulnerability.

`yaml.safe_load()` only loads basic YAML types (strings, numbers, lists, dicts) and ignores any code execution tags.

**The key insight here:** Never trust external data. Even configuration files can be attack vectors if users can modify them.

</details>

### Question 2: When should you use `get()` vs `load()` on TemplateStore?

<details>
<summary>Click to reveal answer</summary>

| Method   | Use When                                                     | Caching                       |
| -------- | ------------------------------------------------------------ | ----------------------------- |
| `get()`  | Normal operation - generating contracts, checking compliance | Yes - returns cached template |
| `load()` | Testing, development, or after template file was modified    | No - always reads from disk   |

**The key insight:** `get()` is for performance (avoid repeated disk I/O), `load()` is for freshness (get the latest version).

</details>

### Question 3: Why use a `TemplateType` enum instead of accepting any string?

<details>
<summary>Click to reveal answer</summary>

**Security:** Prevents path traversal attacks. `"../../../etc/passwd"` isn't a valid enum value.

**Type Safety:** IDE catches typos at write-time. `TemplateType.ENGNEERING` shows an error immediately.

**Discoverability:** `TemplateType.` in your IDE shows all valid options.

**The deeper principle:** Make invalid states unrepresentable. If only 4 template types exist, the type system should only allow those 4 values.

</details>

### Question 4: What happens if a YAML template has a typo in a field name?

<details>
<summary>Click to reveal answer</summary>

Pydantic raises a `ValidationError` immediately when you try to create the model:

```python
# YAML has "requred_sections" (typo) instead of "required_sections"
ContractTemplate(**data)
# ValidationError: Field required [type=missing, ...]
#   required_sections
```

The error tells you exactly which field is missing and what you provided.

**Why this matters for our contract generator:** Errors are caught at template load time, not when a user is waiting for their contract. Fail fast, fail loud.

</details>

### Question 5: How does the template system connect to the rest of the AI Contract Generator?

<details>
<summary>Click to reveal answer</summary>

```
TemplateStore (this chapter)
    ↓ provides templates to
ContractGeneratorEngine (Chapter 14)
    ↓ generates contracts checked by
ContractReviewerAgent (Chapter 17)
    ↓ displayed in
Streamlit UI (Chapters 22-23)
```

Templates define the STRUCTURE. The generator fills in the CONTENT. The reviewer checks COMPLIANCE against the template. The UI lets users SELECT templates and FILL placeholders.

**This is important because:** Every component depends on templates being correctly loaded and validated. If templates are broken, everything downstream breaks.

</details>

---

## Extension: Mini-Project (Optional)

**For learners who want more challenge:** This is an optional extension activity.

**Task:** Add a `validate_template()` method to TemplateStore that checks templates for common issues before they cause problems during contract generation.

**Requirements:**

- [ ] Check that all required sections have at least one clause
- [ ] Check that all placeholders follow `{{lowercase_with_underscores}}` format
- [ ] Check that no titles are empty strings
- [ ] Return a `TemplateValidationResult` with any issues found

**Starter Code:**

```python
import re
from pydantic import BaseModel, Field


class TemplateValidationIssue(BaseModel):
    """A single validation issue found in a template."""
    severity: str  # "error" or "warning"
    location: str  # e.g., "Section: Payment Terms > Clause: Amount"
    message: str   # Description of the issue


class TemplateValidationResult(BaseModel):
    """Result of template validation."""
    valid: bool
    issues: list[TemplateValidationIssue] = Field(default_factory=list)


def validate_template(self, template: ContractTemplate) -> TemplateValidationResult:
    """
    Validate a template for completeness and correctness.

    Checks performed:
    1. Each required section has at least one clause
    2. Placeholders match {{lowercase_with_underscores}} pattern
    3. No empty titles
    """
    issues: list[TemplateValidationIssue] = []

    # Regex for valid placeholder: {{lowercase_with_underscores}}
    placeholder_pattern = re.compile(r'\{\{[a-z][a-z0-9_]*\}\}')

    for section in template.required_sections:
        # TODO: Check required sections have clauses
        # TODO: Check placeholder format in each clause
        # TODO: Check for empty titles
        pass

    return TemplateValidationResult(
        valid=len([i for i in issues if i.severity == "error"]) == 0,
        issues=issues
    )
```

**Verification:**

```bash
python -c "
from stores import TemplateStore
from shared.models.enums import TemplateType

store = TemplateStore()
template = store.get(TemplateType.ENGINEERING)

# Add validate_template method to your TemplateStore class first!
result = store.validate_template(template)

print(f'Template: {template.name}')
print(f'Valid: {result.valid}')
print(f'Issues: {len(result.issues)}')

for issue in result.issues:
    print(f'  [{issue.severity}] {issue.location}: {issue.message}')

print('✓ Mini-project complete!')
"
```

---

## From Scratch vs With Framework

This section shows what you'd have to write WITHOUT Pydantic, helping you appreciate its value.

### The Manual Approach (What We're NOT Doing)

```python
# ❌ WITHOUT Pydantic - verbose, error-prone, no type hints

def validate_template_manually(data: dict) -> dict:
    """Manual template validation - 50+ lines of if statements."""
    errors = []

    # Check name exists and is non-empty string
    if "name" not in data:
        errors.append("Missing required field: name")
    elif not isinstance(data["name"], str):
        errors.append("Field 'name' must be a string")
    elif len(data["name"]) == 0:
        errors.append("Field 'name' cannot be empty")

    # Check type exists and is valid enum value
    if "type" not in data:
        errors.append("Missing required field: type")
    elif data["type"] not in ["engineering", "consulting", "military", "governmental"]:
        errors.append(f"Invalid type: {data['type']}")

    # Check required_sections exists and is a list
    if "required_sections" not in data:
        errors.append("Missing required field: required_sections")
    elif not isinstance(data["required_sections"], list):
        errors.append("Field 'required_sections' must be a list")
    else:
        # Validate each section...
        for i, section in enumerate(data["required_sections"]):
            if "title" not in section:
                errors.append(f"Section {i}: missing title")
            # ... and each clause in each section...
            if "clauses" in section:
                for j, clause in enumerate(section["clauses"]):
                    if "title" not in clause:
                        errors.append(f"Section {i}, Clause {j}: missing title")
                    # ... 30 more lines of validation

    if errors:
        raise ValueError(f"Validation errors: {errors}")

    return data  # Still just a dict, no type hints, no IDE support
```

**Issues:**

- 50+ lines of repetitive validation code
- Easy to miss edge cases (what about None values? Empty lists?)
- No type hints—IDE can't help you
- Error messages are inconsistent
- Returns a dict, not a typed object
- Must be maintained separately from the data structure

### The Framework Approach (What We're Doing)

```python
# ✅ WITH Pydantic - declarative, type-safe, automatic validation

from pydantic import BaseModel, Field

class ClauseTemplate(BaseModel):
    title: str = Field(..., min_length=1)
    placeholder: str = Field(default="")
    required: bool = Field(default=True)

class SectionTemplate(BaseModel):
    title: str = Field(..., min_length=1)
    required: bool = Field(default=True)
    clauses: list[ClauseTemplate] = Field(default_factory=list)

class ContractTemplate(BaseModel):
    name: str = Field(..., min_length=1)
    type: TemplateType
    version: str = Field(default="1.0")
    description: str = Field(default="")
    required_sections: list[SectionTemplate] = Field(default_factory=list)

# Usage - validation is automatic!
template = ContractTemplate(**yaml_data)  # Validates entire hierarchy
print(template.name)  # Type-safe access with IDE autocomplete
```

**Benefits:**

- Declarative schema—structure IS the validation
- Automatic, comprehensive validation
- Clear, consistent error messages with field paths
- Full type hints and IDE support
- Returns typed objects, not dicts
- JSON Schema generation for documentation
- Serialization built-in (`model_dump()`, `model_dump_json()`)

---

## Project Integration

### Learning Path Options

| If you...                             | Then...                                                                       |
| ------------------------------------- | ----------------------------------------------------------------------------- |
| Already know Pydantic and YAML well   | Skip to [Implementation Guide](#implementation-guide-what-you-build)          |
| Want deeper understanding of patterns | Read all 5 concept sections carefully                                         |
| Are struggling with Pydantic basics   | Re-read Chapter 3 first, especially the "BaseModel Basics" section            |
| Want more challenge                   | Complete the [Mini-Project](#extension-mini-project-optional) after finishing |

### How This Chapter Connects to the AI Contract Generator

Let's zoom out and see where this piece fits in the puzzle.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHERE TEMPLATES FIT IN THE SYSTEM                         │
│                                                                              │
│  Chapter 3 (Pydantic Models Core)                                            │
│  └── Contract, Section, Clause models                                        │
│      └── Templates use the SAME hierarchical structure                       │
│          └── ContractTemplate mirrors Contract                               │
│                                                                              │
│  Chapter 5 (Validation Utilities)                                            │
│  └── ValidationResult pattern                                                │
│      └── Used for template validation                                        │
│          └── TemplateValidationResult follows same pattern                   │
│                                                                              │
│  Chapter 6 (This Chapter) ◄── YOU ARE HERE                                   │
│  └── TemplateStore + Template Models                                         │
│      └── Foundation for contract generation                                  │
│                                                                              │
│  Chapter 14 (Contract Generator Engine)                                      │
│  └── Uses TemplateStore.get() to load templates                              │
│      └── Fills placeholders with form data                                   │
│          └── Generates Contract from ContractTemplate                        │
│                                                                              │
│  Chapter 17 (Contract Reviewer Agent)                                        │
│  └── Uses templates to check compliance                                      │
│      └── Compares contract against template requirements                     │
│                                                                              │
│  Chapters 22-23 (Streamlit UI)                                               │
│  └── Uses list_available() to show template dropdown                         │
│      └── User selects template type                                          │
│          └── Form fields generated from template placeholders                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Connection Story

**What came before:** In Chapter 3, we built the core Pydantic models (`Contract`, `Section`, `Clause`) that represent actual contracts. In Chapter 5, we built validation utilities. Those gave us the foundation for data modeling, but we had no way to define what a contract SHOULD look like.

**What we just built:** This chapter's `TemplateStore` and template models fill that gap. Now we have a way to define contract TEMPLATES—the blueprints that specify what sections and clauses each contract type requires. The templates are stored in human-readable YAML files that the legal team can edit.

**What comes next:** Chapter 7 will teach property-based testing with Hypothesis, which we'll use to verify our templates and models work correctly. Then in Chapter 14, the `ContractGeneratorEngine` will use `TemplateStore` to load templates and generate actual contracts by filling in placeholders.

---

## Summary

Alright, let's step back and look at what we just built together.

### The Big Picture

We built a **template-driven architecture** that separates contract structure from generation logic. Before this chapter, we had Pydantic models for contracts but no way to define what different contract types should contain. Now we have YAML templates that define the blueprint for each contract type, a `TemplateStore` that loads and validates them, and a caching layer for performance.

### Don't Miss These Key Points

1. **Templates are data, not code** — Store structure in YAML files that non-developers can edit. This is the same pattern used by CI/CD systems, CMS platforms, and infrastructure-as-code tools.

2. **Always use `yaml.safe_load()`** — Never `yaml.load()`. The security implications are serious—arbitrary code execution from configuration files.

3. **Pydantic validates the entire hierarchy** — When you create a `ContractTemplate`, Pydantic validates all nested `SectionTemplate` and `ClauseTemplate` objects automatically.

4. **The Store pattern centralizes data access** — Instead of scattering file I/O throughout your codebase, one class handles loading, validation, and caching.

5. **Enums prevent path traversal** — Using `TemplateType` enum instead of strings makes it impossible to pass malicious paths like `"../../../etc/passwd"`.

### What We Built

- `stores/template_store.py` — TemplateStore class with load/get/list_available/clear_cache methods, plus ClauseTemplate, SectionTemplate, and ContractTemplate Pydantic models
- `shared/data/templates/*.yaml` — Four contract template files (engineering, consulting, military, governmental)

### The Takeaway

If you remember nothing else from this chapter, remember this: **Separate structure from logic by storing configuration in human-readable files, then validate it with Pydantic before use.** Everything else flows from that insight.

---

## What's Next

**Chapter 7: Testing with Pydantic & Hypothesis**

So we've got templates that define contract structure, and a store that loads and validates them. That's great, but here's the thing—how do we know our templates are correct? How do we know our validation catches all the edge cases?

In the next chapter, we're going to learn **property-based testing** with Hypothesis. Instead of writing individual test cases, we'll define PROPERTIES that should always be true, and Hypothesis will generate hundreds of test cases automatically to try to break our code.

You'll learn:

- **Property-based testing** — Define what should ALWAYS be true, let the computer find counterexamples
- **Hypothesis strategies** — Generate random but valid Pydantic models for testing
- **Testing Pydantic models** — Verify validation rules work correctly
- **The 5 correctness properties** — P1-P5 from the curriculum that our system must satisfy

Think of it like this: we just built the engine, now we need to stress-test it before putting it in a car.

---

## Quick Reference Card

Keep this handy. When you're in the middle of coding and need a quick reminder, this is your cheat sheet:

```python
# ═══════════════════════════════════════════════════════════════════════════
# Template System Quick Reference — AI Contract Generator
# ═══════════════════════════════════════════════════════════════════════════

# Load a template (with caching)
from stores import TemplateStore
from shared.models.enums import TemplateType

store = TemplateStore()
template = store.get(TemplateType.ENGINEERING)

# Access template data
print(template.name)                    # "Engineering Services Agreement"
print(template.type)                    # TemplateType.ENGINEERING
print(len(template.required_sections))  # Number of sections

# Iterate through structure
for section in template.required_sections:
    print(f"Section: {section.title}")
    for clause in section.clauses:
        print(f"  Clause: {clause.title}")
        print(f"  Placeholder: {clause.placeholder}")

# ───────────────────────────────────────────────────────────────────────────
# Common operations
# ───────────────────────────────────────────────────────────────────────────

# List available templates
available = store.list_available()  # [TemplateType.ENGINEERING, ...]

# Force reload (bypass cache)
fresh_template = store.load(TemplateType.ENGINEERING)

# Clear cache (after template files changed)
store.clear_cache()

# Serialize to dict (for saving/sending)
data = template.model_dump()

# Create from dict (for loading)
template = ContractTemplate(**data)

# ───────────────────────────────────────────────────────────────────────────
# Don't forget!
# ───────────────────────────────────────────────────────────────────────────
# ⚠️ Always use yaml.safe_load(), never yaml.load()
# ⚠️ Use TemplateType enum, never raw strings for template types
# ⚠️ Templates are in shared/data/templates/*.yaml
```
