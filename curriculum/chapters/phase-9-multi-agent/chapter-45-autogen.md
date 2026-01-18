# Chapter 45: AutoGen for Iterative Refinement — The Conversation Loop

<!--
METADATA
Phase: 9 - Multi-Agent Systems
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 43 (Multi-Agent)
Builds Toward: Supervisor Pattern (Ch 46)
Correctness Properties: P63 (Termination), P64 (Convergence)
Project Thread: Iterative Problem Solving

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You are Pair Programming.
**You**: "I wrote the function."
**Partner**: "I ran it. Syntax Error on line 5."
**You**: "Oops, fixed."
**Partner**: "Run it again. Logic error on line 10."
**You**: "Fixed."
**Partner**: "It works!"

This back-and-forth is how humans solve hard problems. We iterate.
**AutoGen** (by Microsoft) automates this.
You create two agents: A **Coder** and a **Critic** (or Executor).
They talk to each other. They run code. They fix bugs. They don't stop until the code works.

**By the end of this chapter**, you will build a system where two AI agents talk to each other to solve a problem that neither could solve alone. 🗣️

---

## Prerequisites Check

We need the AutoGen library.

```bash
pip install pyautogen
```

---

## The Story: The "One-Shot" Failure

### The Problem (No Feedback)

You ask ChatGPT: "Write a Python script to plot a fractal."
It gives you code. You run it. It crashes.
You paste the error back. It gives new code. It crashes again.
You are the **middleman**. It's tedious.

### The Solution (The Auto-Loop)

With AutoGen, you replace *yourself* with a **UserProxyAgent**.
This agent can:
1.  **Execute Code**: Run the Python script.
2.  **Report Errors**: Copy-paste the error back to the Coder.
3.  **Terminate**: Stop when the code runs successfully.

You click "Go", get coffee, and come back to a working fractal.

---

## Part 1: The Conversable Agent

AutoGen is built on `ConversableAgent`. All agents (User, Assistant) inherit from this.

### 🔬 Try This! (Hands-On Practice #1)

Let's verify your OpenAI Key is ready (AutoGen needs it).

**Create `autogen_setup.py`**:

```python
import os
from dotenv import load_dotenv

load_dotenv()

config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": os.environ.get("OPENAI_API_KEY")
    }
]

print(f"Config Loaded: {len(config_list)} model(s)")
```

**Run it**.

---

## Part 2: The Number Guessing Game

To understand the loop *without* dangerous code execution, let's play a game.
**Agent A**: Has a secret number.
**Agent B**: Tries to guess it.

### 🔬 Try This! (Hands-On Practice #2)

**Create `guessing_game.py`**:

```python
from autogen import ConversableAgent
import os
from dotenv import load_dotenv

load_dotenv()

config_list = [{"model": "gpt-4o-mini", "api_key": os.environ["OPENAI_API_KEY"]}]

# 1. The Player (Guesser)
player = ConversableAgent(
    "player",
    system_message="You are playing a number guessing game. Guess a number between 1 and 100.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER"
)

# 2. The Game Master (Has the secret)
# We use a human_input_mode="NEVER" to automate it completely.
# We define a function to check the guess.
secret_number = 42

def check_guess(guess: str):
    try:
        # LLM output might be chatty ("Is it 50?"), extract number
        import re
        nums = re.findall(r'\d+', guess)
        if not nums: return "Please guess a number."
        g = int(nums[-1])
        
        if g == secret_number:
            return "CORRECT! The number was 42. TERMINATE"
        elif g < secret_number:
            return "Too low. Guess higher."
        else:
            return "Too high. Guess lower."
    except:
        return "Invalid guess."

game_master = ConversableAgent(
    "game_master",
    system_message="I have a secret number. Tell me if I am high or low.",
    llm_config=False, # This agent is deterministic (code-based), not LLM-based
    human_input_mode="NEVER",
    default_auto_reply="Go ahead.",
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"]
)

# Register the reply function
game_master.register_reply(
    [player],
    lambda recipient, messages, sender, config: (True, check_guess(messages[-1]["content"]))
)

# 3. Start Chat
result = player.initiate_chat(
    game_master,
    message="I am ready to play. Is it 50?",
    max_turns=10
)
```

**Run it**.
Watch the Player guess.
"Is it 50?" -> "Too low."
"Is it 75?" -> "Too high."
"Is it 62?" -> ...
"CORRECT!"

This is the **Conversation Pattern**.

---

## Part 3: Code Execution (The Power)

Now, let's let the agent run python code.
**Warning**: `use_docker=False` runs code on your actual machine. Be careful what you ask for. Ideally, use Docker. For this tutorial, we will use a safe math problem.

### 🔬 Try This! (Hands-On Practice #3)

**Create `code_execution.py`**:

