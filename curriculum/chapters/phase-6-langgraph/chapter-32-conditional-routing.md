# Chapter 32: Conditional Routing — The Fork in the Road

<!--
METADATA
Phase: 6 - LangGraph
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 31 (LangGraph)
Builds Toward: Multi-Agent Teams (Ch 43)
Correctness Properties: P43 (Routing Evaluation), P44 (Branch Coverage)
Project Thread: Intelligent Dispatch

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You walk into a hospital.
You don't walk into a random room and hope for the best.
You go to the **Triage Desk**.
Nurse: "What's wrong?"
You: "My arm hurts." -> Sends you to **X-Ray**.
You: "I have a fever." -> Sends you to **General Practice**.

**Conditional Routing** is the Triage Desk for your AI.
Instead of one giant agent trying to do everything (writing poems, calculating taxes, searching SQL), we build **Specialists**. The Router sends the user to the right specialist.

**By the end of this chapter**, you will build an intelligent traffic controller that routes questions to the perfect expert. 🚦

---

## Prerequisites Check

```bash
# Verify LangGraph
pip show langgraph
```

---

## The Story: The "Jack of All Trades"

### The Problem (Confusion)

You have an agent with 50 tools.
User: "What is 2 + 2?"
Agent: "I'll use the 'Search Google' tool!" (Mistake).
User: "Write a poem."
Agent: "I'll use the 'Calculator' tool!" (Mistake).

When an agent has too many options, it gets confused.

### The Solution (Specialization)

We split the brain.
1.  **Router**: Decides "Is this Math or Writing?"
2.  **Math Expert**: Only has a calculator.
3.  **Writer Expert**: Only has a text editor.

The Math Expert can't write poems. It literally *can't* fail by picking the wrong tool because it doesn't *have* the wrong tool.

---

## Part 1: The Classifier (The Triage Nurse)

We need a small, fast chain that outputs a decision.

### 🔬 Try This! (Hands-On Practice #1)

**Create `classifier.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal

# 1. Define the Router Output
class RouteChoice(BaseModel):
    """Route the user query to the most relevant worker."""
    destination: Literal["math", "writing", "general"] = Field(
        description="The department to send the query to."
    )

# 2. Setup the Model
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm = model.with_structured_output(RouteChoice)

# 3. Create the Prompt
system = """You are a router. Pick the correct destination.
- 'math': For calculations, numbers, logic.
- 'writing': For poems, stories, emails.
- 'general': For greetings or unknown."""

prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "{question}"),
])

# 4. The Chain
router_chain = prompt | structured_llm

# 5. Test it
print("--- Testing Router ---")
print(router_chain.invoke({"question": "What is 50 * 9?"}))
print(router_chain.invoke({"question": "Write a haiku about rain."})
print(router_chain.invoke({"question": "Hello there."})
```

**Run it**.
You should see clear JSON outputs: `destination='math'`, `destination='writing'`, etc.

---

## Part 2: The Nodes (The Specialists)

Now we define the workers.

### 🔬 Try This! (Hands-On Practice #2)

**Create `specialists.py`**:

```python
from typing import TypedDict, Annotated

class State(TypedDict):
    question: str
    answer: str
    path: str # Just for debugging

def math_node(state: State):
    return {
        "answer": "Calculated: 42 (Math Node)",
        "path": "math"
    }

def writing_node(state: State):
    return {
        "answer": "Roses are red... (Writing Node)",
        "path": "writing"
    }

def general_node(state: State):
    return {
        "answer": "How can I help you? (General Node)",
        "path": "general"
    }
```

---

## Part 3: Wiring the Switch

Now we connect the Router to the Nodes using `add_conditional_edges`.

### 🔬 Try This! (Hands-On Practice #3)

**Create `router_graph.py`**:

