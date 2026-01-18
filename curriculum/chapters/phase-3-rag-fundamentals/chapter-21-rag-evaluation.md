# Chapter 21: RAG Evaluation — Grading the Exam

<!--
METADATA
Phase: 3 - RAG Fundamentals
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 17 (RAG)
Builds Toward: Production Systems (Ch 40)
Correctness Properties: P27 (Metric Calculation), P28 (Faithfulness Scoring)
Project Thread: Quality Assurance

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You hire a student to take a test.
You ask: "What is 2 + 2?"
Student: "Fish."
You: "Great job!"

Wait, what? Without **Grading**, you have no idea if your student (or your AI) is genius or clueless.
You tweaked your chunk size in Chapter 15. Did it make things better? Or worse?
Without metrics, you are flying blind.

**By the end of this chapter**, you will build an **Auto-Grader**. An AI that grades your AI. You'll move from "It feels okay" to "It has 92% Faithfulness accuracy." 📊

---

## Prerequisites Check

No new libraries needed! We will build our evaluator using the tools we already have (LangChain/OpenAI)

---

## The Story: The "Feeling" Trap

### The Problem (Subjectivity)

Developer: "I changed the prompt to be polite. I think the answers are better now."
Manager: "Prove it."
Developer: "Uhh..."

In software, we have Unit Tests (Pass/Fail).
In AI, answers are fuzzy. "The sky is blue" vs "It is azure" are both correct. `assert a == b` fails.

### The Solution (LLM-as-a-Judge)

Who is smart enough to grade an LLM? **Another LLM.**
We give GPT-4 a rubric:
1. Here is the Question.
2. Here is the Answer.
3. Here is the Context.
4. **Did the Answer hallucinate? (Yes/No)**

---

## Part 1: The Golden Dataset

You can't grade without an answer key.
We need a **Golden Dataset**: Pairs of `(Question, Ground Truth)`.

### 🔬 Try This! (Hands-On Practice #1)

**Create `dataset.py`**:

```python
# Our "Exam" Questions
GOLDEN_DATASET = [
    {
        "question": "Who is the lead engineer?",
        "ground_truth": "Sarah Jones",
        "context": "The lead engineer for Project Alpha is Sarah Jones."
    },
    {
        "question": "What is the budget?",
        "ground_truth": "$500 million",
        "context": "The budget for Project Alpha is $500 million."
    }
]
```

---

## Part 2: Faithfulness (Did it lie?)

**Faithfulness** measures: Did the answer come *only* from the context?
If context says "Sky is green" and AI says "Sky is blue" (because it knows real life), that is **Low Faithfulness** (Hallucination relative to context).

### 🔬 Try This! (Hands-On Practice #2)

Let's build a judge.

**Create `faithfulness_evaluator.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

# The Judge
eval_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# The Rubric
template = """You are a grader assessing whether an answer is grounded in / supported by a set of facts.

Facts:
{context}

Answer:
{answer}

Give a binary score 'yes' (supported) or 'no' (not supported).
Provide a reason.
Return JSON: {{ "score": "yes/no", "reason": "..." }}
"""

eval_chain = ChatPromptTemplate.from_template(template) | eval_model | JsonOutputParser()

# Test Case 1: Faithful
context = "The apple is red."
answer = "The apple is red."
print("---" + "-" * 10 + " Test 1 (Good) " + "-" * 10 + "---")
res = eval_chain.invoke({"context": context, "answer": answer})
print(res)

# Test Case 2: Hallucination
context = "The apple is red."
answer = "The apple is red and tastes sweet." # "Tastes sweet" is NOT in context!
print("\n" + "---" + "-" * 10 + " Test 2 (Bad) " + "-" * 10 + "---")
res = eval_chain.invoke({"context": context, "answer": answer})
print(res)
```

**Run it**.
Test 2 should likely say "no" because "tastes sweet" isn't supported by the facts. (Strict grading).

---

## Part 3: Answer Relevancy (Did it answer?)

The AI might be faithful ("The sky is green") but irrelevant to the question ("What time is it?").

### 🔬 Try This! (Hands-On Practice #3)

