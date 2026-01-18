# Chapter 25: Output Parsers — The Translator

<!--
METADATA
Phase: 4 - LangChain Core
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 11 (Structured Output), Chapter 18 (LCEL)
Builds Toward: Agents (Ch 26)
Correctness Properties: P7 (Schema Adherence), P33 (Parse Error Recovery)
Project Thread: Data Serialization

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You hire a translator to translate a contract from Japanese to English.
They hand you the translation, but they wrote it on a napkin, in crayon, and added "Hope you like it! :)" at the bottom.
You can't scan that into your legal database. 📄

LLMs are like that translator. Even if they get the *data* right, they wrap it in "Sure, here is the JSON:" or markdown backticks ` ```json `.
Your Python code (`json.loads`) will choke on that extra text.

**Output Parsers** are the strict editor. They take the LLM's messy output, strip the fluff, validate the structure, and hand you a clean Python object. And if the LLM messed up? They send it back to be fixed.

**By the end of this chapter**, you will build pipelines that are immune to "conversational filler" and broken syntax. 🛡️

---

## Prerequisites Check

```bash
# Verify LangChain
pip show langchain-core
```

---

## The Story: The "Backtick" Bug

### The Problem (Markdown Noise)

You ask LLM: "Output JSON: `{"name": "Alice"}`".
LLM replies:
```text
Here is your JSON:
```json
{
  "name": "Alice"
}
```
Have a nice day!
```

If you try `json.loads(response)`, it crashes. It expects `{`, not `Here is...`.

### The Solution (Parsers)

An **Output Parser** does two things:
1.  **Format Instructions**: Tells the LLM *exactly* how to format the output (in the prompt).
2.  **Parsing**: Extracts and validates the data from the response.

---

## Part 1: PydanticOutputParser

This is the gold standard. It uses Pydantic (which you know from Ch 3) to define the schema.

### 🔬 Try This! (Hands-On Practice #1)

Let's build a parser for a Recipe.

**Create `pydantic_parser.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 1. Define the Schema
class Ingredient(BaseModel):
    name: str
    amount: str

class Recipe(BaseModel):
    title: str
    ingredients: List[Ingredient]
    calories: int = Field(description="Estimated calories")

# 2. Setup Parser
parser = PydanticOutputParser(pydantic_object=Recipe)

# 3. Inject Instructions into Prompt
# parser.get_format_instructions() returns a big string explaining JSON schema
print("---" + " Format Instructions " + "---")
print(parser.get_format_instructions())

prompt = ChatPromptTemplate.from_template(
    "Generate a recipe for {dish}.\n{format_instructions}"
)

# 4. The Chain
chain = prompt | model | parser

# 5. Run
print("\n" + "---" + " Result " + "---")
result = chain.invoke({
    "dish": "Omelette",
    "format_instructions": parser.get_format_instructions()
})

print(f"Type: {type(result)}") # Should be <class '__main__.Recipe'>
print(f"Title: {result.title}")
print(f"Calories: {result.calories}")
```

**Run it**.
Notice how we didn't have to manually strip "Here is the recipe". The parser handled it.

---

## Part 2: Handling Errors (Auto-Fixing)

Sometimes, LLMs output invalid JSON (trailing commas, missing quotes).
`PydanticOutputParser` will raise an error.
We can wrap it in an `OutputFixingParser`. This sends the bad JSON *and* the error message back to the LLM and asks it to fix it.

### 🔬 Try This! (Hands-On Practice #2)

**Create `fixing_parser.py`**:

```python
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class Actor(BaseModel):
    name: str
    filmography: list[str]

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
base_parser = PydanticOutputParser(pydantic_object=Actor)

# 1. Simulate Bad Output
# This JSON is broken (single quotes, missing bracket)
bad_json = "{ 'name': 'Tom Hanks', 'filmography': ['Toy Story' " 

print("---" + " Trying Basic Parser " + "---")
try:
    base_parser.parse(bad_json)
except Exception as e:
    print(f"❌ Failed as expected: {e}")

# 2. Setup Fixing Parser
fix_parser = OutputFixingParser.from_llm(parser=base_parser, llm=model)

print("\n" + "---" + " Trying Fixing Parser " + "---")
# The parser calls the LLM: "This JSON failed [error]. Fix it."
result = fix_parser.parse(bad_json)
print(f"✅ Fixed! Name: {result.name}")
print(f"Films: {result.filmography}")
```

**Run it**.
It turns broken text into a valid object! This is **Self-Healing Code**. 🩹

---

## Part 3: JsonOutputParser (Streaming)

`PydanticOutputParser` waits for the *whole* response before parsing.
`JsonOutputParser` can sometimes support partial parsing (advanced), but is generally lighter weight if you just want a Dict, not a Pydantic object.

### 🔬 Try This! (Hands-On Practice #3)

**Create `simple_json.py`**:

```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# We can still use Pydantic to define the schema structure
class Joke(BaseModel):
    setup: str
    punchline: str

model = ChatOpenAI(model="gpt-4o-mini")
parser = JsonOutputParser(pydantic_object=Joke)

prompt = ChatPromptTemplate.from_template(
    "Tell a joke.\n{format_instructions}"
)

chain = prompt | model | parser

# This returns a Dict, not a Pydantic object
result = chain.invoke({"format_instructions": parser.get_format_instructions()})
print(result)
print(type(result)) # <class 'dict'>
```

**Run it**.
Use this when you don't strictly need the validation overhead of Pydantic and just want a dictionary.

---

## Common Mistakes

### Mistake #1: Forgetting Instructions
If you don't pass `format_instructions` to the prompt, the LLM won't know it needs to output JSON. It will just chat.
**Fix**: Always include `{format_instructions}` in your prompt template.

### Mistake #2: Using `OutputFixingParser` for everything
It costs an extra LLM call (money/latency).
**Fix**: Use a good prompt first (temperature=0). Use the fixer only as a fallback mechanism.

### Mistake #3: Validating Logic in Parser
Parsers check *syntax* (Is it valid JSON? Is it an int?). They don't check *truth* (Is the capital of France really Paris?). Use Eval (Ch 21) for truth.

---

## Quick Reference Card

### Parser Types

| Parser | Returns | Use Case |
|--------|---------|----------|
| `StrOutputParser` | `str` | Chat, Essays |
| `PydanticOutputParser` | Object | Strict Data extraction |
| `JsonOutputParser` | `dict` | Flexible Data |
| `OutputFixingParser` | Object | Resilience (Retries) |

---

## Verification (REQUIRED SECTION)

We need to verify **P7 (Schema Adherence)** and **P33 (Error Recovery)**.

**Create `verify_parsers.py`**:

```python
"""
Verification script for Chapter 25.
Properties: P7 (Schema), P33 (Recovery).
"""
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import sys

print("🧪 Running Parser Verification...\n")

class User(BaseModel):
    name: str
    age: int = Field(description="Must be a number")

base_parser = PydanticOutputParser(pydantic_object=User)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# P7: Schema Adherence
print("Test 1: Valid Parsing...")
valid_json = '{"name": "Test", "age": 25}'
user = base_parser.parse(valid_json)
if isinstance(user, User) and user.age == 25:
    print("✅ P7 Passed: Parsed valid JSON into Pydantic model.")
else:
    print("❌ Failed: Valid JSON parsing error.")
    sys.exit(1)

# P33: Parse Error Recovery
print("Test 2: Auto-Fixing...")
# Malformed JSON (missing quotes on keys)
broken_json = '{name: "Test", age: 25}' 

try:
    # First, confirm it fails normally
    base_parser.parse(broken_json)
    print("❌ Failed: Base parser accepted broken JSON (unexpected).")
except Exception:
    print("   (Base parser correctly rejected broken JSON)")

# Now fix it
fix_parser = OutputFixingParser.from_llm(parser=base_parser, llm=model)
fixed_user = fix_parser.parse(broken_json)

if fixed_user.name == "Test":
    print("✅ P33 Passed: OutputFixingParser repaired the JSON.")
else:
    print("❌ Failed: Fixer returned wrong data.")
    sys.exit(1)

print("\n🎉 Chapter 25 Complete! You speak the machine language.")
```

**Run it:** `python verify_parsers.py`

---

## Summary

**What you learned:**

1. ✅ **Format Instructions**: The magic prompt that makes LLMs output JSON.
2. ✅ **PydanticOutputParser**: The bridge between AI text and Python Objects.
3. ✅ **OutputFixingParser**: The self-healing mechanism for broken syntax.
4. ✅ **Robustness**: How to handle the messiness of LLM outputs gracefully.
5. ✅ **Integration**: Combining Prompts, Models, and Parsers in LCEL.

**Key Takeaway**: Never trust raw LLM output. Always Parse and Validate.

**Skills unlocked**: 🎯
- Robust Data Pipelines
- Error Recovery Patterns
- JSON Schema integration

**Looking ahead**: We have all the Core components (Ch 23-25). 
We are finally ready for the exciting part. We are going to build **Agents**.
In **Chapter 26**, we will build an entity that can **Reason** and **Use Tools** to solve problems!

---

**Next**: [Phase 5: Agents (Chapter 26) →](../phase-5-agents/chapter-26-introduction-to-agents.md)
