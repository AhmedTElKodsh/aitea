# Chapter 52: Technical Report Generation System — The Calculator

<!--
METADATA
Phase: 10 - Civil Engineering Application
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Application
Prerequisites: Chapter 49 (Models), Chapter 29 (Tools)
Builds Toward: Complete System (Ch 54)
Correctness Properties: P74 (Calculation Accuracy), P75 (Visualization Correctness)
Project Thread: Analysis

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You ask a calculator, "What is 55 * 142?" It gives you the exact answer.
You ask a poet the same question. They might say, "A lot. Like, thousands. Maybe a million?"

LLMs are poets. They are terrible at math.
If you ask an AI to "Calculate the structural load," it will confidently hallucinate a number that causes your bridge to collapse.

**Technical Reports** require precision.
To build them, we need to force the Poet to use a Calculator.
We will give our AI tools to run Python code, generate real charts, and crunch real data.

**By the end of this chapter**, you will generate a report with charts and tables that are mathematically perfect. 📊

---

## Prerequisites Check

We need data science tools.

```bash
pip install pandas matplotlib
```

Ensure you have `domain_models.py` from Chapter 49.

---

## The Story: The "Hallucinated" Graph

### The Problem (Fake Data)

You ask GPT-4: "Draw a graph of the stress test."
It outputs text: `[Chart showing curve going up]`.
Or it generates SVG code that looks like a squiggly line but matches no real data.
It looks scientific, but it's fiction.

### The Solution (Code Interpreter)

We don't ask the AI to *draw*. We ask it to *write Python code that draws*.
1.  **Reason**: "I need a graph of Load vs Deflection."
2.  **Act**: Write `matplotlib` code.
3.  **Execute**: Run code -> Save `graph.png`.
4.  **Report**: Embed `![Graph](graph.png)` in the document.

---

## Part 1: The Calculation Tool

Never let an LLM do math in its head.

### 🔬 Try This! (Hands-On Practice #1)

**Create `calc_tools.py`**:

```python
from langchain_core.tools import tool
import math

@tool
def calculate_beam_load(length: float, load_per_meter: float) -> float:
    """
    Calculates total load on a beam.
    Formula: length * load_per_meter
    """
    print(f"🧮 Calculating: {length}m * {load_per_meter}kg/m")
    return length * load_per_meter

@tool
def calculate_safety_factor(max_load: float, actual_load: float) -> float:
    """
    Calculates safety factor.
    Formula: max_load / actual_load
    """
    if actual_load == 0: return 0.0
    return max_load / actual_load

# Test
print(calculate_beam_load.invoke({"length": 10, "load_per_meter": 500}))
```

**Run it**.
We now have trusted functions.

---

## Part 2: The Visualization Tool

Now, let's generate a chart.

### 🔬 Try This! (Hands-On Practice #2)

**Create `chart_tools.py`**:

```python
from langchain_core.tools import tool
import matplotlib.pyplot as plt
import os

@tool
def generate_load_chart(loads: list[float], spans: list[float]) -> str:
    """
    Generates a Load vs Span chart and saves it to 'load_chart.png'.
    Returns the filename.
    """
    print("📊 Generating Chart...")
    plt.figure(figsize=(10, 6))
    plt.plot(spans, loads, marker='o', linestyle='-')
    plt.title('Beam Load Distribution')
    plt.xlabel('Span (m)')
    plt.ylabel('Load (kg)')
    plt.grid(True)
    
    filename = "load_chart.png"
    plt.savefig(filename)
    plt.close()
    
    return filename

# Test
# print(generate_load_chart.invoke({"loads": [100, 200, 150], "spans": [0, 5, 10]}))
```

**Run it**.
Check your folder. Do you see `load_chart.png`? Open it. That's a real graph!

---

## Part 3: The Report Generator Agent

Now we put the Poet in charge of the Calculator and the Artist.

### 🔬 Try This! (Hands-On Practice #3)

**Create `report_gen.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from calc_tools import calculate_beam_load, calculate_safety_factor
from chart_tools import generate_load_chart
from dotenv import load_dotenv

load_dotenv()

# 1. Setup
tools = [calculate_beam_load, calculate_safety_factor, generate_load_chart]
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Structural Engineer. Create a technical report."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 2. Run
task = """
We have a 20m beam. The load is 500kg/m.
We have a 20m beam. The load is 500kg/m.
The max capacity is 15,000kg.

1. Calculate the total load.
2. Calculate the safety factor.
3. Generate a chart assuming load increases linearly from 0 to Total over the 20m span.
4. Write a brief report summarizing the findings. Include the chart.
"""

print("--- generating Report ---")
result = executor.invoke({"input": task})
print("\n--- FINAL REPORT ---\n")
print(result["output"])
```

