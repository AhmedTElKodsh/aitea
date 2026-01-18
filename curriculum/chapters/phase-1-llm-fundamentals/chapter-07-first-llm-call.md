# Chapter 7: Your First LLM Call — Hello, Intelligence!

<!--
METADATA
Phase: 1 - LLM Fundamentals
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐
Type: Implementation
Prerequisites: Chapter 1 (Env Setup)
Builds Toward: Multi-Provider Client (Ch 8), Chatbots
Correctness Properties: P1 (API Credentials)
Project Thread: LLM Integration

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You want to build a program that summarizes movie plots.
In the "Old World," you'd have to write rules: "If text contains 'alien', maybe sci-fi?" "If 'love', maybe romance?" It would take years and still suck. 😫

**The New World**: You just *ask*.
"Hey computer, summarize this text." And it does. Perfectly.

This isn't magic (well, it feels like it). It's an **LLM API Call**.
It's the "Hello World" of AI Engineering. Once you master this single function call, you stop being just a coder and start being an AI Engineer.

**By the end of this chapter**, you'll have a Python script that talks to a supercomputer and gets intelligent answers back. Let's make some magic happen! ✨

---

## Prerequisites Check

We need your environment ready.

```bash
# 1. Check Python
python --version  # Should be 3.10+

# 2. Check Virtual Env
# Windows: where python -> should be inside .venv
# Mac/Linux: which python -> should be inside .venv
```

