# Chapter 28: OTAR Loop Pattern — The Self-Correcting Agent

<!--
METADATA
Phase: 5 - Agents
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Implementation
Prerequisites: Chapter 27 (ReAct)
Builds Toward: LangGraph (Ch 31)
Correctness Properties: P38 (State Transition), P39 (Reflection Integration)
Project Thread: Cognitive Architecture

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're writing code. You type `print("Hello"`. You run it.
**Error**: `SyntaxError: unexpected EOF while parsing`.
Do you stop and say "I failed"? No. You say "Ah, I missed a parenthesis," you fix it, and you run it again.

Standard agents (ReAct) act like they only have **one shot**. If the tool fails or gives a weird result, they often hallucinate an answer or give up.

**OTAR (Observe, Think, Act, Reflect)** adds the "Fix it" step.
It gives the agent a mirror. "Did that work? No? Why? Let me try a different way."

**By the end of this chapter**, you will build an agent that makes mistakes, realizes it made a mistake, and fixes it—all by itself. 🔁

---

## Prerequisites Check

```bash
# Verify langchain
pip show langchain
```

---

## The Story: The "Stubborn" Bot

### The Problem (Repeating Mistakes)

You ask an Agent: "What is the weather in 'Narnia'?"
Agent: Calls WeatherTool("Narnia").
Tool: "Error: City not found."
Agent: "The weather in Narnia is sunny." (Hallucination! It ignored the error).

### The Solution (Reflection)

We force the agent to pause after the tool runs.
**Reflect**: "The tool returned an error. This means Narnia isn't a real city (or the API is down). I should tell the user I can't find it, rather than guessing."

---

## Part 1: The OTAR Cycle

1.  **Observe**: Read the user request.
2.  **Think**: Plan the next step.
3.  **Act**: Use a tool.
4.  **Reflect**: Look at the tool output. Is it what I wanted?
    *   *Yes*: Finish.
    *   *No*: Go back to **Think**.

---

## Part 2: Building a Self-Correcting Loop

We'll simulate this with a simple Python loop around our LLM.

### 🔬 Try This! (Hands-On Practice #1)

Let's build a "Python Coder" that fixes its own syntax errors.

**Create `self_correct.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 1. The Generator (Writes Code)
gen_prompt = ChatPromptTemplate.from_template(
    "Write a Python function to {task}. Return ONLY the code."
)
generator = gen_prompt | model | StrOutputParser()

# 2. The Reflector (Checks Code)
# In a real app, we'd run the code. Here, we simulate a syntax checker.
def check_syntax(code):
    try:
        compile(code, "<string>", "exec")
        return "Pass"
    except SyntaxError as e:
        return f"SyntaxError: {e}"

# 3. The OTAR Loop
def run_coding_agent(task):
    print(f"Task: {task}")
    
    # Attempt 1
    code = generator.invoke({"task": task})
    print(f"---\n--- Draft 1 ---\n{code}")
    
    # Reflect
    feedback = check_syntax(code)
    if feedback == "Pass":
        print("✅ Code is valid.")
        return code
    
    print(f"❌ Verification Failed: {feedback}")
    print("🔄 Reflecting and fixing...")
    
    # Attempt 2 (With Feedback)
    fix_prompt = ChatPromptTemplate.from_template(
        "You wrote this code:\n{code}\n\nIt failed with:\n{error}\n\nRewrite it to fix the error."
    )
    fixer = fix_prompt | model | StrOutputParser()
    
    fixed_code = fixer.invoke({"code": code, "error": feedback})
    print(f"---\n--- Draft 2 ---\n{fixed_code}")
    return fixed_code

# Force a mistake (Task that might be tricky or we can inject a bug)
# Since GPT-4o-mini is good, let's manually inject a bug to test the loop.
# We'll mock the generator for the first try.

print("---\n--- Running Simulation ---")
# Mocking a bad first draft
bad_code = "def hello() print('Hi')" # Missing colon
feedback = check_syntax(bad_code)
print(f"Draft 1 (Mocked): {bad_code}")
print(f"Error: {feedback}")

# Now run the fixer
fix_prompt = ChatPromptTemplate.from_template(
    "The code:\n{code}\n\nHas error:\n{error}\n\nFix it."
)
fixer = fix_prompt | model | StrOutputParser()
final = fixer.invoke({"code": bad_code, "error": feedback})
print(f"Final: {final}")
```

