# Chapter 26: Introduction to Agents — The Autonomous Brain

<!--
METADATA
Phase: 5 - Agents
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 18 (LCEL)
Builds Toward: Multi-Agent Systems (Ch 43)
Correctness Properties: P34 (Tool Call Validity), P35 (Loop Termination)
Project Thread: Automation

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You hire a personal assistant.
**Scenario A (The Chain)**: You hand them a strict checklist. "1. Get coffee. 2. Check mail. 3. Call mom." If the coffee shop is closed, they crash. They don't know what to do next. 🤖
**Scenario B (The Agent)**: You say, "Make sure I'm caffeinated and my mom is happy." The assistant goes to the coffee shop. It's closed. *They decide* to go to the tea shop instead. They improvise. 😎

**Chains** (what we've built so far) are checklists.
**Agents** are thinkers. They have a "Toolbox" (Calendar, Email, Calculator) and a "Goal". They figure out the steps themselves.

**By the end of this chapter**, you will build an AI that can use Python functions as tools to solve problems you didn't explicitly program it for.

---

## Prerequisites Check

```bash
# We need langchain community for tool utilities
pip install langchain-community
```

---

## The Story: The "Math" Problem

### The Problem (LLMs are bad at Math)

User: "What is 4.23 * 9.81?"
LLM: "41.5." (Actually it's 41.4963). 
LLMs are language models, not calculators. They hallucinate math.

### The Solution (Tools)

We give the LLM a **Calculator Tool**.
User: "What is 4.23 * 9.81?"
LLM Thought: "I need to calculate this."
Action: `Calculator(4.23, 9.81)`
Observation: `41.4963`
LLM Answer: "The answer is 41.4963."

The LLM becomes the **Orchestrator**, not the computer.

---

## Part 1: Defining Tools

A tool is just a Python function with a clear docstring. The LLM reads the docstring to know *when* and *how* to use it.

### 🔬 Try This! (Hands-On Practice #1)

Let's create a tool using the `@tool` decorator.

**Create `tools.py`**:

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Adds two integers together."""
    print(f"   (Tool: Adding {a} + {b})")
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiplies two integers."""
    print(f"   (Tool: Multiplying {a} * {b})")
    return a * b

# Inspect the tool (This is what the LLM sees)
print(f"Name: {add.name}")
print(f"Description: {add.description}")
print(f"Args: {add.args}")
```

**Run it**.
The LLM will see "Adds two integers together" and know exactly what to do.

---

## Part 2: The Agent Loop (ReAct)

The Agent Loop is often called **ReAct** (Reasoning + Acting).
1.  **Reason**: "I need to add 5 and 5."
2.  **Act**: Call `add(5, 5)`.
3.  **Observe**: Result is 10.
4.  **Reason**: "Now I need to multiply by 2."
5.  **Act**: Call `multiply(10, 2)`.
6.  **Observe**: Result is 20.
7.  **Finish**: "The answer is 20."

---

## Part 3: Building the Agent

We'll use `create_tool_calling_agent`. This is optimized for models like GPT-4 that have native "Function Calling" capabilities.

### 🔬 Try This! (Hands-On Practice #2)

**Create `simple_agent.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from tools import add, multiply # Import our tools

load_dotenv()

# 1. Setup Tools & Model
tools = [add, multiply]
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. Define Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful math assistant."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"), # Where the loop happens
])

# 3. Create the Agent
agent = create_tool_calling_agent(model, tools, prompt)

# 4. Create the Executor (The Loop Runner)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 5. Run it!
print("--- Question 1 ---")
agent_executor.invoke({"input": "What is 5 plus 3?"})

print("\n--- Question 2 (Multi-step) ---")
agent_executor.invoke({"input": "What is (10 plus 2) multiplied by 3?"})
```

**Run it**.
Watch the console output. You'll see it:
1. Call `add(10, 2)` -> Get 12.
2. Call `multiply(12, 3)` -> Get 36.
3. Final Answer: 36.

It figured out the order of operations by itself! 🤯

---

## Common Mistakes

### Mistake #1: Bad Docstrings
If you write `@tool def func(x): pass`, the LLM has no idea what `x` is or what the function does.
**Fix**: Always write descriptive docstrings: `"""Calculates the square root of x."""`

### Mistake #2: Forgetting `agent_scratchpad`
The prompt MUST include `{agent_scratchpad}`. This is where LangChain writes the history of "Thought -> Action -> Observation". Without it, the agent has no memory of what it just did.

### Mistake #3: Infinite Loops
Sometimes an agent gets stuck. "I need to check the weather." -> Error. -> "I need to check the weather." -> Error.
**Fix**: `AgentExecutor` has `max_iterations=10` by default. You can lower this to prevent runaway costs.

---

## Quick Reference Card

### Defining Tools

```python
@tool
def my_tool(arg1: str) -> str:
    """Description for the LLM."""
    return "Result"
```

### Creating Agent

```python
agent = create_tool_calling_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
executor.invoke({"input": "..."})
```

---

## Verification (REQUIRED SECTION)

We need to verify **P34 (Tool Validity)** and **P35 (Termination)**.

**Create `verify_agent.py`**:

```python
"""
Verification script for Chapter 26.
Properties: P34 (Tool Call), P35 (Termination).
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
import sys

print("🧪 Running Agent Verification...\n")

# P34: Tool Call Validity
# We define a "Secret Tool" and verify the agent calls it correctly.
called_secret = False

@tool
def secret_tool(code: str) -> str:
    """Unlocks the safe given a code."""
    global called_secret
    if code == "1234":
        called_secret = True
        return "Unlocked!"
    return "Locked."

tools = [secret_tool]
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a security bot."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

print("Test 1: Tool Usage...")
res = executor.invoke({"input": "Use the code 1234 to unlock the safe."})

if called_secret:
    print("✅ P34 Passed: Agent correctly called the tool with arguments.")
else:
    print("❌ Failed: Agent did not call the tool.")
    sys.exit(1)

# P35: Loop Termination
# The agent should finish and return a string
if isinstance(res['output'], str) and len(res['output']) > 0:
    print("✅ P35 Passed: Agent loop terminated with an answer.")
else:
    print("❌ Failed: No final output.")
    sys.exit(1)

print("\n🎉 Chapter 26 Complete! You have birthed an autonomous agent.")
```

**Run it:** `python verify_agent.py`

---

## Summary

**What you learned:**

1. ✅ **Chains vs Agents**: Chains are hardcoded; Agents are dynamic.
2. ✅ **Tool Definition**: Using `@tool` to expose Python functions to AI.
3. ✅ **The Loop**: Reason -> Act -> Observe.
4. ✅ **AgentExecutor**: The runtime that manages the loop.
5. ✅ **Scratchpad**: The "memory" of the agent's current thought process.

**Key Takeaway**: Agents allow you to connect LLMs to *actions* (APIs, Databases, Calculators). This moves AI from "Chatbot" to "Assistant".

**Skills unlocked**: 🎯
- Agent Architecture
- Tool Engineering
- Dynamic Logic

**Looking ahead**: Our agent uses tools, but it's a bit opaque. We want to see *how* it thinks. We want to explicitly structure its reasoning. In **Chapter 27**, we will dive into the **ReAct Pattern** specifically to understand the internal monologue!

---

**Next**: [Chapter 27: ReAct Pattern →](chapter-27-react-pattern.md)
