# Chapter 16: Document Loaders — Digging for Gold

<!--
METADATA
Phase: 2 - Embeddings & Vectors
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 15 (Chunking)
Builds Toward: RAG Pipeline (Ch 17)
Correctness Properties: P17 (Text Extraction), P18 (Metadata Preservation)
Project Thread: Data Ingestion

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You are a gold miner. ⛏️
The gold (Information) is trapped inside rock (PDFs, Word Docs, HTML).
You can't put the rock in the bank. You need to crush it, extract the gold, and refine it.

**Document Loaders** are your rock crushers.
The world doesn't run on clean `.txt` files. It runs on messy PDFs with headers, footers, and images. It runs on Word docs with track changes.
If you can't read these files, your AI is blind to 90% of the world's data.

**By the end of this chapter**, you'll build a unified ingestion system that turns any file format into clean, AI-ready text. 📄

---

## Prerequisites Check

We need tools to read these formats.

```bash
pip install pypdf python-docx
```

---

## The Story: The "Unreadable" Contract

### The Problem (Binary Blobs)

You try to open a PDF in Python:
```python
with open("contract.pdf", "r") as f:
    print(f.read())
```

**Crash.** `UnicodeDecodeError`.
PDFs aren't text. They are binary instructions for a printer ("Draw line here, put letter 'A' here"). Extracting words from them is surprisingly hard.

### The Solution (Standardized Documents)

We need to convert EVERYTHING into a standard format.
In the AI world, we typically use a **Document Object**:
1.  **page_content**: The raw text.
2.  **metadata**: The source info (Page number, Filename, Author).

---

## Part 1: The Standard Document

Before we write loaders, let's define what a "Document" is.

### 🔬 Try This! (Hands-On Practice #1)

**Create `shared/models/document.py`**:

```python
from pydantic import BaseModel, Field
from typing import Dict, Any

class Document(BaseModel):
    """
    A unified representation of any file.
    """
    page_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __str__(self):
        source = self.metadata.get("source", "Unknown")
        return f"[Doc from {source}]: {self.page_content[:50]}..."
```

**Test it**:
```python
doc = Document(
    page_content="This is the text.",
    metadata={"source": "memo.txt", "page": 1}
)
print(doc)
```

---

## Part 2: The Text Loader (Simple)

Let's start with the easiest format: `.txt`.

### 🔬 Try This! (Hands-On Practice #2)

**Create `shared/ingest/text_loader.py`**:

```python
from typing import List
from shared.models.document import Document
import os

class TextLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Document]:
        """Read text file and return a Document."""
        with open(self.file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        metadata = {
            "source": self.file_path,
            "filename": os.path.basename(self.file_path)
        }
        
        # Text files are usually 1 "page"
        return [Document(page_content=text, metadata=metadata)]
```

---

## Part 3: The PDF Loader (Complex)

Now for the boss fight. extracting text from PDFs.

### 🔬 Try This! (Hands-On Practice #3)

**Create `shared/ingest/pdf_loader.py`**:

```python
from typing import List
from shared.models.document import Document
from pypdf import PdfReader
import os

class PDFLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Document]:
        reader = PdfReader(self.file_path)
        documents = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                metadata = {
                    "source": self.file_path,
                    "page": i + 1, # Humans count from 1
                    "total_pages": len(reader.pages)
                }
                documents.append(Document(page_content=text, metadata=metadata))
                
        return documents
```

**Why one Document per page?**
Because a 50-page PDF is too big for one chunk. Splitting by page is a natural boundary that preserves context (metadata has page number!).

---

## Part 4: The Factory Pattern

We don't want to manually choose the loader every time. We want `load_file("stuff.pdf")` to just work.

### 🔬 Try This! (Hands-On Practice #4)

**Create `shared/ingest/loader_factory.py`**:

```python
from .text_loader import TextLoader
from .pdf_loader import PDFLoader
import os

def load_file(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".txt":
        return TextLoader(file_path).load()
    elif ext == ".pdf":
        return PDFLoader(file_path).load()
    else:
        raise ValueError(f"Unsupported file type: {ext}")
```