**If you need an API Key**:
You will need an OpenAI API Key for this chapter.
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up/Login
3. Create a new secret key
4. **SAVE IT IMMEDIATELY** (you won't see it again)

*Don't have a key or credits? Don't worry! We'll show you how to use a local Mock LLM later.*

---

## The Story: From Rules to Reasoning

### The Problem (The Rule Trap)

Imagine building a "Vibe Checker" for a social media app. You want to know if a post is happy or sad.

**The "Old" Way (Hardcoding)**:
```python
def check_vibe(text):
    if "happy" in text or "yay" in text:
        return "Positive"
    elif "sad" in text or "cry" in text:
        return "Negative"
    else:
        return "Neutral"
```

**Why this breaks**:
- Input: "I'm not happy." → Returns "Positive" (because "happy" is in it). 🤦‍♂️
- Input: "I just dropped my ice cream." → Returns "Neutral" (no keywords found).

You can't write `if` statements for the whole human language.

### The Elegant Solution (The API Call)

We don't write rules. We send the *intent* to an LLM.

```python
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Is 'I dropped my ice cream' happy or sad?"}]
)
# Returns: "Sad"
```

It understands context, negation ("not happy"), and slang. It reasons.

---

## Part 1: The Setup (The Passport)

To talk to the API, we need to authenticate. We use the `.env` file we set up in Chapter 1.

### 🔬 Try This! (Hands-On Practice #1)

Let's configure the credentials safely.

**Step 1: Install the OpenAI library**
```bash
pip install openai python-dotenv
```

**Step 2: Update your `.env` file**
Open the `.env` file in your project root. Add your key:

```env
OPENAI_API_KEY=sk-proj-your-actual-key-here-12345
```

**Step 3: Test the connection**
Create a file named `test_connection.py`:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load secrets
load_dotenv()

# 2. Get the key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Error: OPENAI_API_KEY not found in .env")
    print("Did you rename .env.example to .env?")
else:
    print(f"✅ Key found! Starts with: {api_key[:8]}...")
    
    # 3. Create the client
    try:
        client = OpenAI() # Automatically looks for OPENAI_API_KEY env var
        print("✅ Client initialized successfully!")
    except Exception as e:
        print(f"❌ Client failed: {e}")
```

**Run it:** `python test_connection.py`

<details>
<summary>💡 Security Tip (Important!)</summary>

Never, EVER paste your key directly into the python file like `client = OpenAI(api_key="sk-...")`.
If you accidentally push that to GitHub, hackers will find it in seconds. Always use `os.getenv`.
</details>

---

## Part 2: The Chat Completion (Sending the Letter)

### The `messages` Structure

LLMs don't just take "text". They take a **list of messages**. Think of it like a play script.

**The Cast:**
1. **System**: The Director. Sets the rules ("You are a helpful assistant", "You are a pirate").
2. **User**: You. The person asking questions.
3. **Assistant**: The AI. The one replying.

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]
```

### 🔬 Try This! (Hands-On Practice #2)

Let's make the call!

**Create `first_chat.py`**:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def chat_with_ai(prompt):
    print(f"🤔 Asking AI: '{prompt}'...")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Or "gpt-3.5-turbo" (cheaper)
        messages=[
            {"role": "system", "content": "You are a witty comedian."}, # The Persona
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the actual text
    answer = response.choices[0].message.content
    print(f"🤖 AI says: {answer}")

# Try it out
chat_with_ai("Why did the chicken cross the road?")
```

**Run it:** `python first_chat.py`

**Expected Output**:
Something funny! Because we told the System to be a "witty comedian".

---

## Part 3: The Knobs (Temperature & Tokens)

You can control *how* the AI answers.

### Temperature (Creativity)
- **0.0**: Cold, precise, deterministic. (Good for math, code, facts).
- **1.0**: Hot, creative, random. (Good for stories, brainstorming).

### Max Tokens (Length)
- Controls how long the answer can be. Prevents the AI from writing a novel when you just wanted a sentence.

### 🔬 Try This! (Hands-On Practice #3)

Let's experiment with temperature.

**Create `temperature_test.py`**:

```python
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def get_creative_answer(temp):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Complete this sentence: The sky is..."}],
        temperature=temp,
        max_tokens=10 # Keep it short
    )
    return response.choices[0].message.content

print("🥶 Low Temp (0.0):")
print(get_creative_answer(0.0))
print(get_creative_answer(0.0)) # Should be identical (or very close)

print("\n🔥 High Temp (1.5):")
print(get_creative_answer(1.5))
print(get_creative_answer(1.5)) # Should be wild/different
```

**Run it**. Notice how `0.0` is boring/consistent, and `1.5` gets weird?

---

## Common Mistakes (Learn from Others!)

### Mistake #1: Not handling errors

```python
# ❌ Naive
response = client.chat.completions.create(...)

# ✅ Robust
try:
    response = client.chat.completions.create(...)
except Exception as e:
    print(f"API Error: {e}")
```
APIs go down. Internet fails. Keys expire. Always handle errors (we'll go deep on this in Chapter 12).

### Mistake #2: Forgetting `load_dotenv()`

If you get `api_key=None` errors, 99% of the time you forgot `from dotenv import load_dotenv; load_dotenv()`.

### Mistake #3: Ignoring Costs

Every time you run the script, it costs a tiny fraction of a cent.
**Rule**: Don't put API calls inside infinite `while True` loops without a break! 💸

---

## Quick Reference Card

### The Basic Call

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Be helpful."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7
)
content = response.choices[0].message.content
```

### Models Cheatsheet

| Model | Use Case | Speed | Cost |
|-------|----------|-------|------|
| `gpt-4o` | Complex reasoning, coding | Fast | Moderate |
| `gpt-4o-mini` | Simple tasks, chat | Very Fast | Very Low |
| `gpt-3.5-turbo` | Legacy simple tasks | Fast | Low |

---

## Verification (REQUIRED SECTION)

Let's ensure your API integration is solid.

**Create `verify_llm.py`**:

```python
"""
Verification script for Chapter 7.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

print("🧪 Running LLM Verification...\n")

# 1. Check Env
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: Missing OPENAI_API_KEY in .env")
    exit(1)
print("✅ Environment variables loaded")

# 2. Check Client
try:
    client = OpenAI()
    print("✅ OpenAI Client initialized")
except Exception as e:
    print(f"❌ Failed to init client: {e}")
    exit(1)

# 3. Make a minimal call
print("📞 Calling API (this might take a second)...")
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say exactly: 'System Operational'"}],
        max_tokens=10,
        temperature=0
    )
    content = response.choices[0].message.content
    print(f"🤖 API Response: {content}")
    
    if "System Operational" in content:
        print("✅ Validation Successful! You are connected.")
    else:
        print("⚠️  Warning: Unexpected response content.")
        
except Exception as e:
    print(f"❌ API Call Failed: {e}")
    print("Check your API key, internet connection, or billing status.")
    exit(1)
```

**Run it:** `python verify_llm.py`

---

## Summary

**What you learned:**

1. ✅ **LLMs aren't magic**: They are APIs that accept a list of messages and return a completion.
2. ✅ **Roles matter**: `System` sets the behavior, `User` gives the task.
3. ✅ **Configuration**: `Temperature` controls randomness; `Max Tokens` controls length.
4. ✅ **Security**: Never hardcode keys; use `.env`.
5. ✅ **The Loop**: Request → Processing → Response.

**Key Takeaway**: You just unlocked the ability to add "reasoning" to any Python script. A function that can summarize, translate, joke, or code is now just one API call away.

**Skills unlocked**: 🎯
- OpenAI API
- Environment Security
- Prompt Basics

**Looking ahead**: In **Chapter 8**, we'll stop relying on just OpenAI. We'll build a **Multi-Provider Client** that can switch between OpenAI, Anthropic, and local models (Ollama) instantly!

---

**Next**: [Chapter 8: Multi-Provider LLM Client →](chapter-08-multi-provider-client.md)
