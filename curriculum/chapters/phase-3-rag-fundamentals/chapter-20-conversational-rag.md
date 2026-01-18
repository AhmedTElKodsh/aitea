# Chapter 20: Conversational RAG — Remembering Context

<!--
METADATA
Phase: 3 - RAG Fundamentals
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 18 (LCEL)
Builds Toward: Agents (Ch 26), Memory (Ch 24)
Correctness Properties: P25 (Context Continuity), P26 (Pronoun Resolution)
Project Thread: Conversational Interface

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You meet a friend.
You: "I bought a new car."
Friend: "Cool!"
You: "It's red."
Friend: "What is red?" 😐

That would be weird, right? But that's exactly how our RAG system works right now. Every time you ask a question, the LLM treats you like a total stranger. It has **amnesia**.

If you ask: *"Who is the CEO?"* -> *"Jane Doe."*
Then ask: *"How old is she?"*
The Retrieval system searches for documents containing "How old is she?".
It finds nothing. Because the documents say "Jane Doe", not "she".

**By the end of this chapter**, you will fix the amnesia. You'll build a system that rewrites questions based on history, so "How old is she?" becomes "How old is Jane Doe?", and the search actually works. 🧠

---

## Prerequisites Check

```bash
# Verify LangChain
pip show langchain
```

---

## The Story: The "Broken" Follow-up

### The Problem (Pronouns)

User: "Tell me about the iPhone 15."
Bot: "It has a titanium design."
User: "How much does **it** cost?"

**Behind the Scenes:**
1. Retriever searches for "How much does **it** cost?"
2. Documents found: "It costs $5 to repair..." (Irrelevant).
3. Bot Answer: "I don't know."

### The Solution (Contextualizing)

We need a separate LLM step **before** retrieval.
**Task**: Take the chat history and the new question. Rephrase the question to be standalone.

History:
- Human: Tell me about iPhone 15.
- AI: It has titanium design.
New Input: "How much does it cost?"

**Rewritten Query**: "How much does the iPhone 15 cost?"

Now the retriever searches for "iPhone 15 cost". **Success.**

---

## Part 1: The Chat History

First, we need a way to store messages.

### 🔬 Try This! (Hands-On Practice #1)

Let's represent history.

**Create `history_test.py`**:

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 1. Create a conversation
chat_history = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Hi, my name is Ahmed."),
    AIMessage(content="Hello Ahmed! How can I help?"),
    HumanMessage(content="What is my name?")
]

