# Chapter 23: LangChain Loaders & Splitters — The Standard Library

<!--
METADATA
Phase: 4 - LangChain Core
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 16 (Manual Loaders)
Builds Toward: Production Ingestion
Correctness Properties: P16 (Overlap), P31 (Metadata Propagation)
Project Thread: Framework Migration

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You learned to bake bread from scratch. You grew the wheat, ground the flour, and caught the yeast. It was educational. It was noble.
But now you need to make **10,000 sandwiches** for a conference.
You don't grow wheat. You buy a standardized bag of flour from the store.

In Chapters 15 and 16, we built Loaders and Splitters from scratch. We grew the wheat.
Now, we are going to use **LangChain's Standard Library**. It has loaders for 100+ file formats (Notion, Slack, PDFs, S3). It handles edge cases we didn't even think of.

**By the end of this chapter**, you will replace your custom code with robust, community-tested components that scale. 🍞

---

## Prerequisites Check

```bash
# We need the community package for loaders
pip install langchain-community
```

---

## The Story: The Maintenance Trap

### The Problem (Custom Code Rot)

You wrote a `PDFLoader` in Chapter 16. It works!
Then a user uploads a **password-protected** PDF. Crash.
Then a user uploads a **rotated** PDF. Text comes out backwards.
Then a user uploads a **1GB** PDF. Memory overflow.

Do you really want to spend your life debugging PDF edge cases?

### The Solution (Community Loaders)

LangChain's `PyPDFLoader` handles passwords. It handles rotation. It handles streaming (`lazy_load`).
Someone else fixed those bugs for you.

---

## Part 1: Document Loaders

LangChain loaders all follow the same interface: `load()` or `lazy_load()`.

### 🔬 Try This! (Hands-On Practice #1)

Let's load a folder of mixed files using `DirectoryLoader`.

**Create `langchain_loaders.py`**:

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PythonLoader
import os

# 1. Setup Data
os.makedirs("test_data", exist_ok=True)
with open("test_data/note.txt", "w") as f: f.write("Buy milk.")
with open("test_data/script.py", "w") as f: f.write("print('Hello')")

# 2. Use DirectoryLoader
# It automatically picks the right loader based on extensions if configured,
# or uses a default glob.
print("Loading Directory...")
loader = DirectoryLoader(
    "test_data", 
    glob="**/*.txt", 
    loader_cls=TextLoader
)
docs = loader.load()

print(f"Loaded {len(docs)} documents.")
print(f"Content: {docs[0].page_content}")
print(f"Metadata: {docs[0].metadata}") # Look! Source is auto-populated.

# Cleanup
import shutil
shutil.rmtree("test_data")
```

**Run it**.
Notice how `metadata={'source': 'test_data/note.txt'}` is automatic? We had to code that manually in Chapter 16.

---

## Part 2: Text Splitters

LangChain's splitters are highly optimized.

### 🔬 Try This! (Hands-On Practice #2)

Let's use `RecursiveCharacterTextSplitter`.

**Create `langchain_splitters.py`**:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text = """
Chapter 1.
The beginning of time.

Chapter 2.
The end of time.
"""

# 1. Configure Splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=20,
    chunk_overlap=5,
    separators=["\n\n", "\n", " "] # Priority order
)

# 2. Split Text
chunks = splitter.split_text(text)

print(f"Original Length: {len(text)}")
print(f"Chunks: {len(chunks)}")
for i, c in enumerate(chunks):
    print(f"[{i}] {repr(c)}")
```

**Run it**.
It handles the math of overlap and boundaries for you.

---

## Part 3: Metadata Propagation

This is the most critical feature.
If you load a 100-page PDF and split it into 500 chunks, **every chunk** needs to know it came from "contract.pdf" and "page 1".

LangChain's `split_documents` method handles this.

### 🔬 Try This! (Hands-On Practice #3)

**Create `metadata_propagation.py`**:

