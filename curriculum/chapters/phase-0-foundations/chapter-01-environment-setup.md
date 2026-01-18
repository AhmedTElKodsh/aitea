# Chapter 1: Environment & Project Setup — The Foundation of Everything

<!--
METADATA
Phase: 0 - Shared Foundation
Time: 1 hour (20 min reading + 40 min hands-on)
Difficulty: ⭐
Type: Foundation
Prerequisites: None
Builds Toward: Every subsequent chapter
Correctness Properties: None (Setup phase)
Project Thread: Project Initialization

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You've just spent 3 weeks building the coolest AI app ever. It works perfectly on your laptop. You send it to your boss (or client), they run it, and... *CRASH*. 💥

"Module not found." "Version mismatch." "KeyError: 'OPENAI_API_KEY'".

You spend the next 3 days debugging *their* computer instead of improving your code. 😫

**This is the "it works on my machine" nightmare.**

But here's the good news: **Professional engineers don't have this problem.**

By the end of this chapter, you'll have a bulletproof setup that works anywhere—your laptop, your friend's PC, or a production server—guaranteed. No more "it works on my machine" excuses. Just rock-solid code. 🚀

---

## Prerequisites Check

Since this is Chapter 1, you just need Python installed!

```bash
# Check your python version
python --version
# OR
python3 --version
```

**If this prints "Python 3.10" (or higher)**, you're good to go! ✅

**If it fails**, please install Python 3.10+ from python.org before continuing.

**You should feel comfortable with**: 
- Basic command line usage (cd, ls/dir)
- Using a code editor (VS Code recommended)

---

## The Story: Why Setup Matters

### The Problem (The "Dependency Hell")

Imagine you're working on two projects:
- **Project A** (Old stable app) needs `langchain==0.1.0`
- **Project B** (New shiny app) needs `langchain==0.2.0`

If you just install everything globally (`pip install langchain`), you have a problem. You can't have two versions of the same package installed globally. Installing one breaks the other.

This is called **Dependency Hell**. 🔥

### The Naive Solution

> "I'll just uninstall and reinstall packages every time I switch projects!"

**Why This Breaks**:
- ❌ It's slow.
- ❌ You'll forget what version worked.
- ❌ Eventually, you'll break your system tools that rely on Python.

### The Elegant Solution (Virtual Environments)

Enter the **Virtual Environment**.

Think of it like a soundproof room for your project. Everything you do inside stays inside.
- Project A gets its own room with `langchain==0.1.0`.
- Project B gets its own room with `langchain==0.2.0`.
- Your system Python stays clean.

And for secrets (like API keys)? We use **Environment Variables**. Never hardcode secrets!

---

## Part 1: Virtual Environments (Your Project's Home)

### What is it, really?

**Analogy: Apartments in a Building** 🏢

Think of your computer as an apartment building.
- **Global Python** is the hallway. Everyone uses it.
- **Virtual Environments** are individual apartments.

If Project A paints their walls neon pink (installs a specific library), Project B's apartment doesn't change. Each project lives in isolation.

### 🔬 Try This! (Hands-On Practice #1)

Let's create your first virtual environment.

**Challenge**: Create an isolated environment for our AI Knowledge Base project.

**Step 1: Create the folder and env**
```bash
# 1. Make project folder
mkdir ai-knowledge-base
cd ai-knowledge-base

# 2. Create virtual environment
# Windows:
python -m venv .venv

# Mac/Linux:
python3 -m venv .venv
```

**Step 2: Activate it**
```bash
# Windows (Command Prompt):
.venv\Scripts\activate

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Mac/Linux:
source .venv/bin/activate
```

**Step 3: Verify**
You should see `(.venv)` in your prompt!

```bash
# Check where python runs from
# Windows:
where python
# Mac/Linux:
which python
```

**Success Criteria**: The path should point to `.venv`, NOT your system Python. ✅

---

## Part 2: Configuration & Secrets (Keeping It Safe)

### The "Secret" Problem

