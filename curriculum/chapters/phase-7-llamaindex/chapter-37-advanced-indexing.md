# Chapter 37: Advanced Indexing — Structuring Knowledge

<!--
METADATA
Phase: 7 - LlamaIndex
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 35 (LlamaIndex)
Builds Toward: Production Systems (Ch 40)
Correctness Properties: P52 (Index Appropriateness), P53 (Router Accuracy)
Project Thread: Knowledge Architecture

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You walk into a library.
**Scenario A**: You want a specific quote. You use the **Search Computer** (Vector Index). Fast. ⚡
**Scenario B**: You want to know the *main theme* of the library. Using the Search Computer is useless ("Theme" appears in 1000 books). You need to walk the aisles and skim **Everything** (Summary Index). 🐌

Data isn't one-size-fits-all.
For specific facts, we use **Vectors**.
For summarization, we use **Lists**.
For relationships, we use **Graphs**.

**By the end of this chapter**, you will build a system that *automatically* chooses the right structure for the user's question. A "Router" that knows when to Search and when to Read All. 🚦

---

## Prerequisites Check

```bash
pip show llama-index
```

---

## The Story: The "Summarization" Fail

### The Problem (Vectors can't Read)

You have a 50-page document.
User: "Summarize the document."
Vector Index: Finds top 2 chunks (Page 5 and Page 42).
AI Summary: "This document discusses Page 5 and Page 42."
User: "What about the rest?!" 😡

### The Solution (Summary Index)

A **Summary Index** (formerly List Index) doesn't filter. It stores Nodes in a sequence.
When queried, it reads **all** nodes (using `tree_summarize` mode) to synthesize a complete answer.

---

## Part 1: The Summary Index

Let's build one.

### 🔬 Try This! (Hands-On Practice #1)

**Create `summary_index.py`**:

```python
from llama_index.core import SummaryIndex, Document
from dotenv import load_dotenv

load_dotenv()

# 1. Create Data (3 distinct parts)
docs = [
    Document(text="Part 1: The project started in 2020."),
    Document(text="Part 2: We hired 50 engineers."),
    Document(text="Part 3: We launched in 2022.")
]

# 2. Build Summary Index
# Unlike VectorIndex, this doesn't embed everything upfront.
# It just links them.
index = SummaryIndex.from_documents(docs)

# 3. Query
# This will read ALL 3 nodes to answer.
engine = index.as_query_engine(response_mode="tree_summarize")
response = engine.query("Give me a timeline of the project.")

print(response)
```

**Run it**.
It should mention 2020, the engineers, AND 2022. A Vector Index might have missed one if `k=1` or `k=2`.

---

## Part 2: The Router (The Traffic Controller)

We don't want to use `SummaryIndex` for everything (it's slow/expensive).
We want:
- **Specific questions** -> Vector Index.
- **General summaries** -> Summary Index.

We use a **RouterQueryEngine**.

### 🔬 Try This! (Hands-On Practice #2)

**Create `router_engine.py`**:

```python
from llama_index.core import VectorStoreIndex, SummaryIndex, Document
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector

# 1. Data
docs = [
    Document(text="The capital of France is Paris."),
    Document(text="The capital of Spain is Madrid."),
    Document(text="Europe has many diverse cultures and histories.")
]

# 2. Create Indexes
vector_index = VectorStoreIndex.from_documents(docs)
summary_index = SummaryIndex.from_documents(docs)

# 3. Create Tools (The options for the Router)
vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_index.as_query_engine(),
    description="Useful for retrieving specific facts like capitals."
)

summary_tool = QueryEngineTool.from_defaults(
    query_engine=summary_index.as_query_engine(response_mode="tree_summarize"),
    description="Useful for summarization or general questions about Europe."
)

# 4. Create Router
# LLMSingleSelector uses the LLM to pick the best tool
router = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[vector_tool, summary_tool]
)

# 5. Test
print("---" Test 1: Specific Fact ---")
res1 = router.query("What is the capital of France?")
print(f"Answer: {res1}\n")

print("---" Test 2: General Summary ---")
res2 = router.query("Summarize the text.")
print(f"Answer: {res2}\n")
```

**Run it**.
Observe the logs (if verbose) or the speed. The Router effectively "routes" the user's intent to the correct data structure.

---

## Part 3: Knowledge Graphs (The Web)

**Vectors** find similarity. **Graphs** find connections.
"Elon Musk" -> [IS_CEO_OF] -> "Tesla".

