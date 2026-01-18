# Chapter 34: Persistent State with Checkpoints — Time Travel

<!--
METADATA
Phase: 6 - LangGraph
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 33 (HITL)
Builds Toward: Production Deployment (Ch 41) 
Correctness Properties: P45 (State Persistence), P47 (Recovery Completeness)
Project Thread: Reliability

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're playing a video game. You beat the boss. The power goes out. 🌩️
You restart the game. "Level 1".
You scream. 😱

This is `MemorySaver` (from Chapter 33). It lives in RAM. If the Python script stops, the memory is gone.
In production, servers restart all the time. You need **Save Files** (Disk Persistence).

**Persistent Checkpoints** allow you to:
1.  **Recover**: Pick up exactly where you left off after a crash.
2.  **Time Travel**: "Undo" the last 3 turns and try a different path.
3.  **Fork**: Create alternate timelines from a specific point in history.

**By the end of this chapter**, you'll build an unbreakable workflow that survives reboots and lets you rewind time. ⏳

---

## Prerequisites Check

We need the SQLite adapter for LangGraph.

```bash
pip install langgraph-checkpoint-sqlite
```

---

## The Story: The "Long-Running" Job

### The Problem (Server Restarts)

You have an agent researching a topic. It takes 20 minutes.
At minute 19, you deploy a code update. The server restarts.
The agent dies. The research is lost. The user is angry.

### The Solution (SQLite Persistence)

We swap `MemorySaver` for `SqliteSaver`.
Every step the agent takes is written to a file (`checkpoints.sqlite`).
When the server comes back up, it looks at the `thread_id`, loads the state from the file, and continues.

---

## Part 1: The Database Saver

Setting up SQLite is easy (it's just a file).

### 🔬 Try This! (Hands-On Practice #1)

**Create `sqlite_setup.py`**:

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

# 1. Create connection
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)

# 2. Create Saver
checkpointer = SqliteSaver(conn)

print("✅ Database connected. Checkpoints will be saved to 'checkpoints.sqlite'")
```

---

## Part 2: Crash and Recover

Let's simulate a crash. We will run a graph halfway, stop the script, and then run a *new* script to resume.

### 🔬 Try This! (Hands-On Practice #2)

**Step A: The "Crash" Script (`run_part1.py`)**:

```python
import sqlite3
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

# Setup Graph
class State(TypedDict):
    count: int

def step_1(state):
    print("-- Step 1 Finished --")
    return {"count": state["count"] + 1}

def step_2(state):
    print("-- Step 2 Finished --")
    return {"count": state["count"] + 1}

builder = StateGraph(State)
builder.add_node("1", step_1)
builder.add_node("2", step_2)
builder.set_entry_point("1")
builder.add_edge("1", "2")
builder.add_edge("2", END)

