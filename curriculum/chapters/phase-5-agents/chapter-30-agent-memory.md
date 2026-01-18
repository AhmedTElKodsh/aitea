# Chapter 30: Agent Memory & Context Management — The Elephant in the Room

<!--
METADATA
Phase: 5 - Agents
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 29 (Tool Calling), Chapter 24 (Basic Memory)
Builds Toward: LangGraph (Ch 31), Multi-Agent (Ch 43)
Correctness Properties: P25 (Context Continuity), P41 (Memory Retrieval Relevance)
Project Thread: Memory Architecture

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You have a whiteboard. You write everything you do on it.
Eventually, the whiteboard gets full. You can't write anymore.
**Option A**: Buy a bigger whiteboard? (Expensive, and even that fills up).
**Option B**: Erase the old stuff. (But you forget it).
**Option C**: Take a photo of the old stuff, file it away, and erase the board. When you need it, you look at the photo.

**Context Management** is Option C.
LLMs have a "Context Window" (the whiteboard). If you feed it 100,000 tokens of chat history, it gets slow, expensive, and confused.
We need to **Prune** (erase irrelevant stuff) and **Archive** (store important stuff in a Vector DB).

**By the end of this chapter**, you'll build an Agent that can chat "forever" without crashing or going broke. 🧠

---

## Prerequisites Check

```bash
# We need tiktoken for counting tokens
pip install tiktoken langchain-chroma
```

---

## The Story: The "Expensive" Friend

### The Problem (Context Overflow)

You deploy a chatbot.
User A chats for 3 hours. The history is 50,000 tokens.
Each new message sends *all* 50,000 tokens back to OpenAI.
Cost: $0.50 per message. Speed: 10 seconds.
**Result**: Bankruptcy. 💸

### The Solution (Pruning & Recall)

1.  **Short-Term**: Keep only the last 10 messages in active RAM.
2.  **Long-Term**: If the user asks about "that thing we discussed an hour ago", search the Vector DB for the old chat logs.

---

## Part 1: Context Pruning (The Trimmer)

LangChain provides `trim_messages` to intelligently cut history.

### 🔬 Try This! (Hands-On Practice #1)

**Create `trimming.py`**:

```python
from langchain_core.messages import HumanMessage, AIMessage, trim_messages, SystemMessage
from langchain_openai import ChatOpenAI

# 1. Create a Long History
messages = [SystemMessage("You are a bot.")]
for i in range(100):
    messages.append(HumanMessage(f"User message {i}"))
    messages.append(AIMessage(f"AI response {i}"))

print(f"Original Length: {len(messages)}")

# 2. Trim Strategy
# Keep last 5 messages. Always keep SystemMessage (index 0).
trimmer = trim_messages(
    strategy="last",
    token_counter=ChatOpenAI(model="gpt-4o-mini"), 
    max_tokens=50, # Rough estimate limit
    start_on="human", # Ensure we don't cut in middle of a pair
    include_system=True
)

# 3. Trim
trimmed = trimmer.invoke(messages)

print(f"Trimmed Length: {len(trimmed)}")
print("--- Messages Kept ---")
for m in trimmed:
    print(f"{m.type}: {m.content}")
```

**Run it**.
You should see the System Message + the last few messages. The middle 90+ messages are gone from the *Prompt*, but we can still keep them in the *Database*.

---

## Part 2: Long-Term Memory (Vector Store)

Now, let's store the chat history in ChromaDB so we can recall it later.

### 🔬 Try This! (Hands-On Practice #2)

**Create `vector_memory.py`**:

```python
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import time

# 1. Setup Vector Store
vectorstore = Chroma(
    collection_name="chat_memory",
    embedding_function=OpenAIEmbeddings()
)

# 2. Simulate "Archiving" a conversation
chats = [
    "User: My favorite color is blue.",
    "AI: Nice.",
    "User: I own a Honda Civic.",
    "AI: Cool car.",
    "User: My dog's name is Rex.",
    "AI: Cute."
]

# We store each turn as a document
print("Archiving memories...")
docs = [Document(page_content=c, metadata={"timestamp": time.time()}) for c in chats]
vectorstore.add_documents(docs)

# 3. Recall
query = "What car do I have?"
print(f"\nQuery: {query}")

# Search
results = vectorstore.similarity_search(query, k=1)
print(f"Found Memory: {results[0].page_content}")
```

**Run it**.
It should find "I own a Honda Civic". This is RAG, but applied to *History*.

---

## Part 3: The Memory-Augmented Agent

Let's combine Tools + Short-Term Memory + Long-Term Recall.

### 🔬 Try This! (Hands-On Practice #3)

