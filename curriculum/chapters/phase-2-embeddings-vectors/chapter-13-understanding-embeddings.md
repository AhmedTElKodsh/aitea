# Chapter 13: Understanding Embeddings — The GPS of Meaning

<!--
METADATA
Phase: 2 - Embeddings & Vectors
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 8 (Client)
Builds Toward: RAG (Ch 17), Vector Stores (Ch 14)
Correctness Properties: P11 (Dimensions), P12 (Symmetry)
Project Thread: Semantic Search

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're organizing a library.
You have a book titled *"The Art of Canine Care"*.
A user asks: *"Do you have anything about puppies?"*

**Keyword Search (The Old Way)**: Looks for the word "puppy".
Result: **No match**. (The book says "Canine", not "Puppy"). ❌

**Semantic Search (The New Way)**: Understands that "Canine" and "Puppy" are basically the same thing.
Result: **Match!** ✅

How? **Embeddings**.
Embeddings translate text into lists of numbers (Vectors). In this number world, "Dog" is mathematically close to "Puppy", but far from "Toaster".

Think of it like GPS coordinates for meaning.
**By the end of this chapter**, you will build a search engine that "understands" concepts, not just keywords. 🧠

---

## Prerequisites Check

We need two new libraries for math and local models.

```bash
pip install numpy sentence-transformers scikit-learn
```

---

## The Story: The "Smart" Search

### The Problem (Rigid Keywords)

You built a FAQ bot.
FAQ: "How to reset password."
User: "I forgot my login code."
Bot: "Sorry, I don't know that." (Because "login code" != "password").

### The Solution (Vector Space)

We convert sentences into **Vectors** (lists of floats).
`[0.1, 0.5, -0.2, ...]`

If we plot these on a graph:
- "Password" is at (10, 10).
- "Login code" is at (10.1, 9.9).
- "Banana" is at (-50, -50).

We just measure the distance. Small distance = Similar meaning.

---

## Part 1: Generating OpenAI Embeddings

OpenAI's `text-embedding-3-small` model is the industry standard. It turns text into a vector of **1,536 numbers**.

### 🔬 Try This! (Hands-On Practice #1)

Let's see what a "thought" looks like in numbers.

**Create `generate_embedding.py`**:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# 1. Get embedding
vector = get_embedding("Apple")

# 2. Inspect it
print(f"Text: 'Apple'")
print(f"Dimensions: {len(vector)}") # Should be 1536
print(f"First 5 numbers: {vector[:5]}")
```

**Run it**. You'll see a list of floats. That list *is* the meaning of "Apple" to the AI.

---

## Part 2: Local Embeddings (Free & Fast)

You don't always need OpenAI. For simple tasks, local models like `all-MiniLM-L6-v2` run on your laptop for free.

### 🔬 Try This! (Hands-On Practice #2)

Let's use `sentence-transformers`.

**Create `local_embedding.py`**:

```python
from sentence_transformers import SentenceTransformer

# Load a small, fast model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode
text = "The quick brown fox"
vector = model.encode(text)

print(f"Model: all-MiniLM-L6-v2")
print(f"Dimensions: {len(vector)}") # Should be 384
print(f"First 5: {vector[:5]}")
```

**Why distinct dimensions?**
- OpenAI: 1536 dimensions (More detail, costs money).
- MiniLM: 384 dimensions (Less detail, free/fast).
**Rule**: You cannot compare vectors from different models!

---

## Part 3: Cosine Similarity (The Ruler)

How do we measure distance?
**Euclidean Distance** (ruler) works, but **Cosine Similarity** (angle) is better for text.
- **1.0**: Identical meaning.
- **0.0**: Unrelated.
- **-1.0**: Opposite meaning.

### 🔬 Try This! (Hands-On Practice #3)

Let's build a semantic calculator.

**Create `similarity_test.py`**:

```python
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def get_embedding(text):
    return client.embeddings.create(input=text, model="text-embedding-3-small").data[0].embedding

def cosine_similarity(v1, v2):
    # Math: (A . B) / (|A| * |B|)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# 1. Get vectors
vec_apple = get_embedding("Apple")
vec_iphone = get_embedding("iPhone")
vec_fruit = get_embedding("Fruit")
vec_dog = get_embedding("Dog")

