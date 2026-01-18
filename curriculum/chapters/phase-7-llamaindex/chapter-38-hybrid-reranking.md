# Chapter 38: Hybrid Search & Reranking — The Perfect Match

<!--
METADATA
Phase: 7 - LlamaIndex
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 35 (LlamaIndex)
Builds Toward: Production Deployment (Ch 40)
Correctness Properties: P23 (Query Diversity), P54 (Reranking Monotonicity)
Project Thread: Search Optimization

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're looking for "The Rock".
**Vector Search** sees "Rock" and thinks "Stone, Mountain, Mineral". 🪨
**Keyword Search** sees "The Rock" and matches "Dwayne Johnson" because that phrase appears exactly in the text. 💪

Neither is perfect.
- **Vectors** are great for concepts ("Action movies").
- **Keywords** are great for exact matches ("Part Number XJ-900").

**Hybrid Search** combines them. It uses both methods and merges the results.
**Reranking** is the cherry on top. It takes the top 50 results and uses a super-smart (but slow) model to carefully re-read and rank them, ensuring the absolute best document is #1.

**By the end of this chapter**, you will build a search pipeline that captures *everything*—concepts and keywords—and ranks them with precision. 🎯

---

## Prerequisites Check

We need the reranking library.

```bash
pip install llama-index-postprocessor-colbert-rerank
# Or just use standard:
pip install llama-index-embeddings-huggingface
```

---

## The Story: The "SKU" Problem

### The Problem (Exact Matches)

User: *"Where is part XJ-900?"
Vector Search: Finds documents about "X-rays" and "90s music" because vectors are fuzzy.
Result: The user gets unrelated junk.

### The Solution (Hybrid + Rerank)

1.  **Hybrid**: Run BM25 (Keywords) to catch "XJ-900". Run Vector to catch "Spare Parts".
2.  **Merge**: Combine lists. (Now we have 50 items).
3.  **Rerank**: Use a Cross-Encoder to score each of the 50 items against the query "Where is part XJ-900?".
4.  **Result**: The manual for XJ-900 bubbles to the top.

---

## Part 1: Hybrid Search

LlamaIndex supports hybrid search if the underlying Vector DB supports it (like Chroma).

### 🔬 Try This! (Hands-On Practice #1)

**Create `hybrid_test.py`**:

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.core import Document

# 1. Setup Chroma with Hybrid support
# Note: Chroma enables simple hybrid by default in newer versions, 
# or we simulate it by combining retrievers. 
# For LlamaIndex + Chroma, let's use the standard "hybrid" mode if available
# or stick to the "Fusion" concept.

# Let's use a simpler approach for this demo: FusionRetriever
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.retrievers import VectorIndexRetriever

# Data
docs = [
    Document(text="The XJ-900 is a high-performance engine."),
    Document(text="Bananas are rich in potassium."),
    Document(text="Engine maintenance requires skill."),
]
index = VectorStoreIndex.from_documents(docs)

# 2. Vector Retriever
vector_retriever = index.as_retriever(similarity_top_k=2)

# 3. BM25 Retriever (Keyword)
from llama_index.retrievers.bm25 import BM25Retriever
bm25_retriever = BM25Retriever.from_defaults(nodes=index.docstore.docs.values(), similarity_top_k=2)

# 4. Fusion (Hybrid)
retriever = QueryFusionRetriever(
    [vector_retriever, bm25_retriever],
    similarity_top_k=2,
    num_queries=1, # No query expansion for now
    mode="reciprocal_rerank",
    use_async=False
)

# 5. Search
nodes = retriever.retrieve("XJ-900")
print(f"Top Result: {nodes[0].node.get_text()}")
```

**Run it**.
It should confidently pick XJ-900.

---

## Part 2: Reranking (The Judge)

Now let's add a Reranker. This is a "Post-Processor" in LlamaIndex.
We will use `SentenceTransformerRerank` (local) or `Colbert`. Let's use `SentenceTransformer` as it's standard and easy.

### 🔬 Try This! (Hands-On Practice #2)

**Create `rerank_test.py`**:

```python
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.postprocessor import SentenceTransformerRerank

# Data with subtle differences
docs = [
    Document(text="Python is a snake."),
    Document(text="Python is a programming language."),
    Document(text="Pythons live in the jungle.")
]
index = VectorStoreIndex.from_documents(docs)

