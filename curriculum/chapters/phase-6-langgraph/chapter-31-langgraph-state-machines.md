# Chapter 31: LangGraph State Machines — Beyond the Loop

<!--
METADATA
Phase: 6 - LangGraph
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 28 (OTAR)
Builds Toward: Multi-Agent Teams (Ch 43)
Correctness Properties: P38 (State Transition), P42 (Graph Execution)
Project Thread: Workflows

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You run a newspaper.
You have a process: **Writer** -> **Editor** -> **Publisher**.
If the Editor hates the draft, they send it *back* to the Writer.
If they like it, they send it *forward* to the Publisher.

Standard Agents (Chapter 26) are like "Solo Freelancers". They figure it out themselves.
**LangGraph** allows you to build the **Newsroom**. You define the roles (Nodes) and the rules (Edges). You control the flow.

**By the end of this chapter**, you will build a deterministic, reliable workflow engine that ensures steps happen in the exact order you designed. 🗞️

---

## Prerequisites Check

We need the LangGraph library.

```bash
pip install langgraph
```

---

## The Story: The "Chaotic" Agent

### The Problem (Unpredictability)

You asked your Agent to "Write and Review a blog post."
Agent: "Here is the post!" (It forgot to review).
Or: "I reviewed it." (It forgot to write it first).
Agents are probabilistic. Processes need to be deterministic.

### The Solution (State Machines)

A **State Machine** is a graph where:
1.  **Nodes** are workers (Writer, Editor).
2.  **Edges** are the paths between them.
3.  **State** is the document being passed around.

---

## Part 1: The State (The Clipboard)

The **State** is a dictionary (or Pydantic model) that holds the data. Everyone reads from it and writes to it.

### 🔬 Try This! (Hands-On Practice #1)

**Create `state_def.py`**:

```python
from typing import TypedDict, Annotated
import operator

# 1. Define the State
class AgentState(TypedDict):
    # The topic we are writing about
    topic: str 
    # The drafted content
    draft: str
    # The review feedback
    feedback: str
    # How many revisions we've done
    revision_count: int

print("State defined!")
```

**Run it**. Nothing happens yet, but we have our schema.

---

## Part 2: The Nodes (The Workers)

Nodes are just Python functions. They take the current `State` and return an **update** (a partial dictionary).

### 🔬 Try This! (Hands-On Practice #2)

**Create `graph_nodes.py`**:

```python
from state_def import AgentState

# Node 1: Writer
def writer_node(state: AgentState):
    print("✍️  Writer is working...")
    return {
        "draft": f"Draft about {state['topic']} (Revision {state.get('revision_count', 0)})",
        "revision_count": state.get("revision_count", 0) + 1
    }

# Node 2: Editor
def editor_node(state: AgentState):
    print("🧐 Editor is reviewing...")
    # Simulate feedback
    if state["revision_count"] < 2:
        return {"feedback": "Too short. Expand it."}
    return {"feedback": "Looks good!"}

print("Nodes defined!")
```

---

## Part 3: The Graph (The Assembly Line)

Now we wire them together.

### 🔬 Try This! (Hands-On Practice #3)

**Create `simple_graph.py`**:

```python
from langgraph.graph import StateGraph, END
from state_def import AgentState
from graph_nodes import writer_node, editor_node

# 1. Initialize Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("writer", writer_node)
workflow.add_node("editor", editor_node)

# 3. Add Edges (The Flow)
workflow.set_entry_point("writer") # Start here
workflow.add_edge("writer", "editor") # Writer -> Editor
workflow.add_edge("editor", END) # Editor -> Finish

# 4. Compile
app = workflow.compile()

# 5. Run
print("---" Running Graph ---")
result = app.invoke({"topic": "AI Agents", "revision_count": 0})

print("\n---" Final State ---")
print(result)
```

**Run it**.
You should see: "Writer is working..." -> "Editor is reviewing..." -> Final State.

---

## Part 4: Conditional Edges (The Logic)

We want the Editor to send it *back* to the Writer if it's bad.

### 🔬 Try This! (Hands-On Practice #4)

**Create `conditional_graph.py`**:

