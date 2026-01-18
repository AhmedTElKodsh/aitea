# Chapter 18: LangChain Expression Language (LCEL) — The UNIX Pipe of AI

<!--
METADATA
Phase: 3 - RAG Fundamentals
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 17 (RAG)
Builds Toward: Agents (Ch 26), LangGraph (Ch 31)
Correctness Properties: P21 (Execution Order), P22 (Data Passthrough)
Project Thread: Pipeline Architecture

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're in a Linux terminal.
You want to find a file, read it, search for a word, and count the lines.
Do you write a Python script? No. You use **Pipes**:
`cat file.txt | grep "error" | wc -l`

Data flows from left to right. It's clean. It's readable. It's beautiful.

**LCEL (LangChain Expression Language)** is the "Pipe" for AI.
Instead of writing spaghetti code (`result = step3(step2(step1(input)))`), you write:
`chain = prompt | llm | output_parser`

**By the end of this chapter**, you'll replace your messy, procedural RAG code with elegant, composable pipelines that are easier to read, test, and stream. 🔗

---

## Prerequisites Check

We need the LangChain library.

```bash
pip install langchain langchain-openai langchain-core
```

---

## The Story: The "Spaghetti" Code

### The Problem (Procedural Mess)

In Chapter 17, our RAG function looked like this:

```python
def ask_rag(question):
    # Step 1
    docs = store.search(question)
    context = "\n".join(docs)
    
    # Step 2
    prompt_str = template.format(context=context, question=question)
    
    # Step 3
    response = client.generate(prompt_str)
    
    # Step 4
    return response.strip()
```

It works. But what if we want to stream Step 3? What if we want to run Step 1 in parallel with another search? What if we want to add a logging step between 2 and 3?
The function grows ugly fast.

### The Elegant Solution (LCEL)

```python
chain = retriever | format_docs | prompt | llm | StrOutputParser()
chain.invoke("question")
```

Every component has a standard interface (`invoke`, `stream`, `batch`). You can swap them like Lego bricks.

---

## Part 1: The Basic Chain

Let's build a simple "Joke Generator" chain.

### 🔬 Try This! (Hands-On Practice #1)

**Create `basic_chain.py`**:

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# 1. The Model
model = ChatOpenAI(model="gpt-4o-mini")

# 2. The Prompt
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")

# 3. The Output Parser (Extracts string from Message object)
parser = StrOutputParser()

# 4. The Chain (The Magic Pipe | )
chain = prompt | model | parser

# 5. Run it
print("Invoking chain...")
result = chain.invoke({"topic": "ice cream"})
print(f"Result: {result}")
```

**Run it**.
Notice how we didn't call `model.invoke()` directly. The `|` operator wired it all up.

---

## Part 2: The RAG Chain (Runnables)

Now let's rebuild RAG. We need to fetch data *inside* the chain.
We use `RunnablePassthrough` to pass data along and `RunnableLambda` for custom functions.

### 🔬 Try This! (Hands-On Practice #2)

**Create `lcel_rag.py`**:

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

# Simulate our Vector Store (Ch 14)
def fake_retriever(query):
    print(f"   (Searching for: {query})")
    return ["Fact 1: The sky is blue.", "Fact 2: Grass is green."]

# Format function
def format_docs(docs):
    return "\n".join(docs)

# The Chain
template = """Answer based on context:
{context}

Question: {question}"""
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI(model="gpt-4o-mini")

rag_chain = (
    # The Setup: Create a dict with context AND question
    {"context": itemgetter("question") | RunnableLambda(fake_retriever) | format_docs,
     "question": itemgetter("question")}
    | prompt
    | model
    | StrOutputParser()
)

print("Asking RAG Chain...")
result = rag_chain.invoke({"question": "What color is the sky?"})
print(f"Answer: {result}")
```

**Wait, what just happened?**
The first dictionary is a **Parallel Step**.
1. `context`: Takes input -> extracts "question" -> runs retriever -> formats docs.
2. `question`: Takes input -> extracts "question".
3. BOTH results are passed to the `prompt`.

This handles the data flow logic declaratively!

---

## Part 3: Why LCEL? (Streaming & Batching)

Because we used standard Runnables, we get features for free.

### 🔬 Try This! (Hands-On Practice #3)

Try streaming the same chain. You don't need to rewrite it!

**Append to `lcel_rag.py`**:

