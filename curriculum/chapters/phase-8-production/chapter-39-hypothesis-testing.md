# Chapter 39: Testing AI Systems with Hypothesis — Breaking It On Purpose

<!--
METADATA
Phase: 8 - Production
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 15 (Chunking)
Builds Toward: Evaluation (Ch 40)
Correctness Properties: The Meta-Chapter (Explains the P-Properties)
Project Thread: Quality Assurance

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You built a bridge.
**Unit Test**: You drive a Honda Civic over it. It holds.
**Property-Based Test**: You drive a Honda, a tank, a bicycle, and a herd of elephants over it. You heat the bridge to 50°C and freeze it to -50°C.
If it holds *all* of those, it's safe.

In standard coding, we test specific cases: `add(2, 2) == 4`.
In AI Engineering, data is infinite. Users will type emojis, Chinese characters, and SQL injection code. You can't write a test for every case.

**Hypothesis** is a library that writes the tests *for you*. It generates thousands of random inputs to find the *one* edge case that crashes your app.

**By the end of this chapter**, you will learn how to write tests that find bugs you didn't even know existed. 🧪

---

## Prerequisites Check

```bash
pip install hypothesis pytest
```

---

## The Story: The "Invisible" Bug

### The Problem (Manual Tests Miss Things)

You wrote a text chunker (Chapter 15).
You tested it with: `"Hello world"`. It worked.
You released it.
A user uploaded a document containing only Chinese characters `你好你好...`.
Your chunker assumed 1 char = 1 byte. It crashed.

### The Solution (Property-Based Testing)

Instead of testing `input="Hello"`, we tell Hypothesis:
**"Test ANY string."**
Hypothesis tries:
- Empty string `""`
- Giant string `"A" * 10000`
- Emoji string `"😀"`
- Unicode string `"你好"`

It hunts for crashes.

---

## Part 1: Your First Property Test

Let's test a simple function: "Reversing a string".
**Property**: `reverse(reverse(x)) == x`. (If you flip it twice, you get the original).

### 🔬 Try This! (Hands-On Practice #1)

**Create `test_reverse.py`**:

```python
from hypothesis import given, strategies as st

def my_reverse(s: str) -> str:
    return s[::-1]

# 1. Define the input strategy (Any text)
@given(st.text())
def test_reverse_property(s):
    # 2. Assert the property (Invariant)
    assert my_reverse(my_reverse(s)) == s

# Run it with pytest
# pytest test_reverse.py
```

**Run it:** `pytest test_reverse.py`
It passes. Hypothesis ran it 100 times with random garbage.

---

## Part 2: Breaking the Chunker

Let's go back to our Fixed Size Chunker from Chapter 15.
**Property P15**: "No chunk should be larger than `size`."
**Property P16**: "Rejoining chunks should equal original text."

### 🔬 Try This! (Hands-On Practice #2)

**Create `test_chunking_hypothesis.py`**:

```python
from hypothesis import given, strategies as st, settings

# The Code to Test
def chunk_text(text, size):
    if size <= 0: raise ValueError("Size must be > 0")
    return [text[i:i+size] for i in range(0, len(text), size)]

# The Test
@given(
    text=st.text(), 
    size=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=500) # Run 500 times
def test_chunking_properties(text, size):
    # Action
    chunks = chunk_text(text, size)
    
    # Invariant 1: No chunk exceeds size
    for chunk in chunks:
        assert len(chunk) <= size
        
    # Invariant 2: Lossless reconstruction
    assert "".join(chunks) == text

# Run
# pytest test_chunking_hypothesis.py
```

**Run it**.
It passes! But what if we made a mistake?
Change the chunker to: `return [text[i:i+size+1] ...] `.
Run the test again. Hypothesis will find a counter-example immediately!

---

## Part 3: Testing AI Logic (Without Spending Money)

We can't call OpenAI 500 times in a test loop.
But we can test the **parsers** and **prompts** around it.

**Property P7 (Schema Adherence)**: "The JSON Parser should handle ANY valid JSON string matching the schema."

### 🔬 Try This! (Hands-On Practice #3)

We'll test a JSON parser resilience.

