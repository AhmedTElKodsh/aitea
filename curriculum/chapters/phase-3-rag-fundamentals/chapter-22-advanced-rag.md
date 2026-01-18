# Chapter 22: Advanced RAG Patterns — The Power Tools

<!--
METADATA
Phase: 3 - RAG Fundamentals
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 19 (Retrieval)
Builds Toward: LlamaIndex (Ch 35)
Correctness Properties: P29 (Parent-Child Integrity), P30 (Merge Boundary)
Project Thread: Context Optimization

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You use Google Maps to find a coffee shop.
You zoom in all the way. You see a pixel that says "Door". Great precision!
But... you have no idea what street you're on. You lost the **Context**.

**RAG has this problem.**
Small chunks are easy to find (high precision).
But small chunks (100 words) often lack the information needed to answer the question ("See Appendix A for details" - wait, where is Appendix A?).

**Advanced RAG Patterns** fix this.
We search with the microscope (Small Chunks), but we deliver the whole map (Parent Documents).
It's the best of both worlds: Precision searching, Contextual answering. 🗺️

---

## Prerequisites Check

We need advanced retrievers from LangChain.

```bash
pip install langchain langchain-community chromadb
```

---

## The Story: The "Fragmented" Answer

### The Problem (Missing Pieces)

User: "What are the payment terms?"
Chunk 1: "Payment shall be made..."
Chunk 2: "...within 30 days of receipt."
Chunk 3: "...unless disputed."

If the Retriever only finds Chunk 1 and 3, the AI says: "Payment shall be made unless disputed."
It missed the "30 days" part! Dangerous for contracts.

### The Solution (Parent-Child)

1.  **Split** document into Big Chunks (Parents) and Small Chunks (Children).
2.  **Index** only the Children (for search).
3.  **Link** Children to Parents.
4.  **Retrieve**: Find a Child -> Return the Parent.

Now the AI gets the *entire* paragraph, guaranteed.

---

## Part 1: Parent Document Retriever

Let's build this hierarchy.

### 🔬 Try This! (Hands-On Practice #1)

**Create `parent_retriever.py`**:

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# 1. Setup
# We need two stores: 
# - VectorStore (for searching small chunks)
# - DocStore (for holding big chunks)
vectorstore = Chroma(collection_name="split_parents", embedding_function=OpenAIEmbeddings())
docstore = InMemoryStore()

# 2. Splitters
# Children: Small, specific (for search)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=100)
# Parents: Large, contextual (for answer)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=500)

# 3. The Retriever
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=docstore,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# 4. Add Data
# Create a dummy doc
from langchain_core.documents import Document
long_text = "The code to unlock the safe is 1234. " * 20 + "The safe contains gold."
doc = Document(page_content=long_text, metadata={"title": "Secret"})

print("Adding document...")
retriever.add_documents([doc], ids=None)

# 5. Search
# Search for a specific detail
query = "contains gold"
results = retriever.invoke(query)

print(f"\nQuery: {query}")
print(f"Retrieved {len(results)} doc(s).")
print(f"Content Length: {len(results[0].page_content)}") # Should be ~500 (Parent), not ~100 (Child)
print(f"Snippet: {results[0].page_content[:50]}...")
```

**Run it**.
Even though "contains gold" is a tiny part at the end, the retriever returns the *whole* 500-char parent chunk. Context restored!

---

## Part 2: Hypothetical Document Embeddings (HyDE)

Sometimes the user asks a question that looks *nothing* like the answer.
Q: "How do I fix a null pointer?"
Doc: "Check for uninitialized variables."

Vector similarity might follow "pointer" to "laser pointer". ❌

**HyDE Strategy**:
1. Ask LLM to **hallucinate** an answer.
   *Fake Answer: "To fix a null pointer, ensure your variables are not null before accessing them."
2. Embed the **Fake Answer**.
3. Search for that.

The Fake Answer is semantically closer to the Real Answer than the Question is!

### 🔬 Try This! (Hands-On Practice #2)

**Create `hyde.py`**:

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import HydeRetrievalChain, LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma

# 1. Setup Vector Store (Standard)
vectorstore = Chroma(embedding_function=OpenAIEmbeddings())
vectorstore.add_texts(["To resolve NullPointer, check variable initialization."])

# 2. HyDE Generator
# We need a chain that generates the hypothetical document
llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template(
    "Write a scientific paragraph answering the question: {question}"
)
llm_chain = LLMChain(llm=llm, prompt=prompt)

# 3. Embed the HYPOTHETICAL document
embeddings = OpenAIEmbeddings()

# 4. Search
query = "How do I fix a null pointer?"

# MANUAL HyDE Logic (to understand it):
print(f"Query: {query}")
# A: Hallucinate
hypothetical = llm_chain.invoke(query)["text"]
print(f"👻 Hallucination: {hypothetical[:60]}...")
# B: Embed & Search
results = vectorstore.similarity_search(hypothetical, k=1)
print(f"✅ Found: {results[0].page_content}")
```

