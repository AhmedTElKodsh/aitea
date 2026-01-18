# Chapter 29: Tool Calling & Function Calling — The API Connector

<!--
METADATA
Phase: 5 - Agents
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 26 (Agents)
Builds Toward: Multi-Agent Systems (Ch 43)
Correctness Properties: P34 (Tool Call Validity), P40 (Schema Validation)
Project Thread: Integration

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're ordering dinner.
**Option A (Text)**: You write a note: "Please get me a pizza, large, with pepperoni." The chef has to read it and hope they understand your handwriting.
**Option B (App)**: You select "Size: Large" and "Topping: Pepperoni" from a dropdown menu.

**ReAct (Chapter 27)** was Option A. The LLM tried to "write" the tool call using text ("Action: Calculator"). It works, but it's messy.
**Function Calling** (or Tool Calling) is Option B. The LLM has a native "menu" of functions. It selects one and fills in the fields with JSON. It's cleaner, faster, and much less prone to typos.

**By the end of this chapter**, you will build a robust system where your AI can push buttons and turn dials on your code directly. 🎛️

---

## Prerequisites Check

```bash
# Verify langchain-core
pip show langchain-core
```

---

## The Story: The "JSON" Struggle

### The Problem (Parsing Text is Hard)

In ReAct, if the LLM outputted:
`Action: search_tool Input: "cats"`
It worked.
But if it outputted:
`I will use the Action: search_tool with Input: 'cats'`
The parser broke. 💥

### The Solution (Native Tool Calling)

OpenAI (and Anthropic, Google) updated their models. Now, they don't just output text. They output a special **Tool Call Object**.
The model *guarantees* (mostly) that the output will match the function signature you provided.

---

## Part 1: Defining Strong Tools

We used `@tool` before. Now let's see how to make them rock-solid using Pydantic.

### 🔬 Try This! (Hands-On Practice #1)

**Create `pydantic_tools.py`**:

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# 1. Define the Arguments Schema
class SearchInput(BaseModel):
    query: str = Field(description="The search query")
    max_results: int = Field(default=5, description="Number of results to return")

# 2. Define the Tool using the args_schema
@tool("internet_search", args_schema=SearchInput)
def search(query: str, max_results: int = 5):
    """Searches the fake internet for results."""
    return f"Searching for '{query}'... Found {max_results} results."

# 3. Inspect the Schema
print(f"Tool Name: {search.name}")
print("JSON Schema:")
import json
print(json.dumps(search.args, indent=2))
```

**Run it**.
Notice how `args` is a perfect JSON Schema? The LLM reads this to know *exactly* what inputs are valid.

---

## Part 2: Binding Tools to the LLM

We don't need a complex AgentExecutor to see tool calling in action. We can do it raw.

### 🔬 Try This! (Hands-On Practice #2)

**Create `bind_tools.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return "Sunny"

tools = [get_weather]

# 1. Bind tools to the model
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
model_with_tools = model.bind_tools(tools)

# 2. Invoke
print("--- Query 1: Weather ---")
response = model_with_tools.invoke("What is the weather in Tokyo?")

# 3. Inspect Response
print(f"Content: '{response.content}'") # Might be empty!
print(f"Tool Calls: {response.tool_calls}") # This is where the magic is
```

**Run it**.
You should see `tool_calls=[{'name': 'get_weather', 'args': {'city': 'Tokyo'}, ...}]`.
The LLM didn't "say" anything. It "did" something.

---

## Part 3: Building a Tool Registry

Managing 50 tools is hard. Let's build a **Registry** to keep track of them.

### 🔬 Try This! (Hands-On Practice #3)

**Create `tool_registry.py`**:

```python
from typing import Dict, Callable, List
from langchain_core.tools import BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool
        print(f"✅ Registered tool: {tool.name}")

    def get_list(self) -> List[BaseTool]:
        return list(self._tools.values())

    def execute(self, name: str, args: dict):
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found")
        return self._tools[name].invoke(args)

# Usage
registry = ToolRegistry()

@tool
def calculate_tax(amount: float) -> float:
    """Calculates 10% tax."""
    return amount * 0.1

registry.register(calculate_tax)

# Simulate execution
print(f"Executing: {registry.execute('calculate_tax', {'amount': 100})}")
```

**Run it**.
This pattern is critical for large agents (Ch 43+).

---

## Part 4: Handling Tool Outputs

The LLM gives us the *Call*. We must execute it and give back the *Result*.

### 🔬 Try This! (Hands-On Practice #4)

Let's complete the loop manually.

**Create `tool_loop.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