print(f"History Length: {len(chat_history)}")
print(f"Last User: {chat_history[-1].content}")
```

**Run it**. Simple enough.

---

## Part 2: The Rephrase Chain

Now for the magic. We build a chain just for rewriting.

### 🔬 Try This! (Hands-On Practice #2)

**Create `rephrase_chain.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# The Prompt
# Note: We stick the history inside the prompt!
rephrase_prompt = ChatPromptTemplate.from_messages([
    ("system", "Given a chat history and the latest user question "
               "which might reference context in the chat history, "
               "formulate a standalone question which can be understood "
               "without the chat history. Do NOT answer the question, "
               "just reformulate it if needed and otherwise return it as is."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

rephrase_chain = rephrase_prompt | model | StrOutputParser()

# Test Data
history = [
    HumanMessage(content="Tell me about the Eiffel Tower."),
    AIMessage(content="It is a wrought-iron lattice tower in Paris.")
]

question = "When was it built?"

print(f"Original: {question}")
rewritten = rephrase_chain.invoke({
    "chat_history": history,
    "question": question
})
print(f"Rewritten: {rewritten}")
```

**Run it**.
Expected Output: *"When was the Eiffel Tower built?"*

---

## Part 3: The Full Conversational RAG

Now we combine:
1. Rephrase Chain
2. Retriever
3. Answer Chain

### 🔬 Try This! (Hands-On Practice #3)

**Create `conversational_rag.py`**:

```python
from langchain_core.runnables import RunnablePassthrough, RunnableBranch
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

# 1. Setup Mock Retriever (Simulating Ch 14)
def fake_retriever(query):
    print(f"🔎 Searching for: '{query}'")
    if "eiffel" in query.lower():
        return "The Eiffel Tower was built in 1889."
    return "No info found."

# 2. Setup Components
model = ChatOpenAI(model="gpt-4o-mini")

# 3. Rephrase Chain (From Part 2)
rephrase_system = "Given chat history, rewrite the question to be standalone."
rephrase_prompt = ChatPromptTemplate.from_messages([
    ("system", rephrase_system),
    MessagesPlaceholder("chat_history"),
    ("human", "{question}"),
])
rephrase_chain = rephrase_prompt | model | StrOutputParser()

# 4. The Answer Chain
answer_system = "Answer the question based on the context: {context}"
answer_prompt = ChatPromptTemplate.from_messages([
    ("system", answer_system),
    MessagesPlaceholder("chat_history"),
    ("human", "{question}"),
])

# 5. The Master Chain (LCEL Logic)
# Logic: If history exists, rewrite question. Else, use original.
def get_search_query(input_dict):
    if input_dict.get("chat_history"):
        return rephrase_chain
    else:
        return input_dict["question"]

retriever_chain = RunnablePassthrough.assign(
    context=get_search_query | fake_retriever
)

final_chain = retriever_chain | answer_prompt | model | StrOutputParser()

# 6. Test it
history = [
    HumanMessage(content="Tell me about the Eiffel Tower."),
    AIMessage(content="It is in Paris.")
]

print("---" + " Conversational Query" + " ---")
response = final_chain.invoke({
    "chat_history": history,
    "question": "When was it built?"
})
print(f"🤖 Answer: {response}")
```

**Run it**.
Notice the "Searching for" log. It should search for "Eiffel Tower", NOT "it".

---

## Common Mistakes

### Mistake #1: Rewriting EVERYTHING
If the user says "Hello", the rephraser might try to turn it into a query.
**Fix**: Tune the system prompt: "If the input is just a greeting, return it as is."

### Mistake #2: Passing History to Retriever
The Vector Store doesn't understand `[HumanMessage, AIMessage]`. It only understands strings. That's why the **Rephrase Step** is mandatory—it flattens history into a single string query.

### Mistake #3: Infinite History
If history gets too long, you hit token limits.
**Fix**: `history[-10:]` (Keep only last 10 messages). We'll cover advanced memory management in Chapter 24.

---

## Quick Reference Card

### Conversational Flow

```
User Input ("It?") + History
       ⬇
[Rephrase Chain] -> "iPhone 15?"
       ⬇
[Retriever] -> Context
       ⬇
[Answer Chain] (Input + Context + History) -> "It costs $999."
```

---

## Verification (REQUIRED SECTION)

We need to prove **P26 (Pronoun Resolution)**.

**Create `verify_conversation.py`**:

```python
"""
Verification script for Chapter 20.
Property P26: Pronoun Resolution.
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
import sys

print("🧪 Running Conversation Verification...\n")

# Setup Rephraser
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Rewrite the question to be standalone."),
    MessagesPlaceholder("chat_history"),
    ("human", "{question}"),
])
chain = prompt | model | StrOutputParser()

# Scenario
history = [
    HumanMessage("Who is the CEO of Tesla?"),
    AIMessage("Elon Musk.")
]
question = "How old is he?"

# Test P26
print(f"Original: {question}")
rewritten = chain.invoke({"chat_history": history, "question": question})
print(f"Rewritten: {rewritten}")

# Check if "he" became "Elon Musk" (or "CEO of Tesla")
if "Elon" in rewritten or "Musk" in rewritten or "CEO" in rewritten:
    print("✅ P26 Passed: Pronoun resolved correctly.")
else:
    print(f"❌ Failed: Rewritten query ambiguous: '{rewritten}'")
    sys.exit(1)

print("\n🎉 Chapter 20 Complete! Your AI has memory.")
```

**Run it:** `python verify_conversation.py`

---

## Summary

**What you learned:**

1. ✅ **Statelessness**: LLMs reset every call. We must manually inject history.
2. ✅ **Query Transformation**: Converting "It" into "The Object" is crucial for retrieval.
3. ✅ **History Aware Retrievers**: The pattern of Rephrase -> Retrieve -> Answer.
4. ✅ **Chat Prompt Templates**: Using `MessagesPlaceholder` to insert history dynamically.
5. ✅ **User Intent**: Searching for what they *mean*, not what they *typed*.

**Key Takeaway**: A chatbot is just a RAG system that rewrites its own queries.

**Skills unlocked**: 🎯
- Conversational Design
- Query Rewriting
- History Management

**Looking ahead**: We have a great retrieval system. But how do we know if it's actually *good*? Is it retrieving the right docs? Is the answer accurate? In **Chapter 21**, we will learn **RAG Evaluation** to measure performance scientifically.

---

**Next**: [Chapter 21: RAG Evaluation →](chapter-21-rag-evaluation.md)