**Run it**.
HyDE bridges the gap between questions and answers.

---

## Part 3: Multi-Vector Retriever (Summary vs Detail)

Sometimes you want to search a **Summary**, but retrieve the **Full Document** (or a Table, or Image).
This decouples the "Searchable Representation" from the "Returnable Content".

**Concept**:
1.  Doc: `[Image of a cat]`
2.  Summary: "A photo of a cute kitten."
3.  Embed Summary.
4.  Search "Kitten" -> Find Summary -> Return Image.

*(We won't code this one now as it requires multi-modal setup, but remember the concept!)*

---

## Common Mistakes

### Mistake #1: Parent Chunks too big
If your parent chunk is 10,000 tokens, you might overflow the LLM context window when you pass 5 of them.
**Fix**: Balance. Parent chunks of 500-1000 tokens are usually sweet spots.

### Mistake #2: Slow HyDE
HyDE requires an LLM call *before* search. It adds latency.
**Fix**: Only use HyDE for complex/vague queries.

### Mistake #3: Memory Store Persistence
In `ParentDocumentRetriever`, we used `InMemoryStore`. If you restart the app, the parents are gone (even if Chroma persists the children vectors!).
**Fix**: You must use a persistent DocStore (like Redis, SQL, or local file store) for production.

---

## Quick Reference Card

### Retriever Types

| Retriever | Strategy | Pros | Cons |
|-----------|----------|------|------|
| **ParentDoc** | Small Index -> Big Result | Great Context | Storage complexity |
| **HyDE** | Search by Hallucination | High Recall | High Latency |
| **MultiVector** | Summary Index -> Full Doc | Flexible | Setup complexity |

---

## Verification (REQUIRED SECTION)

We need to verify **P29 (Parent-Child Integrity)**.

**Create `verify_advanced.py`**:

```python
"""
Verification script for Chapter 22.
Properties: P29 (Parent Integrity).
"""
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import sys

print("🧪 Running Advanced RAG Verification...\n")

# Setup
vectorstore = Chroma(collection_name="verify_parents", embedding_function=OpenAIEmbeddings())
docstore = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=docstore,
    child_splitter=RecursiveCharacterTextSplitter(chunk_size=20), # Tiny children
    parent_splitter=RecursiveCharacterTextSplitter(chunk_size=100) # Medium parent
)

# P29: Parent-Child Integrity
# We verify that searching for a child's content returns the correct parent
print("Test 1: Parent-Child Link...")
parent_content = "This is a unique parent document identifier code 9999."
doc = Document(page_content=parent_content)
retriever.add_documents([doc])

# Search for a fragment (Child)
query = "identifier code"
results = retriever.invoke(query)

if len(results) > 0 and results[0].page_content == parent_content:
    print("✅ P29 Passed: Retrieved full parent from child fragment.")
else:
    print(f"❌ Failed: Expected parent, got {results}")
    sys.exit(1)

print("\n🎉 Chapter 22 Complete! You are a RAG Architect.")
```

**Run it:** `python verify_advanced.py`

---

## Summary

**What you learned:**

1. ✅ **The Context Tradeoff**: Small chunks search well; big chunks explain well.
2. ✅ **Parent Document Retriever**: The bridge between searchability and readability.
3. ✅ **HyDE**: Using hallucination as a feature, not a bug.
4. ✅ **DocStore**: Separating vectors from content storage.
5. ✅ **Decoupling**: The index doesn't have to be the content.

**Key Takeaway**: Advanced RAG isn't about better models. It's about better **Architecture**. It's about putting the right data in the right shape for the right step.

**Skills unlocked**: 🎯
- Architectural Patterns
- Latency/Accuracy Trade-offs
- Advanced LangChain Retrievers

**Looking ahead**: We have covered Loaders, Chunking, Vectors, Retrieval, and RAG. But we're mostly using high-level LangChain wrappers.
In **Phase 4**, we will dive deeper into **LangChain Core** to understand exactly how the sausage is made, preparing us for Agents!

---

**Next**: [Phase 4: LangChain Core (Chapter 23) →](../phase-4-langchain-core/chapter-23-langchain-loaders.md)