```python
from langgraph.graph import StateGraph, END
from state_def import AgentState
from graph_nodes import writer_node, editor_node

# Logic Function
def should_continue(state: AgentState):
    if state["feedback"] == "Looks good!":
        return "end" # Go to END
    return "revise" # Go back to Writer

# 1. Setup
workflow = StateGraph(AgentState)
workflow.add_node("writer", writer_node)
workflow.add_node("editor", editor_node)

workflow.set_entry_point("writer")
workflow.add_edge("writer", "editor")

# 2. Add Conditional Edge
# From "editor", look at "should_continue".
# If "end", go to END. If "revise", go to "writer".
workflow.add_conditional_edges(
    "editor",
    should_continue,
    {
        "end": END,
        "revise": "writer"
    }
)

# 3. Run
app = workflow.compile()
print("---" Running Loop ---")
result = app.invoke({"topic": "Loops", "revision_count": 0})

print(f"\nFinal Revision Count: {result['revision_count']}")
# Should be 2, because Editor rejects revision 1 ("Too short")
```

**Run it**.
It loops!
Writer (Rev 1) -> Editor ("Too short") -> Writer (Rev 2) -> Editor ("Looks good") -> End.

---

## Common Mistakes

### Mistake #1: Modifying State In-Place
Nodes should return a **dictionary of updates**, not modify the state object directly. LangGraph merges the updates for you.

### Mistake #2: Missing Entry Point
If you forget `workflow.set_entry_point("node")`, the graph doesn't know where to start.

### Mistake #3: Infinite Loops
If `should_continue` always returns "revise", your graph runs forever.
**Fix**: Add a `recursion_limit` when calling invoke, or logic in your node to force-stop (like checking `revision_count > 5`).

```python
app.invoke(input, config={"recursion_limit": 10})
```

---

## Quick Reference Card

### Graph Setup

```python
workflow = StateGraph(MyState)
workflow.add_node("name", func)
workflow.add_edge("start", "end")
workflow.add_conditional_edges("source", decider, path_map)
app = workflow.compile()
```

---

## Verification (REQUIRED SECTION)

We need to verify **P42 (Graph Execution)**.

**Create `verify_graph.py`**:

```python
"""
Verification script for Chapter 31.
Property P42: Execution Path Correctness.
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict
import sys

print("🧪 Running Graph Verification...\n")

class TestState(TypedDict):
    path: list[str]
    count: int

def step_1(state):
    return {"path": ["step_1"], "count": 1}

def step_2(state):
    # Appends to path due to LangGraph merge behavior if configured, 
    # but here we manually append for list types usually requires Reducer.
    # For simple Dict, it overwrites. Let's act like we overwrite for this test logic
    # or simple append if we read old state.
    current = state.get("path", [])
    return {"path": current + ["step_2"], "count": state["count"] + 1}

workflow = StateGraph(TestState)
workflow.add_node("1", step_1)
workflow.add_node("2", step_2)
workflow.set_entry_point("1")
workflow.add_edge("1", "2")
workflow.add_edge("2", END)

app = workflow.compile()

print("Test 1: Linear Execution...")
res = app.invoke({"path": [], "count": 0})

if res["path"] == ["step_1", "step_2"]:
    print("✅ P42 Passed: Nodes executed in correct order.")
else:
    print(f"❌ Failed: Path mismatch {res['path']}")
    sys.exit(1)

if res["count"] == 2:
    print("✅ State updated correctly.")
else:
    print(f"❌ Failed: Count mismatch {res['count']}")
    sys.exit(1)

print("\n🎉 Chapter 31 Complete! You are a Workflow Engineer.")
```

**Run it:** `python verify_graph.py`

---

## Summary

**What you learned**:

1. ✅ **State Graphs**: Modeling logic as nodes and edges.
2. ✅ **The State**: A shared memory board for all nodes.
3. ✅ **Conditional Edges**: How to make decisions ("If X, goto Y").
4. ✅ **Cycles**: Building reliable loops (Writer <-> Editor).
5. ✅ **Deterministic AI**: Forcing the chaos of LLMs into a strict process.

**Key Takeaway**: Don't hope the Agent figures out the process. **Design** the process.

**Skills unlocked**: 🎯
- Workflow Orchestration
- State Machine Design
- Process Control

**Looking ahead**: We have a graph. But sometimes the decision isn't simple logic (`if x > 5`). Sometimes the decision requires **AI**. In **Chapter 32**, we will build **Conditional Routing** where the LLM decides which path to take!

---

**Next**: [Chapter 32: Conditional Routing →](chapter-32-conditional-routing.md)
