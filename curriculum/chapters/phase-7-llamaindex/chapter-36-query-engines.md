# Chapter 36: Query Engines & Response Synthesis — The Art of the Answer

<!--
METADATA
Phase: 7 - LlamaIndex
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 35 (LlamaIndex)
Builds Toward: Advanced Indexing (Ch 37)
Correctness Properties: P50 (Synthesis Mode), P51 (Transformation Accuracy)
Project Thread: Response Generation

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You have 10 friends who witnessed a crime.
**Strategy A**: You put them all in a room and shout "What happened?!" (Chaos).
**Strategy B**: You interview them one by one. You refine your notes after each person. (Thorough).
**Strategy C**: You group them into pairs, have them agree on a story, then group the pairs... ( Consensus).

LlamaIndex behaves the same way when it retrieves 10 documents.
It doesn't just "stuff them in the prompt." It has **Response Synthesis Strategies**.
It can **Refine** its answer as it reads. It can **Summarize** recursively.

**By the end of this chapter**, you will control exactly *how* your AI constructs its answers, optimizing for speed, detail, or summary. 🍳

---

## Prerequisites Check

```bash
# Verify llama-index
pip show llama-index
```

---

## The Story: The "Cut-Off" Summary

### The Problem (Context Limits)

You ask: "Summarize this 100-page book."
The retrieval engine finds the top 20 pages.
Standard RAG pastes them into the prompt.
**Error**: `ContextWindowExceeded`. Or the AI only reads the first 5 pages and ignores the rest.

### The Solution (Synthesis Modes)

We need a strategy that handles *more data than fits in the context window*.
1.  **Refine**: Read Chunk 1 -> Generate Answer. Read Chunk 2 -> Update Answer. (Sequential).
2.  **Tree Summarize**: Summarize chunks in parallel, then summarize the summaries. (Hierarchical).

---

## Part 1: The Default (Compact)

`compact` is the default. It stuffs as many chunks as possible into the prompt. If they fit, great. If not, it fails or truncates.

### 🔬 Try This! (Hands-On Practice #1)

Let's look at the default behavior.

**Create `test_compact.py`**:

```python
from llama_index.core import VectorStoreIndex, Document
from dotenv import load_dotenv

load_dotenv()

# Create dummy docs
text = ["Fact 1: The sky is blue."] * 10 
docs = [Document(text="\n".join(text))]

index = VectorStoreIndex.from_documents(docs)

# Default is 'compact'
engine = index.as_query_engine(response_mode="compact")
response = engine.query("What are the facts?")
print(response)
```

**Run it**. Fast and simple.

---

## Part 2: The Iterator (Refine)

`refine` is powerful. It allows the LLM to "read through" the documents sequentially.

**How it works:**
1.  Query + Chunk 1 -> Answer 1.
2.  Query + Answer 1 + Chunk 2 -> Answer 2.
3.  ...

### 🔬 Try This! (Hands-On Practice #2)

**Create `test_refine.py`**:

```python
from llama_index.core import VectorStoreIndex, Document

# Documents representing a story told in parts
docs = [
    Document(text="Part 1: Alice went to the market."),
    Document(text="Part 2: She bought an apple."),
    Document(text="Part 3: She ate it.")
]

index = VectorStoreIndex.from_documents(docs)

# Use 'refine' mode
# We set similarity_top_k=3 to ensure it sees all parts
engine = index.as_query_engine(
    response_mode="refine", 
    similarity_top_k=3
)

response = engine.query("Tell me the whole story of Alice.")
print(response)
```

**Run it**.
The answer should seamlessly combine all parts because the LLM refined its answer step-by-step.

---

## Part 3: The Summarizer (Tree Summarize)

`tree_summarize` is best for "What are the common themes?" or summarizing vast amounts of data. It builds a tree of summaries.

### 🔬 Try This! (Hands-On Practice #3)

**Create `test_tree.py`**:

```python
from llama_index.core import VectorStoreIndex, Document

# Lots of data
docs = [Document(text=f"Review {i}: I loved the service.") for i in range(20)]

index = VectorStoreIndex.from_documents(docs)

# Use 'tree_summarize'
engine = index.as_query_engine(
    response_mode="tree_summarize", 
    similarity_top_k=10
)

response = engine.query("What is the general sentiment?")
print(response)
```

