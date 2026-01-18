# Chapter 48: Debugging Multi-Agent Systems — The Detective

<!--
METADATA
Phase: 9 - Multi-Agent Systems
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 43 (Multi-Agent)
Builds Toward: Civil Engineering App (Ch 49)
Correctness Properties: P68 (Trace Completeness), P69 (State Inspection)
Project Thread: Quality Assurance

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You walk into a room. Two people are arguing.
"He said X!" "No, she said Y!"
To find the truth, you need a **Recording**. Or better, a **Transcript**.

Debugging one Agent is like debugging a single function. You check the input and output.
Debugging a **Team** of Agents is like debugging a distributed system.
- Did Agent A send the wrong message?
- Did Agent B misunderstand it?
- Did the Supervisor route it to the wrong person?
- Are they stuck in an infinite loop of politeness? ("After you." "No, after you.")

**By the end of this chapter**, you will learn how to freeze time, inspect the brains of your agents, and visualize the invisible connections between them. 🕵️‍♂️

---

## Prerequisites Check

```bash
# Verify LangGraph
pip show langgraph
```

---

## The Story: The "Silent" Failure

### The Problem (Deadlocks)

You built a team: `Researcher <-> Writer`.
Researcher: "I need a topic."
Writer: "I need research."
Researcher: "I need a topic."
Writer: "I need research."
... forever.
The system is spinning, costing money, but producing nothing.

### The Solution (Visualization & Inspection)

1.  **Visualize**: Draw the graph. See the cycle.
2.  **Inspect**: Pause the graph. Look at the `State`. Realize `topic` is empty.
3.  **Fix**: Inject a `topic` into the state manually.

---

## Part 1: Visualizing the Graph

LangGraph can draw itself. This is the first step in debugging: "Does the code look like the diagram in my head?"

### 🔬 Try This! (Hands-On Practice #1)

**Create `visualize_graph.py`**:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    status: str

def node_a(state):
    return {"status": "A"}
def node_b(state):
    return {"status": "B"}

workflow = StateGraph(State)
workflow.add_node("A", node_a)
workflow.add_node("B", node_b)

workflow.set_entry_point("A")
workflow.add_edge("A", "B")
workflow.add_edge("B", END)

app = workflow.compile()

# 1. Print ASCII Art
print("--- ASCII Graph ---")
app.get_graph().print_ascii()

# 2. Get Mermaid (for Markdown/Diagrams)
print("\n--- Mermaid Diagram ---")
print(app.get_graph().draw_mermaid())
```

**Run it**.
You should see a clear arrow `[Start] -> A -> B -> [End]`.
If you see `A -> A`, you found a bug in your wiring!

---

## Part 2: Inspecting State History

When a crash happens, you need to know *what* the state was at that moment.

### 🔬 Try This! (Hands-On Practice #2)

**Create `inspect_state.py`**:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

class State(TypedDict):
    # We track the history of operations
    steps: Annotated[List[str], operator.add]

def step_1(state):
    return {"steps": ["Step 1 Done"]}
def step_2(state):
    return {"steps": ["Step 2 Done"]}

workflow = StateGraph(State)
workflow.add_node("1", step_1)
workflow.add_node("2", step_2)
workflow.set_entry_point("1")
workflow.add_edge("1", "2")
workflow.add_edge("2", END)

# Use Memory to enable inspection
from langgraph.checkpoint.memory import MemorySaver
mem = MemorySaver()
app = workflow.compile(checkpointer=mem)

config = {"configurable": {"thread_id": "debug_session"}}

# Run
app.invoke({"steps": []}, config=config)

# Inspect History
print("--- State History ---")
# get_state_history returns a generator of snapshots
history = list(app.get_state_history(config))

for i, snapshot in enumerate(history):
    print(f"Snapshot {i}: {snapshot.values['steps']}")
```

**Run it**.
You can see the state evolving:
`[]` -> `['Step 1 Done']` -> `['Step 1 Done', 'Step 2 Done']`.
If Step 2 produced garbage, you'd see it here.

---

## Part 3: Debugging Deadlocks (Loops)

Let's intentionally create an infinite loop and catch it.

### 🔬 Try This! (Hands-On Practice #3)

**Create `catch_loop.py`**:

```python
from langgraph.graph import StateGraph
from typing import TypedDict
from langgraph.errors import GraphRecursionError

class State(TypedDict):
    count: int

def loop_node(state):
    print(f"Looping... {state['count']}")
    return {"count": state["count"] + 1}

workflow = StateGraph(State)
workflow.add_node("loop", loop_node)
workflow.set_entry_point("loop")
workflow.add_edge("loop", "loop") # Infinite Edge!

app = workflow.compile()

print("--- Starting Infinite Loop ---")
try:
    # Set a strict limit (e.g., 5 steps)
    app.invoke({"count": 0}, config={"recursion_limit": 5})
except GraphRecursionError:
    print("🛑 Caught Infinite Loop! System stopped safely.")
```

**Run it**.
It counts to 5 and stops.
**Lesson**: Always set `recursion_limit` in production.

---

## Common Mistakes

### Mistake #1: Logging inside Nodes
`print()` is okay for dev, but in production, logs get mixed up.
**Fix**: Use a `TraceCallback` or LangSmith to capture logs structured by *Run ID*.

### Mistake #2: Changing State Schema
If you change `TypedDict` definition but try to load an old Checkpoint, it crashes.
**Fix**: Version your state or clear the database when deploying breaking changes.

### Mistake #3: Ignoring "Wait" States
If you use Human-in-the-Loop, the state might be "Waiting". If you try to debug it assuming it's "Done", you'll be confused.
**Fix**: Check `snapshot.next` to see if it's waiting for input.

---

## Quick Reference Card

### Debugging Tools

| Tool | Usage |
|------|------|
| `print_ascii()` | Visualize structure |
| `get_state(config)` | See current memory |
| `get_state_history()` | Time travel |
| `recursion_limit` | Prevent infinite loops |

---

## Verification (REQUIRED SECTION)

We need to verify **P68 (Trace Completeness)** and **P69 (State Inspection)**.

**Create `verify_debug.py`**:

```python
"""
Verification script for Chapter 48.
Properties: P68 (Trace), P69 (Inspection).
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict
import sys

print("🧪 Running Debugger Verification...\n")

class State(TypedDict):
    log: str

def node(state):
    return {"log": state["log"] + "->Node"}

# Setup
workflow = StateGraph(State)
workflow.add_node("A", node)
workflow.set_entry_point("A")
workflow.add_edge("A", END)
mem = MemorySaver()
app = workflow.compile(checkpointer=mem)
config = {"configurable": {"thread_id": "verify"}}

# Run
app.invoke({"log": "Start"}, config=config)

# P69: Inspection Accuracy
state = app.get_state(config)
expected = "Start->Node"

if state.values["log"] == expected:
    print("✅ P69 Passed: State inspection reflects execution.")
else:
    print(f"❌ Failed: Expected '{expected}', got '{state.values['log']}'")
    sys.exit(1)

# P68: Trace Completeness (History)
history = list(app.get_state_history(config))
# We expect at least Start and End states
if len(history) >= 2:
    print("✅ P68 Passed: History contains multiple snapshots.")
else:
    print("❌ Failed: History is empty or incomplete.")
    sys.exit(1)

print("\n🎉 Chapter 48 Complete! You see all.")
```

**Run it:** `python verify_debug.py`

---

## Summary

**What you learned:**

1. ✅ **Visualization**: Using ASCII/Mermaid to verify graph topology.
2. ✅ **Snapshots**: Accessing the state at any point in time.
3. ✅ **History**: Replaying the sequence of events.
4. ✅ **Safety Limits**: Using recursion limits to stop runaway bots.
5. ✅ **Checkpointing**: How it enables debugging live systems.

**Key Takeaway**: A bug in a single-agent system is a typo. A bug in a multi-agent system is a communication breakdown. You need tools to see the conversation.

**Skills unlocked**: 🎯
- Advanced Debugging
- Graph Visualization
- State Forensics

**Looking ahead**: You have completed **Phase 9: Multi-Agent Systems**. You are now an expert in orchestrating AI teams.
Now, for the Grand Finale. **Phase 10: Civil Engineering Application**.
We will take *everything* we have learned (Pydantic, RAG, Agents, LangGraph) and build a massive, real-world system to generate Contracts, Proposals, and Reports.

---

**Next**: [Phase 10: Civil Engineering Application (Chapter 49) →](../phase-10-civil-engineering/chapter-49-civil-eng-models.md)

