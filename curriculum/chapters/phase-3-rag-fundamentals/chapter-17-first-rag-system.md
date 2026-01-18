# Chapter 17: Your First RAG System — Chatting with Data

<!--
METADATA
Phase: 3 - RAG Fundamentals
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 14 (Vector Store), Chapter 8 (Client)
Builds Toward: Advanced RAG (Ch 19), Agents (Ch 26)
Correctness Properties: P19 (Citation Accuracy), P20 (Consistency)
Project Thread: Knowledge Retrieval

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're taking a history exam.
**Scenario A**: You have to memorize every date and name. (Closed Book). Hard. 😓
**Scenario B**: You can bring the textbook into the exam room. (Open Book). Easy. 😎

LLMs are normally "Closed Book". They only know what they were trained on (internet data up to 2023). They don't know about *your* private emails, *your* contracts, or *your* new product launch.

**RAG (Retrieval-Augmented Generation)** is the "Open Book" strategy.
Instead of forcing the LLM to memorize your data, we just **show it the relevant page** right before it answers the question.

**By the end of this chapter**, you will build a system that can answer questions about documents the AI has *never seen before*. You are about to give the AI eyes. 👀

---

## Prerequisites Check

Ensure you have your Vector Store (Ch 14) and LLM Client (Ch 8) ready.

```bash
# Check project structure
ls shared/infrastructure
# Should see: llm/ vector_store.py
```

---

## The Story: The "Hallucination"

### The Problem (Confidently Wrong)

You ask ChatGPT: *"Who is the lead engineer on Project Alpha?"*
ChatGPT: *"The lead engineer is John Smith."* (It made that up. It has no idea who your engineers are).

### The Solution (Grounding)

We need to **Ground** the AI in reality.
1.  **Retrieve**: Find the document that says "Lead Engineer: Sarah Jones".
2.  **Augment**: Paste that text into the prompt.
3.  **Generate**: Ask the AI, "Based on this text, who is the lead?"

It can't hallucinate if the answer is right in front of its face.

---

## Part 1: The RAG Architecture

The workflow is a circle:

1.  **Ingestion** (One time):
    *   Load PDF -> Chunk -> Embed -> Save to ChromaDB.
2.  **Retrieval** (Every query):
    *   User Question -> Embed -> Search ChromaDB -> Get Top 3 Chunks.
3.  **Synthesis** (Every query):
    *   Prompt: "Context: {chunks}. Question: {question}." -> LLM -> Answer.

---

## Part 2: Building the Pipeline

Let's assemble the pieces we built in Phase 2.

### 🔬 Try This! (Hands-On Practice #1)

**Create `simple_rag.py`**:

```python
from shared.infrastructure.llm.client import MultiProviderClient
from shared.infrastructure.vector_store import VectorStore
import os

# 1. Setup
client = MultiProviderClient(provider="openai")
# Use a temporary DB for this test
store = VectorStore(path="./rag_test_db", collection_name="rag_demo")

# 2. Ingest Data (Simulating Ch 16 + 15)
# In a real app, we'd use PDFLoader -> RecursiveChunker
print("📚 Ingesting Knowledge...")
knowledge = [
    "Project Alpha is a secret initiative to build a flying car.",
    "The lead engineer for Project Alpha is Sarah Jones.",
    "The budget for Project Alpha is $500 million."
]

for i, text in enumerate(knowledge):
    store.add_document(doc_id=str(i), text=text, metadata={"source": "memo.txt"})

# 3. The RAG Function
def ask_rag(question):
    print(f"\n❓ Question: {question}")
    
    # Step A: Retrieve
    results = store.search(question, limit=2)
    context_text = "\n".join(results)
    print(f"🔎 Found Context: {context_text}")
    
    # Step B: Augment Prompt
    prompt = f"""
    You are a helpful assistant. Answer the question using ONLY the provided context.
    If you don't know, say "I don't know".
    
    Context:
    {context_text}
    
    Question: {question}
    """
    
    # Step C: Generate
    answer = client.generate(prompt)
    print(f"🤖 Answer: {answer}")
    return answer

# 4. Test it
ask_rag("Who is running Project Alpha?")
ask_rag("What is the budget?")
ask_rag("Who is the CEO?") # Should say "I don't know"
```

**Run it**.
Watch it answer questions it couldn't possibly know without the context!

---

## Part 3: Citations (Showing Your Work)

Users don't trust AI. They trust **Documents**.
We must tell the user *where* the answer came from.

### 🔬 Try This! (Hands-On Practice #2)

Let's modify our Vector Store search to return metadata too.

**Update `shared/infrastructure/vector_store.py`**:

```python
    # Update the search method signature to return more details
    def search_with_metadata(self, query: str, limit: int = 3):
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        # Zip documents and metadatas together
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        return list(zip(docs, metas))
```

**Now verify it in `rag_citations.py`**:

```python
from shared.infrastructure.vector_store import VectorStore

store = VectorStore(path="./rag_test_db", collection_name="rag_demo")

# Query
results = store.search_with_metadata("Sarah Jones", limit=1)
text, metadata = results[0]

print(f"Fact: {text}")
print(f"Source: {metadata['source']}")
```

**Why is this huge?**
In a legal app, you can link the answer directly to "Contract.pdf, Page 5".

---

## Part 4: The "I Don't Know" Guardrail

The most important part of a RAG prompt is telling the AI to **shut up** if it doesn't have the info.

**The Prompt Pattern:**
```text
Answer using ONLY the context.
If the answer is not in the context, say "I don't know".
DO NOT make things up.
```

### 🔬 Try This! (Hands-On Practice #3)

Let's try to trick it.

**Create `hallucination_test.py`**:

```python
from shared.infrastructure.llm.client import MultiProviderClient

client = MultiProviderClient()

context = "The sky is green in this dimension."

# Prompt WITHOUT guardrails
bad_prompt = f"Context: {context}. What color is the grass?"
print("Bad Prompt:", client.generate(bad_prompt))
# It might say "Green" (guessing) or "I don't know", but it's unpredictable.

# Prompt WITH guardrails
good_prompt = f"""
Context: {context}
Question: What color is the grass?
Answer using ONLY the context. If not mentioned, say "Unknown".
"""
print("Good Prompt:", client.generate(good_prompt))
```

**Expected Output**: "Unknown".
This reliability is essential for business applications.

---

## Common Mistakes

### Mistake #1: Stuffing Too Much Context
"I'll just paste the whole book!"
LLMs have token limits. Plus, "Lost in the Middle" phenomenon means they forget stuff in the middle of a huge prompt.
**Fix**: Retrieve only the top 3-5 most relevant chunks.

### Mistake #2: Bad Chunking
If your chunks cut off sentences, the context is broken (Chapter 15). Garbage In, Garbage Out.

### Mistake #3: Ignoring Metadata
If you have 5 versions of "Contract.pdf", and you don't filter by `version="final"`, the AI might cite the draft!

---

## Quick Reference Card

### The RAG Prompt Template

```python
RAG_PROMPT = """
Use the following pieces of context to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question:
{question}
"""
```

---

## Verification (REQUIRED SECTION)

We need to prove **P20 (Consistency)**: The AI uses the provided context, not its training data.

**Create `verify_rag.py`**:

```python
"""
Verification script for Chapter 17.
Property P20: Consistency with Context.
"""
from shared.infrastructure.llm.client import MultiProviderClient
import sys

print("🧪 Running RAG Verification...\n")

client = MultiProviderClient(provider="openai")

# 1. Counter-Factual Context
# We tell the AI something false to see if it obeys.
fake_fact = "The moon is made of cheddar cheese."
question = "What is the moon made of?"

prompt = f"""
Context: {fake_fact}
Question: {question}
Answer using ONLY the context provided.
"""

# 2. Generate
answer = client.generate(prompt)
print(f"AI Answer: {answer}")

# 3. Verify P20
if "cheese" in answer.lower():
    print("✅ P20 Passed: AI grounded in context (overrode training data).")
else:
    print("❌ Failed: AI hallucinated or ignored context.")
    sys.exit(1)

print("\n🎉 Chapter 17 Complete! You have built a thinking machine.")
```

**Run it:** `python verify_rag.py`

---

## Summary

**What you learned:**

1. ✅ **RAG Flow**: Ingest -> Retrieve -> Augment -> Generate.
2. ✅ **Context Injection**: How to feed data into the prompt.
3. ✅ **Grounding**: Forcing the AI to stick to the facts provided.
4. ✅ **Citations**: Linking answers back to sources.
5. ✅ **Guardrails**: Teaching the AI to admit ignorance.

**Key Takeaway**: You don't train the model to teach it new facts. You just hand it the facts at runtime. This is cheaper, faster, and more accurate than training.

**Skills unlocked**: 🎯
- RAG Architecture
- Prompt Engineering (Context)
- Search Implementation

**Looking ahead**: We've been building components by hand (`if`, `for` loops). As apps get complex, this gets messy. In **Chapter 18**, we will introduce **LCEL (LangChain Expression Language)** to chain these steps together elegantly!

---

**Next**: [Chapter 18: LangChain Expression Language (LCEL) →](chapter-18-lcel.md)
