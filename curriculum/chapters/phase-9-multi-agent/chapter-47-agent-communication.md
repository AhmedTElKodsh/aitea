# Chapter 47: Agent Communication Protocols — The Language of Teams

<!--
METADATA
Phase: 9 - Multi-Agent Systems
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 46 (Supervisor)
Builds Toward: Debugging (Ch 48)
Correctness Properties: P59 (Structured Messaging), P67 (Shared State Consistency)
Project Thread: Inter-Agent Protocol

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You are in a loud kitchen.
Chef A shouts: "Burger!"
Chef B shouts: "Done!"
Chef C shouts: "What is done? The burger or the fries?" 🤯

Effective teams don't just "talk". They have **Protocols**.
"Order 45: Burger Ready." "Service: Picking up Order 45."

In Multi-Agent systems, if Agent A dumps a 50-page PDF into the chat log for Agent B, your token budget explodes.
We need a **Blackboard**. Agent A pins the PDF to the board. Agent B walks over and reads it. The chat log stays clean: "I posted the PDF on the board."

**By the end of this chapter**, you will build a high-efficiency communication system where agents share massive data without crashing the chat. 📡

---

## Prerequisites Check

```bash
# Verify LangGraph
pip show langgraph
```

---

## The Story: The "Context Explosion"

### The Problem (Passing Data by Value)

**Agent A**: "I researched the topic. Here is the 10,000-word report: [Insert 10k words...]"
**Agent B**: "Thanks. I will summarize it. [Insert Summary...]"
**Supervisor**: "Great."

Total Tokens: 20,000+.
Cost: $0.60.
Latency: 1 minute.
And if you loop? Bankruptcy.

### The Solution (Passing Data by Reference)

**Agent A**: "I researched the topic. Saved to `report.md`."
**Agent B**: "Thanks. I read `report.md`. Summarizing..."

Total Tokens: 50.
Cost: $0.001.
We use the **State** as a Blackboard to store *pointers*, not data.

---

## Part 1: The Blackboard Pattern

Let's define a state that holds artifacts separately from the conversation.

### 🔬 Try This! (Hands-On Practice #1)

**Create `blackboard_state.py`**:

```python
from typing import TypedDict, Annotated, Dict, Any
import operator

class Artifact(TypedDict):
    content: str
    source: str

class BlackboardState(TypedDict):
    # The Conversation (Small, chatty)
    messages: Annotated[list[str], operator.add]
    
    # The Data (Big, structured)
    # Mapping: filename -> content
    artifacts: Dict[str, Artifact]

# Test it
state = {
    "messages": [],
    "artifacts": {}
}

# Agent A writes to blackboard
state["artifacts"]["report.txt"] = {"content": "Huge content...", "source": "Agent A"}
state["messages"].append("Agent A: Added report.txt")

# Agent B reads
print(f"Chat: {state['messages']}")
print(f"Data: {state['artifacts'].keys()}")
```

**Run it**.
The chat remains clean. The data is accessible.

---

## Part 2: Implementing the Blackboard in LangGraph

Let's build a Researcher that "saves" files and an Analyst that "reads" them.

### 🔬 Try This! (Hands-On Practice #2)

**Create `blackboard_agents.py`**:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Dict, Any
import operator

# 1. State Definition
class State(TypedDict):
    messages: Annotated[list[str], operator.add]
    artifacts: Dict[str, Any] # The Blackboard

# 2. Researcher Node
def researcher(state):
    print("🔎 Researcher: Analyzing data...")
    # Simulate generating big data
    big_data = "Row 1: 100\nRow 2: 200\n... (Imagine 1000 rows)"
    
    # Save to Blackboard (preserving existing artifacts)
    new_artifacts = state.get("artifacts", {}).copy()
    new_artifacts["data.csv"] = big_data
    
    return {
        "messages": ["Researcher: Data saved to data.csv"],
        "artifacts": new_artifacts
    }

# 3. Analyst Node
def analyst(state):
    print("📊 Analyst: Checking blackboard...")
    # Read from Blackboard
    data = state["artifacts"].get("data.csv", "")
    
    # Process
    summary = f"Summary of {len(data)} chars"
    
    return {
        "messages": [f"Analyst: Processed data. {summary}"]
    }

# 4. Graph
workflow = StateGraph(State)
workflow.add_node("researcher", researcher)
workflow.add_node("analyst", analyst)

workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "analyst")
workflow.add_edge("analyst", END)

app = workflow.compile()