@tool
def secret_word() -> str:
    """Returns the secret word."""
    return "Pineapple"

tools = [secret_word]
model = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

# Step 1: Ask
messages = [HumanMessage("What is the secret word?")]
ai_msg = model.invoke(messages)
messages.append(ai_msg)

# Step 2: Check for tool calls
if ai_msg.tool_calls:
    for call in ai_msg.tool_calls:
        # Execute
        print(f"Calling: {call['name']}")
        if call['name'] == 'secret_word':
            result = secret_word.invoke(call['args'])
            
            # Create ToolMessage (The response)
            tool_msg = ToolMessage(
                content=str(result),
                tool_call_id=call['id'] # Important! Links response to call
            )
            messages.append(tool_msg)

# Step 3: Get Final Answer
final_response = model.invoke(messages)
print(f"AI: {final_response.content}")
```

**Run it**.
AI: "The secret word is Pineapple." 🍍

---

## Common Mistakes

### Mistake #1: Ignoring `tool_call_id`
When sending the tool result back to the LLM, you MUST include the `tool_call_id` from the request. Otherwise, the LLM doesn't know which function call this result belongs to.

### Mistake #2: Ambiguous Arguments
Function: `search(q: str)`.
LLM might call `search(query="cat")` if your docstring says "query". Pydantic validation (Ch 3) is key here!

### Mistake #3: Too Many Tools
Binding 100 tools confuses the model.
**Fix**: Use separate agents or retrieve tools dynamically (Advanced).

---

## Quick Reference Card

### Binding Tools
```python
llm_with_tools = llm.bind_tools([tool1, tool2])
```

### Checking for Calls
```python
if response.tool_calls:
    # Handle logic
```

---

## Verification (REQUIRED SECTION)

We need to verify **P34 (Validity)** and **P40 (Schema)**.

**Create `verify_tool_calling.py`**:

```python
"""
Verification script for Chapter 29.
Properties: P34 (Validity), P40 (Schema).
"""
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import sys

print("🧪 Running Tool Calling Verification...\n")

# P40: Schema Validation
# Define a strict tool
class MathInput(BaseModel):
    a: int = Field(description="First number")
    b: int = Field(description="Second number")

@tool("add_tool", args_schema=MathInput)
def add(a: int, b: int) -> int:
    return a + b

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
model_bound = model.bind_tools([add])

print("Test 1: Schema Adherence...")
# We ask it to add numbers. It MUST output valid JSON for the tool.
res = model_bound.invoke("Add 10 and 20")

if not res.tool_calls:
    print("❌ Failed: No tool call generated.")
    sys.exit(1)

call = res.tool_calls[0]
if call['name'] == 'add_tool' and call['args'] == {'a': 10, 'b': 20}:
    print("✅ P40 Passed: Tool called with correct schema.")
else:
    print(f"❌ Failed: Incorrect call data: {call}")
    sys.exit(1)

# P34: Execution
print("Test 2: Execution...")
# Manually execute to verify connection
result = add.invoke(call['args'])
if result == 30:
    print("✅ P34 Passed: Tool logic executed successfully.")
else:
    print(f"❌ Failed: Math error.")
    sys.exit(1)

print("\n🎉 Chapter 29 Complete! You control the API.")
```

**Run it:** `python verify_tool_calling.py`

---

## Summary

**What you learned:**

1. ✅ **Native Tool Calling**: The modern way to use tools (JSON over Text).
2. ✅ **Pydantic Schemas**: Defining strong contracts for inputs.
3. ✅ **Tool Registry**: Organizing your toolbox.
4. ✅ **The Loop**: Invoke -> Tool Call -> Execute -> Tool Message -> Final Answer.
5. ✅ **Binding**: Connecting Python functions to LLM capabilities.

**Key Takeaway**: Don't parse strings. Use the API. It's safer, faster, and cleaner.

**Skills unlocked**: 🎯
- API Integration
- Function Calling
- Advanced Schema Design

**Looking ahead**: We have Agents. We have Tools. But what if the conversation gets *long*? We need to manage context window limits. In **Chapter 30**, we will learn **Agent Memory & Context Management**.

---

**Next**: [Chapter 30: Agent Memory & Context Management →](chapter-30-agent-memory.md)