**Run it**.
Watch the trace.
1. It calculates `20 * 500 = 10,000`.
2. It calculates `15,000 / 10,000 = 1.5`.
3. It calls the chart tool.
4. It writes text referencing the numbers and the image.

This report is **grounded in math**.

---

## Part 4: Integration with Pydantic

We can parse the final text into our `TechnicalReport` model.

### 🔬 Try This! (Hands-On Practice #4)

**Create `structured_report.py`**:

```python
from domain_models import TechnicalReport, Calculation
from langchain_core.output_parsers import PydanticOutputParser

# Assume 'result_text' comes from the agent in Part 3
result_text = """
REPORT: Structural Analysis
The total load is 10,000 kg.
The safety factor is 1.5.
Conclusion: The beam is safe.
Approved by: AI Engineer
"""

# We can use an extractor (Ch 11) to structure this final text
# Or, better, we could have the Agent output JSON directly.
# Let's mock the extraction for this exercise.

report = TechnicalReport(
    report_id="RPT-001",
    title="Structural Analysis",
    calculations=[
        Calculation(name="Total Load", formula="20 * 500", result=10000, units="kg"),
        Calculation(name="Safety Factor", formula="15000 / 10000", result=1.5, units="ratio")
    ],
    conclusion="The beam is safe.",
    approved_by="AI Engineer"
)

print(f"Report ID: {report.report_id}")
print(f"Calcs: {len(report.calculations)}")
```

---

## Common Mistakes

### Mistake #1: Using `eval()`
Never let the LLM write arbitrary Python code and run it with `eval()`. It can delete your files.
**Fix**: Define specific tools (`calculate_load`) or use a sandboxed environment (Docker) if using generic code execution.

### Mistake #2: Hallucinated Units
LLM calculates "100". Is it kg? lbs?
**Fix**: Tools should return strings with units ("100 kg") or Pydantic models with unit fields.

### Mistake #3: Overwriting Charts
If you run the report twice, `load_chart.png` gets overwritten.
**Fix**: Generate unique filenames (`chart_{uuid}.png`).

---

## Quick Reference Card

### Plotting with Matplotlib

```python
plt.plot(x_values, y_values)
plt.savefig("chart.png")
```

### Markdown Images
To show an image in the report: `![Description](filename.png)`

---

## Verification (REQUIRED SECTION)

We need to verify **P74 (Calculation)** and **P75 (Files)**.

**Create `verify_report.py`**:

```python
"""
Verification script for Chapter 52.
Properties: P74 (Math), P75 (Files).
"""
from calc_tools import calculate_beam_load
from chart_tools import generate_load_chart
import os
import sys

print("🧪 Running Report Verification...\n")

# P74: Calculation Accuracy
print("Test 1: Math Logic...")
res = calculate_beam_load.invoke({"length": 10, "load_per_meter": 5})
if res == 50.0:
    print("✅ P74 Passed: 10 * 5 = 50.")
else:
    print(f"❌ Failed: Math error. Got {res}")
    sys.exit(1)

# P75: Visualization Correctness
print("Test 2: Chart Generation...")
chart_file = "load_chart.png"
# Cleanup
if os.path.exists(chart_file): os.remove(chart_file)

generate_load_chart.invoke({"loads": [1, 2], "spans": [1, 2]})

if os.path.exists(chart_file):
    size = os.path.getsize(chart_file)
    if size > 0:
        print(f"✅ P75 Passed: Chart created ({size} bytes).")
    else:
        print("❌ Failed: Chart is empty.")
        sys.exit(1)
else:
    print("❌ Failed: Chart file not created.")
    sys.exit(1)

print("\n🎉 Chapter 52 Complete! You are a Data Scientist.")
```

**Run it:** `python verify_report.py`

---

## Summary

**What you learned:**

1. ✅ **Tools over Thoughts**: Using Python for math is 100% accurate; using LLM "thoughts" is risky.
2. ✅ **Visuals**: Generating real image files from data.
3. ✅ **Integration**: Combining text generation with data processing.
4. ✅ **Structured Output**: Fitting analysis into the `TechnicalReport` schema.
5. ✅ **Sandboxing**: Why specific tools are safer than generic `exec()`.

**Key Takeaway**: The LLM is not the calculator. The LLM is the *operator* of the calculator.

**Skills unlocked**: 🎯
- Data Visualization
- Computational Tools
- Report Automation

**Looking ahead**: We have contracts, proposals, and reports.
But are they legal? Are they compliant?
In **Chapter 53**, we will build the **Compliance Review Agent** to check our work against regulations.

---

**Next**: [Chapter 53: Compliance Review Agent →](chapter-53-compliance-review.md)
