# Chapter 5: Validation Utilities

## Header

- **Phase**: 0 - Foundation (Pydantic-First)
- **Time Estimate**: 1.5 hours
- **Difficulty**: Beginner
- **Prerequisites**: Chapter 3 (Pydantic Models Core), Chapter 4 (Pydantic Advanced)
- **Builds**: `shared/utils/validation.py`
- **Requirements**: Req 2, 5, 8.1, 10

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. **Implement** reusable validation utilities using Pydantic
2. **Create** regex patterns for project codes and emails
3. **Extract** user-friendly error messages from Pydantic ValidationError
4. **Apply** validation patterns for form data validation
5. **Debug** common validation errors and understand error messages

---

## Key Concepts

### 1. Why Centralized Validation?

**Concrete Example First:**

Imagine validation logic scattered across your codebase:

```python
# ❌ BAD: Validation scattered everywhere
# In file1.py
if not re.match(r'^PROJ-\d{4}-\d{4}$', code):
    raise ValueError("Invalid code")

# In file2.py
if not re.match(r'^PROJ-\d{4}-\d{4}$', project_code):  # Duplicated!
    return {"error": "Bad project code"}

# In file3.py
pattern = r'^PROJ-\d{4}-\d{4}$'  # Duplicated again!
if not re.match(pattern, code):
    print("Invalid")
```

**Problems:**

- Pattern duplicated 3 times
- Different error messages
- Hard to update if pattern changes
- No consistency

```python
# ✅ GOOD: Centralized validation
from shared.utils.validation import validate_project_code, PROJECT_CODE_PATTERN

# In file1.py, file2.py, file3.py - all use the same function
if not validate_project_code(code):
    # Handle error consistently
```

**Benefits:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CENTRALIZED VALIDATION                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  shared/utils/validation.py                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ PROJECT_CODE_PATTERN = r'^PROJ-\d{4}-\d{4}$'                 │   │
│  │ EMAIL_PATTERN = r'^[\w.+-]+@[\w.-]+\.\w+$'                   │   │
│  │                                                               │   │
│  │ def validate_project_code(code: str) -> bool: ...            │   │
│  │ def validate_form_data(data, required) -> ValidationResult   │   │
│  │ def get_pydantic_errors(model, data) -> ValidationResult     │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          │                                           │
│          ┌───────────────┼───────────────┐                          │
│          ▼               ▼               ▼                          │
│     Streamlit UI    API Endpoints    CLI Tools                      │
│     (forms)         (requests)       (scripts)                      │
│                                                                      │
│  Benefits:                                                           │
│  ✅ Single source of truth for patterns                             │
│  ✅ Consistent error messages                                       │
│  ✅ Easy to update and test                                         │
│  ✅ Reusable across the entire application                          │
└─────────────────────────────────────────────────────────────────────┘
```

**Formal Definition:**
**Validation utilities** are centralized functions and patterns that validate input data, providing consistent behavior and error messages across an application.

---

### 2. Project Code Validation

**Concrete Example First:**

Project codes follow a specific format: `PROJ-YYYY-NNNN`

```python
import re

# WHY: Centralize the pattern for reuse
# WHAT: Matches PROJ-YYYY-NNNN format
# HOW: Regex with literal prefix, 4 digits, hyphen, 4 digits
PROJECT_CODE_PATTERN = r'^PROJ-\d{4}-\d{4}$'

def validate_project_code(code: str) -> bool:
    """
    Validate project code format.

    Args:
        code: The project code to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_project_code("PROJ-2025-0001")
        True
        >>> validate_project_code("invalid")
        False
    """
    return bool(re.match(PROJECT_CODE_PATTERN, code))
```

**Pattern Breakdown:**

```
PROJ-2025-0001
│    │    │
│    │    └── \d{4} - Exactly 4 digits (sequence number)
│    └─────── \d{4} - Exactly 4 digits (year)
└──────────── PROJ- - Literal prefix

Full pattern: ^PROJ-\d{4}-\d{4}$
              │                 │
              └── Start anchor  └── End anchor
