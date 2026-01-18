# Chapter 33: Human-in-the-Loop Workflows — The Supervisor

<!--
METADATA
Phase: 6 - LangGraph
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 31 (LangGraph)
Builds Toward: Production Deployment (Ch 41)
Correctness Properties: P45 (State Persistence), P46 (Resume Correctness)
Project Thread: Safety & Control

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're teaching a teenager to drive. 🚗
Do you hand them the keys and say "See you in 5 hours"?
No. You sit in the passenger seat. If they try to merge into a truck, you **Intervene**. You grab the wheel. You hit the brake.

AI is a teenager. It's smart, but sometimes it hallucinates or tries to delete your database.
**Human-in-the-Loop (HITL)** puts you in the passenger seat.
You can tell the AI: "Pause here. Let me check your work. Okay, proceed." Or "No, that's wrong, change it to X, *then* proceed."

**By the end of this chapter**, you will build a safety system that pauses right before "pushing the big red button," waits for your approval, and even lets you rewrite the AI's homework. 🛑

---

## Prerequisites Check

```bash
# Verify LangGraph
pip show langgraph
```

---

## The Story: The "Viral" Tweet

### The Problem (No Filter)

You built a "Twitter Bot".
Prompt: "Write a funny tweet about startups."
AI: "Startups are like Ponzi schemes!" 😱
*Bot auto-posts it.*
*You get cancelled.*

### The Solution (The Approval Step)

We need a workflow:
1.  **Generate**: AI writes tweet.
2.  **Pause**: Wait for Human.
3.  **Review**: Human says "Approve" or "Edit".
4.  **Post**: API call happens only *after* approval.

---

## Part 1: Checkpoints (Saving the Game)

To pause a program and resume it later (maybe hours later), we need to save its state. In LangGraph, we use a **Checkpointer**.

### 🔬 Try This! (Hands-On Practice #1)

Let's setup memory.

**Create `checkpoint_setup.py`**:

```python
from langgraph.checkpoint.memory import MemorySaver

# 1. Initialize Checkpointer
# In production, use Postgres/Sqlite. For learning, Memory is fine.
memory = MemorySaver()

# 2. Config object
# This acts like a "Session ID" to find your saved game.
config = {"configurable": {"thread_id": "1"}}

print("Checkpointer ready!")
```

---

## Part 2: The Interrupt

We tell LangGraph: "Stop *before* you enter the 'publish' node."

### 🔬 Try This! (Hands-On Practice #2)

**Create `hitl_graph.py`**:

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# 1. State
class State(TypedDict):
    content: str

# 2. Nodes
def write_node(state: State):
    print("✍️  AI is writing...")
    return {"content": "AI says: Python is actually a snake."}

def publish_node(state: State):
    print(f"🚀 PUBLISHING: '{state['content']}'")
    return {} # Done

# 3. Build Graph
builder = StateGraph(State)
builder.add_node("write", write_node)
builder.add_node("publish", publish_node)

builder.set_entry_point("write")
builder.add_edge("write", "publish")
builder.add_edge("publish", END)

# 4. Compile with Interrupts & Memory
checkpointer = MemorySaver()
app = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["publish"] # <--- THE BRAKE PEDAL
)

# 5. Run Part 1
thread_config = {"configurable": {"thread_id": "1"}}

print("---"" Start ---")
app.invoke({"content": ""}, config=thread_config)
print("---"" Paused ---")
```

**Run it**.
It should print "AI is writing..." and then **STOP**. It will NOT print "PUBLISHING".
The program has exited. But the state is saved in `checkpointer`.

---

## Part 3: Resuming and Editing

Now, we act as the human. We look at the state, maybe change it, and hit play.

### 🔬 Try This! (Hands-On Practice #3)

**Append to `hitl_graph.py`** (or create a new file loading the same setup):

```python
# ... previous code ...

# 6. Check the State
current_state = app.get_state(thread_config)
print(f"Current Draft: {current_state.values['content']}")
print(f"Next Step: {current_state.next}")

