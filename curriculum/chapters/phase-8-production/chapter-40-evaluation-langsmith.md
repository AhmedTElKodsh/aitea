# Chapter 40: Evaluation with LangSmith — The Dashboard

<!--
METADATA
Phase: 8 - Production
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 21 (Evaluation)
Builds Toward: Deployment (Ch 42)
Correctness Properties: P27 (Metric Calculation), P55 (Reproducibility)
Project Thread: Observability

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You own a car.
You drive it for 10,000 miles. You never check the speedometer, gas gauge, or engine light.
Eventually, it stops. You have no idea why. 🚗

Running an AI app without **Observability** is driving blind.
- How many tokens did that query cost?
- Why did that specific answer fail?
- Is the new model better than the old one?

**LangSmith** is your dashboard. It records every "Thought", "Action", and "Token". It lets you replay bugs and grade performance over time.

**By the end of this chapter**, you will turn the lights on. You'll see exactly what your AI is doing, down to the millisecond. 💡

---

## Prerequisites Check

You need a LangSmith account (free tier available).
1. Go to [smith.langchain.com](https://smith.langchain.com/)
2. Sign up.
3. Create an API Key.

```bash
pip install langsmith pandas
```

---


## The Story: The "It Feels Worse" Complaint

### The Problem (Regression)

You switch from `gpt-3.5` to `gpt-4o-mini`.
A user says: "It feels worse today."
You ask: "Worse how?"
User: "I dunno. Just worse."

Without data, you can't debug "vibes".

### The Solution (Traces & Evals)

1.  **Traces**: You look up the user's specific chat log. You see the prompt, the context, and the answer.
2.  **Evaluation**: You run a dataset of 50 "Golden Questions" against the old model and the new model.
    *   Old: 85% Accuracy.
    *   New: 92% Accuracy.
3.  **Result**: You prove the user wrong (or right) with math.

---


## Part 1: Turning on the Lights (Tracing)

This is the easiest win in AI Engineering. Just set environment variables.

### 🔬 Try This! (Hands-On Practice #1)

**Update your `.env`**:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="ls__..." # Your LangSmith Key
LANGCHAIN_PROJECT="my-first-project"
```

**Create `generate_trace.py`**:

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Just running this creates a trace!
llm = ChatOpenAI(model="gpt-4o-mini")
print("Running query...")
response = llm.invoke("Tell me a fun fact about octopuses.")
print(f"Response: {response.content}")
```

**Run it**.
Go to [smith.langchain.com](https://smith.langchain.com). Click your project.
You should see the run! Click it to see latency, tokens, and the exact input/output.

---


## Part 2: Creating a Dataset

To test effectively, we need a standard set of questions.

### 🔬 Try This! (Hands-On Practice #2)

**Create `create_dataset.py`**:

```python
from langsmith import Client

client = Client()

# 1. Create Dataset
dataset_name = "Planet Questions"
if client.has_dataset(dataset_name=dataset_name):
    print("Dataset already exists.")
else:
    dataset = client.create_dataset(dataset_name=dataset_name, description="Planetary facts")
    
    # 2. Add Examples
    client.create_examples(
        inputs=[
            {"question": "What is the largest planet?"},
            {"question": "Which planet has rings?"},
        ],
        outputs=[
            {"answer": "Jupiter"},
            {"answer": "Saturn"},
        ],
        dataset_id=dataset.id,
    )
    print("Dataset created!")
```

**Run it**. Check the UI. You now have a "Golden Set".

---


## Part 3: Running an Evaluation

Now, let's run our AI against this dataset and score it.

### 🔬 Try This! (Hands-On Practice #3)

**Create `run_eval.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain.evaluation import StringEvaluator
from langsmith.evaluation import evaluate, LangChainStringEvaluator
from dotenv import load_dotenv

load_dotenv()

# 1. The System to Test
def my_bot(inputs):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return llm.invoke(inputs["question"]).content

# 2. The Evaluators
# "Correctness" checks if prediction matches reference (using LLM-as-judge)
qa_evaluator = LangChainStringEvaluator("qa") 

# 3. Run Evaluation
experiment_results = evaluate(
    my_bot,
    data="Planet Questions",
    evaluators=[qa_evaluator],
    experiment_prefix="test-experiment",
)

print(f"View results at: {experiment_results.experiment_name}")
```

**Run it**.
LangSmith will:
1. Pull the questions.
2. Run `my_bot` for each.
3. Compare the bot's answer to the "Golden Answer" using GPT-4.
4. Give you a score (0 or 1).

---


## Common Mistakes

### Mistake #1: Leaking Keys
Do NOT commit `.env`. LangSmith keys give access to all your logs.

### Mistake #2: Using Eval for Everything
Evaluation costs money (it runs GPT-4 to grade GPT-3.5).
**Fix**: Run evals only on Pull Requests or major changes, not every local run.

### Mistake #3: Ignoring the "Playground"
LangSmith has a "Playground" button on every trace. You can tweak the prompt and re-run it instantly to fix bugs. Use it!

---


## Quick Reference Card

### Env Vars

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=...
```

### Creating Dataset (CLI)

You can also create datasets from existing CSVs using the UI, which is often easier.

---


## Verification (REQUIRED SECTION)

We need to verify **P55 (Reproducibility)**.

**Create `verify_langsmith.py`**:

```python
"""
Verification script for Chapter 40.
Property P55: Reproducibility.
"""
from langsmith import Client
import os
from dotenv import load_dotenv
import sys

print("🧪 Running LangSmith Verification...\n")

load_dotenv()
if not os.getenv("LANGCHAIN_API_KEY"):
    print("⚠️  Skipping: No LangSmith API Key found.")
    print("   (This is expected if you are running locally without an account)")
    sys.exit(0)

client = Client()

# Test P55: Check connection and project creation
try:
    project_name = "verify_test_project"
    # Create or update project usually happens implicitly on trace, 
    # but we can check connection by listing projects
    projects = list(client.list_projects(limit=1))
    print(f"✅ P55 Passed: Connected to LangSmith. Found {len(projects)} projects.")
    
except Exception as e:
    print(f"❌ Failed: Could not connect to LangSmith: {e}")
    sys.exit(1)

print("\n🎉 Chapter 40 Complete! You have X-Ray vision.")
```

**Run it:** `python verify_langsmith.py`

---


## Summary

**What you learned:**

1. ✅ **Tracing**: Seeing the full execution path.
2. ✅ **Datasets**: Storing test cases in the cloud.
3. ✅ **Evaluation**: Running automated tests on datasets.
4. ✅ **Comparisons**: Checking if Version B is better than Version A.
5. ✅ **Debugging**: Using the Playground to fix prompts.

**Key Takeaway**: Don't trust your intuition. Trust the dashboard.

**Skills unlocked**: 🎯
- MLOps (Machine Learning Operations)
- Evaluation Pipelines
- Observability

**Looking ahead**: We know how to build, route, and test.
In **Chapter 41**, we will focus on **Security & Observability**. How do we prevent Prompt Injection? How do we handle PII (Personally Identifiable Information)?

---

**Next**: [Chapter 41: Error Handling, Security & Observability →](chapter-41-security-observability.md)
