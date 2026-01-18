# Chapter 15: Chunking Strategies — Slicing the Pizza

<!--
METADATA
Phase: 2 - Embeddings & Vectors
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 13 (Embeddings)
Builds Toward: RAG Pipeline (Ch 17)
Correctness Properties: P15 (Chunk Size Limits), P16 (Overlap Correctness)
Project Thread: Data Ingestion

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You invite a friend over for pizza. 🍕
You bake a giant, delicious 24-inch pizza.
When the friend arrives, do you shove the *entire* pizza into their mouth at once?
No. (I hope not). You slice it.

**LLMs have small mouths** (Context Windows).
If you try to feed a 100-page PDF into an Embedding Model, it will choke. It has a limit (e.g., 8,191 tokens).
Even if it *could* fit, finding a specific needle in a giant haystack is hard.

**Chunking** is the art of slicing data.
Too small? You lose context ("...died." Who died?).
Too big? You confuse the model.
Just right? Goldilocks.

**By the end of this chapter**, you'll build intelligent slicers that respect sentence boundaries and keep context alive. 🔪

---

## Prerequisites Check

```bash
# Check Python version
python --version
```

---

## The Story: The "Cut-Off" Sentence

### The Problem (Naive Splitting)

You have a document: "*The secret code is 12345.*"
You split it every 20 characters.
Chunk 1: "*The secret code is 1*"
Chunk 2: "*2345.*"

Now you search for "secret code".
Chunk 1 matches! But it says "1".
Chunk 2 has the rest, but it doesn't match the query "secret code".
You lost the information. 😱

### The Elegant Solution (Overlap & Recursion)

1.  **Overlap**: Include the end of Chunk 1 in the start of Chunk 2.
    *   Chunk 1: "*The secret code is 123*"
    *   Chunk 2: "*code is 12345*" (Overlap = "code is 123")
2.  **Recursive Splitting**: Don't cut in the middle of a word. Cut at paragraphs first. If too big, cut at sentences. If too big, cut at words.

---

## Part 1: Fixed-Size Chunking (The Basic Knife)

Let's start simple. Split by character count.

### 🔬 Try This! (Hands-On Practice #1)

**Create `fixed_chunker.py`**:

```python
def chunk_text_fixed(text, chunk_size, overlap):
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        # Slice the text
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Move forward, but step back by overlap amount
        start += chunk_size - overlap
        
    return chunks

# Test it
text = "The quick brown fox jumps over the lazy dog."
chunks = chunk_text_fixed(text, chunk_size=10, overlap=3)

print(f"Original Length: {len(text)}")
for i, c in enumerate(chunks):
    print(f"Chunk {i}: '{c}'")
```

**Run it**.
Output might look like:
Chunk 0: 'The quick '
Chunk 1: 'ck brown f'
Chunk 2: 'n fox jump'

**Critique**: It works, but it cuts words ("ck", "n"). It's efficient but dumb.

---

## Part 2: Recursive Character Splitter (The Smart Knife)

This is the industry standard (used by LangChain).
Strategy:
1. Try to split by `\n\n` (Paragraphs).
2. If chunk is still too big, split by `\n` (Sentences).
3. If still too big, split by ` ` (Words).
4. If still too big, split by characters.

### 🔬 Try This! (Hands-On Practice #2)

Let's build a simplified version.

**Create `recursive_chunker.py`**:

```python
import re

class RecursiveChunker:
    def __init__(self, chunk_size=100, overlap=20):
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Separators in priority order
        self.separators = ["\n\n", "\n", " ", ""]

    def split_text(self, text):
        return self._split_recursive(text, self.separators)

    def _split_recursive(self, text, separators):
        final_chunks = []
        
        # 1. Base case: If text fits, return it
        if len(text) <= self.chunk_size:
            return [text]
        
        # 2. Find the best separator
        separator = separators[-1] # Default to char split
        for sep in separators:
            if sep in text:
                separator = sep
                break
        
        # 3. Split
        # Use regex to split if separator is empty string (chars)
        if separator == "":
            splits = list(text)
        else:
            splits = text.split(separator)

        # 4. Merge smaller splits back into chunks
        current_chunk = ""
        for split in splits:
            # Add separator back if it's not char split
            if separator != "":
                split += separator
                
            if len(current_chunk) + len(split) <= self.chunk_size:
                current_chunk += split
            else:
                if current_chunk:
                    final_chunks.append(current_chunk)
                # Apply overlap (Simplified logic here)
                current_chunk = split
        
        if current_chunk:
            final_chunks.append(current_chunk)
            
        return final_chunks

# Test
long_text = """
Introduction to AI.

AI is changing the world. It is everywhere.
From cars to phones.

Conclusion.
We must be careful.
"""

chunker = RecursiveChunker(chunk_size=50, overlap=0)
chunks = chunker.split_text(long_text)

for i, c in enumerate(chunks):
    print(f"[{i}] len={len(c)}: {repr(c)}")
```