# 7. Edit the State (Human Intervention)
print("👨‍💼 Human: That's wrong. I'm changing it.")
app.update_state(
    thread_config,
    {"content": "Human says: Python is a language."}
)

# 8. Resume
print("---"" Resuming ---")
# Passing None means "Continue from where you left off"
app.invoke(None, config=thread_config)
```

**Run it**.
You should see:
1. AI writes "Snake".
2. Pause.
3. Human changes to "Language".
4. PUBLISHING: "Language".

You effectively "reached into the brain" of the AI and fixed a thought before it acted. 🧠🖐️

---

## Common Mistakes

### Mistake #1: Forgetting `thread_id`
If you change the `thread_id`, the graph starts from scratch (empty memory). You must use the same ID to resume.

### Mistake #2: `interrupt_after` vs `interrupt_before`
*   `before`: Stops *before* the node runs. Good for approval (don't run this action yet).
*   `after`: Stops *after* the node runs. Good for review (look at what it did).

### Mistake #3: State Schema Mismatch
When using `update_state`, you must match the schema of your `State` object. If you add a random key not in `TypedDict`, it might be ignored or cause errors.

---

## Quick Reference Card

### Checkpoint Syntax

```python
# Pause before node 'b'
app = graph.compile(
    checkpointer=mem, 
    interrupt_before=["b"]
)

# Resume
app.invoke(None, config=thread_config)

# Update State
app.update_state(thread_config, {"key": "new_value"})
```

---

## Verification (REQUIRED SECTION)

We need to verify **P45 (Persistence)** and **P46 (Resume/Edit)**.

**Create `verify_hitl.py`**:

```python
"""
Verification script for Chapter 33.
Properties: P45 (Persistence), P46 (Resume/Edit).
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict
import sys

print("🧪 Running HITL Verification...\n")

class State(TypedDict):
    value: str

def step_1(state):
    return {"value": "Original"}
def step_2(state):
    return {"value": state["value"] + " -> Final"}

# Setup Graph
workflow = StateGraph(State)
workflow.add_node("1", step_1)
workflow.add_node("2", step_2)
workflow.set_entry_point("1")
workflow.add_edge("1", "2")
workflow.add_edge("2", END)

mem = MemorySaver()
app = workflow.compile(checkpointer=mem, interrupt_before=["2"])
config = {"configurable": {"thread_id": "test"}}

# 1. Run until Interrupt
print("Test 1: Interrupt...")
app.invoke({"value": "Init"}, config=config)
state = app.get_state(config)

if state.values["value"] == "Original" and state.next == ("2",):
    print("✅ P45 Passed: State persisted and paused correctly.")
else:
    print(f"❌ Failed: State={state.values}")
    sys.exit(1)

# 2. Modify and Resume
print("Test 2: Human Edit...")
app.update_state(config, {"value": "Edited"})
final_res = app.invoke(None, config=config)

if final_res["value"] == "Edited -> Final":
    print("✅ P46 Passed: Resumed with edited state.")
else:
    print(f"❌ Failed: Result={final_res}")
    sys.exit(1)

print("\n🎉 Chapter 33 Complete! You are the Supervisor.")
```

**Run it:** `python verify_hitl.py`

---

## Summary

**What you learned:**

1. ✅ **Checkpoints**: Saving the graph's brain to disk/memory.
2. ✅ **Interrupts**: Pausing the assembly line.
3. ✅ **Human-in-the-Loop**: The pattern of Review -> Approve -> Execute.
4. ✅ **State Injection**: Modifying the graph's memory manually.
5. ✅ **Time Travel**: You can technically use `get_state_history` to go back in time! (Advanced).

**Key Takeaway**: Autonomous agents are scary. HITL agents are safe. Use interrupts for any "high-stakes" action (email, purchase, delete).

**Skills unlocked**: 🎯
- Workflow Control
- Safety Engineering
- State Management

**Looking ahead**: We can pause and resume. But what if the computer crashes? Or we want to roll back to a previous version? In **Chapter 34**, we will deep dive into **Persistent State & Checkpoints** using a real database!

---

**Next**: [Chapter 34: Persistent State with Checkpoints →](chapter-34-persistent-state.md)