**Run it**.
The LLM sees the `SyntaxError`, realizes it missed a colon, and writes valid code.

---

## Part 3: Recursive Chains

What if we want it to loop *until* it passes (up to a limit)?

### 🔬 Try This! (Hands-On Practice #2)

**Create `recursive_otar.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def check_length(text):
    if len(text) < 10:
        return f"Too short ({len(text)} chars). Must be > 10."
    return "Pass"

def generate_until_valid(topic, attempt=1):
    print(f"\n---\n--- Attempt {attempt} ---")
    
    # Generate
    if attempt == 1:
        prompt = f"Write a VERY short sentence about {topic}."
    else:
        # Reflection included in prompt
        prompt = f"Write a sentence about {topic}. Make it longer than 10 characters."
        
    response = model.invoke(prompt).content
    print(f"Bot: {response}")
    
    # Reflect
    feedback = check_length(response)
    if feedback == "Pass":
        print("✅ Passed!")
        return response
    
    if attempt >= 3:
        print("❌ Given up.")
        return response
        
    print(f"⚠️ Feedback: {feedback}")
    return generate_until_valid(topic, attempt + 1)

generate_until_valid("Sun")
```

**Run it**.
1. "Sun hot." (Too short)
2. "The sun is very hot." (Pass!)

This recursive pattern allows the agent to "learn" within the session.

---

## Common Mistakes

### Mistake #1: Bad Feedback
If the Reflection step gives vague feedback ("Wrong."), the agent can't fix it.
**Fix**: Provide specific error messages ("SyntaxError line 1") or criteria ("Length must be > 10").

### Mistake #2: Infinite Loops
The agent keeps failing and retrying forever.
**Fix**: Always pass a `max_attempts` counter.

### Mistake #3: Distraction
Sometimes, in trying to fix one error, the agent introduces a new one.
**Fix**: Use a "Critic" prompt that checks *all* criteria, not just the one that failed.

---

## Quick Reference Card

### The OTAR Loop
```python
while attempts < max_attempts:
    action = plan()
    result = execute(action)
    if is_good(result):
        break
    feedback = critique(result)
    attempts += 1
```

---

## Verification (REQUIRED SECTION)

We need to verify **P39 (Reflection Integration)**.

**Create `verify_otar.py`**:

```python
"""
Verification script for Chapter 28.
Property P39: Self-Correction.
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys

print("🧪 Running OTAR Verification...\n")

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Setup: A math corrector
# We give it a wrong answer and an error message.
# It must return the correct answer.

wrong_answer = "2 + 2 = 5"
error_msg = "The result of 2+2 is 4, not 5."

prompt = ChatPromptTemplate.from_template(
    """
Current Answer: {answer}
Critique: {error}    
Please correct the answer based on the critique.
Return ONLY the corrected equation.
    """
)

chain = prompt | model | StrOutputParser()

print("Test 1: Self-Correction...")
correction = chain.invoke({"answer": wrong_answer, "error": error_msg})
print(f"Correction: {correction}")

if "2 + 2 = 4" in correction or "2+2=4" in correction:
    print("✅ P39 Passed: Agent successfully reflected and corrected.")
else:
    print(f"❌ Failed: Agent did not correct. Got: {correction}")
    sys.exit(1)

print("\n🎉 Chapter 28 Complete! Your agent can fix its own mistakes.")
```

**Run it:** `python verify_otar.py`

---

## Summary

**What you learned:**

1. ✅ **Looping**: Agents aren't just one-shot; they iterate.
2. ✅ **Feedback Loops**: Using output to guide the next input.
3. ✅ **Self-Correction**: The ability to fix errors without human help.
4. ✅ **Recursion**: A clean way to implement retries in code.
5. ✅ **Critique**: The art of generating useful error messages.

**Key Takeaway**: Intelligence isn't knowing the answer immediately. It's knowing how to figure it out when you're wrong.

**Skills unlocked**: 🎯
- Error Recovery Logic
- Recursive Logic
- Prompt Chaining

**Looking ahead**: We've been using simple function tools (`add`, `multiply`). But LLMs can call **Functions** natively via APIs (OpenAI Function Calling). In **Chapter 29**, we will master **Tool Calling** to connect to real-world APIs robustly.

---

**Next**: [Chapter 29: Tool Calling & Function Calling →](chapter-29-tool-calling.md)
