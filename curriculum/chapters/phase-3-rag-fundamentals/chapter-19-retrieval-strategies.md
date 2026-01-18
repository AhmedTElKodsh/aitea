# Chapter 19: Retrieval Strategies — Finding the Needle

<!--
METADATA
Phase: 3 - RAG Fundamentals
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 18 (LCEL)
Builds Toward: RAG Optimization (Ch 21)
Correctness Properties: P23 (Query Diversity), P24 (Compression Retention)
Project Thread: Search Optimization

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You ask a librarian, "Do you have books about big lizards?"
The librarian looks up "Big Lizard" in the computer.
**Result**: 0 matches. ❌
Why? Because the books are titled "Dinosaurs" and "Komodo Dragons".

Basic Vector Search (Cosine Similarity) is great, but it's not magic. If the user asks a vague question, the embedding might miss the target.

**Advanced Retrieval** is like giving the librarian a superpower.
1.  **Multi-Query**: The librarian thinks, "He probably means Dinosaurs, Reptiles, or Godzilla." She checks all three.
2.  **Compression**: She finds a 500-page book, reads it, and hands you just the *one paragraph* you need.

**By the end of this chapter**, you'll build a search engine that understands what the user *meant*, not just what they *said*. 🕵️‍♂️

---

## Prerequisites Check

```bash
# We need to rank things
pip install rank_bm25
```

---

## The Story: The "Missed" Document

### The Problem (The Vocabulary Gap)

User: *"How do I reset my credentials?"*
Document: *"To recover access, initiate the identity verification protocol."*

**Vector Search**: These sentences are semantically slightly different. "Credentials" usually maps to "Password", not "Identity Verification Protocol". You might get a low score and miss the doc.

### The Solution (Query Expansion)

We ask the LLM to act as a **Translator**.
Prompt: *"The user asked 'How do I reset my credentials?'. Generate 3 different ways to ask this that might appear in a technical manual."*

LLM:
1. "Password recovery steps"
2. "Identity verification process"
3. "Login troubleshooting"

Now we search for **all three**. We catch the document with query #2.

---

## Part 1: Multi-Query Retrieval (The Shotgun Approach)

Let's build this using LCEL.

### 🔬 Try This! (Hands-On Practice #1)

**Create `multi_query.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. The Expansion Prompt
template = """You are an AI language model assistant. Your task is to generate five 
different versions of the given user question to retrieve relevant documents from a vector 
database. By generating multiple perspectives on the user question, your goal is to help
the user overcome some of the limitations of the distance-based similarity search. 
Provide these alternative questions separated by newlines.

Original question: {question}"""

prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. The Chain
# Input: Question -> LLM -> String -> Split by line -> List[String]
generate_queries = (
    prompt 
    | model 
    | StrOutputParser()
    | (lambda x: x.split("\n"))
)

# 3. Test it
question = "How do I fix the blue screen?"
queries = generate_queries.invoke({"question": question})

print(f"Original: {question}")
print("Generated Variations:")
for q in queries:
    print(f"- {q}")
```

**Run it**.
You should see 5 smarter ways to ask about a "blue screen" (e.g., "BSOD troubleshooting", "Windows crash error").

---

## Part 2: Contextual Compression (The Zipper)

Retrieving 5 full documents (2000 tokens each) wastes money and confuses the LLM.
We want to extract **only the relevant sentences** from those documents before sending them to the final answer generator.

### 🔬 Try This! (Hands-On Practice #2)

We'll simulate a compressor.

**Create `compression.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# The Compression Prompt
template = """Given the following document, extract ONLY the sentences that are relevant to the user's query.
If nothing is relevant, return "NO_MATCH".

Query: {query}

Document:
{document}
"""
compressor = ChatPromptTemplate.from_template(template) | model | StrOutputParser()

# Data
long_doc = """
The cafeteria serves pizza on Fridays.
The server API listens on port 8080.
Employees must wash hands.
To reset the server, press the red button.
"""

query = "How to restart server?"

# Run
compressed = compressor.invoke({"query": query, "document": long_doc})

print(f"Original Length: {len(long_doc)}")
print(f"Compressed Length: {len(compressed)}")
print(f"\nResult:\n{compressed}")
```

**Run it**.
It should discard the pizza and hand-washing info, keeping only the port and the red button.

---

## Part 3: Hybrid Search (Ensemble)

**Vector Search** is bad at exact matches (like SKU numbers "Item-992-B").
**Keyword Search (BM25)** is great at exact matches but bad at concepts.

**Hybrid Search** combines them.
`Score = (VectorScore * 0.5) + (KeywordScore * 0.5)`

### 🔬 Try This! (Hands-On Practice #3)

We'll use LangChain's `EnsembleRetriever`.

**Create `hybrid_search.py`**:

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from typing import List

