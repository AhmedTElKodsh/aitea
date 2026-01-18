# Chapter 11: Structured Output with Pydantic — Taming the Chaos

<!--
METADATA
Phase: 1 - LLM Fundamentals
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 3 (Pydantic), Chapter 8 (Client)
Builds Toward: Agents (Ch 26), RAG (Ch 17)
Correctness Properties: P7 (Schema Adherence), P8 (Required Field Extraction)
Project Thread: Data Extraction

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You ask a friend for their phone number.
They reply: "*Oh hey! Yeah, it's 555, wait, no, 555-0199. Call me maybe!*"

If you're a human, you understand.
If you're a database, you explode. 💥 databases want `5550199`. They don't want "Oh hey!" or "Call me maybe!".

LLMs love to chat. They love adding "Here is the data you requested:" or "Sure!".
But your code needs raw, clean data. You need **JSON**. And you need it to match your **Pydantic** models exactly.

**By the end of this chapter**, you'll build an **Extraction Engine**. You will feed it messy text (like a movie review), and it will spit out a pristine Python object. No regex required. 🧹

---

## Prerequisites Check

```bash
# Check if Pydantic is installed (we used it in Ch 3)
python -c "import pydantic; print('Pydantic Ready')"
```

---

## The Story: The "Regex" Nightmare

### The Problem (Parsing is Hard)

You want to extract movie details.
Text: "*Inception (2010) is a great movie directed by Nolan.*"

**The "Old" Way (Regex):**
```python
title = re.search(r"(.*) \(", text) # Matches "Inception"
year = re.search(r"\((\d{4})\)", text) # Matches "2010"
```
It works... until the text is: "*The movie 1917 (released in 2019)...*"
Your regex breaks. You write a new one. It breaks again. You cry. 😭

### The Elegant Solution (Structured Output)

We just tell the LLM: "*Here is the Schema. Fill it.*"

```python
class Movie(BaseModel):
    title: str
    year: int
    director: str

# The LLM does the "regex" for us!
result = client.extract(text, Movie)
print(result.year) # 2010 (Integer!)
```

---

## Part 1: The Schema (Pydantic Recap)

We need a shape for our data. Let's reuse our skills from Chapter 3.

### 🔬 Try This! (Hands-On Practice #1)

Define a model for a Restaurant Review.

**Create `extraction_models.py`**:

```python
from pydantic import BaseModel, Field
from typing import List

class Dish(BaseModel):
    name: str
    price: float = Field(description="Price in USD")

class RestaurantReview(BaseModel):
    restaurant_name: str
    rating: int = Field(ge=1, le=5, description="1-5 stars")
    dishes_mentioned: List[Dish]
    sentiment: str = Field(description="positive, negative, or neutral")
```

---

## Part 2: The Prompt (JSON Mode)

To get JSON, we must **ask** for JSON.
OpenAI (and others) have a special flag `response_format={"type": "json_object"}` that forces the model to output valid JSON.

### 🔬 Try This! (Hands-On Practice #2)

Let's verify JSON mode works manually.

**Create `test_json_mode.py`**:

```python
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

prompt = """
Extract data from this review:
"Burger King was okay. The Whopper cost $5.99. Gave it 3 stars."

Return JSON with keys: restaurant_name, rating, dishes (list of name/price).
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You output JSON only."},
        {"role": "user", "content": prompt}
    ],
    response_format={"type": "json_object"} # <--- THE MAGIC SWITCH
)

content = response.choices[0].message.content
print(f"Raw Output:\n{content}")

# Parse it!
data = json.loads(content)
print(f"\nParsed Name: {data['restaurant_name']}")
```

**Run it**. You should see clean JSON.

---

## Part 3: The Abstraction (Adding `extract`)

Now let's upgrade our `LLMProvider` to handle this automatically.

### 🔬 Try This! (Hands-On Practice #3)

We need to update our base class and implementation.

**Step 1: Update `shared/infrastructure/llm/base.py`**

```python
# Add imports
from typing import Type, TypeVar
T = TypeVar("T", bound=BaseModel)

class LLMProvider(ABC):
    # ... existing methods ...

    # NEW METHOD
    @abstractmethod
    def extract(self, text: str, schema: Type[T]) -> T:
        """Extract structured data matching the Pydantic schema."""
        pass
```

**Step 2: Update `shared/infrastructure/llm/openai_provider.py`**

```python
# Add imports
import json

class OpenAIProvider(LLMProvider):
    # ... existing methods ...

    def extract(self, text: str, schema: Type[T]) -> T:
        # 1. Build the prompt
        # We inject the JSON Schema into the prompt so the LLM knows the shape!
        json_schema = schema.model_json_schema()
        
        system_prompt = f"""
        You are a data extraction engine.
        Extract data from the text to match this JSON schema:
        {json.dumps(json_schema, indent=2)}
        
        Return ONLY valid JSON.
        """
        
        # 2. Call API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            temperature=0 # Zero temp for precision
        )
        
        # 3. Parse and Validate
        content = response.choices[0].message.content
        data_dict = json.loads(content)
        
        # This line performs the Pydantic Magic (Validation + Coercion)
        return schema.model_validate(data_dict)
```

**Step 3: Update `shared/infrastructure/llm/client.py`**