You need an API key to call OpenAI.

**❌ Naive Approach (The Danger Zone)**
```python
# DO NOT DO THIS
api_key = "sk-proj-12345secret"
```

If you commit this to GitHub, bots will find it in seconds, steal your credits, and you'll wake up to a $5,000 bill. 💸

**✅ The Professional Approach (.env)**
We store secrets in a hidden file called `.env` and load them into variables.

### 🔬 Try This! (Hands-On Practice #2)

Let's set up secure configuration.

**Challenge**: Create your `.env` file and load it.

**Step 1: Install `python-dotenv`**
```bash
pip install python-dotenv
```

**Step 2: Create a file named `.env`**
```bash
# .env content:
MY_SECRET_KEY=super_secret_value_123
LOG_LEVEL=INFO
```

**Step 3: Create `test_env.py`**
```python
# test_env.py
import os
from dotenv import load_dotenv

# Load secrets
load_dotenv()

secret = os.getenv("MY_SECRET_KEY")
print(f"My secret is: {secret}")
```

**Step 4: Run it**
```bash
python test_env.py
```

**Expected Output**: `My secret is: super_secret_value_123`

<details>
<summary>💡 Hint (If it prints None)</summary>

Did you name the file exactly `.env`? Not `.env.txt` or `env`?
Did you save the file?
</details>

---

## Part 3: Type-Safe Config (Pydantic Settings)

### Why "Normal" Config Isn't Enough

Using `os.getenv` everywhere is messy.
- You have to repeat the key name (`"MY_SECRET_KEY"`) everywhere.
- What if you need an `int` (like timeout) but env vars are strings?
- What if the key is missing?

**Enter Pydantic Settings**. It handles loading, validation, and type conversion for you.

**Analogy: The Bouncer** 🕵️‍♂️
`os.getenv` is like an unlocked door. Anyone comes in (strings, None, wrong types).
`Pydantic Settings` is a bouncer. "Oh, you're a string? Sorry, I need an Integer. You're missing a key? You can't come in."

### 🔬 Try This! (Hands-On Practice #3)

Let's build a robust configuration system.

**Challenge**: Create a `config.py` that loads settings securely and validates them.

**Step 1: Install dependencies**
```bash
pip install pydantic pydantic-settings
```

**Step 2: Create `config.py`**

```python
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file
load_dotenv()

class OllamaConfig(BaseSettings):
    """Configuration for Ollama LLM."""
    
    # Auto-load env vars starting with OLLAMA_
    model_config = SettingsConfigDict(env_prefix="OLLAMA_", case_sensitive=False)

    cloud_url: str = "https://api.ollama.ai"
    local_url: str = "http://localhost:11434"
    timeout: int = 30  # Auto-converts string "30" to int 30!

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Timeout must be positive!")
        return v

class AppConfig(BaseSettings):
    """Main application config."""
    ollama: OllamaConfig = OllamaConfig()
    log_level: str = "INFO"

# Singleton instance
config = AppConfig()

if __name__ == "__main__":
    # Test it out!
    print(f"✅ Config Loaded!")
    print(f"URL: {config.ollama.local_url}")
    print(f"Timeout: {config.ollama.timeout} (Type: {type(config.ollama.timeout)})")
```

**Step 3: Update your `.env`**
```bash
OLLAMA_TIMEOUT=60
LOG_LEVEL=DEBUG
```

**Step 4: Run it**
```bash
python config.py
```

**Expected Output**:
```
✅ Config Loaded!
URL: http://localhost:11434
Timeout: 60 (Type: <class 'int'>)
```

**See the magic?** You put "60" (string) in `.env`, but got `60` (int) in code! 🎩

---

## Bringing It All Together: Project Structure

Now let's set up the actual structure for our course.

**Challenge**: Initialize the full project skeleton.

**Create this file structure**:
```
ai-knowledge-base/
├── .env                    # Secrets
├── .env.example            # Template (commit this)
├── .gitignore              # Ignore list
├── config.py               # Pydantic config
├── requirements.txt        # Dependencies
└── src/
    └── __init__.py
```