**Run it**.
It summarizes the 10 reviews into a single coherent statement.

---

## Part 4: Streaming Responses

LlamaIndex supports streaming too!

### 🔬 Try This! (Hands-On Practice #4)

**Create `llama_stream.py`**:

```python
from llama_index.core import VectorStoreIndex, Document
import sys

docs = [Document(text="Streaming is cool because it reduces latency perception.")]
index = VectorStoreIndex.from_documents(docs)

# Enable streaming
engine = index.as_query_engine(streaming=True)
response = engine.query("Why is streaming cool?")

# Iterate and print
print("Response: ", end="")
for token in response.response_gen:
    print(token, end="", flush=True)
print()
```

**Run it**.
Matrix mode enabled. 🟢

---

## Common Mistakes

### Mistake #1: Using `refine` for everything
`refine` is **slow**. If you retrieve 10 chunks, it makes 10 LLM calls sequentially.
**Fix**: Use `compact` for simple lookups. Use `refine` only when detail is critical.

### Mistake #2: `similarity_top_k` too low
If you set `k=1`, `refine` acts just like `compact`. It only sees one chunk.
**Fix**: Increase `k` when using advanced synthesis modes.

### Mistake #3: Ignoring Prompt Templates
Each mode uses specific prompts ("Here is the context...", "Here is the existing answer...").
**Fix**: You can customize these prompts using `engine.update_prompts()`.

---

## Quick Reference Card

### Response Modes

| Mode | Behavior | Pros | Cons |
|------|----------|------|------|
| `compact` | Stuffs context | Fast, Cheap | Context limits |
| `refine` | Sequential update | Detailed, Thorough | Slow, Expensive |
| `tree_summarize` | Recursive summary | Good for aggregation | Multiple calls |
| `no_text` | Returns nodes only | Debugging | No answer |

---

## Verification (REQUIRED SECTION)

We need to verify **P50 (Synthesis Mode Correctness)**.

**Create `verify_synthesis.py`**:

```python
"""
Verification script for Chapter 36.
Property P50: Synthesis Mode.
"""
from llama_index.core import VectorStoreIndex, Document
import sys

print("🧪 Running Synthesis Verification...\n")

# Setup: A contradiction that requires refinement to resolve
# Chunk 1 says X. Chunk 2 says "Correction: It is Y."
docs = [
    Document(text="The code is 1234."),
    Document(text="UPDATE: The code changed to 9999.")
]
index = VectorStoreIndex.from_documents(docs)

# Test 1: Refine Mode
# If it works, it should see the update and refine the answer to 9999.
print("Test 1: Refine Mode...")
engine = index.as_query_engine(response_mode="refine", similarity_top_k=2)
res = engine.query("What is the code?")

if "9999" in str(res):
    print("✅ P50 Passed: Refine mode successfully updated the answer.")
else:
    print(f"❌ Failed: Did not refine. Got: {res}")
    sys.exit(1)

print("\n🎉 Chapter 36 Complete! You master the synthesis.")
```

**Run it:** `python verify_synthesis.py`

---

## Summary

**What you learned:**

1. ✅ **Synthesis Strategies**: How the sausage is made.
2. ✅ **Refine**: The sequential reader.
3. ✅ **Tree Summarize**: The parallel aggregator.
4. ✅ **Compact**: The fast default.
5. ✅ **Streaming**: Real-time output in LlamaIndex.

**Key Takeaway**: Don't just "Retrieve". Think about how you want the AI to *process* what it retrieved.

**Skills unlocked**: 🎯
- Response Optimization
- Latency Engineering
- Advanced LlamaIndex Config

**Looking ahead**: We've used the basic `VectorStoreIndex`. But data isn't always a flat list of text. Sometimes it's a **Tree**, a **Graph**, or a **Table**.
In **Chapter 37**, we will explore **Advanced Indexing** structures to model complex knowledge!

---

**Next**: [Chapter 37: Advanced Indexing →](chapter-37-advanced-indexing.md)