```

**Valid vs Invalid:**

| Input                  | Valid? | Why               |
| ---------------------- | ------ | ----------------- |
| `PROJ-2025-0001`       | ✅     | Correct format    |
| `PROJ-9999-9999`       | ✅     | Correct format    |
| `proj-2025-0001`       | ❌     | Lowercase         |
| `PROJ-25-01`           | ❌     | Not enough digits |
| `PROJECT-2025-0001`    | ❌     | Wrong prefix      |
| `PROJ-2025-0001-extra` | ❌     | Extra characters  |

---

### 3. Form Data Validation

**Concrete Example First:**

Forms need to validate multiple fields and return all errors at once:

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ValidationResult(BaseModel):
    """
    Structured result from validation operations.

    Attributes:
        valid: Whether all validation passed
        errors: List of error messages
        field_errors: Dict mapping field names to their errors
    """
    valid: bool
    errors: List[str] = []
    field_errors: Dict[str, List[str]] = {}


def validate_form_data(
    data: Dict[str, Any],
    required_fields: List[str]
) -> ValidationResult:
    """
    Validate form data for missing required fields.

    Args:
        data: Form data dictionary
        required_fields: List of required field names

    Returns:
        ValidationResult with valid status and errors

    Example:
        >>> result = validate_form_data({'name': 'Test'}, ['name', 'email'])
        >>> result.valid
        False
        >>> 'email' in result.errors[0]
        True
    """
    errors = []
    field_errors = {}

    for field in required_fields:
        if field not in data or not data[field]:
            error_msg = f"Missing required field: {field}"
            errors.append(error_msg)
            field_errors[field] = [error_msg]

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        field_errors=field_errors
    )
```

**Usage Flow:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FORM VALIDATION FLOW                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User Form Data                                                      │
│  {                                                                   │
│    "project_code": "PROJ-2025-0001",                                │
│    "client_name": "Acme Corp",                                      │
│    "client_email": ""  ← Missing!                                   │
│  }                                                                   │
│         │                                                            │
│         ▼                                                            │
│  validate_form_data(data, ['project_code', 'client_name', 'email']) │
│         │                                                            │
│         ▼                                                            │
│  ValidationResult(                                                   │
│    valid=False,                                                      │
│    errors=["Missing required field: client_email"],                 │
│    field_errors={"client_email": ["Missing required field: ..."]}   │
│  )                                                                   │
│         │                                                            │
│         ▼                                                            │
│  Show errors to user in UI                                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 4. Extracting Pydantic Errors

**Concrete Example First:**

When Pydantic validation fails, we need user-friendly error messages:

```python
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any

def get_pydantic_errors(
    model_class: type,
    data: Dict[str, Any]
) -> ValidationResult:
    """
    Validate data against a Pydantic model and return structured errors.

    Args:
        model_class: The Pydantic model class to validate against
        data: Data dictionary to validate

    Returns:
        ValidationResult with valid status and errors

    Example:
        >>> class User(BaseModel):
        ...     name: str = Field(min_length=1)
        ...     age: int = Field(ge=0)
        >>> result = get_pydantic_errors(User, {'name': '', 'age': -1})
        >>> result.valid
        False
    """
    try:
        model_class(**data)
        return ValidationResult(valid=True)
    except ValidationError as e:
        errors = []
        field_errors = {}

        for error in e.errors():
            # Extract field path (handles nested fields)
            field = '.'.join(str(loc) for loc in error['loc'])
            msg = error['msg']

            errors.append(f"{field}: {msg}")

            if field not in field_errors:
                field_errors[field] = []
            field_errors[field].append(msg)

        return ValidationResult(
            valid=False,
            errors=errors,
            field_errors=field_errors
        )
```

**Pydantic Error Structure:**

```python
# When validation fails, e.errors() returns:
[
    {
        'type': 'string_too_short',
        'loc': ('name',),           # Field location (tuple)
        'msg': 'String should have at least 1 character',
        'input': '',
        'ctx': {'min_length': 1}
    },
    {
        'type': 'greater_than_equal',
        'loc': ('age',),
        'msg': 'Input should be greater than or equal to 0',
        'input': -1,
        'ctx': {'ge': 0}
    }
]
```

---

### 5. Pydantic Model for Form Validation

**Concrete Example First:**

Combine patterns into a reusable form validator:

```python
from pydantic import BaseModel, Field, field_validator
import re

PROJECT_CODE_PATTERN = r'^PROJ-\d{4}-\d{4}$'
EMAIL_PATTERN = r'^[\w.+-]+@[\w.-]+\.\w+$'


class ContractFormData(BaseModel):
    """
    Pydantic model for validating contract form submissions.

    WHY: Centralize form validation with clear error messages
    WHAT: Validates all required contract fields
    HOW: Uses Field constraints and custom validators
    """
    project_code: str = Field(..., pattern=PROJECT_CODE_PATTERN)
    client_name: str = Field(..., min_length=1, max_length=200)
    client_email: str = Field(..., pattern=EMAIL_PATTERN)
    template_type: str = Field(..., min_length=1)

    @field_validator('client_email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        return v.lower()
```

---

## Implementation Guide

### What You're Building

Create `shared/utils/validation.py` with:

```
shared/utils/validation.py
├── Constants
│   ├── PROJECT_CODE_PATTERN
│   └── EMAIL_PATTERN
├── Models
│   ├── ValidationResult
│   ├── ProjectCodeValidator
│   └── ContractFormData
└── Functions
    ├── validate_project_code()
    ├── validate_form_data()
    └── get_pydantic_errors()
```

---

### Starter Scaffold

**File: `shared/utils/validation.py`**