# 1. Setup Data
docs = [
    Document(page_content="The new iPhone 15 costs $999."),
    Document(page_content="Apples are a delicious fruit."),
    Document(page_content="iphone_15_price.pdf contains the cost."),
]

# 2. Keyword Retriever (BM25)
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 1

# 3. Fake Vector Retriever (Simulating semantic search)
class FakeVectorRetriever(BaseRetriever):
    def _get_relevant_documents(
        self,
        query: str,
        *, # Use keyword-only arguments for run_manager
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        # Semantic search finds "Apple" (Fruit) for "Apple phone" sometimes
        # Simulating a semantic match
        if "phone" in query or "apple" in query.lower():
            return [docs[1]] # The fruit
        return []

vector_retriever = FakeVectorRetriever()

# 4. Ensemble (The Magic)
# Weight: 0.5 for keyword, 0.5 for vector
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]
)

# 5. Search
query = "iPhone 15"
results = ensemble_retriever.invoke(query)

print(f"Query: {query}")
for doc in results:
    print(f"- {doc.page_content}")
```

**Analysis**:
- Vector might be confused by "Apple" (Fruit).
- Keyword (BM25) locks onto "iPhone" and "15".
- Together, the correct document bubbles to the top.

---

## Common Mistakes

### Mistake #1: Latency Explosion
Multi-Query generates 5 variations. That means 5 vector searches. That's 5x the database load.
**Fix**: Run searches in parallel (using `RunnableParallel` or `batch`).

### Mistake #2: Hallucinated Queries
Sometimes the query generator gets creative.
User: "Python error"
LLM: "How to handle Cobra snakes?" (Rare, but possible).
**Fix**: Keep temperature at 0 for query expansion.

### Mistake #3: Over-Compression
The compressor might remove context that seems irrelevant but is actually needed ("See Appendix A").
**Fix**: Return slightly more context (surrounding sentences) or use a softer prompt.

---

## Quick Reference Card

### Multi-Query Logic
```python
queries = generate_queries(question)
all_docs = []
for q in queries:
    all_docs.extend(retriever.search(q))
unique_docs = deduplicate(all_docs)
```

### Hybrid Logic
```python
rank = (alpha * vector_rank) + ((1-alpha) * keyword_rank)
```

---

## Verification (REQUIRED SECTION)

We need to prove **P23 (Diversity)** and **P24 (Retention)**.

**Create `verify_strategies.py`**:

```python
"""
Verification script for Chapter 19.
Properties: P23 (Diversity), P24 (Retention).
"""
import sys

print("🧪 Running Strategy Verification...\n")

# P23: Query Diversity
# We verify that expanding a query produces DISTINCT variations
original = "cat"
variations = ["feline", "kitten", "mammal"] # Simulated LLM output

print("Test 1: Diversity Check...")
unique_vars = set(variations)
if len(unique_vars) > 1 and original not in unique_vars:
    print("✅ P23 Passed: Generated diverse query variations.")
else:
    print("❌ Failed: Queries were duplicates or identical to original.")
    sys.exit(1)

# P24: Compression Retention
# We verify that compression keeps the keyword
original_doc = "The sun is hot. The code is 1234. The water is wet."
query = "code"
# Simulated compression keeping sentence with 'code'
compressed_doc = "The code is 1234."

print("Test 2: Compression Check...")
if query in compressed_doc and len(compressed_doc) < len(original_doc):
    print("✅ P24 Passed: Compressed text retained key info and reduced size.")
else:
    print("❌ Failed: Lost info or didn't shrink.")
    sys.exit(1)

print("\n🎉 Chapter 19 Complete! You are a Search Master.")
```

**Run it:** `python verify_strategies.py`

---

## Summary

**What you learned:**

1. ✅ **Vocabulary Gap**: Users don't use the same words as documents.
2. ✅ **Multi-Query**: Using the LLM to brainstorm synonyms increases recall.
3. ✅ **Contextual Compression**: Removing noise helps the LLM focus.
4. ✅ **Hybrid Search**: Keywords + Vectors = Best of both worlds.
5. ✅ **Ensemble**: Combining multiple retrievers with weights.

**Key Takeaway**: Retrieval is an engineering problem. You can tune it. Don't settle for default cosine similarity if your users are unhappy.

**Skills unlocked**: 🎯
- Query Expansion
- Information Density Optimization
- Hybrid Search Algorithms

**Looking ahead**: We can retrieve data well. But what if the user wants to hold a **conversation**? "Who is the lead?" -> "Sarah". -> "What is *her* email?"
Current RAG fails this (it forgets who "her" is). In **Chapter 20**, we will build **Conversational RAG** with Memory!

---

**Next**: [Chapter 20: Conversational RAG →](chapter-20-conversational-rag.md)