```python
print("\nStreaming RAG Chain...")
# Standard iterator interface!
for chunk in rag_chain.stream({"question": "What color is the grass?"}):
    print(chunk, end="", flush=True)
print()
```

**Run it**.
It just works. If you wrote the function manually, you'd have to rewrite it to support `yield`.

---

## Common Mistakes

### Mistake #1: Confusing input types
`prompt | model`. The prompt expects a dictionary. The model expects a PromptValue. The parser expects a Message.
If you break the chain (e.g., passing a string to a prompt expecting a dict), you get cryptic errors.
**Fix**: Use `chain.get_graph().print_ascii()` to visualize inputs/outputs.

### Mistake #2: Forgetting `invoke`
Defining the chain `chain = a | b` does nothing. You must call `chain.invoke(input)` to run it.

### Mistake #3: Complexity Overload
LCEL is powerful but can be unreadable if you nest 10 lambdas.
**Rule**: If a step is complex Python logic, move it to a `@tool` or a dedicated function (`RunnableLambda`), don't try to write it all in the pipe.

---

## Quick Reference Card

### The Operators

| Operator | Meaning |
|----------|---------|
| `|` | Pipe output of Left to input of Right |
| `dict` | Run values in parallel |

### Runnable Methods

| Method | Usage |
|--------|-------|
| `invoke(x)` | Run once |
| `stream(x)` | Stream output chunks |
| `batch([x1, x2])` | Run multiple inputs in parallel |

---

## Verification (REQUIRED SECTION)

We need to prove **P21 (Execution Order)** and **P22 (Data Passthrough)**.

**Create `verify_lcel.py`**:

```python
"""
Verification script for Chapter 18.
Properties: P21 (Order), P22 (Passthrough).
"""
from langchain_core.runnables import RunnableLambda
import sys

print("🧪 Running LCEL Verification...\n")

log = []

def step_1(x):
    log.append(1)
    return x + 1

def step_2(x):
    log.append(2)
    return x * 2

# Test P21: Execution Order
print("Test 1: Chain Order...")
chain = RunnableLambda(step_1) | RunnableLambda(step_2)
result = chain.invoke(1)

# Logic: (1 + 1) * 2 = 4
# Log: [1, 2]
if result == 4 and log == [1, 2]:
    print("✅ P21 Passed: Steps executed in correct order (Left -> Right).")
else:
    print(f"❌ Failed: Result={result}, Log={log}")
    sys.exit(1)

# Test P22: Parallel Passthrough
print("Test 2: Parallel Execution...")
par_chain = {
    "original": lambda x: x,
    "modified": chain
}
# Input 5. 
# original -> 5
# modified -> (5+1)*2 = 12
res = RunnableLambda(lambda x: x).invoke(5) # Just to prep types if needed
# Actually, let's just run the dict directly wrapped in RunnableLambda implicitly via invoke or just use the chain pattern
from langchain_core.runnables import RunnableParallel
par_chain = RunnableParallel(
    original=RunnableLambda(lambda x: x),
    modified=chain
)
res = par_chain.invoke(5)

if res["original"] == 5 and res["modified"] == 12:
    print("✅ P22 Passed: Data passed through parallel branches correctly.")
else:
    print(f"❌ Failed: {res}")
    sys.exit(1)

print("\n🎉 Chapter 18 Complete! You are a Pipeline Plumber.")
```

**Run it:** `python verify_lcel.py`

---

## Summary

**What you learned:**

1. ✅ **Composition**: Building complex logic from simple blocks.
2. ✅ **The Pipe (`|`)**: The syntax that glues LangChain together.
3. ✅ **Parallelism**: Using dictionaries (RunnableParallel) to do two things at once.
4. ✅ **Standard Interface**: Invoke, Stream, and Batch work on *everything*.
5. ✅ **Cleanliness**: Converting procedural spaghetti into declarative pipelines.

**Key Takeaway**: LCEL separates the *intent* (the chain structure) from the *execution* (invoke/stream). This abstraction makes your code future-proof.

**Skills unlocked**: 🎯
- Functional Programming Concepts
- Pipeline Architecture
- LangChain Fundamentals

**Looking ahead**: We've mastered the basics of RAG and Chains. Now we need to improve our retrieval. Simple search isn't enough. In **Chapter 19**, we'll learn **Advanced Retrieval Strategies** (Hybrid Search, Re-ranking) to find the needle in the haystack every time.

---

**Next**: [Chapter 19: Retrieval Strategies →](chapter-19-retrieval-strategies.md)