```python
from autogen import AssistantAgent, UserProxyAgent
import os
from dotenv import load_dotenv

load_dotenv()
config_list = [{"model": "gpt-4o-mini", "api_key": os.environ["OPENAI_API_KEY"]}]

# 1. The Coder (Assistant)
coder = AssistantAgent(
    name="Coder",
    llm_config={"config_list": config_list}
)

# 2. The Executor (User Proxy)
user_proxy = UserProxyAgent(
    name="User_Proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=5,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding_task",
        "use_docker": False # ⚠️ Uses local environment
    }
)

# 3. Task
task = """
Write a python script to output the first 10 Fibonacci numbers.
Print the list.
If it works, reply TERMINATE.
"""

user_proxy.initiate_chat(
    coder,
    message=task
)
```

**Run it**.
1. Coder writes `fib.py`.
2. UserProxy runs it.
3. UserProxy sees output `[0, 1, 1, 2, 3...]`.
4. Coder sees output, confirms it works, says "TERMINATE".

---

## Common Mistakes

### Mistake #1: Infinite Loops (Chatty Agents)
Agents love to say "Thank you!" "You're welcome!" "No problem!" "Bye!".
This wastes money and never triggers `TERMINATE`.
**Fix**: Add "Reply TERMINATE when done" to the system prompt.

### Mistake #2: Missing Libraries
Coder writes `import pandas`. You don't have pandas installed. Execution fails.
**Fix**: The Coder is smart. If it sees `ModuleNotFoundError`, it will usually write `pip install pandas` in the next turn!

### Mistake #3: Security
Running generated code locally is risky.
**Fix**: Use `use_docker=True` (requires Docker Desktop installed) for any real-world app.

---

## Quick Reference Card

### ConversableAgent

```python
agent = ConversableAgent(
    "name",
    system_message="...",
    llm_config=...,
    is_termination_msg=lambda x: "TERMINATE" in x["content"]
)
```

### Initiate Chat

```python
sender.initiate_chat(receiver, message="Start!", max_turns=5)
```

---

## Verification (REQUIRED SECTION)

We need to verify **P63 (Termination)** and **P64 (Convergence)**.

**Create `verify_autogen.py`**:

```python
"""
Verification script for Chapter 45.
Properties: P63 (Termination), P64 (Convergence).
"""
from autogen import ConversableAgent
import sys

print("🧪 Running AutoGen Verification...\n")

# Mock Agent A (The Solver)
# It pretends to solve a problem after 2 turns
turn = 0
def mock_reply(recipient, messages, sender, config):
    global turn
    turn += 1
    if turn == 1: return (True, "Thinking...")
    if turn == 2: return (True, "The answer is 42. TERMINATE")
    return (True, "Bug.")

agent_a = ConversableAgent("a", llm_config=False, human_input_mode="NEVER")
agent_a.register_reply([dict, None], mock_reply)

# Mock Agent B (The User)
agent_b = ConversableAgent(
    "b", 
    llm_config=False, 
    human_input_mode="NEVER",
    is_termination_msg=lambda x: "TERMINATE" in x["content"]
)

# Run Chat
res = agent_b.initiate_chat(agent_a, message="Start", max_turns=5)

# Verify P63: Termination
# The chat should have stopped at turn 2 (plus init message = 3 items in history)
print(f"History Length: {len(res.chat_history)}")
last_msg = res.chat_history[-1]["content"]

if "TERMINATE" in last_msg:
    print("✅ P63 Passed: Conversation terminated successfully.")
else:
    print(f"❌ Failed: Did not terminate. Last msg: {last_msg}")
    sys.exit(1)

# Verify P64: Convergence (Did we get the answer?)
if "42" in last_msg:
    print("✅ P64 Passed: Converged on correct answer.")
else:
    print("❌ Failed: Answer not found.")
    sys.exit(1)

print("\n🎉 Chapter 45 Complete! You have automated the loop.")
```

**Run it:** `python verify_autogen.py`

---

## Summary

**What you learned:**

1. ✅ **Conversational Programming**: Solving problems by talking.
2. ✅ **UserProxyAgent**: The bridge between AI and the OS.
3. ✅ **Code Generation Pipelines**:
4. ✅ **Iterative Refinement**: Fixing bugs through feedback loops.
5. ✅ **Termination**: Knowing when to stop.

**Key Takeaway**: AutoGen is "Pair Programming as a Service."

**Skills unlocked**: 🎯
- Multi-Agent Orchestration
- Code Generation Pipelines
- Automated Debugging

**Looking ahead**: We have autonomous teams. But what if we need a **Manager**? Someone to say "You do this, You do that"?
In **Chapter 46**, we will implement the **Supervisor Pattern** to hierarchically control our agents!

---

**Next**: [Chapter 46: Supervisor Pattern →](chapter-46-supervisor-pattern.md)
