# Chapter 9: Prompt Engineering Basics — The Art of Instruction

<!--
METADATA
Phase: 1 - LLM Fundamentals
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐
Type: Concept + Implementation
Prerequisites: Chapter 7 (LLM Call), Chapter 8 (Client)
Builds Toward: Agents (Ch 26), RAG (Ch 17)
Correctness Properties: P4 (Prompt Variable Substitution)
Project Thread: Prompt Management

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You walk into a coffee shop and say, "I want a drink."
The barista gives you a glass of water.
You complain: "I meant a hot, caffeinated drink!"
Barista: "You didn't say that." 🤷‍♂️

This is exactly how LLMs work. They aren't mind readers; they are **completion machines**. If you give them garbage instructions, you get garbage output.

**Prompt Engineering** isn't some mystical dark art. It's just clear communication. It's the difference between saying *"Write a contract"* (Bad) and *"Write a Utah-compliant software consulting contract for a Senior Engineer, max 2 pages, focused on IP ownership"* (Good).

By the end of this chapter, you won't just be "talking" to AI. You'll be **programming** it with precise, reusable, and version-controlled instructions. 📜

---

## Prerequisites Check

```bash
# Check if you have the directory structure from Ch 8
# Windows:
if exist shared\infrastructure\llm\base.py (echo Ready) else (echo Missing Chapter 8)
# Mac/Linux:
[ -f shared/infrastructure/llm/base.py ] && echo Ready || echo Missing Chapter 8
```

---

## The Story: The "Magic String" Chaos

### The Problem (Strings Everywhere)

You're building a feature to summarize emails.
In `email_bot.py`:
```python
prompt = f"Summarize this email: {email_body}"
```

Later, you want to add "Keep it professional." You update the code.
Then you want to add "Translate to Spanish." You update the code.
Suddenly, your Python files are 90% text strings. You can't version them, you can't test them separately, and if you have a bug in the text, you have to redeploy the whole app.

### The Naive Solution (Text Files)

> "I'll put prompts in `prompts.txt`!"

Okay, but how do you handle variables? `{{name}}`? `{name}`? `%s`?
And what about chat history? System messages?

### The Elegant Solution (Prompt Templates)

We treat Prompts as **Objects**, not strings.
A `PromptTemplate` has:
1. **The Template**: The static text ("Summarize this: {text}")
2. **The Variables**: The dynamic parts (`text`)
3. **The Logic**: Validation to ensure you didn't forget a variable.

---

## Part 1: The Anatomy of a Perfect Prompt

Before we build the code, let's learn the *structure*. Good prompts usually follow the **CIF** pattern:

1.  **C**ontext: "You are a senior lawyer." (Who acts)
2.  **I**nstructions: "Extract the payment terms." (What to do)
3.  **F**ormat: "Output JSON only." (How to look)

### 🔬 Try This! (Hands-On Practice #1)

Let's compare a bad prompt vs. a CIF prompt using the Client we built in Chapter 8.

**Create `test_prompting.py`**:

```python
from shared.infrastructure.llm.client import MultiProviderClient

client = MultiProviderClient()

# ❌ BAD Prompt
bad_prompt = "Fix this contract: The party of the first part agrees to pay money."
print("--- Bad Prompt Result ---")
print(client.generate(bad_prompt))

# ✅ GOOD Prompt (CIF)
good_prompt = """
[CONTEXT]
You are a legal expert specializing in plain English contract rewriting.

[INSTRUCTIONS]
Rewrite the following clause to be clearer and more professional.
Identify the payer and payee clearly.

[INPUT TEXT]
The party of the first part agrees to pay money.

[FORMAT]
Return only the rewritten text. No conversational filler.
"""
print("\n--- Good Prompt Result ---")
print(client.generate(good_prompt))
```

**Run it**. The difference in quality should be obvious!

---

## Part 2: The Template Engine

Now let's build a class to manage these strings so we don't have to copy-paste them.

### 🔬 Try This! (Hands-On Practice #2)

We'll build a `PromptTemplate` class that handles variable substitution safely.

**Step 1: Create `shared/utils/prompting.py`**

```python
from typing import List, Dict, Any
import re

class PromptTemplate:
    def __init__(self, template: str, input_variables: List[str]):
        self.template = template
        self.input_variables = input_variables
        self.validate_template()

    def validate_template(self):
        """Ensure all variables in list exist in template string."""
        for var in self.input_variables:
            # Check for {var} syntax
            if f"{{{var}}}" not in self.template:
                raise ValueError(f"Variable '{var}' expected but not found in template.")

    def format(self, **kwargs) -> str:
        """Replace variables with values."""
        # 1. Check for missing variables
        missing = [var for var in self.input_variables if var not in kwargs]
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
            
        # 2. Format
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Extra variable in template not provided: {e}")
```

**Step 2: Test it**
Create `test_template.py`:

```python
from shared.utils.prompting import PromptTemplate

# Define
summary_prompt = PromptTemplate(
    template="Summarize the following text in {language}:\n\n{text}",
    input_variables=["language", "text"]
)

# Use
final_string = summary_prompt.format(
    language="French",
    text="Hello world. This is a test."
)

print(final_string)
```

**Run it**. You should see the formatted string. Try removing `language="French"` and verify it raises a useful error!

---

## Part 3: Few-Shot Prompting (The Cheat Code)

The single most effective way to improve LLM performance is **Few-Shot Prompting**.
Instead of just giving instructions ("Zero-Shot"), you give instructions + examples.

**Zero-Shot:**
> Extract the fruit: "I ate an apple." -> Apple

