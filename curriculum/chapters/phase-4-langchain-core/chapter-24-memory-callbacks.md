# Chapter 24: Memory & Callbacks — The Brain's RAM

<!--
METADATA
Phase: 4 - LangChain Core
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐
Type: Implementation
Prerequisites: Chapter 20 (Conversational RAG)
Builds Toward: Agents (Ch 26)
Correctness Properties: P25 (Context Continuity), P32 (Callback Order)
Project Thread: State Management

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're watching a movie, but every 5 minutes, you forget everything that happened before.
"Who is that guy?" "Why are they running?"
You'd be annoying to watch a movie with. 🍿

LLMs are like that. They are **stateless**. They forget the previous message the instant they generate a response.
**Memory** is the trick of feeding the conversation history *back* into the prompt, so the AI "remembers".

But what if the history gets too long?
What if you want to know *how much* it costs to remember?
That's where **Memory Strategies** and **Callbacks** come in.

**By the end of this chapter**, you'll build a chatbot that remembers you, summarizes old conversations to save money, and tells you exactly how many tokens it's eating. 🧠

---

## Prerequisites Check

```bash
pip install langchain langchain-openai
```

---

## The Story: The "Infinite" Scroll

### The Problem (Token Overflow)

You built a chatbot.
User: "Hi" (History: 2 tokens)
... 1 hour later ...
User: "Cool." (History: 20,000 tokens)
**Crash.** `ContextWindowExceededError`.

You can't just keep appending messages forever. You need a strategy.

### The Solution (Summarization)

Instead of storing:
"Hi." "Hello." "How are you?" "Good." "What's up?" "Not much."

We store a **Summary**:
"User and AI exchanged pleasantries."

This compresses 50 tokens into 5.

---

## Part 1: Managing History (The Raw Data)

LangChain provides `ChatMessageHistory` to store messages in RAM (or a DB).

### 🔬 Try This! (Hands-On Practice #1)

**Create `basic_memory.py`**:

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# 1. Initialize History
history = InMemoryChatMessageHistory()

# 2. Add Messages
history.add_user_message("Hi, I'm Ahmed.")
history.add_ai_message("Hello Ahmed!")

# 3. Retrieve
print(f"Messages: {len(history.messages)}")
print(f"Last: {history.messages[-1].content}")

# 4. Use in Prompt (Manual injection)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

formatted = prompt.format(
    history=history.messages,
    input="What is my name?"
)
print("\nFormatted Prompt (Snippet):")
print(formatted)
```

**Run it**.
This is the raw mechanism. We simply inject the list of messages into the prompt.

---

## Part 2: Automatic History (RunnableWithMessageHistory)

Manually passing `history=` every time is annoying.
`RunnableWithMessageHistory` automates it. It keeps track of "Sessions".

### 🔬 Try This! (Hands-On Practice #2)

**Create `auto_memory.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful bot."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = prompt | model | StrOutputParser()

# 1. Define the Store (Where history lives)
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 2. Wrap the Chain
conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 3. Chat with Session "A"
print("--- Session A ---")
print(conversation.invoke(
    {"input": "My name is Bob."}, 
    config={"configurable": {"session_id": "A"}}
))
print(conversation.invoke(
    {"input": "What is my name?"}, 
    config={"configurable": {"session_id": "A"}}
)) # Should say Bob

# 4. Chat with Session "B" (New User)
print("\n--- Session B ---")
print(conversation.invoke(
    {"input": "What is my name?"}, 
    config={"configurable": {"session_id": "B"}}
)) # Should NOT know Bob
```

**Run it**.
Session B doesn't know about Session A. This is how you handle multiple users!

---

## Part 3: Callbacks (Spying on the AI)

How do you debug a chain? How do you count tokens?
**Callbacks** hook into the lifecycle: `on_chain_start`, `on_llm_end`, etc.

### 🔬 Try This! (Hands-On Practice #3)

Let's build a custom logger.

**Create `custom_callback.py`**:

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI

class MyLogger(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"🟢 Starting LLM...")
        
    def on_llm_end(self, response, **kwargs):
        print(f"🔴 Finished LLM.")
        token_usage = response.llm_output['token_usage']
        print(f"   Tokens used: {token_usage['total_tokens']}")

model = ChatOpenAI(
    model="gpt-4o-mini",
    callbacks=[MyLogger()] # Attach callback here
)

print("Invoking...")
model.invoke("Hi")
```

