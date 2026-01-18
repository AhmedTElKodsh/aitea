# Chapter 35: LlamaIndex Fundamentals — The Data Framework

<!--
METADATA
Phase: 7 - LlamaIndex
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 14 (Vector Stores)
Builds Toward: Advanced Indexing (Ch 37)
Correctness Properties: P48 (Index Construction), P49 (Query Relevance)
Project Thread: Knowledge Architecture

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You have a pile of 10,000 unsorted tax documents.
**LangChain** is like a team of workers. You give them instructions: "Pick up a paper, read it, file it here." It gives you infinite control, but you have to manage the workers.
**LlamaIndex** is a Master Librarian. You just say "Here is the pile. Organize it." And it does. It indexes, chunks, embeds, and stores everything optimally.

**LangChain** is great for *Flow* (Chains, Agents).
**LlamaIndex** is great for *Data* (Indexing, Retrieval).

**By the end of this chapter**, you will build a sophisticated RAG system in about 5 lines of code. It's shockingly easy. 🦙

---

## Prerequisites Check

We need the LlamaIndex library.

```bash
pip install llama-index
```

---


## The Story: The "Boilerplate" Fatigue

### The Problem (Too Much Code)

In Phase 2 and 3, we wrote code to:
1. Load PDF.
2. Chunk text.
3. Embed chunks.
4. Store in Chroma.
5. Retrieve.
6. Send to LLM.

It was 100+ lines of code. It was educational, but tedious for quick projects.

### The Solution (The Index)

LlamaIndex abstracts this into one concept: **The Index**.
You feed it data. It gives you a **Query Engine**.

```python
index = VectorStoreIndex.from_documents(docs)
engine = index.as_query_engine()
response = engine.query("What is the tax rate?")
```

That's it. That's the whole RAG pipeline.

---

## Part 1: Documents and Nodes

LlamaIndex has two core data units:
1.  **Document**: The raw file (e.g., a PDF).
2.  **Node**: A chunk of that document. Nodes are smarter than simple text chunks; they know their relationship ("I am chunk 2, my previous chunk is 1, next is 3").

### 🔬 Try This! (Hands-On Practice #1)

Let's load data using `SimpleDirectoryReader`.

**Create `load_data.py`**:

```python
import os
from llama_index.core import SimpleDirectoryReader

# 1. Create dummy data
os.makedirs("data", exist_ok=True)
with open("data/paul_graham_essay.txt", "w", encoding="utf-8") as f:
    f.write("I worked on writing and programming. I wrote essays. I built a startup.")

# 2. Load
print("Loading data...")
reader = SimpleDirectoryReader("./data")
documents = reader.load_data()

print(f"Loaded {len(documents)} documents.")
print(f"Content: {documents[0].text[:50]}...")
print(f"Metadata: {documents[0].metadata}")

# Cleanup
import shutil
shutil.rmtree("data")
```

**Run it**.
`SimpleDirectoryReader` is magic. It handles extensions automatically.

---


## Part 2: The Vector Store Index

This is the standard "Index" for RAG. It takes documents, splits them into Nodes, embeds them (using OpenAI by default), and stores them.

### 🔬 Try This! (Hands-On Practice #2)

**Create `basic_index.py`**:

```python
from llama_index.core import VectorStoreIndex, Document
from dotenv import load_dotenv

load_dotenv()

# 1. Create Documents
docs = [
    Document(text="LlamaIndex is a data framework for LLM applications."),
    Document(text="LangChain is an orchestration framework for LLM applications.")
]

# 2. Build Index (Ingest -> Chunk -> Embed -> Store)
print("Building Index...")
index = VectorStoreIndex.from_documents(docs)

# 3. Query
print("Querying...")
query_engine = index.as_query_engine()
response = query_engine.query("What is LlamaIndex?")

print(f"Response: {response}")
```

**Run it**.
It just works. Behind the scenes, it did everything we spent 3 chapters building manually.

---


## Part 3: Customization (Persisting)

By default, the index is in RAM. Let's save it to disk.

### 🔬 Try This! (Hands-On Practice #3)

**Create `persist_index.py`**:

```python
from llama_index.core import VectorStoreIndex, Document, StorageContext, load_index_from_storage
import os

PERSIST_DIR = "./storage"

if not os.path.exists(PERSIST_DIR):
    print("Creating new index...")
    docs = [Document(text="The secret code is 9999.")]
    index = VectorStoreIndex.from_documents(docs)
    
    # Save to disk
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    print("Loading existing index...")
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

# Query
engine = index.as_query_engine()
print(engine.query("What is the secret code?"))
```

**Run it twice**.
The second time, it loads instantly from disk.

---


## Common Mistakes

### Mistake #1: Missing API Key
LlamaIndex uses OpenAI by default. Ensure `OPENAI_API_KEY` is in your `.env`.

### Mistake #2: "It's too easy"
Users think LlamaIndex *only* does simple RAG. It actually supports Graphs, SQL, and complex routing. We start simple, but it goes deep.

### Mistake #3: Ignoring Metadata
`SimpleDirectoryReader` extracts some metadata, but you can add more.
`Document(text="...", metadata={"author": "Paul"})`. This is crucial for advanced filtering later.

---


## Quick Reference Card

### The "Hello World" of LlamaIndex

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("Question?")
```

---


## Verification (REQUIRED SECTION)

We need to verify **P48 (Construction)** and **P49 (Relevance)**.

**Create `verify_llamaindex.py`**:

```python
"""
Verification script for Chapter 35.
Properties: P48 (Construction), P49 (Relevance).
"""
from llama_index.core import VectorStoreIndex, Document
import sys

print("🧪 Running LlamaIndex Verification...\n")

# P48: Index Construction
print("Test 1: Building Index...")
try:
    doc = Document(text="Apples are red. Bananas are yellow.")
    index = VectorStoreIndex.from_documents([doc])
    print("✅ P48 Passed: Index built successfully.")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# P49: Query Response Relevance
print("Test 2: Querying...")
engine = index.as_query_engine()
response = engine.query("What color are apples?")

if "red" in str(response).lower():
    print(f"✅ P49 Passed: Answer is relevant ({response}).")
else:
    print(f"❌ Failed: Answer irrelevant. Got: {response}")
    sys.exit(1)

print("\n🎉 Chapter 35 Complete! You have a new superpower.")
```

**Run it:** `python verify_llamaindex.py`

---


## Summary

**What you learned:**

1. ✅ **LlamaIndex Philosophy**: Data-first AI.
2. ✅ **VectorStoreIndex**: The Swiss Army Knife of indexing.
3. ✅ **Query Engine**: The interface for asking questions.
4. ✅ **Nodes**: How LlamaIndex sees data (chunks with relationships).
5. ✅ **Persistence**: Saving the index to disk.

**Key Takeaway**: For RAG applications, LlamaIndex is often faster to setup and cleaner to maintain than raw LangChain. Use LangChain for Agents, LlamaIndex for Knowledge.

**Skills unlocked**: 🎯
- Rapid RAG Prototyping
- Index Management
- Data Ingestion

**Looking ahead**: `VectorStoreIndex` is just the beginning. LlamaIndex has specialized engines for **Summarization** and **Comparing** documents. In **Chapter 36**, we will learn about **Query Engines & Response Synthesis**!

---

**Next**: [Chapter 36: Query Engines & Response Synthesis →](chapter-36-query-engines.md)
