# Chapter 27: ReAct Pattern — The Internal Monologue

<!--
METADATA
Phase: 5 - Agents
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Concept + Implementation
Prerequisites: Chapter 26 (Agents)
Builds Toward: OTAR Loop (Ch 28)
Correctness Properties: P36 (Reasoning Trace), P37 (Action Validity)
Project Thread: Cognitive Architecture

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You're in a math exam.
Question: "What is 15 * 12?"
Student A writes: "180". (Correct, but risky. If they calculated 170 in their head, they get 0 points).
Student B writes: "10 * 15 = 150. 2 * 15 = 30. 150 + 30 = 180." (Correct, and robust).

**ReAct (Reason + Act)** is asking the AI to be Student B.
Instead of just jumping to an action ("Call API"), we force it to **Thinking out loud**:
*"I need to find the weather. I should use the Weather Tool. Then I need to calculate the difference..."*

This "Internal Monologue" makes the AI smarter, less prone to hallucinations, and much easier to debug.

**By the end of this chapter**, you'll look inside the brain of your agent and see exactly how it solves problems step-by-step. 🧠

---

## Prerequisites Check

```bash
# Verify langchain installation
pip show langchain
```

---

## The Story: The "Black Box"

### The Problem (Invisible Logic)

In Chapter 26, we used `create_tool_calling_agent`. It worked, but it felt a bit like magic.
The LLM just outputted a JSON blob to call a function. We didn't see *why*.
If it fails, why did it fail? Did it misunderstand the question? Did it pick the wrong tool?

### The Solution (ReAct Traces)

We use a text-based prompting strategy that forces this structure:

1.  **Question**: User input.
2.  **Thought**: The LLM analyzes the situation.
3.  **Action**: The LLM chooses a tool.
4.  **Observation**: The output of the tool (fed back to LLM).
5.  **Final Answer**: The result.

This loop repeats until done.

---

## Part 1: The ReAct Prompt

The prompt is the engine. It tells the LLM the rules of the game.

### 🔬 Try This! (Hands-On Practice #1)

Let's pull the standard ReAct prompt from LangChain Hub (or define it manually).

**Create `react_prompt.py`**:

```python
from langchain import hub

# 1. Pull the standard prompt
# This is the industry standard prompt for ReAct agents
prompt = hub.pull("hwchase17/react")

# 2. Inspect it
print("--- Template ---")
print(prompt.template)
```

**Run it**.
You'll see something like:
`Answer the following questions as best you can...`
`Use the following format:`
`Question: ...`
`Thought: ...`
`Action: ...`

This **Format Instruction** is what drives the behavior.

---

## Part 2: Building a ReAct Agent

We will use `create_react_agent`. This is different from `create_tool_calling_agent`. It works purely on text completion, which makes it compatible with almost **any** LLM (even local ones via Ollama).

### 🔬 Try This! (Hands-On Practice #2)

**Create `react_agent.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import tool
from langchain import hub
from dotenv import load_dotenv

load_dotenv()

# 1. Define Tools
@tool
def get_length(text: str) -> int:
    """Returns the length of a string in characters."""
    print(f"   (Tool: Counting chars in '{text}')")
    return len(text)

tools = [get_length]

# 2. Setup Model & Prompt
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = hub.pull("hwchase17/react")

# 3. Create Agent
agent = create_react_agent(model, tools, prompt)

# 4. Execute
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print("--- Running ReAct ---")
agent_executor.invoke({"input": "How many characters are in the word 'Supercalifragilistic'?"})
```

**Run it**.
Look closely at the output (verbose mode).
You will see:
`Thought: I need to count the characters...`
`Action: get_length`
`Action Input: 'Supercalifragilistic'`
`Observation: 20`
`Thought: I have the length.`
`Final Answer: 20`

This is the **Trace**.

---

## Part 3: Debugging Logic (Why did it do that?)

If an agent gets stuck, the Trace tells you why.