---

## Bringing It All Together: The Ingestion Pipeline

Let's test our system with a real file.

**Create `test_ingest.py`**:

```python
from shared.ingest.loader_factory import load_file

# 1. Create a dummy file
with open("test_doc.txt", "w") as f:
    f.write("This is a test document.\nIt has important secrets.")

# 2. Load it via Factory
print("Loading file...")
docs = load_file("test_doc.txt")

# 3. Inspect
for doc in docs:
    print(f"---\nMetadata: {doc.metadata}"
    print(f"Content: {doc.page_content}")

import os
os.remove("test_doc.txt") # Cleanup
```

**Run it**.
It should auto-detect `.txt` and load it perfectly.

---

## Common Mistakes

### Mistake #1: Ignoring OCR
If a PDF is just **scanned images**, `pypdf` will return empty strings. You need OCR (Optical Character Recognition) tools like `tesseract` for that. That's advanced, but be aware of it.

### Mistake #2: Losing Metadata
If you chunk the text *after* loading but forget to copy the metadata to the chunks, you won't know which page the answer came from!
**Fix**: Pass metadata through the chunking process (we'll see this in Ch 17).

### Mistake #3: Encryption
Some PDFs are password protected. `pypdf` supports decryption, but you need to handle the `PasswordError` exception.

---

## Quick Reference Card

### pypdf Basic Usage

```python
reader = PdfReader("file.pdf")
page = reader.pages[0]
text = page.extract_text()
```

### File Extension Check

```python
ext = os.path.splitext(filename)[1].lower()
# returns ".pdf", ".txt", etc.
```

---

## Verification (REQUIRED SECTION)

We need to prove **P17 (Extraction Completeness)** and **P18 (Metadata Preservation)**.

**Create `verify_loaders.py`**:

```python
"""
Verification script for Chapter 16.
Properties: P17 (Text), P18 (Metadata).
"""
import sys
from shared.ingest.text_loader import TextLoader
import os

print("🧪 Running Loader Verification...\n")

# Setup
filename = "verify_test.txt"
content = "Verification Content 123"
with open(filename, "w") as f:
    f.write(content)

# 1. Run Loader
loader = TextLoader(filename)
docs = loader.load()

# Test P17: Text Extraction
print("Test 1: Content Accuracy...")
if docs[0].page_content == content:
    print("✅ P17 Passed: Text matches exactly.")
else:
    print(f"❌ Failed: Expected '{content}', got '{docs[0].page_content}'")
    sys.exit(1)

# Test P18: Metadata
print("Test 2: Metadata Check...")
meta = docs[0].metadata
if meta["source"] == filename and meta["filename"] == filename:
    print("✅ P18 Passed: Metadata preserved.")
else:
    print(f"❌ Failed: Metadata missing or wrong: {meta}")
    sys.exit(1)

# Cleanup
os.remove(filename)
print("\n🎉 Chapter 16 Complete! You can mine data.")
```

**Run it:** `python verify_loaders.py`

---

## Summary

**What you learned:**

1. ✅ **Format Chaos**: Why we need unified Loaders.
2. ✅ **Document Object**: The universal standard (content + metadata).
3. ✅ **PDF Parsing**: It's hard, but libraries help.
4. ✅ **Factory Pattern**: Auto-selecting the right tool for the job.
5. ✅ **Metadata**: The context that makes search useful (page numbers!).

**Key Takeaway**: A file on disk is useless. A `Document` object in memory is gold. You have built the machinery to convert one to the other.

**Skills unlocked**: 🎯
- File I/O
- Binary File Parsing
- Design Patterns (Factory)

**Looking ahead**: We have all the pieces!
- Ch 13: Embeddings
- Ch 14: Vector Store
- Ch 15: Chunking
- Ch 16: Loading

In **Chapter 17**, we combine them all into the **RAG Pipeline**. This is the holy grail. We will chat with our documents! 🏆

---

**Next**: [Phase 3: RAG Fundamentals (Chapter 17) →](../phase-3-rag-fundamentals/chapter-17-first-rag-system.md)