# 2. Compare
print(f"Apple vs Fruit:  {cosine_similarity(vec_apple, vec_fruit):.4f}")
print(f"Apple vs iPhone: {cosine_similarity(vec_apple, vec_iphone):.4f}")
print(f"Apple vs Dog:    {cosine_similarity(vec_apple, vec_dog):.4f}")
```

**Run it**.
Expected Logic:
- Apple vs Fruit: High (~0.6 - 0.7)
- Apple vs iPhone: Medium-High (Context dependent, maybe 0.4 - 0.5)
- Apple vs Dog: Low (< 0.3)

*Note: In high-dimensional space, "Low" is often anything below 0.2 or 0.3. It rarely hits 0.0.*

---

## Bringing It All Together: The Search Engine

Let's build a mini-search engine for our movie database.

**Create `mini_search.py`**:

```python
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def get_embedding(text):
    return client.embeddings.create(input=text, model="text-embedding-3-small").data[0].embedding

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# Database
documents = [
    "The movie 'Interstellar' features space travel and black holes.",
    "A romantic comedy about a wedding in Greece.",
    "A documentary on the history of World War II.",
    "How to bake a perfect chocolate cake."
]

# Pre-compute embeddings (Indexing)
print("Indexing documents...")
doc_vectors = [get_embedding(doc) for doc in documents]

# Search
query = "films about the universe"
print(f"\nQuery: '{query}'")
query_vector = get_embedding(query)

# Find Best Match
scores = []
for doc_vec in doc_vectors:
    scores.append(cosine_similarity(query_vector, doc_vec))

best_idx = np.argmax(scores)
print(f"Best Match ({scores[best_idx]:.4f}):")
print(f"-> {documents[best_idx]}")
```

**Run it**.
It should find "Interstellar" even though the word "universe" isn't in the text! "Space" and "Universe" are semantically close. 🌌

---

## Common Mistakes

### Mistake #1: Mixing Models
Comparing an OpenAI vector to a HuggingFace vector yields garbage.
**Fix**: Stick to one model for your entire database.

### Mistake #2: Re-embedding constantly
Embeddings cost money/time.
**Fix**: Generate them once, save them (Database/File), and reuse them. We'll learn **Vector Stores** in Chapter 14 to handle this.

### Mistake #3: Ignoring Normals
Cosine similarity requires normalized vectors. OpenAI embeddings usually come normalized, but local ones might not. Using `np.linalg.norm` in the denominator handles this safely.

---

## Quick Reference Card

### OpenAI Embeddings
```python
resp = client.embeddings.create(input="text", model="text-embedding-3-small")
vec = resp.data[0].embedding # List[float]
```

### Local Embeddings
```python
model = SentenceTransformer("all-MiniLM-L6-v2")
vec = model.encode("text") # List[float]
```

---

## Verification (REQUIRED SECTION)

We need to verify dimensions (Property P11) and symmetry (P12).

**Create `verify_embeddings.py`**:

```python
"""
Verification script for Chapter 13.
Properties: P11 (Dimensions), P12 (Symmetry).
"""
import numpy as np
from sentence_transformers import SentenceTransformer
import sys

print("🧪 Running Embedding Verification...\n")

# Use local model for speed/cost in tests
model = SentenceTransformer("all-MiniLM-L6-v2")

# Test P11: Dimension Consistency
print("Test 1: Checking Dimensions...")
v1 = model.encode("Hello")
v2 = model.encode("World")

if len(v1) == 384:
    print(f"✅ P11 Passed: Correct dimension (384).")
else:
    print(f"❌ Failed: Expected 384, got {len(v1)}")
    sys.exit(1)

# Test P12: Symmetry (Distance A->B == Distance B->A)
print("Test 2: Checking Symmetry...")
def sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

s1 = sim(v1, v2)
s2 = sim(v2, v1)

# Float comparison with tolerance
if abs(s1 - s2) < 0.000001:
    print(f"✅ P12 Passed: Similarity is symmetric ({s1:.6f}).")
else:
    print(f"❌ Failed: Asymmetric {s1} != {s2}")
    sys.exit(1)

print("\n🎉 Chapter 13 Complete! You understand the geometry of language.")
```

**Run it:** `python verify_embeddings.py`

---

## Summary

**What you learned:**

1. ✅ **Embeddings**: Converting text to numbers captures meaning.
2. ✅ **Semantic Search**: Finding things by intent, not just keywords.
3. ✅ **Dimensions**: The "resolution" of the meaning (1536 vs 384).
4. ✅ **Cosine Similarity**: The math of measuring conceptual distance.
5. ✅ **Models**: OpenAI (Powerful) vs SentenceTransformers (Fast/Local).

**Key Takeaway**: Words are fuzzy. Vectors are precise. By moving to vector space, we can do math on meaning.

**Skills unlocked**: 🎯
- Vector Arithmetic
- Semantic Indexing
- Embedding API Usage

**Looking ahead**: We computed vectors in memory. But what if we have 1,000,000 documents? We can't keep them all in a Python list. In **Chapter 14**, we will introduce **Vector Stores** (ChromaDB) to manage this data at scale!

---

**Next**: [Chapter 14: Vector Stores with Chroma →](chapter-14-vector-stores.md)