**Create `relevancy_evaluator.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

template = """You are a grader assessing relevance.
Question: {question}
Answer: {answer}

Does the answer address the question?
Score 1 (Irrelevant) to 5 (Perfect).
Return JSON: {{ "score": int, "reason": "..." }}
"""

chain = ChatPromptTemplate.from_template(template) | model | JsonOutputParser()

# Test
q = "What is the capital of France?"
a1 = "Paris."
a2 = "I like pizza."

print("---" + "-" * 10 + " Answer 1 " + "-" * 10 + "---")
print(chain.invoke({"question": q, "answer": a1}))

print("\n---" + "-" * 10 + " Answer 2 " + "-" * 10 + "---")
print(chain.invoke({"question": q, "answer": a2}))
```

**Run it**.
Answer 1 should be Score 5. Answer 2 should be Score 1.

---

## Common Mistakes

### Mistake #1: Using the same model for grading
If you use `gpt-3.5` to generate and `gpt-3.5` to grade, it might make the same logic errors twice.
**Fix**: Use a stronger model (GPT-4) to grade a weaker one (GPT-3.5/Ollama).

### Mistake #2: Vague Rubrics
Prompt: "Is this good?"
LLM: "Yes." (It's polite).
**Fix**: Be specific. "Does the answer contain the name 'Sarah Jones'? Yes/No."

### Mistake #3: Evaluating single examples
Judging one query tells you nothing.
**Fix**: Run evaluation over a dataset of 20-50 examples and calculate the **Average Score**.

---

## Quick Reference Card

### The RAGAS Metrics (Industry Standard)

| Metric | Checks... |
|--------|-----------|
| **Faithfulness** | Answer vs Context (Hallucination) |
| **Answer Relevance** | Answer vs Question (Helpfulness) |
| **Context Precision** | Retrieved Docs vs Ground Truth (Search Quality) |

---

## Verification (REQUIRED SECTION)

We need to prove **P27 (Calculation)** and **P28 (Faithfulness)**.

**Create `verify_eval.py`**:

```python
"""
Verification script for Chapter 21.
Properties: P27 (Metric Calc), P28 (Faithfulness).
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import sys

print("🧪 Running Evaluation Verification...\n")

# Setup Judge
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
template = """
Facts: {context}
Answer: {answer}
Is the answer supported by facts? JSON: {{ "score": 1 (yes) or 0 (no) }}
"""
chain = ChatPromptTemplate.from_template(template) | model | JsonOutputParser()

# P28: Faithfulness Scoring
print("Test 1: Faithfulness Check...")
# Case A: Good
res_good = chain.invoke({"context": "A is 1.", "answer": "A is 1."})))
# Case B: Bad
res_bad = chain.invoke({"context": "A is 1.", "answer": "A is 2."})))

if res_good['score'] == 1 and res_bad['score'] == 0:
    print("✅ P28 Passed: Judge correctly identified hallucination.")
else:
    print(f"❌ Failed: Good={{res_good}}, Bad={{res_bad}}")
    sys.exit(1)

# P27: Metric Calculation (Average)
print("Test 2: Aggregation...")
scores = [1, 1, 0, 1] # 3 good, 1 bad
avg = sum(scores) / len(scores)
if avg == 0.75:
    print("✅ P27 Passed: Metrics aggregated correctly.")
else:
    print(f"❌ Failed: {avg}")
    sys.exit(1)

print("\n🎉 Chapter 21 Complete! You can now grade your homework.")
```

**Run it:** `python verify_eval.py`

---

## Summary

**What you learned:**

1. ✅ **Subjectivity is the enemy**: We need numbers to improve.
2. ✅ **LLM-as-a-Judge**: Using AI to evaluate AI.
3. ✅ **Faithfulness**: The most important metric for RAG (preventing lies).
4. ✅ **Relevance**: Ensuring the bot actually answers the user.
5. ✅ **Golden Datasets**: The test set you measure against.

**Key Takeaway**: Don't guess. Measure. If your Faithfulness score drops from 95% to 80%, revert your changes immediately.

**Skills unlocked**: 🎯
- Automated Evaluation
- Dataset Creation
- Quality Assurance (QA)

**Looking ahead**: We have covered simple RAG. But simple RAG fails when you ask "Summarize this 500-page document" or "Compare these 10 contracts".
In **Chapter 22**, we will learn **Advanced RAG Patterns** like Parent-Child retrieval to handle complex docs!

---

**Next**: [Chapter 22: Advanced RAG Patterns →](chapter-22-advanced-rag.md)