# Setup Persistence
conn = sqlite3.connect("my_db.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

# Interrupt before Step 2 (Simulating a crash/pause)
app = builder.compile(checkpointer=memory, interrupt_before=["2"])

# Run
config = {"configurable": {"thread_id": "session_1"}}
app.invoke({"count": 0}, config=config)
print("🛑 System stopping (simulated crash).")
```

**Run it**. It does Step 1 and stops.

**Step B: The "Recovery" Script (`run_part2.py`)**:

```python
# Copy the EXACT same graph setup code from above...
# (In a real app, this would be in a shared module)
import sqlite3
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

class State(TypedDict):
    count: int

def step_1(state): return {"count": state["count"] + 1}
def step_2(state):
    print("-- Step 2 Resumed! --")
    return {"count": state["count"] + 1}

builder = StateGraph(State)
builder.add_node("1", step_1)
builder.add_node("2", step_2)
builder.set_entry_point("1")
builder.add_edge("1", "2")
builder.add_edge("2", END)

# CONNECT TO SAME DB
conn = sqlite3.connect("my_db.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

# Compile
app = builder.compile(checkpointer=memory, interrupt_before=[]) # Remove interrupt!

# Resume
config = {"configurable": {"thread_id": "session_1"}}
print("🔄 Recovering session...")
final = app.invoke(None, config=config)
print(f"Final Count: {final['count']}") # Should be 2
```

**Run Part 2**.
It should magically skip Step 1 (already done) and execute Step 2.
**You just survived a reboot.**

---

## Part 3: Time Travel (History)

What if Step 2 was a mistake?
The DB stores *every* step. We can look back.

### 🔬 Try This! (Hands-On Practice #3)

**Create `time_travel.py`**:

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect("my_db.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)
config = {"configurable": {"thread_id": "session_1"}}

# Get History
history = list(memory.list(config))

print(f"Found {len(history)} checkpoints.")
for i, checkpoint in enumerate(history):
    print(f"[{i}] State: {checkpoint.checkpoint['channel_values']}")
```

**Run it**.
You will see the state at Step 2 (`count: 2`) and at Step 1 (`count: 1`) and Start (`count: 0`).
To "rewind", you just pick an old config and `invoke` from there!

---

## Common Mistakes

### Mistake #1: Changing Graph Topology
If you change the graph structure (e.g., rename nodes) and try to load an old checkpoint, it might crash. Checkpoints are tied to the graph definition.

### Mistake #2: Not Committing SQLite
`SqliteSaver` usually handles auto-commit, but if you share the connection, ensure it's not closed prematurely.

### Mistake #3: Thread ID Collision
If two users use `thread_id="1"`, they will overwrite each other's save files. Always use unique IDs (UUIDs).

---

## Quick Reference Card

### SqliteSaver

```python
conn = sqlite3.connect("db.sqlite", check_same_thread=False)
checkpointer = SqliteSaver(conn)
app = graph.compile(checkpointer=checkpointer)
```

---

## Verification (REQUIRED SECTION)

We need to verify **P47 (Recovery Completeness)**.

**Create `verify_persistence.py`**:

```python
"""
Verification script for Chapter 34.
Property P47: Recovery Completeness.
"""
import sqlite3
import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict
import sys

print("🧪 Running Persistence Verification...\n")

DB_FILE = "verify.sqlite"
if os.path.exists(DB_FILE): os.remove(DB_FILE)

class State(TypedDict):
    val: str

def node_a(state): return {"val": "A"}
def node_b(state): return {"val": state["val"] + "B"}

# Graph Def
def build_app(mem):
    workflow = StateGraph(State)
    workflow.add_node("a", node_a)
    workflow.add_node("b", node_b)
    workflow.set_entry_point("a")
    workflow.add_edge("a", "b")
    workflow.add_edge("b", END)
    return workflow.compile(checkpointer=mem, interrupt_before=["b"])

# 1. Run Halfway
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
mem = SqliteSaver(conn)
app = build_app(mem)
config = {"configurable": {"thread_id": "test_thread"}}

app.invoke({"val": ""}, config=config)
# Should stop before B. State should be "A".

# 2. Close and Reopen (Simulate Restart)
conn.close()
conn2 = sqlite3.connect(DB_FILE, check_same_thread=False)
mem2 = SqliteSaver(conn2)
app2 = build_app(mem2) # Rebuild app with new connection

# 3. Verify State
state = app2.get_state(config)
if state.values["val"] == "A":
    print("✅ P47 Passed: State 'A' recovered from disk.")
else:
    print(f"❌ Failed: State lost or wrong. Got {state.values}")
    sys.exit(1)

# Cleanup
conn2.close()
os.remove(DB_FILE)

print("\n🎉 Chapter 34 Complete! You are a Time Lord.")
```

**Run it:** `python verify_persistence.py`

---

## Summary

**What you learned:**

1. ✅ **Transient vs Persistent**: Why RAM isn't enough.
2. ✅ **SqliteSaver**: The simplest database backend for LangGraph.
3. ✅ **Thread IDs**: The key to finding your save file.
4. ✅ **Recovery**: Resuming execution after a shutdown.
5. ✅ **History**: Inspecting past states.

**Key Takeaway**: Persistence makes your AI robust. It turns a "script" into a "service".

**Skills unlocked**: 🎯
- Database Integration
- State Serialization
- Crash Recovery

**Looking ahead**: We have finished **Phase 6: LangGraph**. We have sophisticated, reliable, persistent agents.
In **Phase 7: LlamaIndex**, we will switch gears. We will focus deeply on **Data Indexing**. LangChain is great for *flow*; LlamaIndex is great for *data*. We will learn how to organize massive knowledge bases efficiently.

---

**Next**: [Phase 7: LlamaIndex (Chapter 35) →](../phase-7-llamaindex/chapter-35-llamaindex-fundamentals.md)