```python
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter

# 1. Create a Source Document
doc = Document(
    page_content="A long time ago in a galaxy far far away...",
    metadata={"source": "movie_script.txt", "author": "Lucas"}
)

# 2. Split it
splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0, separator=" ")
split_docs = splitter.split_documents([doc])

# 3. Verify Metadata
print(f"Original Metadata: {doc.metadata}")
print("--- Chunks ---")
for chunk in split_docs:
    print(f"Content: '{chunk.page_content}'")
    print(f"Metadata: {chunk.metadata}") # Should match original!
```

**Run it**.
You should see that *every* chunk has `{'source': 'movie_script.txt', 'author': 'Lucas'}`.
This ensures that when RAG retrieves a chunk, it knows where it came from.

---

## Common Mistakes

### Mistake #1: Using `load()` on huge datasets
`load()` reads everything into RAM. If you have 10GB of text, your computer crashes.
**Fix**: Use `lazy_load()` which yields documents one by one (a Generator!).

```python
for doc in loader.lazy_load():
    process(doc)
```

### Mistake #2: Wrong Separators
If splitting code, `\n\n` is bad. Python splits on `def`, `class`.
**Fix**: Use `Language.PYTHON` splitter.
`RecursiveCharacterTextSplitter.from_language(Language.PYTHON, ...)`

### Mistake #3: Losing Metadata
Using `split_text` (strings) instead of `split_documents` (objects). `split_text` returns strings, so metadata is lost. Always use `split_documents`.

---

## Quick Reference Card

### Standard Loaders

| Format | Loader |
|--------|--------|
| .txt | `TextLoader` |
| .pdf | `PyPDFLoader` |
| .csv | `CSVLoader` |
| Folder | `DirectoryLoader` |

### Splitting

```python
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = splitter.split_documents(original_docs)
```

---

## Verification (REQUIRED SECTION)

We need to verify **P31 (Metadata Propagation)**.

**Create `verify_langchain.py`**:

```python
"""
Verification script for Chapter 23.
Property P31: Metadata Propagation.
"""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import sys

print("🧪 Running LangChain Verification...\n")

# Setup
original_meta = {"id": 123, "confidential": True}
doc = Document(
    page_content="Chunk1. Chunk2. Chunk3.",
    metadata=original_meta
)

# Split
splitter = RecursiveCharacterTextSplitter(
    chunk_size=10,
    chunk_overlap=0,
    separators=["."]
)
chunks = splitter.split_documents([doc])

# Verify P31
print("Test 1: Metadata Check...")
if len(chunks) < 2:
    print("❌ Failed: Setup error, didn't split enough.")
    sys.exit(1)

for i, chunk in enumerate(chunks):
    if chunk.metadata != original_meta:
        print(f"❌ Failed: Chunk {i} lost metadata. Got: {chunk.metadata}")
        sys.exit(1)

print("✅ P31 Passed: Metadata propagated to all chunks.")
print("\n🎉 Chapter 23 Complete! You are now using the industrial toolset.")
```

**Run it:** `python verify_langchain.py`

---

## Summary

**What you learned:**

1. ✅ **Standard Library**: LangChain has pre-built tools for everything.
2. ✅ **DirectoryLoader**: Loading entire folders at once.
3. ✅ **Lazy Loading**: Handling big data without crashing RAM.
4. ✅ **Splitter Logic**: How `RecursiveCharacterTextSplitter` prioritizes separators.
5. ✅ **Propagation**: Keeping metadata attached to chunks is vital for RAG.

**Key Takeaway**: Don't write your own PDF parser unless you really, really have to. Use the community standard.

**Skills unlocked**: 🎯
- LangChain Ingestion
- Data Pipeline Optimization
- Metadata Management

**Looking ahead**: We can load and split data. But what about the conversation *history*? How do we store it efficiently? In **Chapter 24**, we will master **Memory & Callbacks**.

---

**Next**: [Chapter 24: Memory & Callbacks →](chapter-24-memory-callbacks.md)