```python
from langgraph.graph import StateGraph, END
from classifier import router_chain
from specialists import math_node, writing_node, general_node, State

# 1. Routing Logic
def route_question(state: State):
    print(f"🚦 Routing: {state['question']}")
    decision = router_chain.invoke({"question": state["question"]})
    return decision.destination # Returns "math", "writing", or "general"

# 2. Build Graph
workflow = StateGraph(State)

# Add Workers
workflow.add_node("math", math_node)
workflow.add_node("writing", writing_node)
workflow.add_node("general", general_node)

# 3. Add Conditional Entry
# From START, look at 'route_question'. 
# If it returns 'math', go to 'math' node. Etc.
workflow.set_conditional_entry_point(
    route_question,
    {
        "math": "math",
        "writing": "writing",
        "general": "general"
    }
)

# 4. End Edges
workflow.add_edge("math", END)
workflow.add_edge("writing", END)
workflow.add_edge("general", END)

# 5. Compile
app = workflow.compile()

# 6. Run
print("\n--- Test 1: Math ---")
res = app.invoke({"question": "Calculate tax."})
print(f"Result: {res['answer']}")

print("\n--- Test 2: Writing ---")
res = app.invoke({"question": "Write a song."})
print(f"Result: {res['answer']}")
```

**Run it**.
Watch the traffic flow to the correct destination! 🚦

---

## Common Mistakes

### Mistake #1: Overlapping Categories
If you have "Coding" and "Math", asking for "Python math script" confuses the router.
**Fix**: Provide clear examples in the prompt. "Python code goes to Coding, simple arithmetic goes to Math."

### Mistake #2: String Matching fragility
If your LLM returns "Math" (capitalized) but your edge map expects "math", it breaks.
**Fix**: Use Pydantic/Enum (like we did) to guarantee exact string matches. Pydantic handles the normalization.

### Mistake #3: No Fallback
What if the router is unsure? 
**Fix**: Always have a "General" or "Fallback" node.

---

## Quick Reference Card

### Conditional Edge Syntax

```python
workflow.add_conditional_edges(
    "source_node",
    decision_function,
    {
        "output_a": "destination_a",
        "output_b": "destination_b"
    }
)
```

---

## Verification (REQUIRED SECTION)

We need to verify **P43 (Routing Logic)** and **P44 (Branch Coverage)**.

**Create `verify_routing.py`**:

```python
"""
Verification script for Chapter 32.
Properties: P43 (Logic), P44 (Coverage).
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict
import sys

print("🧪 Running Routing Verification...\n")

class State(TypedDict):
    input: str
    visited: str

# Mock Router Function
def simple_router(state):
    if "a" in state["input"]:
        return "a"
    return "b"

# Nodes
def node_a(state): return {"visited": "A"}
def node_b(state): return {"visited": "B"}

# Graph
workflow = StateGraph(State)
workflow.add_node("node_a", node_a)
workflow.add_node("node_b", node_b)

workflow.set_conditional_entry_point(
    simple_router,
    {"a": "node_a", "b": "node_b"}
)
workflow.add_edge("node_a", END)
workflow.add_edge("node_b", END)
app = workflow.compile()

# Test P43: Routing Evaluation
print("Test 1: Route A...")
res_a = app.invoke({"input": "apple"})
if res_a["visited"] == "A":
    print("✅ P43 Passed: Routed to A correctly.")
else:
    print(f"❌ Failed: Went to {res_a['visited']}")
    sys.exit(1)

# Test P44: Branch Coverage
print("Test 2: Route B...")
res_b = app.invoke({"input": "banana"}) # No 'a'
if res_b["visited"] == "B":
    print("✅ P44 Passed: Routed to B correctly.")
else:
    print(f"❌ Failed: Went to {res_b['visited']}")
    sys.exit(1)

print("\n🎉 Chapter 32 Complete! You are a Traffic Controller.")
```

**Run it:** `python verify_routing.py`

---

## Summary

**What you learned:**

1. ✅ **Specialization**: Dividing complex tasks into simple sub-tasks.
2. ✅ **The Classifier**: Using LLMs to make architectural decisions.
3. ✅ **Conditional Entry**: Starting the graph at different points.
4. ✅ **Structured Output**: Ensuring the router returns valid destinations.
5. ✅ **Architecture**: The Hub-and-Spoke pattern.

**Key Takeaway**: Don't ask one agent to be a Lawyer, Doctor, and Artist. Create three agents and a Receptionist.

**Skills unlocked**: 🎯
- Classification
- Conditional Logic
- System Design

**Looking ahead**: We can route. We can loop. But sometimes we need a human to check the work before it's final. In **Chapter 33**, we will build **Human-in-the-Loop** workflows!

---

**Next**: [Chapter 33: Human-in-the-Loop Workflows →](chapter-33-hitl.md)