# 1. Setup Reranker
# Uses a cross-encoder model trained to score relevance
reranker = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-6-v2", 
    top_n=1
)

# 2. Query with Reranking
# First, retrieve top 3 (Vectors). Then Rerank to top 1.
engine = index.as_query_engine(
    similarity_top_k=3,
    node_postprocessors=[reranker]
)

response = engine.query("How do I write code?")
print(f"Answer: {response}")
print(f"Source: {response.source_nodes[0].node.get_text()}")
```

**Run it**.
Vectors might think "Python is a snake" is similar to "code" (low similarity).
But the Reranker reads "How do I write code?" vs "Python is a snake" and gives it a low score.
It reads "How do I write code?" vs "Python is a programming language" and gives it a high score.
The correct doc wins.

---

## Common Mistakes

### Mistake #1: Reranking EVERYTHING
Rerankers are **slow**. Cross-encoders run `O(N)` BERT passes.
Do NOT rerank 1,000 documents.
**Fix**: Retrieve top 50 with Vectors -> Rerank top 50 -> Keep top 5.

### Mistake #2: Ignoring Score Threshold
Sometimes *none* of the documents are relevant. The Reranker gives low scores (e.g., 0.1).
**Fix**: Filter out nodes with `score < 0.5`.

### Mistake #3: Missing Dependencies
BM25 and Rerankers often need extra packages (`rank_bm25`, `torch`). Watch your imports.

---

## Quick Reference Card

### Reranking Pipeline

```python
reranker = SentenceTransformerRerank(model="...", top_n=5)
engine = index.as_query_engine(
    similarity_top_k=20, # Fetch broad
    node_postprocessors=[reranker] # Filter deep
)
```

---

## Verification (REQUIRED SECTION)

We need to verify **P54 (Monotonicity)**. The scores returned by the reranker must be sorted descending.

**Create `verify_rerank.py`**:

```python
"""
Verification script for Chapter 38.
Property P54: Reranking Monotonicity.
"""
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.postprocessor import SentenceTransformerRerank
import sys

print("🧪 Running Reranking Verification...\n")

# Setup
docs = [
    Document(text="A"),
    Document(text="B"),
    Document(text="C"),
    Document(text="D")
]
index = VectorStoreIndex.from_documents(docs)

# Reranker
reranker = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-6-v2", 
    top_n=4
)

# Retrieve nodes directly (bypass query engine to inspect scores)
retriever = index.as_retriever(similarity_top_k=4)
nodes = retriever.retrieve("A") # Should match A best

# Apply Reranker
reranked_nodes = reranker.postprocess_nodes(nodes, query_str="A")

# P54: Monotonicity
print("Test 1: Score Order...")
scores = [n.score for n in reranked_nodes]
print(f"Scores: {scores}")

# Check if sorted descending
is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

if is_sorted:
    print("✅ P54 Passed: Results are sorted by relevance.")
else:
    print("❌ Failed: Reranker did not sort results.")
    sys.exit(1)

print("\n🎉 Chapter 38 Complete! Your search is optimized.")
```

**Run it:** `python verify_rerank.py`

---

## Summary

**What you learned:**

1. ✅ **The Limits of Vectors**: They miss exact keywords.
2. ✅ **Hybrid Search**: Combining BM25 and Vectors increases recall.
3. ✅ **Cross-Encoders**: Models that compare Query+Doc directly.
4. ✅ **Two-Stage Retrieval**: Retrieve fast (Vectors), Rank slow (Cross-Encoder).
5. ✅ **LlamaIndex Pipelines**: Adding post-processors easily.

**Key Takeaway**: Search is a funnel. Wide at the top (Hybrid), narrow at the bottom (Rerank).

**Skills unlocked**: 🎯
- Information Retrieval (IR)
- Search Relevance Tuning
- Pipeline Optimization

**Looking ahead**: We have finished **Phase 7: LlamaIndex**. We have mastered Data and Indexing.
In **Phase 8: Production**, we stop playing in notebooks. We will learn **Testing** (Property-Based), **Evaluation** (LangSmith), and **Deployment** patterns. The training wheels come off!

---

**Next**: [Phase 8: Production (Chapter 39) →](../phase-8-production/chapter-39-hypothesis-testing.md)