We won't implement a full KG here (requires complex setup), but know that `KnowledgeGraphIndex` exists. It extracts triplets `(Subject, Predicate, Object)` from text and stores them in a Graph DB (like NebulaGraph or Neo4j).

**Use Case**: "How is Person A connected to Person B?" (Vectors fail at this. Graphs excel).

---

## Common Mistakes

### Mistake #1: Using Summary Index for Large Datasets without filtering
If you have 1,000 docs, `SummaryIndex` tries to read them all. Expensive!
**Fix**: Use metadata filters first, or use a hierarchical approach (Vector Search to find top 50 docs -> Summary Index on those 50).

### Mistake #2: Vague Tool Descriptions
The Router relies on `description="..."` to make choices.
**Bad**: "Use this for data."
**Good**: "Use this for specific fact retrieval about specific entities."

### Mistake #3: Over-Routing
Sometimes you need *both*.
**Fix**: Use `LLMMultiSelector` instead of `LLMSingleSelector` to query multiple indexes and combine answers.

---

## Quick Reference Card

### Index Types

| Index | Best For | Complexity |
|-------|----------|------------|
| **VectorStoreIndex** | Specific lookup, semantic search | Low |
| **SummaryIndex** | Summarization, "Read Everything" | Low |
| **KnowledgeGraph** | Relationships, Multi-hop reasoning | High |
| **TreeIndex** | Hierarchical navigation | Medium |

### Router Setup

```python
RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[tool1, tool2]
)
```

---

## Verification (REQUIRED SECTION)

We need to verify **P53 (Routing Accuracy)**.

**Create `verify_router.py`**:

```python
"""
Verification script for Chapter 37.
Property P53: Router Accuracy.
"""
from llama_index.core.tools import QueryEngineTool
from llama_index.core.selectors import LLMSingleSelector
import sys

# Mock Selector to test routing logic without full index overhead
# In a real unit test, we'd mock the LLM decision.
# Here, we use the real selector but with dummy tools description.

selector = LLMSingleSelector.from_defaults()

tools = [
    QueryEngineTool.from_defaults(
        query_engine=None, # Placeholder
        name="vector_tool",
        description="Useful for finding specific numbers and facts."
    ),
    QueryEngineTool.from_defaults(
        query_engine=None, # Placeholder
        name="summary_tool",
        description="Useful for summarizing long documents."
    )
]

print("🧪 Running Router Verification...\n")

# Test 1: Fact Routing
print("Test 1: Fact Routing...")
# "What is the price?" -> Should pick vector_tool
result1 = selector.select(tools, "What is the price of the item?")
if result1.selections[0].index == 0: # Index 0 is vector_tool
    print("✅ Routed to Vector Tool.")
else:
    print(f"❌ Failed: Routed to {result1.selections[0].index}")
    sys.exit(1)

# Test 2: Summary Routing
print("Test 2: Summary Routing...")
# "Summarize the document" -> Should pick summary_tool
result2 = selector.select(tools, "Give me a summary of the whole text.")
if result2.selections[0].index == 1: # Index 1 is summary_tool
    print("✅ P53 Passed: Routed to Summary Tool.")
else:
    print(f"❌ Failed: Routed to {result2.selections[0].index}")
    sys.exit(1)

print("\n🎉 Chapter 37 Complete! You are an Architect.")
```

**Run it:** `python verify_router.py`

---

## Summary

**What you learned:**

1. ✅ **Index Diversity**: Data structures matter.
2. ✅ **Summary Index**: The tool for "Reading it all".
3. ✅ **Router Engine**: The AI traffic controller.
4. ✅ **Tool Descriptions**: Prompt engineering for indexes.
5. ✅ **Architecture**: Combining multiple indexes for one app.

**Key Takeaway**: Don't force everything into a Vector Store. If the user wants a summary, give them a Summary Index.

**Skills unlocked**: 🎯
- Knowledge Modeling
- Router Design
- LlamaIndex Composability

**Looking ahead**: We have mastered LlamaIndex and LangGraph. We have Retrieval and Agents.
In **Chapter 38**, we will finalize our RAG skills with **Hybrid Search & Re-Ranking** in LlamaIndex to squeeze the last 10% of accuracy out of our system.

---

**Next**: [Chapter 38: Hybrid Search & Reranking →](chapter-38-hybrid-reranking.md)