# 5. Run
print("---" Running Blackboard Flow ---")
final = app.invoke({"messages": [], "artifacts": {}})

print("\n---" Final Chat History ---")
for m in final["messages"]:
    print(m)

print("\n---" Final Artifacts ---")
print(final["artifacts"].keys())
```

**Run it**.
Notice how the "1000 rows" never entered the `messages` list? Efficiency achieved.

---

## Part 3: Structured Messages (The Protocol)

Sometimes you *do* need to pass data in the chat, but it must be structured.
Instead of plain text, agents should speak **JSON**.

### 🔬 Try This! (Hands-On Practice #3)

**Create `protocol_test.py`**:

```python
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

# 1. Define the Protocol
class HandoffMessage(BaseModel):
    """Standard message format between agents."""
    sender: str
    receiver: str
    task_id: str
    status: str = Field(description="success, failure, or in_progress")
    summary: str

# 2. Agent Generator
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm = model.with_structured_output(HandoffMessage)

# 3. Simulate Agent
print("---" Generating Structured Message ---")
msg = structured_llm.invoke(
    "Tell the Analyst that task #101 is done successfully. It was about sales data."
)

print(f"Type: {type(msg)}")
print(f"JSON: {msg.json()}")

# 4. Routing Logic (Hypothetical)
if msg.receiver == "Analyst" and msg.status == "success":
    print("✅ Routing to Analyst Node...")
```

**Run it**.
Using Pydantic models as the "Language" ensures Agent B never has to guess what Agent A meant.

---

## Common Mistakes

### Mistake #1: Modifying State incorrectly
In LangGraph, if you return `{"artifacts": {"new": 1}}`, it might *overwrite* the old artifacts if you don't define a reducer or copy the dict.
**Fix**: `new = state['artifacts'].copy(); new['x'] = 1; return {'artifacts': new}`. (Or use a custom reducer).

### Mistake #2: Hallucinating Files
The Agent thinks it saved a file, but code execution failed. Agent B tries to read it and crashes.
**Fix**: Using **Tool Output** (Ch 29) to confirm "File Saved" before the Agent claims it.

### Mistake #3: Dirty Blackboard
Old artifacts pile up.
**Fix**: Implement a `cleanup` node or TTL (Time To Live) for data.

---

## Quick Reference Card

### Blackboard Pattern

```python
class State(TypedDict):
    # Chat logic
    messages: list[str]
    # Data logic (passed by reference)
    blackboard: dict[str, Any]
```

---

## Verification (REQUIRED SECTION)

We need to verify **P67 (Shared State Consistency)** and **P59 (Structured Messaging)**.

**Create `verify_protocol.py`**:

```python
"""
Verification script for Chapter 47.
Properties: P67 (State Consistency), P59 (Protocol).
"""
import sys

print("🧪 Running Protocol Verification...\n")

# P67: Blackboard Consistency
# Verify that data written by A is readable by B
shared_state = {"data": {}}

def write(key, val):
    shared_state["data"][key] = val

def read(key):
    return shared_state["data"].get(key)

print("Test 1: Blackboard Read/Write...")
write("report", "123")
val = read("report")

if val == "123":
    print("✅ P67 Passed: Shared state is consistent.")
else:
    print(f"❌ Failed: Read {val}")
    sys.exit(1)

# P59: Structured Messaging
# Verify strict schema compliance
from pydantic import BaseModel, ValidationError

class Protocol(BaseModel):
    status: str

print("Test 2: Schema Enforcement...")
try:
    # Invalid message
    Protocol(status=123) # Should be string, but pydantic coerces. 
    # Let's try missing field
    Protocol() 
    print("❌ Failed: Schema accepted invalid data.")
    sys.exit(1)
except ValidationError:
    print("✅ P59 Passed: Schema caught invalid message.")

print("\n🎉 Chapter 47 Complete! Your agents speak fluent Protocol.")
```

**Run it:** `python verify_protocol.py`

---

## Summary

**What you learned:**

1. ✅ **Pass by Reference**: Moving pointers, not payloads.
2. ✅ **The Blackboard**: A shared data repository for the team.
3. ✅ **Structured Handoffs**: Using Pydantic to standardize communication.
4. ✅ **State Management**: Handling dictionary updates safely.
5. ✅ **Efficiency**: Saving tokens by keeping the chat context clean.

**Key Takeaway**: A chat log is for *conversation*. A database is for *data*. Don't mix them.

**Skills unlocked**: 🎯
- Protocol Design
- State Optimization
- Data Engineering

**Looking ahead**: We have built complex systems. But debugging them is getting hard. Traces help, but we need tools specifically for **Multi-Agent Debugging**.
In **Chapter 48**, we will build a **Debugger Dashboard** for our agents!

---

**Next**: [Chapter 48: Debugging Multi-Agent Systems →](chapter-48-debugging-agents.md)
