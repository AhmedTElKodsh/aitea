# Chapter 14: Vector Stores with Chroma — Building the Brain's Library 🗄️

<!--
METADATA
Phase: Phase 2: Embeddings & Vectors
Time: 2.0 hours (60 minutes reading + 60 minutes hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation / Foundation
Prerequisites: Chapter 13 (Embeddings), Chapter 3 (Pydantic)
Builds Toward: Chapter 15 (Chunking), Chapter 17 (First RAG), Chapter 54 (Complete System)
Correctness Properties: [P21, P23]
Project Thread: CEVectorStore - connects to Ch 17, 54

NAVIGATION
→ Quick Reference: #quick-reference
→ Verification: #verification
→ What's Next: #whats-next

TEMPLATE VERSION: v2.1 (2026-01-17)
-->

---

## ☕ Coffee Shop Intro

Imagine you have a million books in a library, but no Dewey Decimal System, no alphabetization, and no computer catalog. 📚😱

If you want to find "books about structural safety," you have to pick up *every single book*, read it, and decide if it's relevant. That's what we call `O(N)` complexity, or in plain English: **Impossible at scale.**

**A Vector Store is the magical catalog.** ✨

It takes those embedding vectors we learned about in Chapter 13 and organizes them in a multi-dimensional space. When you ask a question, it doesn't scan everything. It instantly "teleports" to the right neighborhood in that space and hands you the 5 closest matches.

**By the end of this chapter**, you'll know how to:
- Set up **ChromaDB** (the open-source standard for local vector storage).
- Create **Collections** (like folders for your vectors).
- **Add** documents with metadata (Author, Date, Version).
- **Query** your database to find "The Top 3 most relevant paragraphs."

Let's build the library of the future! 🚀

---

## Prerequisites Check

We need to install ChromaDB. Note: It might require a C++ compiler on some systems, but the pre-built wheels usually work fine.

```bash
pip install chromadb
```

**You should feel comfortable with**:
- **Embeddings** (Chapter 13): You know what a vector is.
- **Dictionaries** (Python Basics): Vectors usually come with "Metadata" (dictionaries).

*Warning: Chroma creates files on your disk. Don't be surprised if you see a `chroma_db` folder appear!* 📂

---

## What You Already Know 🧩

We are upgrading our storage game:

<table>
<tr>
<th>Traditional Database (SQL)</th>
<th>Vector Database (Chroma)</th>
</tr>
<tr>
<td>Stores: Rows & Columns</td>
<td>Stores: Vectors & Metadata</td>
</tr>
<tr>
<td>Query: `WHERE title = 'Report'`</td>
<td>Query: `NEAR vector([0.1, 0.5...])`</td>
</tr>
<tr>
<td>Exact Match only</td>
<td>Semantic Match ("Close enough")</td>
</tr>
</table>

---

## Part 1: Setting Up Chroma 🛠️

Chroma is amazing because it can run **Ephemeral** (in RAM, disappears when you close Python) or **Persistent** (saves to disk).

### The "Hello World" of Vector Stores

```python
import chromadb

# 1. Initialize the Client (In-Memory for now)
client = chromadb.Client()

# 2. Create a Collection (Think of it like a SQL Table)
collection = client.create_collection(name="civil_engineering_docs")

# 3. Add Data (Chroma handles the embedding automatically by default!)
collection.add(
    documents=[
        "Concrete requires 28 days to reach full strength.",
        "Steel beams expand when heated.",
        "The project manager loves pizza."
    ],
    metadatas=[
        {"type": "material", "source": "handbook"},
        {"type": "material", "source": "handbook"},
        {"type": "personal", "source": "chat_log"}
    ],
    ids=["id1", "id2", "id3"]
)

# 4. Query
results = collection.query(
    query_texts=["How long for concrete to harden?"],
    n_results=1
)

print(results['documents'])
```

**Output**:
```
[['Concrete requires 28 days to reach full strength.']]
```

**Wait, what just happened?** 🤯
We didn't generate embeddings! Chroma uses a default model (`all-MiniLM-L6-v2`) if you don't provide one. It embedded your query, embedded the documents, compared them, and returned the winner. Magic.

---

### 🔬 Try This! (Hands-On Practice #1)

**Challenge**: Modify the code above to query for "Lunch options". What does it return?

<details>
<summary>✅ Solution</summary>

It returns: `[['The project manager loves pizza.']]`

Even though "Lunch" isn't in the text, "pizza" is semantically close!
</details>

---

## Part 2: Persistence (Saving Your Work) 💾

RAM is great for testing, but if we process 1,000 PDFs, we don't want to re-do it every time we restart the script.

```python
import chromadb
import os

# Create a folder for the DB
db_path = os.path.join(os.getcwd(), "chroma_db")

# Initialize Persistent Client
client = chromadb.PersistentClient(path=db_path)

# Get or Create the collection
collection = client.get_or_create_collection(name="persistent_docs")

print(f"Database saved at: {db_path}")
```

Now, if you run this script, add data, stop it, and run it again, your data is still there!

---

## Part 3: Using OpenAI Embeddings with Chroma 🧠

The built-in model is okay, but for our Civil Engineering system, we want the power of **OpenAI**.

We need to tell Chroma exactly how to use the OpenAI API.

```python
import chromadb.utils.embedding_functions as embedding_functions
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Create the Embedding Function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# 2. Pass it to the Collection
collection = client.get_or_create_collection(
    name="openai_collection",
    embedding_function=openai_ef
)

# Now when you .add() or .query(), it uses OpenAI automatically!
```

---

### 🔬 Try This! (Hands-On Practice #2)

**Challenge**: Create a persistent collection using OpenAI embeddings. Add two documents about "Bridges" and "Tunnels". Query for "Underground structures".

<details>
<summary>💡 Hint</summary>
"Underground structures" should match "Tunnels" much better than "Bridges".
</details>

---

## Part 4: Metadata Filtering (Precision Targeting) 🎯

Sometimes, semantic search isn't enough. You don't just want "Structural Reports"; you want "Structural Reports **from 2024**".

Chroma allows **Metadata Filtering** (like a SQL `WHERE` clause).

```python
results = collection.query(
    query_texts=["safety issues"],
    n_results=2,
    where={"source": "handbook"}  # <-- The Filter
)
```

**Common Filter Operators**:
- `$eq`: Equal to
- `$ne`: Not equal to
- `$gt` / `$lt`: Greater/Less than (good for dates!)
- `$in`: In a list of values

---

## Bringing It All Together: The Knowledge Keeper 📚

Let's build a class that manages our engineering knowledge base.

```python
# src/vector_store.py
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import os

class KnowledgeBase:
    def __init__(self, db_path="chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        
        self.ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        
        self.collection = self.client.get_or_create_collection(
            name="engineering_knowledge",
            embedding_function=self.ef
        )

    def add_document(self, doc_id: str, text: str, metadata: dict):
        self.collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata]
        )
        print(f"Saved: {doc_id}")

    def search(self, query: str, limit=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        return results['documents'][0], results['metadatas'][0]

# Usage
kb = KnowledgeBase()
kb.add_document("doc1", "Steel melts at 1370C", {"topic": "materials"})
docs, metas = kb.search("melting point of metal")
print(docs[0])  # "Steel melts at 1370C"
```

---

## Common Mistakes (Learn from Others!) 🚫

### Mistake #1: Forgetting to Persist
If you use `chromadb.Client()` (the default), your data is gone when the script ends. Always use `PersistentClient` for real apps.

### Mistake #2: ID Collisions
Chroma requires unique IDs for every chunk. If you add "doc1" twice, the second one overwrites the first.
**Fix**: Use UUIDs or structured IDs like `filename_chunk_index`.

### Mistake #3: Changing Models
If you fill a database using `all-MiniLM-L6-v2` and then try to query it using `OpenAI`, you will get garbage results. The vector dimensions won't match.
**Fix**: Pick a model and stick with it for the life of the collection.

---

## Quick Reference Card 🃏

| Method | Syntax | Purpose |
|--------|--------|---------|
| **Init** | `chromadb.PersistentClient(path="...")` | Load DB from disk |
| **Get** | `client.get_or_create_collection(...)` | Get a "table" |
| **Add** | `collection.add(ids=..., documents=...)` | Insert data |
| **Query** | `collection.query(query_texts=...)` | Semantic Search |
| **Delete** | `collection.delete(ids=...)` | Remove data |

---

## Verification

Let's verify your vector store implementation works correctly.

### Test Script

Create this file:

```python
# test_vector_store.py
"""
Automated verification script for Chapter 14
Tests: ChromaDB setup, CRUD operations, semantic search
"""

import chromadb
import os
import shutil

def test_persistent_client():
    """Test 1: Persistent client creates database"""
    try:
        # Clean up any existing test database
        test_path = "./test_chroma_db"
        if os.path.exists(test_path):
            shutil.rmtree(test_path)

        # Create persistent client
        client = chromadb.PersistentClient(path=test_path)

        # Verify directory was created
        assert os.path.exists(test_path), "Database directory should exist"

        # Cleanup
        shutil.rmtree(test_path)

        print("✅ PASS: Persistent client creates database")
        return True

    except Exception as e:
        print(f"❌ FAIL: Persistent client test failed: {e}")
        return False

def test_crud_operations():
    """Test 2: Create, Read, Update, Delete operations work"""
    try:
        # Use in-memory client for faster testing
        client = chromadb.Client()
        collection = client.create_collection(name="test_collection")

        # CREATE: Add documents
        collection.add(
            documents=["Document 1", "Document 2", "Document 3"],
            metadatas=[{"type": "A"}, {"type": "B"}, {"type": "A"}],
            ids=["id1", "id2", "id3"]
        )

        # READ: Query
        results = collection.query(
            query_texts=["Document 1"],
            n_results=1
        )

        assert len(results['documents'][0]) == 1, "Should return 1 document"
        assert "Document 1" in results['documents'][0][0], "Should match Document 1"

        # UPDATE: Upsert
        collection.upsert(
            ids=["id1"],
            documents=["Document 1 Updated"],
            metadatas=[{"type": "A", "updated": True}]
        )

        # DELETE: Remove
        collection.delete(ids=["id3"])

        # Verify count
        count = collection.count()
        assert count == 2, f"Should have 2 documents after delete, got {count}"

        print("✅ PASS: CRUD operations work correctly")
        return True

    except Exception as e:
        print(f"❌ FAIL: CRUD operations test failed: {e}")
        return False

def test_semantic_search():
    """Test 3: Semantic search finds related documents"""
    try:
        client = chromadb.Client()
        collection = client.create_collection(name="semantic_test")

        # Add documents
        collection.add(
            documents=[
                "The bridge has a structural issue.",
                "There is a crack in the concrete beam.",
                "I love eating pizza on Fridays."
            ],
            ids=["doc1", "doc2", "doc3"]
        )

        # Search for structural problems
        results = collection.query(
            query_texts=["Problems with the bridge structure"],
            n_results=2
        )

        # Top 2 results should be the engineering docs, not pizza
        top_docs = results['documents'][0]
        assert len(top_docs) == 2, "Should return 2 documents"

        # Check that pizza doc is not in top 2
        pizza_in_top_2 = any("pizza" in doc.lower() for doc in top_docs)
        assert not pizza_in_top_2, "Pizza document should not be in top 2 results"

        print("✅ PASS: Semantic search finds related documents")
        print(f"   Top results: {top_docs[:2]}")
        return True

    except Exception as e:
        print(f"❌ FAIL: Semantic search test failed: {e}")
        return False

def test_metadata_filtering():
    """Test 4: Metadata filtering works"""
    try:
        client = chromadb.Client()
        collection = client.create_collection(name="filter_test")

        # Add documents with metadata
        collection.add(
            documents=["Doc A1", "Doc B1", "Doc A2"],
            metadatas=[
                {"type": "A", "year": 2024},
                {"type": "B", "year": 2024},
                {"type": "A", "year": 2023}
            ],
            ids=["id1", "id2", "id3"]
        )

        # Query with metadata filter
        results = collection.query(
            query_texts=["Document"],
            n_results=10,
            where={"type": "A"}
        )

        # Should only return type A documents
        assert len(results['ids'][0]) == 2, f"Should return 2 type A docs, got {len(results['ids'][0])}"

        for metadata in results['metadatas'][0]:
            assert metadata['type'] == 'A', "All results should have type A"

        print("✅ PASS: Metadata filtering works")
        return True

    except Exception as e:
        print(f"❌ FAIL: Metadata filtering test failed: {e}")
        return False

def run_all_tests():
    """Run all verification tests"""
    print("="*60)
    print("Chapter 14 Verification Tests")
    print("="*60)

    tests = [
        ("Persistent Client", test_persistent_client),
        ("CRUD Operations", test_crud_operations),
        ("Semantic Search", test_semantic_search),
        ("Metadata Filtering", test_metadata_filtering)
    ]

    results = []
    for name, test_func in tests:
        print(f"\n[Test] {name}")
        results.append(test_func())

    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! You've mastered vector stores!")
        return True
    else:
        print("\n⚠️  Some tests failed. Review the concepts above.")
        return False

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

### Run the test:

```bash
python test_vector_store.py
```

### Expected output:

```
============================================================
Chapter 14 Verification Tests
============================================================

[Test] Persistent Client
✅ PASS: Persistent client creates database

[Test] CRUD Operations
✅ PASS: CRUD operations work correctly

[Test] Semantic Search
✅ PASS: Semantic search finds related documents
   Top results: ['The bridge has a structural issue.', 'There is a crack in the concrete beam.']

[Test] Metadata Filtering
✅ PASS: Metadata filtering works

============================================================
Results: 4/4 tests passed
============================================================

🎉 ALL TESTS PASSED! You've mastered vector stores!
```

---

## Assessment

**1. What is the difference between `Client` and `PersistentClient`?**
a) `Client` is faster.
b) `PersistentClient` saves data to disk; `Client` stores in RAM.
c) `PersistentClient` uses OpenAI.

**2. What happens if you don't provide an embedding function to Chroma?**
a) It crashes.
b) It uses a default, open-source model.
c) It sends the text to Google.

**3. Why do we need Metadata Filtering?**
a) To search by specific fields (like Date or Author) combined with meaning.
b) To make the search slower.
c) To encrypt the data.

<details>
<summary>💡 Answers</summary>
1. b
2. b
3. a
</details>

---

## What's Next?

You have a Brain (LLM) and a Memory (Chroma). But right now, we're feeding the memory whole sentences manually.

Real documents are **Huge**. A 50-page PDF doesn't fit in one vector. We need to cut it up into bite-sized pieces.

In **Chapter 15: Chunking Strategies**, you'll learn the art of splitting text so that the AI understands context without getting overwhelmed. 

Let's get chopping! ✂️

---

## Summary

**What you learned:**

1. ✅ **ChromaDB basics** — Open-source vector database for local/cloud storage
2. ✅ **Persistent storage** — PersistentClient saves data to disk (vs in-memory Client)
3. ✅ **Collections** — Organize vectors like SQL tables
4. ✅ **CRUD operations** — Add, query, update, delete documents with vectors
5. ✅ **Metadata filtering** — Combine semantic search with exact filters (`where` clause)
6. ✅ **Embedding functions** — Use OpenAI or local models for vector generation
7. ✅ **Production patterns** — KnowledgeBase class manages engineering knowledge

**Key takeaway:** Vector databases transform semantic search from O(N) (scan everything) to near-instant retrieval using multi-dimensional indexing. ChromaDB is the "catalog" that makes finding relevant information effortless, even with millions of documents! 🗄️

**Skills unlocked:** 🎯
- Set up persistent vector storage with ChromaDB
- Perform CRUD operations on vector collections
- Implement semantic search with metadata filtering
- Integrate OpenAI embeddings with vector stores

**Looking ahead:** In the next chapters, you'll learn how to split large documents into chunks (Chapter 15), load various document types (Chapter 16), and build your first complete RAG system (Chapter 17) that combines everything you've learned!

---

**Next**: [Chapter 15: Chunking Strategies →](chapter-15-chunking-strategies.md)

*Great job making it through Chapter 14! You now have a persistent memory for your AI!* 💪