**Run it**.
You should see the green and red logs. This is how tools like LangSmith work under the hood!

---

## Common Mistakes

### Mistake #1: Infinite Session Growth
In `auto_memory.py`, the `store` dict grows forever. In production, use Redis or Postgres to store history, and implement a TTL (Time To Live).

### Mistake #2: Wrong Keys
If `input_messages_key="input"` doesn't match your prompt's variable `("human", "{input}")`, it crashes.

### Mistake #3: Callback Thread Safety
If you reuse the same Callback object across parallel threads, ensure it is thread-safe (e.g., using locks for printing).

---

## Quick Reference Card

### RunnableWithMessageHistory

```python
chain_with_history = RunnableWithMessageHistory(
    runnable=my_chain,
    get_session_history=get_history_func,
    input_messages_key="question",
    history_messages_key="chat_history"
)
```

---

## Verification (REQUIRED SECTION)

We need to verify **P25 (Context Continuity)** and **P32 (Callback Order)**.

**Create `verify_memory.py`**:

```python
"""
Verification script for Chapter 24.
Properties: P25 (Memory), P32 (Callbacks).
"""
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import sys

print("🧪 Running Memory Verification...\n")

# P25: Context Continuity
print("Test 1: Memory Persistence...")
history = InMemoryChatMessageHistory()
history.add_user_message("Secret code is 1234")
history.add_ai_message("Ok, saved.")

# Manual prompt construction to test if history is accessible
messages = history.messages + [HumanMessage(content="What is the code?")]
# Use a simple model invocation
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
response = model.invoke(messages)

if "1234" in response.content:
    print("✅ P25 Passed: AI remembers context from history.")
else:
    print(f"❌ Failed: AI forgot code. Got: {response.content}")
    sys.exit(1)

# P32: Callback Order
print("Test 2: Callback Execution...")
log = []

class TestCallback(BaseCallbackHandler):
    def on_llm_start(self, *args, **kwargs):
        log.append("start")
    def on_llm_end(self, *args, **kwargs):
        log.append("end")

model_cb = ChatOpenAI(model="gpt-4o-mini", callbacks=[TestCallback()])
model_cb.invoke("Hi")

if log == ["start", "end"]:
    print("✅ P32 Passed: Callbacks fired in correct order.")
else:
    print(f"❌ Failed: Log={log}")
    sys.exit(1)

print("\n🎉 Chapter 24 Complete! You have mastering state.")
```

**Run it:** `python verify_memory.py`

---

## Summary

**What you learned:**

1. ✅ **State**: LLMs are stateless; Systems are stateful.
2. ✅ **History Objects**: Storing messages in memory.
3. ✅ **Sessions**: Managing multiple users with `RunnableWithMessageHistory`.
4. ✅ **Callbacks**: The ability to inspect execution at runtime.
5. ✅ **Token Tracking**: Why measuring usage matters.

**Key Takeaway**: Memory turns a "Text Generator" into a "Conversation Partner."

**Skills unlocked**: 🎯
- State Management
- Session Handling
- Observability Implementation

**Looking ahead**: We have memory. We have tools. We have logic.
In **Chapter 25**, we will learn **Output Parsers** deeply to ensure our Agents always speak perfectly formatted computer languages.

---

**Next**: [Chapter 25: Output Parsers →](chapter-25-output-parsers.md)
