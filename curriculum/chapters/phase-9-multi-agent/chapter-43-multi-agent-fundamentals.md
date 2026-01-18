# Chapter 43: Multi-Agent Fundamentals — The Team

<!--
METADATA
Phase: 9 - Multi-Agent Systems
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 31 (LangGraph)
Builds Toward: CrewAI (Ch 44), AutoGen (Ch 45)
Correctness Properties: P59 (Message Passing), P60 (State Consistency)
Project Thread: Team Architecture

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You want to build a house.
You don't hire one person who is an Architect AND a Plumber AND an Electrician.
You hire a team.
The Architect draws the plans. They hand the plans to the Builder. The Builder calls the Plumber.

One Agent is powerful. A **Team of Agents** is unstoppable.
But teams have new problems: Communication. Coordination. Conflict.
"I thought *you* were doing the roof!" "No, I'm doing the floor!"

**By the end of this chapter**, you will orchestrate your first digital workforce. You'll make two agents talk to each other, solve a problem, and high-five (digitally). 🤝

---

## Prerequisites Check

We are using LangGraph (Chapter 31 skills).

```bash
pip show langgraph
```

---

## The Story: The "Bottleneck"

### The Problem (The Generalist)

You have one Agent. You tell it: "Research the history of AI and write a blog post."
It researches. It writes.
But it's mediocre at both. It forgets citations. The writing is dry.
It's overwhelmed.

### The Solution (Specialists)

We hire:
1.  **Researcher Agent**: Only uses Google. Outputs raw facts.
2.  **Writer Agent**: Only writes. Takes facts, makes them sing.

We connect them: `User -> Researcher -> Writer -> User`.

---

## Part 1: The Shared Brain (State)

In a multi-agent system, the **State** is the project file. Everyone reads it, everyone adds to it.

### 🔬 Try This! (Hands-On Practice #1)

**Create `team_state.py`**:

```python
from typing import TypedDict, Annotated, List
import operator

class TeamState(TypedDict):
    # 'messages' is a list that grows.
    # operator.add ensures new messages are appended, not overwritten.
    messages: Annotated[List[str], operator.add]
    next_agent: str
```

**Run it**. (Just definitions).
Why `Annotated[..., operator.add]`?
In LangGraph, if Node A returns `{"messages": ["Hi"]}` and Node B returns `{"messages": ["Bye"]}`, standard dicts would overwrite. `operator.add` makes it `["Hi", "Bye"]`. It merges them!

---

## Part 2: The Handoff (The Pass)

Let's build the graph.

### 🔬 Try This! (Hands-On Practice #2)

**Create `simple_handoff.py`**:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

class State(TypedDict):
    messages: Annotated[List[str], operator.add]

# Agent 1: Researcher
def research_node(state):
    print("🔎 Researcher: Found info on AI.")
    return {"messages": ["Fact: AI started in 1956."]}

# Agent 2: Writer
def writer_node(state):
    print("✍️  Writer: Writing blog post...")
    # Read the previous message
    last_message = state["messages"][-1]
    return {"messages": [f"Blog Post: {last_message} It is cool."]}

# Graph
workflow = StateGraph(State)
workflow.add_node("researcher", research_node)
workflow.add_node("writer", writer_node)

# Hardcoded Handoff: Researcher ALWAYS passes to Writer
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)

app = workflow.compile()

# Run
print("--- Starting Team ---")
result = app.invoke({"messages": []})
print("\nFinal State:")
for m in result["messages"]:
    print(f"- {m}")