```python
"""
Validation utilities using Pydantic.

WHY: Centralize validation logic for reuse across the application
WHAT: Provides validation functions and Pydantic models for common patterns
HOW: Uses Pydantic Field constraints and validators
"""

from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Dict, Any
import re


# ============================================================================
# CONSTANTS
# ============================================================================

# WHY: Centralize patterns for reuse and easy updates
# WHAT: Regex pattern for project codes (PROJ-YYYY-NNNN)
# HOW: Literal prefix + 4 digits + hyphen + 4 digits
PROJECT_CODE_PATTERN = r'^PROJ-\d{4}-\d{4}$'

# WHY: Basic email validation pattern
# WHAT: Matches common email formats
# HOW: word chars + @ + domain + TLD
# NOTE: For production, consider using email-validator library
EMAIL_PATTERN = r'^[\w.+-]+@[\w.-]+\.\w+$'


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ValidationResult(BaseModel):
    """
    Structured result from validation operations.

    WHY: Provide consistent validation response format
    WHAT: Contains valid status, error list, and field-specific errors
    HOW: Used as return type for all validation functions

    Attributes:
        valid: Whether all validation passed
        errors: List of error messages
        field_errors: Dict mapping field names to their specific errors

    Example:
        >>> result = ValidationResult(valid=False, errors=["Missing field: name"])
        >>> result.valid
        False
    """
    valid: bool
    errors: List[str] = Field(default_factory=list)
    field_errors: Dict[str, List[str]] = Field(default_factory=dict)


class ProjectCodeValidator(BaseModel):
    """
    Validates project code format using Pydantic.

    WHY: Leverage Pydantic's pattern validation
    WHAT: Ensures code matches PROJ-YYYY-NNNN format
    HOW: Uses Field(pattern=...) constraint

    Example:
        >>> ProjectCodeValidator(code="PROJ-2025-0001")  # ✅ Valid
        >>> ProjectCodeValidator(code="invalid")  # ❌ ValidationError
    """
    code: str = Field(..., pattern=PROJECT_CODE_PATTERN)


class ContractFormData(BaseModel):
    """
    Validates contract creation form data.

    WHY: Centralize form validation with clear error messages
    WHAT: Validates all required contract fields
    HOW: Uses Field constraints and custom validators

    Attributes:
        project_code: Unique identifier (PROJ-YYYY-NNNN format)
        client_name: Client's name (1-200 characters)
        client_email: Client's email address (normalized to lowercase)
        template_type: Type of contract template

    Example:
        >>> form = ContractFormData(
        ...     project_code="PROJ-2025-0001",
        ...     client_name="Acme Corp",
        ...     client_email="Contact@ACME.com",
        ...     template_type="engineering"
        ... )
        >>> form.client_email
        'contact@acme.com'
    """
    project_code: str = Field(..., pattern=PROJECT_CODE_PATTERN)
    client_name: str = Field(..., min_length=1, max_length=200)
    client_email: str = Field(..., pattern=EMAIL_PATTERN)
    template_type: str = Field(..., min_length=1)

    @field_validator('client_email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """
        Normalize email to lowercase.

        WHY: Emails are case-insensitive, normalize for consistency
        WHAT: Converts email to lowercase
        HOW: Uses str.lower()
        """
        return v.lower()


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_project_code(code: str) -> bool:
    """
    Validate a project code string.

    WHY: Provide simple boolean validation for project codes
    WHAT: Returns True if code matches PROJ-YYYY-NNNN format
    HOW: Uses Pydantic model internally for validation

    Args:
        code: The project code to validate

    Returns:
        True if code matches PROJ-YYYY-NNNN format, False otherwise

    Example:
        >>> validate_project_code("PROJ-2025-0001")
        True
        >>> validate_project_code("invalid")
        False
    """
    try:
        ProjectCodeValidator(code=code)
        return True
    except ValidationError:
        return False


def validate_form_data(
    data: Dict[str, Any],
    required_fields: List[str]
) -> ValidationResult:
    """
    Validate form data for missing required fields.

    WHY: Check for missing fields before Pydantic validation
    WHAT: Returns ValidationResult with missing field errors
    HOW: Iterates through required fields and checks presence

    Args:
        data: Form data dictionary
        required_fields: List of required field names

    Returns:
        ValidationResult with valid status and list of missing fields

    Example:
        >>> result = validate_form_data({'name': 'Test'}, ['name', 'email'])
        >>> result.valid
        False
        >>> 'email' in result.errors[0]
        True
    """
    errors = []
    field_errors = {}

    for field in required_fields:
        if field not in data or not data[field]:
            error_msg = f"Missing required field: {field}"
            errors.append(error_msg)
            field_errors[field] = [error_msg]

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        field_errors=field_errors
    )


def get_pydantic_errors(
    model_class: type,
    data: Dict[str, Any]
) -> ValidationResult:
    """
    Validate data against a Pydantic model and return structured errors.

    WHY: Extract user-friendly errors from Pydantic ValidationError
    WHAT: Attempts validation and parses error details
    HOW: Catches ValidationError and extracts field/message info

    Args:
        model_class: The Pydantic model class to validate against
        data: Data dictionary to validate

    Returns:
        ValidationResult with valid status and detailed errors

    Example:
        >>> result = get_pydantic_errors(ContractFormData, {'project_code': 'bad'})
        >>> result.valid
        False
        >>> len(result.errors) > 0
        True
    """
    try:
        model_class(**data)
        return ValidationResult(valid=True)
    except ValidationError as e:
        errors = []
        field_errors = {}

        for error in e.errors():
            # Extract field path (handles nested fields)
            field = '.'.join(str(loc) for loc in error['loc'])
            msg = error['msg']

            errors.append(f"{field}: {msg}")

            if field not in field_errors:
                field_errors[field] = []
            field_errors[field].append(msg)

        return ValidationResult(
            valid=False,
            errors=errors,
            field_errors=field_errors
        )
```

---

### Acceptance Criteria

Your implementation is complete when:

- [ ] `PROJECT_CODE_PATTERN` matches `PROJ-XXXX-YYYY` format
- [ ] `EMAIL_PATTERN` matches basic email format
- [ ] `ValidationResult` has `valid`, `errors`, `field_errors` fields
- [ ] `ProjectCodeValidator` validates project code format
- [ ] `ContractFormData` validates all form fields with constraints
- [ ] `ContractFormData` normalizes email to lowercase
- [ ] `validate_project_code()` returns True for valid codes, False otherwise
- [ ] `validate_form_data()` returns ValidationResult with missing fields
- [ ] `get_pydantic_errors()` extracts errors from Pydantic ValidationError
- [ ] All functions have comprehensive docstrings with WHY/WHAT/HOW

---

### Verification Commands