**Create `test_json_parsing.py`**:

```python
from hypothesis import given, strategies as st
import json
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    name: str
    age: int

# Strategy: Generate dictionaries that MATCH the schema
user_strategy = st.fixed_dictionaries({
    "name": st.text(),
    "age": st.integers()
})

@given(user_strategy)
def test_pydantic_parsing(data):
    # Simulate LLM outputting valid JSON
    json_str = json.dumps(data)
    
    # Action
    user = User.model_validate_json(json_str)
    
    # Invariant: Parsed data matches input data
    assert user.name == data["name"]
    assert user.age == data["age"]
```

**Run it**.
This proves your Pydantic model correctly handles integers, weird strings, empty strings, etc.

---

## Common Mistakes

### Mistake #1: Testing the LLM itself
Don't use `@given` to call `client.generate()`.
1. It costs money.
2. It's slow.
3. LLMs are non-deterministic.
**Fix**: Mock the LLM. Test the *code around the LLM*.

### Mistake #2: Unrealistic Strategies
Testing a "Year" field with `st.integers()` checks numbers like `-9999999`.
If your app only supports 1900-2100, constrain the strategy: `st.integers(min_value=1900, max_value=2100)`.

### Mistake #3: Ignoring "Flaky" Failures
Hypothesis is deterministic *if* you save the database. If a test fails once, Hypothesis remembers the input that killed it and tries it first next time. Don't ignore these!

---

## Quick Reference Card

### Strategies

| Strategy | Generates |
|----------|-----------|
| `st.text()` | Random Unicode strings |
| `st.integers()` | Random Ints |
| `st.booleans()` | True/False |
| `st.lists(st.integers())` | List of ints |
| `st.one_of(...)` | Union of strategies |

--- 

## Verification (REQUIRED SECTION)

We need to see Hypothesis find a bug. We will plant one intentionally.

**Create `verify_hypothesis.py`**:

```python
"""
Verification script for Chapter 39.
We plant a bug and ensure Hypothesis finds it.
"""
from hypothesis import given, strategies as st, settings, Phase
import sys

print("🧪 Running Hypothesis Verification...\n")

# Buggy Function: Crashes if string length is exactly 10
def buggy_function(s: str):
    if len(s) == 10:
        raise ValueError("Boom! Length 10 found.")
    return s

# The Test
@given(st.text())
@settings(max_examples=500, phases=[Phase.generate]) 
def test_find_bug(s):
    try:
        buggy_function(s)
    except ValueError:
        # We WANT this to happen for verification
        raise AssertionError("Hypothesis successfully found the bug!")

print("Test 1: Hunting for the bug...")
try:
    test_find_bug()
    print("❌ Failed: Hypothesis did NOT find the bug (unlikely with 500 examples).")
    sys.exit(1)
except AssertionError as e:
    if "Hypothesis successfully found" in str(e):
        print("✅ Passed: Hypothesis generated a string of length 10 and crashed the code.")
    else:
        # Real assertion error from Hypothesis
        print("✅ Passed: Hypothesis found the crash.")

print("\n🎉 Chapter 39 Complete! You are a Test Engineer.")
```

**Run it:** `python verify_hypothesis.py`

---

## Summary

**What you learned:**

1. ✅ **Unit vs Property**: Unit tests check one case; Property tests check *all* cases.
2. ✅ **Strategies**: Describing the *shape* of data (Int, String, List).
3. ✅ **Invariants**: Truths that never change (Reverse(Reverse(x)) == x).
4. ✅ **Fuzzing**: Throwing random data at parsers to break them.
5. ✅ **Mocking**: Testing logic without calling APIs.

**Key Takeaway**: If you can define *what* your code should satisfy (Properties), Hypothesis will find *how* it breaks.

**Skills unlocked**: 🎯
- Property-Based Testing
- Fuzzing
- Robust Engineering

**Looking ahead**: We can test the *code*. But how do we test the *quality* of the AI's answers over time? In **Chapter 40**, we will learn about **Evaluation with LangSmith** (Traces and Datasets).

---

**Next**: [Chapter 40: Evaluation with LangSmith →](chapter-40-evaluation-langsmith.md)