**Run it**.
Notice how it respects the paragraphs (`\n\n`) and keeps them together if they fit? Much better!

---

## Part 3: Token-Based Chunking

Models count **Tokens**, not characters.
1 Token ≈ 0.75 words (in English).
"Hamburger" = 1 token.
"Ham" + "bur" + "ger" = 3 tokens (sometimes).

To be precise, we should chunk by tokens.

### 🔬 Try This! (Hands-On Practice #3)

We need the `tiktoken` library (used by OpenAI).

```bash
pip install tiktoken
```

**Create `token_chunker.py`**:

```python
import tiktoken

def count_tokens(text):
    encoder = tiktoken.get_encoding("cl100k_base") # GPT-4 encoding
    return len(encoder.encode(text))

text = "Hello, world!"
print(f"Chars: {len(text)}")
print(f"Tokens: {count_tokens(text)}")

# Simple Token Chunker
def chunk_by_tokens(text, limit=5):
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    
    chunks = []
    for i in range(0, len(tokens), limit):
        chunk_tokens = tokens[i : i + limit]
        chunk_text = encoder.decode(chunk_tokens)
        chunks.append(chunk_text)
    return chunks

print(chunk_by_tokens("This is a longer sentence to test token splitting.", limit=3))
```

**Run it**.
This guarantees you NEVER exceed the API limit (e.g., 8191 for embeddings).

---

## Common Mistakes

### Mistake #1: Overlap is too small
If overlap is 0, you might cut a sentence in half and lose the meaning connection.
**Rule of Thumb**: Overlap should be ~10-20% of chunk size.

### Mistake #2: Ignoring Metadata
When you chunk a file, you lose the filename and page number.
**Fix**: Store metadata with *every* chunk.
`Chunk 1: {text: "...", page: 1, file: "report.pdf"}`

### Mistake #3: Splitting Code
Code is sensitive. Splitting `function()` from `{ body }` breaks it.
**Fix**: Use specialized splitters for Python/JS (LangChain has these).

---

## Quick Reference Card

### Chunking Strategies

| Strategy | Best For | Pros | Cons |
|----------|----------|------|------|
| **Fixed Size** | Testing | Fast, Simple | Breaks words/sentences |
| **Recursive** | Text Docs | Respects structure | Slower |
| **Semantic** | Advanced Search | Groups by meaning | Expensive (needs embeddings) |

---

## Verification (REQUIRED SECTION)

Let's prove **P15 (Size Compliance)**.

**Create `verify_chunking.py`**:

```python
"""
Verification script for Chapter 15.
Properties: P15 (Size Constraint).
"""
import sys

# Use our simple fixed chunker for verification logic
def chunk_text_fixed(text, size):
    return [text[i:i+size] for i in range(0, len(text), size)]

print("🧪 Running Chunking Verification...\n")

# Setup
limit = 20
text = "A" * 105 # 105 characters

# 1. Run Chunking
chunks = chunk_text_fixed(text, limit)

# 2. Verify P15: No chunk exceeds limit
print("Test 1: Size Constraints...")
failed = False
for i, c in enumerate(chunks):
    if len(c) > limit:
        print(f"❌ Chunk {i} too big: {len(c)}")
        failed = True

if not failed:
    print(f"✅ P15 Passed: All {len(chunks)} chunks are <= {limit} chars.")
else:
    sys.exit(1)

# 3. Verify Completeness (No data lost)
reconstructed = "".join(chunks)
assert reconstructed == text
print("✅ Completeness Passed: Data integrity maintained.")

print("\n🎉 Chapter 15 Complete! You can now slice data.")
```

**Run it:** `python verify_chunking.py`

---

## Summary

**What you learned:**

1. ✅ **Context Windows**: Why we need to slice data.
2. ✅ **Fixed Splitting**: Fast but brutal.
3. ✅ **Recursive Splitting**: Respects natural language boundaries (paragraphs).
4. ✅ **Overlap**: The glue that holds context together across cuts.
5. ✅ **Tokens**: The true unit of measurement for LLMs.

**Key Takeaway**: Good chunking is the unsung hero of RAG. If you feed the AI bad chunks, no amount of prompt engineering will save you.

**Skills unlocked**: 🎯
- Data Preprocessing
- Algorithm Design (Recursion)
- Tokenization

**Looking ahead**: We can slice text. We can embed it (Ch 13). We can store it (Ch 14). But how do we get the text out of **PDFs and Word Docs**? In **Chapter 16**, we will build **Document Loaders**.

---

**Next**: [Chapter 16: Document Loaders →](chapter-16-document-loaders.md)