```

**Run it**.
You should see the "Fact" followed by the "Blog Post".
They communicated! The Writer *read* what the Researcher *wrote*.

---

## Part 3: The Router (Conditional Handoff)

What if the Researcher says "I can't find anything"?
We shouldn't write a blog post about nothing. We should go to END.

### 🔬 Try This! (Hands-On Practice #3)

**Create `smart_handoff.py`**:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
import random

class State(TypedDict):
    messages: Annotated[List[str], operator.add]
    status: str

def researcher(state):
    if random.random() < 0.5:
        print("🔎 Researcher: Success!")
        return {"messages": ["Found Data"], "status": "success"}
    else:
        print("🔎 Researcher: Failed.")
        return {"messages": ["No Data"], "status": "fail"}

def writer(state):
    print("✍️  Writer: Writing...")
    return {"messages": ["Draft Complete"]}

def router(state):
    if state["status"] == "success":
        return "writer"
    return "end"

workflow = StateGraph(State)
workflow.add_node("researcher", researcher)
workflow.add_node("writer", writer)

workflow.set_entry_point("researcher")
workflow.add_conditional_edges(
    "researcher",
    router,
    {"writer": "writer", "end": END}
)
workflow.add_edge("writer", END)

app = workflow.compile()

# Run multiple times to see both paths
for i in range(3):
    print(f"\n--- Run {i+1} ---")
    app.invoke({"messages": []})
```

**Run it**.
Sometimes it writes. Sometimes it quits. Smart team.

---

## Common Mistakes

### Mistake #1: Overwriting State
If you forget `Annotated[..., operator.add]`, the Researcher's notes disappear when the Writer speaks. The State is blown away.
**Fix**: Use Reducers (like `operator.add`).

### Mistake #2: Infinite Handoffs
A -> B -> A -> B...
**Fix**: Add a `loop_count` to the state and stop if it hits 10.

### Mistake #3: Context Bloat
If A and B talk for 100 turns, the context window fills up (see Chapter 30).
**Fix**: Summarize the state periodically.

---

## Quick Reference Card

### State Reducers

```python
from langgraph.graph.message import add_messages
class State(TypedDict):
    # Automatically handles appending lists of messages
    messages: Annotated[list, add_messages]
```

---

## Verification (REQUIRED SECTION)

We need to verify **P59 (Message Passing)** and **P60 (State Consistency)**.

**Create `verify_team.py`**:

```python
"""
Verification script for Chapter 43.
Properties: P59 (Passing), P60 (Consistency).
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
import sys

print("🧪 Running Team Verification...\n")

class State(TypedDict):
    msgs: Annotated[List[str], operator.add]

def agent_a(state):
    return {"msgs": ["A was here"]}
def agent_b(state):
    # Check if A's message exists (P59)
    if "A was here" in state["msgs"]:
        return {"msgs": ["B saw A"]}
    return {"msgs": ["B is blind"]}

workflow = StateGraph(State)
workflow.add_node("a", agent_a)
workflow.add_node("b", agent_b)
workflow.set_entry_point("a")
workflow.add_edge("a", "b")
workflow.add_edge("b", END)
app = workflow.compile()

# Run
res = app.invoke({"msgs": []})

# Verify P59: Message Passing
if "B saw A" in res["msgs"]:
    print("✅ P59 Passed: Agent B successfully read Agent A's output.")
else:
    print(f"❌ Failed: Message passing broken. {res['msgs']}")
    sys.exit(1)

# Verify P60: State Consistency (Append vs Overwrite)
if len(res["msgs"]) == 2:
    print("✅ P60 Passed: State preserved history (List appended).")
else:
    print(f"❌ Failed: State overwritten. {res['msgs']}")
    sys.exit(1)

print("\n🎉 Chapter 43 Complete! You are a Team Leader.")
```

**Run it:** `python verify_team.py`

---

## Summary

**What you learned:**

1. ✅ **Multi-Agent Pattern**: Splitting tasks among specialized nodes.
2. ✅ **Shared State**: The global memory of the team.
3. ✅ **Reducers**: How to merge updates (`operator.add`) instead of overwriting.
4. ✅ **Handoffs**: Explicitly passing control.
5. ✅ **Conditional Routing**: Deciding who works next based on results.

**Key Takeaway**: A Multi-Agent System is just a Graph where the Nodes are Agents.

**Skills unlocked**: 🎯
- Team Orchestration
- State Reducers
- Distributed Logic

**Looking ahead**: Building graphs manually is powerful but verbose.
Frameworks like **CrewAI** automate this "Team Building" process. They handle the graph, the prompts, and the handoffs for you.
In **Chapter 44**, we will use **CrewAI** to build a complex research team in minutes.

---

**Next**: [Chapter 44: CrewAI for Team-Based Workflows →](chapter-44-crewai.md)