**Scenario**: You ask "What is the weather?" but you didn't give it a weather tool.
**Trace**:
`Thought: I need to check the weather.`
`Action: WeatherTool`
`Observation: Tool not found.`
`Thought: I don't have a tool for this. I will apologize.`
`Final Answer: Sorry, I can't check weather.`

Without ReAct, the LLM might just hallucinate "It's sunny" because it doesn't know it *can't* do it. ReAct forces it to look at its tools first.

---

## Common Mistakes

### Mistake #1: Weak Docstrings
In ReAct, the LLM has to read the tool description to decide to use it. If your docstring is vague, the `Thought` step will fail.
**Fix**: `"""Use this tool to calculate X given Y."""`

### Mistake #2: Parsing Errors
Since ReAct relies on the LLM outputting exact text strings (`Action: ...`), sometimes the LLM makes a typo.
**Fix**: `AgentExecutor` handles some parsing errors automatically, but using a stronger model (GPT-4) helps.

### Mistake #3: Infinite Loops
"Thought: I need X. Action: Tool. Observation: Error. Thought: I need X. Action: Tool..."
**Fix**: `max_iterations=5`.

---

## Quick Reference Card

### ReAct Flow
1. **Thought**: What do I do next?
2. **Action**: Select a tool.
3. **Action Input**: Arguments for the tool.
4. **Observation**: Result of the tool.
5. **Final Answer**: Return to user.

---

## Verification (REQUIRED SECTION)

We need to verify **P36 (Trace Completeness)**.

**Create `verify_react.py`**:

```python
"""
Verification script for Chapter 27.
Property P36: Reasoning Trace.
"""
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain import hub
import sys
import io

print("🧪 Running ReAct Verification...\n")

@tool
def magic_number_tool(x: str) -> int:
    """Returns the magic number 42."""
    return 42

tools = [magic_number_tool]
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Capture stdout to check the trace
# (In production, use callbacks, but for this simple check, capture works)
from langchain_core.callbacks import BaseCallbackHandler

class TraceCallback(BaseCallbackHandler):
    def __init__(self):
        self.thoughts = []
    
    def on_agent_action(self, action, **kwargs):
        self.thoughts.append(action.log)

tracer = TraceCallback()

print("Test 1: Analyzing Trace...")
res = executor.invoke(
    {"input": "What is the magic number?"},
    config={"callbacks": [tracer]}
)

# Verify Trace
trace_log = "".join(tracer.thoughts)
if "Thought" in trace_log and "Action" in trace_log:
    print("✅ P36 Passed: Agent produced a reasoning trace.")
else:
    print(f"❌ Failed: No trace found. Log: {trace_log}")
    sys.exit(1)

# Verify Result
if "42" in res['output']:
    print("✅ Result Correct.")
else:
    print(f"❌ Failed result: {res['output']}")
    sys.exit(1)

print("\n🎉 Chapter 27 Complete! You can see the matrix code.")
```

**Run it:** `python verify_react.py`

---

## Summary

**What you learned:**

1. ✅ **ReAct**: The loop of Reasoning and Acting.
2. ✅ **Transparency**: Why seeing the "Thought" is critical for debugging.
3. ✅ **Model Agnostic**: ReAct works on models without special "Function Calling" APIs.
4. ✅ **Prompting**: How the prompt enforces the `Action: ...` syntax.
5. ✅ **Tracing**: Catching the agent in the act.

**Key Takeaway**: ReAct turns black-box AI into glass-box AI. You can see the gears turning.

**Skills unlocked**: 🎯
- Cognitive Modeling
- Debugging AI Logic
- Trace Analysis

**Looking ahead**: We have a loop. But what if the agent needs to *reflect* on its mistakes? "I tried Tool A and it failed. I should try Tool B."
In **Chapter 28**, we will learn the **OTAR Pattern** (Observe, Think, Act, Reflect) to build self-correcting agents!

---

**Next**: [Chapter 28: OTAR Loop Pattern →](chapter-28-otar-loop.md)