```bash
# Test 1: Import validation utilities
python -c "from shared.utils.validation import validate_project_code, validate_form_data, get_pydantic_errors; print('✓ Imports work')"

# Test 2: Test project code validation
python -c "
from shared.utils.validation import validate_project_code

# Valid codes
assert validate_project_code('PROJ-2025-0001') == True
assert validate_project_code('PROJ-9999-9999') == True

# Invalid codes
assert validate_project_code('proj-2025-0001') == False  # lowercase
assert validate_project_code('PROJ-24-01') == False  # wrong format
assert validate_project_code('invalid') == False

print('✓ Project code validation works')
"

# Test 3: Test form validation
python -c "
from shared.utils.validation import validate_form_data

# Missing fields
result = validate_form_data({'name': 'Test'}, ['name', 'email', 'phone'])
assert result.valid == False
assert len(result.errors) == 2  # email and phone missing

# All fields present
result = validate_form_data({'name': 'Test', 'email': 'a@b.com'}, ['name', 'email'])
assert result.valid == True

print('✓ Form validation works')
"

# Test 4: Test Pydantic error extraction
python -c "
from shared.utils.validation import get_pydantic_errors, ContractFormData

# Invalid data
result = get_pydantic_errors(ContractFormData, {'project_code': 'bad'})
assert result.valid == False
assert len(result.errors) > 0

print('✓ Pydantic error extraction works')
"

# Test 5: Test email normalization
python -c "
from shared.utils.validation import ContractFormData

form = ContractFormData(
    project_code='PROJ-2025-0001',
    client_name='Test',
    client_email='Test@EXAMPLE.COM',
    template_type='engineering'
)
assert form.client_email == 'test@example.com'

print('✓ Email normalization works')
"

# Test 6: Test pattern constants
python -c "
from shared.utils.validation import PROJECT_CODE_PATTERN, EMAIL_PATTERN
import re

# Test PROJECT_CODE_PATTERN
assert re.match(PROJECT_CODE_PATTERN, 'PROJ-2025-0001')
assert not re.match(PROJECT_CODE_PATTERN, 'invalid')

# Test EMAIL_PATTERN
assert re.match(EMAIL_PATTERN, 'test@example.com')
assert not re.match(EMAIL_PATTERN, 'not-an-email')

print('✓ Pattern constants work')
"
```

---

## Interactive Checkpoint Exercise

Create a validation workflow for contract creation:

```python
from shared.utils.validation import (
    validate_project_code,
    validate_form_data,
    get_pydantic_errors,
    ContractFormData
)

# Simulate form submission
form_data = {
    "project_code": "PROJ-2025-0001",
    "client_name": "Acme Corporation",
    "client_email": "Contact@ACME.com",
    "template_type": "engineering"
}

# Step 1: Check required fields
required = ["project_code", "client_name", "client_email", "template_type"]
result = validate_form_data(form_data, required)
print(f"Required fields check: {result.valid}")

# Step 2: Validate with Pydantic model
result = get_pydantic_errors(ContractFormData, form_data)
print(f"Pydantic validation: {result.valid}")

# Step 3: If valid, create the model
if result.valid:
    form = ContractFormData(**form_data)
    print(f"Email normalized: {form.client_email}")

# Verify
assert result.valid == True
assert form.client_email == "contact@acme.com"
print("✓ Checkpoint passed!")
```

---

## Debugging Challenge

**The Bug:**

A learner wrote this validation function:

```python
def validate_project_code(code: str) -> bool:
    try:
        ProjectCodeValidator(code=code)
        return True
    except Exception:  # Bug: Too broad!
        return False
```

When they test it:

```python
# This should raise an error, but returns False instead
validate_project_code(None)  # Returns False, no error
validate_project_code(123)   # Returns False, no error
```

**Your Task:**

1. Why is catching `Exception` problematic?
2. What specific exception should be caught?
3. What other issues might be hidden?

<details>
<summary>💡 Click to reveal answer</summary>

**Root Cause:**
Catching `Exception` hides ALL errors, including:

- `TypeError` when passing wrong types (None, int)
- `AttributeError` if code has bugs
- Any other unexpected errors

**The Fix:**

```python
from pydantic import ValidationError

def validate_project_code(code: str) -> bool:
    try:
        ProjectCodeValidator(code=code)
        return True
    except ValidationError:  # ✅ Specific exception
        return False
```

**Why This Matters:**