**Few-Shot:**
> Extract the fruit.
> Input: "I ate a banana." Output: Banana
> Input: "I ate a cherry." Output: Cherry
> Input: "I ate an apple." Output: Apple

### 🔬 Try This! (Hands-On Practice #3)

Let's verify this actually works. We'll use our `MultiProviderClient` to extract structured data.

**Create `few_shot_test.py`**:

```python
from shared.infrastructure.llm.client import MultiProviderClient

client = MultiProviderClient()

# Task: Extract the project code (PROJ-XXXX)
# The LLM might struggle with messy text without examples.

# 1. Zero-Shot (Hard Mode)
zero_shot = "Extract the project code from: 'The file is in folder 2024/PROJ-ALPHA-01/docs'. Return only the code."
print(f"Zero-Shot: {client.generate(zero_shot)}")

# 2. Few-Shot (Easy Mode)
few_shot = """
Extract the project code from the path.
Examples:
Input: 'users/docs/PROJ-2023-99/budget.pdf' -> Output: PROJ-2023-99
Input: 'backup/PROJ-X-1/save.zip' -> Output: PROJ-X-1

Input: 'The file is in folder 2024/PROJ-ALPHA-01/docs' -> Output:
"""
print(f"Few-Shot: {client.generate(few_shot)}")
```

*Note: Modern models like GPT-4 are smart enough to get Zero-Shot right often, but Few-Shot guarantees the **format** matches your expectations perfectly.*

---

## Common Mistakes

### Mistake #1: Loose Braces `{}` in Prompts
If you are generating JSON examples inside a Python f-string or `.format()` call, you need to escape braces.
**Bad**: `template = "Return JSON: {"key": "value"}"` (Python thinks `{key}` is a variable).
**Good**: `template = "Return JSON: {{ \"key\": \"value\" }}"` (Double braces escape them).

### Mistake #2: Huge Prompts
Don't put 50 examples in the prompt. It costs money (tokens) and confuses the model ("Lost in the Middle" phenomenon). 3-5 examples is usually the sweet spot.

### Mistake #3: Silent Failures
If you use simple string replacement (`str.replace()`) instead of `.format()`, you won't get errors if you miss a variable. The prompt will just contain `{name}` literally, and the LLM will be very confused.

---

## Quick Reference Card

### CIF Pattern
- **C**ontext (Persona)
- **I**nstructions (Task)
- **F**ormat (Output style)

### Python Formatting
```python
template = "Hello {name}"
output = template.format(name="Ahmed")
```

### Escaping JSON in Templates
```python
# To output: {"status": "ok"}
template = "{{ \"status\": \"ok\" }}"
```

---

## Verification (REQUIRED SECTION)

Let's verify your Prompting System.

**Create `verify_prompts.py`**:

```python
"""
Verification script for Chapter 9.
"""
from shared.utils.prompting import PromptTemplate
import sys

print("🧪 Running Prompt Engineering Verification...\n")

# Test 1: Basic Substitution
print("Test 1: Variable Substitution...")
try:
    pt = PromptTemplate("Hello {name}", ["name"])
    res = pt.format(name="World")
    assert res == "Hello World"
    print("✅ Substitution works")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 2: Validation (Missing Variable)
print("Test 2: Validation Logic...")
try:
    pt.format() # Missing 'name'
    print("❌ Failed: Should have raised error")
    sys.exit(1)
except ValueError as e:
    assert "Missing" in str(e)
    print("✅ Caught missing variable error")

# Test 3: Validation (Template Mismatch)
print("Test 3: Template Definition Validation...")
try:
    # 'age' is in input_variables but not in string
    PromptTemplate("Hello {name}", ["name", "age"])
    print("❌ Failed: Should have detected missing placeholder")
    sys.exit(1)
except ValueError as e:
    assert "expected but not found" in str(e)
    print("✅ Caught definition mismatch")

print("\n🎉 Chapter 9 Complete! You can now manage prompts like code.")
```

**Run it:** `python verify_prompts.py`

### Expected output:

```
============================================================
Chapter 9 Verification Tests
============================================================

[Test] Template Substitution
✅ PASS: Template variable substitution works correctly

[Test] Required Variables Validation
✅ PASS: Missing required variables raises appropriate error

[Test] Few-Shot Pattern
✅ PASS: Few-shot examples format correctly

[Test] Message Roles
✅ PASS: System and user messages separate correctly

[Test] Chain-of-Thought Structure
✅ PASS: Chain-of-thought prompt includes reasoning steps

============================================================
Results: 5/5 tests passed
============================================================

🎉 ALL TESTS PASSED! You understand prompt engineering!
```

---

## Summary

**What you learned:**

1. ✅ **Prompt anatomy** — Role, task, guidelines, examples, input, output format
2. ✅ **Template systems** — Reusable prompts with variable substitution
3. ✅ **Few-shot learning** — Teaching through 1-3 examples for consistent output
4. ✅ **Chain-of-thought** — Step-by-step reasoning for complex tasks
5. ✅ **Message roles** — System (persistent behavior) vs user (task-specific)
6. ✅ **Temperature tuning** — Low for structure, high for creativity
7. ✅ **Production patterns** — Centralized prompt management with PromptConfig

**Key Takeaway**: A prompt is not just a question. It is a precise specification. Treat it with the same care you treat your database schema.

**Skills unlocked**: 🎯
- Prompt Engineering
- String Interpolation
- Templating Logic

**Looking ahead**: Now we have a Client (Ch 8) and a Prompt System (Ch 9). In **Chapter 10**, we will learn how to make the AI respond **word-by-word** (Streaming) for that real-time "thinking" feel!

---

**Next**: [Chapter 10: Streaming Responses →](chapter-10-streaming-responses.md)