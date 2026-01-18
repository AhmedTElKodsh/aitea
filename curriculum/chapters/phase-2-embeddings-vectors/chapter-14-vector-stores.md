# Chapter 14: Vector Stores with Chroma — The Brain's Filing Cabinet

<!--
METADATA
Phase: 2 - Embeddings & Vectors
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 13 (Embeddings)
Builds Toward: RAG (Ch 17), Long-Term Memory
Correctness Properties: P13 (Retrieval Relevance), P14 (Persistence)
Project Thread: Knowledge Base

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You have a super-smart librarian (The Embedding Model).
She reads a book, understands it instantly, and... throws it in a pile on the floor. 📚
Next time you ask a question, she has to pick up *every single book* from the floor and re-read it to find the answer.

This is what we did in Chapter 13. We calculated embeddings, used them once, and threw them away. That's slow and expensive.

We need a **Filing Cabinet**.
A place to store the embeddings so we can find them instantly later.
This is a **Vector Database**. We're going to use **ChromaDB**—it's free, runs on your laptop, and is surprisingly powerful.

**By the end of this chapter**, you'll have a persistent database that "remembers" information forever. 🧠

---

## Prerequisites Check

```bash
pip install chromadb
```

*Note: If you are on Windows and get errors, you might need to install C++ Build Tools. Chroma usually includes binaries, though.*

---

## The Story: The "Amnesia" Problem

### The Problem (Recalculating)

In Chapter 13, our script calculated `get_embedding("Interstellar")` every time we ran it.
If you have 10,000 documents:
1. It costs ~$1.00 per run (OpenAI).
2. It takes 5 minutes to generate them.
3. Your app feels sluggish.

### The Solution (Vector Store)

We calculate the embedding **once**.
We save it to disk (`./chroma_db`).
When the user asks a question, we only calculate the embedding for the *question* (1 item), then instantly look up the nearest match in the database (microseconds).

---

## Part 1: Your First Collection

In SQL, you have Tables. In Vector DBs, you have **Collections**.

### 🔬 Try This! (Hands-On Practice #1)

Let's create an in-memory database (disappears when script ends).

**Create `test_chroma.py`**:

```python
import chromadb

# 1. Initialize Client (In-Memory)
client = chromadb.Client()

# 2. Create Collection
collection = client.create_collection(name="my_movies")

# 3. Add Documents
# Chroma handles the embedding automatically (using a built-in mini-model)!
print("Adding documents...")
collection.add(
    documents=[
        "Interstellar is about space travel and time dilation.",
        "The Godfather is a mafia crime drama.",
        "Toy Story is an animated movie about toys coming to life."
    ],
    metadatas=[
        {"genre": "sci-fi", "year": 2014},
        {"genre": "crime", "year": 1972},
        {"genre": "animation", "year": 1995}
    ],
    ids=["id1", "id2", "id3"]
)

# 4. Query
print("\nQuerying: 'films about the universe'")
results = collection.query(
    query_texts=["films about the universe"],
    n_results=1
)

print(f"Top Match: {results['documents'][0][0]}")
```

**Run it**.
It should find "Interstellar". You didn't even have to write embedding code! Chroma did it for you.

---

## Part 2: Persistence (Saving to Disk)

In-memory is great for testing, but we want **Long-Term Memory**.

### 🔬 Try This! (Hands-On Practice #2)

Let's make it permanent.

**Create `persistent_db.py`**:

```python
import chromadb
import os

# 1. Persistent Client
# This creates a folder './chroma_db'
client = chromadb.PersistentClient(path="./chroma_db")

# 2. Get or Create Collection
# get_or_create means: "Load it if exists, else make new one"
collection = client.get_or_create_collection(name="knowledge_base")

# 3. Add Data (Only if empty)
if collection.count() == 0:
    print("Database empty. Adding info...")
    collection.add(
        documents=["Python is a programming language.", "Chroma is a vector DB."],
        ids=["doc1", "doc2"]
    )
else:
    print(f"Database loaded! Contains {collection.count()} docs.")

# 4. Query
results = collection.query(query_texts=["coding tools"], n_results=1)
print(f"Result: {results['documents'][0][0]}")
```

**Run it TWICE.**
- **Run 1**: Prints "Database empty. Adding info..."
- **Run 2**: Prints "Database loaded! Contains 2 docs."

You just gave your AI persistent memory! 💾

---

## Part 3: Metadata Filtering (The Scalpel)

Semantic search is fuzzy. Sometimes you want precise filtering.
"Find me contracts about 'Software' (Semantic) but ONLY from '2024' (Filter)."

### 🔬 Try This! (Hands-On Practice #3)

**Create `filtering.py`**:

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("filtered_search")

collection.add(
    documents=[
        "Contract A: Consulting services.",
        "Contract B: Consulting services.",
        "Contract C: Web Development."
    ],
    metadatas=[
        {"year": 2023, "status": "signed"},
        {"year": 2024, "status": "draft"},
        {"year": 2024, "status": "signed"}
    ],
    ids=["1", "2", "3"]
)