**Your `requirements.txt`**:
```text
python-dotenv==1.0.0
pydantic>=2.5.2
pydantic-settings==2.1.0
```

**Your `.gitignore`** (Crucial!):
```text
# Python
__pycache__/
*.py[cod]
.venv/
virtualenv/

# Env vars (NEVER COMMIT THESE)
.env
.env.local
```

---

## Common Mistakes (Learn from Others!)

### Mistake #1: Committing `.env` to Git 😱

```bash
# ❌ WRONG
git add .env
git commit -m "Add secrets"  # STOP! You just leaked your keys.
```

**The Fix**: Always put `.env` in your `.gitignore` file immediately.

### Mistake #2: Hardcoding Paths

```python
# ❌ WRONG
config_path = "C:\\Users\\Ahmed\\project\\config.yaml"
```

**The Fix**: Use relative paths or environment variables.
```python
# ✅ CORRECT
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "config.yaml")
```

---

## Quick Reference Card

### Pydantic Settings Template

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class MyConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")
    
    api_key: str
    debug: bool = False
    
config = MyConfig()
```

### Virtual Env Cheatsheet

| Action | Windows | Mac/Linux |
|--------|---------|-----------|
| **Create** | `python -m venv .venv` | `python3 -m venv .venv` |
| **Activate** | `.venv\Scripts\activate` | `source .venv/bin/activate` |
| **Install** | `pip install -r requirements.txt` | `pip install -r requirements.txt` |

---

## Verification (REQUIRED SECTION)

Let's verify your environment setup is 100% correct.

**Create a file named `verify_setup.py` and run it:**

```python
"""
Verification script for Chapter 1.
Run this to ensure your environment is perfect.
"""
import sys
import os

print("🧪 Running Setup Verification...\n")

# Test 1: Python Version
print("Test 1: Checking Python Version...")
major, minor = sys.version_info[:2]
assert major == 3 and minor >= 10, f"❌ Python 3.10+ required, found {major}.{minor}"
print(f"✅ Python {major}.{minor} looks good!\n")

# Test 2: Virtual Environment
print("Test 2: Checking Virtual Environment...")
# In venv, sys.prefix != sys.base_prefix
is_venv = sys.prefix != sys.base_prefix
if not is_venv:
    print("⚠️  WARNING: You don't appear to be in a virtual environment.")
    print("   If you are using Conda, this might be a false positive.")
else:
    print("✅ Virtual Environment active!\n")

# Test 3: Imports
print("Test 3: Checking Dependencies...")
try:
    import pydantic
    import pydantic_settings
    import dotenv
    print("✅ Dependencies installed!\n")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Run: pip install -r requirements.txt")
    exit(1)

print("🎉 Environment is PERFECT! You are ready for Chapter 2.")
```

**Run it:**
```bash
python verify_setup.py
```

---

## Summary

**What you learned:**

1. ✅ **Virtual Environments** are mandatory to avoid "Dependency Hell".
2. ✅ **.env files** keep secrets safe and out of your code.
3. ✅ **Pydantic Settings** automates loading and validating configuration.
4. ✅ **Type Safety** prevents bugs by ensuring configs are the right type (int vs str).
5. ✅ **Project Structure** matters—start clean to stay clean.
6. ✅ **Singleton Pattern** ensures your config is loaded once and used everywhere.
7. ✅ **Git Hygiene**: `__pycache__` and `.env` belong in `.gitignore`.

**Key Takeaway**: A robust setup is the difference between "it works on my machine" and "it works everywhere." You now have a professional-grade foundation. 🏗️

**Skills unlocked**: 🎯
- Environment Management
- Secrets Security
- Type-Safe Configuration

**Looking ahead**: In **Chapter 2**, we'll dive deeper into **Type Hints and Enums** to make your code impossible to break!

---

**Next**: [Chapter 2: Enums & Type Hints →](chapter-02-enums-type-hints.md)