```python
class MultiProviderClient:
    # ... existing ...

    def extract(self, text: str, schema: Type[T]) -> T:
        # Simple passthrough (could add fallback logic later!)
        return self.primary_provider.extract(text, schema)
```

---

## Bringing It All Together: The Extraction Engine

Let's test our new superpower.

**Create `run_extraction.py`**:

```python
from shared.infrastructure.llm.client import MultiProviderClient
from pydantic import BaseModel, Field
from typing import List

# 1. Define Model
class MovieFact(BaseModel):
    title: str
    year: int
    actors: List[str]
    is_sci_fi: bool

# 2. Init Client
client = MultiProviderClient(provider="openai") # Or "mock" if you implement it

# 3. The Messy Text
text = """
I watched Interstellar last night. It came out in 2014 I think?
Matthew McConaughey was great. Anne Hathaway too.
Definitely a space movie.
"""

# 4. Magic
print("🧠 Extracting...")
try:
    fact = client.extract(text, MovieFact)
    
    print(f"Title: {fact.title}")
    print(f"Year: {fact.year} (Type: {type(fact.year)})")
    print(f"Actors: {fact.actors}")
    print(f"Sci-Fi?: {fact.is_sci_fi}")
    
except Exception as e:
    print(f"Failed: {e}")
```

**Run it**.
Expected output:
- Title: Interstellar
- Year: 2014 (int)
- Actors: ['Matthew McConaughey', 'Anne Hathaway']
- Sci-Fi: True

It reasoned that "space movie" -> `is_sci_fi=True`. **That is the power of LLMs.** 🧠

---

## Common Mistakes

### Mistake #1: Confusing Descriptions
The `Field(description="...")` is critical. The LLM reads that.
**Bad**: `price: float` (Is it USD? EUR? Cents?)
**Good**: `price: float = Field(description="Price in USD")`

### Mistake #2: Complex Nested Schemas (Hallucinations)
If your schema is 10 layers deep, the LLM might get lost. Keep schemas flat and simple where possible. Break complex extractions into multiple steps.

### Mistake #3: JSON Syntax Errors
Sometimes (rarely with GPT-4), the LLM returns broken JSON (missing `}`). Pydantic will raise a `ValidationError`. You should catch this and maybe retry.

---

## Quick Reference Card

### Converting Model to Schema
```python
schema_str = MyModel.model_json_schema()
```

### Validating Dictionary
```python
# Dict -> Object
obj = MyModel.model_validate(my_dict)

# JSON String -> Object
obj = MyModel.model_validate_json(json_str)
```

---

## Verification (REQUIRED SECTION)

We need to verify that our system correctly enforces schema constraints (Property P7) and extracts fields (Property P8).

**Create `verify_extraction.py`**:

```python
"""
Verification script for Chapter 11.
"""
from shared.infrastructure.llm.client import MultiProviderClient
from shared.infrastructure.llm.mock_provider import MockProvider
from shared.infrastructure.llm.base import LLMProvider
from pydantic import BaseModel
from typing import Type, TypeVar
import json

print("🧪 Running Extraction Verification...\n")

# Setup: We need a Mock Provider that supports extract()
# Since we didn't implement extract() in MockProvider in the hands-on,
# let's quick-patch it here for the test.
class SmartMock(MockProvider):
    def extract(self, text: str, schema: Type[BaseModel]):
        # Simulate a perfect LLM response
        data = {
            "name": "Mock User",
            "age": 42
        }
        return schema.model_validate(data)

# Define Schema
class User(BaseModel):
    name: str
    age: int

# 1. Test Extraction
print("Test 1: Mock Extraction...")
client = MultiProviderClient(provider="mock")
client.primary_provider = SmartMock() # Inject smart mock

user = client.extract("My name is Mock User and I am 42", User)

# Verify P8: Required Field Extraction
assert user.name == "Mock User"
assert user.age == 42
print("✅ Fields extracted correctly")

# Verify P7: Schema Adherence (Type Checking)
assert isinstance(user.age, int)
print("✅ Types enforced correctly")

print("\n🎉 Chapter 11 Complete! You can now restructure reality.")
```

**Run it:** `python verify_extraction.py`

---

## Summary

**What you learned:**

1. ✅ **Unstructured vs Structured**: Text is for humans; JSON is for machines.
2. ✅ **JSON Mode**: Using `response_format` to force LLM compliance.
3. ✅ **Schema Injection**: Passing `model_json_schema()` in the prompt guides the LLM.
4. ✅ **Validation**: Pydantic guarantees the output is safe to use.
5. ✅ **Extraction**: Converting fuzzy language into strict data.

**Key Takeaway**: You don't need to write parsers anymore. You define the **Goal** (Schema), and the AI figures out how to map the data.

**Skills unlocked**: 🎯
- Data Extraction
- Schema Engineering
- Pydantic &lt;&gt; LLM Integration

**Looking ahead**: We have covered the basics: Calls, Clients, Prompts, Streaming, and Extraction.
Now we need to handle the inherent **unreliability** of these systems. In **Chapter 12**, we will build robust **Error Handling & Retries**.

---

**Next**: [Chapter 12: Error Handling & Retries →](chapter-12-error-handling.md)