print("--- Query: 'Consulting' ---")
# Normal search
res = collection.query(query_texts=["Consulting"], n_results=3)
print(f"Found: {res['ids'][0]}") # Should be ['1', '2']

print("\n--- Query: 'Consulting' + Filter (Year=2024) ---")
# Filtered search
res = collection.query(
    query_texts=["Consulting"],
    where={"year": 2024}, # <--- THE FILTER
    n_results=3
)
print(f"Found: {res['ids'][0]}") # Should ONLY be ['2']
```

**Why is this powerful?**
You can filter by User ID (`{"user_id": "123"}`) to ensure users only search *their own* documents.
Security + Intelligence. 🔒

---

## Bringing It All Together: The Knowledge Base Manager

Let's build a clean class to manage this.

**Create `shared/infrastructure/vector_store.py`**:

```python
import chromadb
from typing import List, Dict

class VectorStore:
    def __init__(self, path: str = "./chroma_db", collection_name: str = "default"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_document(self, doc_id: str, text: str, metadata: Dict = None):
        if metadata is None:
            metadata = {}
        self.collection.add(
            documents=[text],
            ids=[doc_id],
            metadatas=[metadata]
        )

    def search(self, query: str, limit: int = 3) -> List[str]:
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        return results["documents"][0]
    
    def count(self):
        return self.collection.count()
```

---

## Common Mistakes

### Mistake #1: Re-adding Duplicate IDs
Chroma requires unique IDs. If you try to add `id="doc1"` twice, it might error or overwrite (depending on version).
**Fix**: Use `collection.get(ids=["doc1"])` to check existence, or use unique IDs (like UUIDs or Hashes).

### Mistake #2: Forgetting to Persist
Using `chromadb.Client()` (in-memory) instead of `PersistentClient` means data vanishes when the script stops. Great for tests, bad for apps.

### Mistake #3: Ignoring Distances
`results['distances']` tells you *how* similar the match is.
- Distance 0.1 = Very close.
- Distance 1.5 = Not really relevant.
You should filter out results with high distance (low relevance) to avoid hallucinations.

---

## Quick Reference Card

### Chroma Basics

```python
client = chromadb.PersistentClient(path="./db")
col = client.get_or_create_collection("docs")

# Add
col.add(documents=["text"], metadatas=[{"k":"v"}], ids=["1"])

# Query
res = col.query(query_texts=["q"], n_results=2)

# Delete
col.delete(ids=["1"])
```

---

## Verification (REQUIRED SECTION)

We need to prove **P14 (Persistence)** and **P13 (Relevance)**.

**Create `verify_chroma.py`**:

```python
"""
Verification script for Chapter 14.
"""
import chromadb
import shutil
import os

print("🧪 Running Vector Store Verification...\n")

DB_PATH = "./test_chroma_db"

# Cleanup previous runs
if os.path.exists(DB_PATH):
    shutil.rmtree(DB_PATH)

# Test P14: Persistence
print("Test 1: Persistence...")
# Open, Add, Close
client1 = chromadb.PersistentClient(path=DB_PATH)
col1 = client1.get_or_create_collection("test")
col1.add(documents=["Secret Data"], ids=["1"])
del client1 # Force close

# Re-open
client2 = chromadb.PersistentClient(path=DB_PATH)
col2 = client2.get_collection("test")
cnt = col2.count()

if cnt == 1:
    print("✅ P14 Passed: Data persisted across sessions.")
else:
    print(f"❌ Failed: Expected 1 doc, got {cnt}")
    exit(1)

# Test P13: Relevance
print("Test 2: Relevance Search...")
col2.add(documents=["Banana", "Computer"], ids=["2", "3"])
# Search for 'Fruit' -> Should match Banana (id 2)
res = col2.query(query_texts=["Fruit"], n_results=1)
top_doc = res["documents"][0][0]

if "Banana" in top_doc:
    print(f"✅ P13 Passed: Semantically relevant match found ({top_doc}).")
else:
    print(f"❌ Failed: Expected Banana, got {top_doc}")
    exit(1)

# Cleanup
shutil.rmtree(DB_PATH)
print("\n🎉 Chapter 14 Complete! Your knowledge is now permanent.")
```

**Run it:** `python verify_chroma.py`

---

## Summary

**What you learned:**

1. ✅ **Vector Databases**: Specialized storage for embeddings.
2. ✅ **Collections**: Organizing data (like tables).
3. ✅ **Persistence**: Saving intelligence to disk.
4. ✅ **Metadata**: Filtering by date, user, or category.
5. ✅ **Hybrid Power**: Combining semantic search ("about contracts") with exact filters ("year=2024").

**Key Takeaway**: You now have a **Knowledge Base**. You can feed it PDFs, text files, or documentation, and retrieve exactly what you need in milliseconds.

**Skills unlocked**: 🎯
- Database Engineering (Vector)
- Semantic Indexing
- Search Optimization

**Looking ahead**: We can store text. But real-world documents are huge. You can't feed a 100-page PDF into an embedding model in one piece. In **Chapter 15**, we will learn **Chunking Strategies** to slice data into digestable pieces!

---

**Next**: [Chapter 15: Chunking Strategies →](chapter-15-chunking-strategies.md)