- `ValidationError` is raised for invalid data (expected)
- `TypeError` is raised for wrong types (bug in calling code)
- By catching only `ValidationError`, other bugs surface properly

**Key Lesson:** Always catch the most specific exception possible.

</details>

---

## Quick Check Questions

### Question 1

Why use `Field(pattern=...)` instead of a custom `@field_validator` for regex?

<details>
<summary>Answer</summary>

**Prefer `Field(pattern=...)` when:**

- Simple regex validation is sufficient
- You want the pattern in the JSON schema
- Less code to maintain

**Use `@field_validator` when:**

- You need to transform the value
- Validation logic is complex
- You need custom error messages

```python
# ✅ Simple pattern - use Field
code: str = Field(pattern=r'^PROJ-\d{4}-\d{4}$')

# ✅ Need transformation - use validator
@field_validator('email')
@classmethod
def normalize_email(cls, v):
    return v.lower()  # Transform!
```

</details>

### Question 2

What's the difference between `validate_form_data()` and `get_pydantic_errors()`?

<details>
<summary>Answer</summary>

| Function                | Purpose                           | When to Use                    |
| ----------------------- | --------------------------------- | ------------------------------ |
| `validate_form_data()`  | Check for missing required fields | Before Pydantic validation     |
| `get_pydantic_errors()` | Full Pydantic model validation    | After checking required fields |

**Typical workflow:**

```python
# Step 1: Check required fields exist
result = validate_form_data(data, required_fields)
if not result.valid:
    return result  # Missing fields

# Step 2: Full Pydantic validation
result = get_pydantic_errors(MyModel, data)
if not result.valid:
    return result  # Invalid data
```

</details>

### Question 3

How do you access nested field errors from Pydantic?

<details>
<summary>Answer</summary>

Pydantic uses `loc` (location) tuple for nested fields:

```python
# For nested model:
class Inner(BaseModel):
    value: int = Field(ge=0)

class Outer(BaseModel):
    inner: Inner

# Error location for invalid inner.value:
error['loc']  # ('inner', 'value')

# Convert to string path:
field = '.'.join(str(loc) for loc in error['loc'])  # "inner.value"
```

</details>

---

## Mini-Project

**Task:** Create a comprehensive contract form validator

**Acceptance Criteria:**

- [ ] Validate project code format
- [ ] Validate client name (1-200 chars)
- [ ] Validate and normalize email
- [ ] Validate template type is one of: engineering, consulting, military, governmental
- [ ] Return all errors at once (not just first error)

**Verification:**

```bash
python -c "
from shared.utils.validation import get_pydantic_errors, ContractFormData

# Test with multiple errors
result = get_pydantic_errors(ContractFormData, {
    'project_code': 'bad',
    'client_name': '',
    'client_email': 'not-email',
    'template_type': ''
})

assert result.valid == False
assert len(result.errors) >= 3  # Multiple errors
print(f'Found {len(result.errors)} errors')
print('✓ Mini-project complete!')
"
```

---

## Project Integration

**How This Connects:**

- **Chapter 3 (Core Models)**: Validation utilities work with Contract models
- **Chapter 4 (Advanced Pydantic)**: Uses same validation patterns
- **Chapter 7 (Testing)**: Property tests will verify P1 (project code validation)
- **Chapter 22-23 (Streamlit)**: UI will use these utilities for form validation

**What's Next:**

Chapter 6 will teach the Template System - loading contract templates from YAML files and validating them with Pydantic.

---

## From Scratch vs With Framework

### Manual Approach

```python
import re

def validate_project_code(code):
    if not isinstance(code, str):
        return False
    if not re.match(r'^PROJ-\d{4}-\d{4}$', code):
        return False
    return True

def validate_form(data, required):
    errors = []
    for field in required:
        if field not in data:
            errors.append(f"Missing: {field}")
    # ... 50 more lines of validation
    return errors
```

**Cons:** Verbose, inconsistent, no type safety

### Framework Approach (Pydantic)

```python
from pydantic import BaseModel, Field

class ProjectCodeValidator(BaseModel):
    code: str = Field(pattern=r'^PROJ-\d{4}-\d{4}$')

# Done! Type checking, error messages, JSON schema included
```

**Pros:** Declarative, consistent, reusable, industry standard