**Create `smart_agent.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# 1. The Recall Tool
vectorstore = Chroma(collection_name="agent_mem", embedding_function=OpenAIEmbeddings())

@tool
def recall_memory(query: str) -> str:
    """Search through past conversations for details."""
    print(f"🧠 (Thinking about: {query})")
    results = vectorstore.similarity_search(query, k=2)
    if not results:
        return "No memory found."
    return "\n".join([d.page_content for d in results])

@tool
def save_memory(info: str) -> str:
    """Save an important fact to long-term memory."""
    print(f"💾 (Saving: {info})")
    vectorstore.add_texts([info])
    return "Saved."

tools = [recall_memory, save_memory]

# 2. The Agent
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a thoughtful assistant with long-term memory. "
               "Use 'save_memory' to remember facts. "
               "Use 'recall_memory' to answer questions about the past."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 3. Run Simulation
print("---")
executor.invoke({"input": "My favorite food is Pizza."})

print("\n---")
# We start a NEW interaction (no history passed in prompt!)
# The agent must use the TOOL to remember.
executor.invoke({"input": "What is my favorite food?"})
```

**Run it**.
1. It saves "Pizza".
2. It uses `recall_memory("favorite food")` -> gets "Pizza" -> Answers "Pizza".

It remembered *without* the chat history being passed in the context window!

---

## Common Mistakes

### Mistake #1: Over-Saving
If the agent saves "Hi" and "How are you", the memory gets polluted.
**Fix**: Prompt engineering. "Only save *facts* or *preferences*."

### Mistake #2: Vector Drift
"My favorite food is Pizza." (Day 1). "My favorite food is Sushi." (Day 2).
The Vector Store finds both.
**Fix**: Use timestamps metadata. Filter by recent, or ask LLM to resolve conflicts.

### Mistake #3: Infinite Loops
Agent tries to recall -> finds nothing -> tries to recall -> ...
**Fix**: `max_iterations` on AgentExecutor.

---

## Quick Reference Card

### Memory Architecture

| Type | Implementation | Pros | Cons |
|------|----------------|------|------|
| **Short-Term** | List of Messages (RAM) | Fast, Full Context | Expensive, Limited Size |
| **Long-Term** | Vector Store (Chroma) | Infinite Size, Cheap | Fuzzy retrieval, slower |

---

## Verification (REQUIRED SECTION)

We need to verify **P41 (Memory Relevance)**.

**Create `verify_memory_agent.py`**:

```python
"""
Verification script for Chapter 30.
Property P41: Relevance.
"""
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import shutil
import sys

print("🧪 Running Memory Agent Verification...\n")

DB_PATH = "./verify_mem_db"
# Clean start
try:
    shutil.rmtree(DB_PATH)
except:
    pass

vectorstore = Chroma(
    collection_name="verify_mem",
    embedding_function=OpenAIEmbeddings(),
    persist_directory=DB_PATH
)

# 1. Plant Memory
secret = "The secret code is BLUEBERRY."
vectorstore.add_texts([secret])

# 2. Recall
print("Test 1: Recall Accuracy...")
results = vectorstore.similarity_search("What is the code?", k=1)

if "BLUEBERRY" in results[0].page_content:
    print("✅ P41 Passed: Retrieved highly relevant memory.")
else:
    print(f"❌ Failed: Retrieved {results[0].page_content}")
    sys.exit(1)

# Cleanup
shutil.rmtree(DB_PATH)
print("\n🎉 Chapter 30 Complete! You have built a sentient being (sort of).")
```

**Run it:** `python verify_memory_agent.py`

---

## Summary

**What you learned:**

1. ✅ **The Context Bottleneck**: Why we can't just keep adding messages.
2. ✅ **Pruning**: Strategically forgetting the middle.
3. ✅ **Vector Memory**: Using the database as a "hippocampus".
4. ✅ **Memory Tools**: Giving the agent active control over its own memory.
5. ✅ **Architecture**: Combining Short-Term (Prompt) + Long-Term (Vector) memory.

**Key Takeaway**: A smart agent isn't one that knows everything. It's one that knows *where to look* for what it forgot.

**Skills unlocked**: 🎯
- Memory Systems Design
- Cognitive Architecture
- Long-term State Management

**Looking ahead**: Congratulations! You have finished **Phase 5: Agents**.
You now have the building blocks: Clients, RAG, Chains, and Agents.
In **Phase 6: LangGraph**, we will take "Agents" to the next level. We will build **State Machines** to handle complex, multi-step workflows that standard Agents can't handle.

---

**Next**: [Phase 6: LangGraph (Chapter 31) →](../phase-6-langgraph/chapter-31-langgraph-state-machines.md)
