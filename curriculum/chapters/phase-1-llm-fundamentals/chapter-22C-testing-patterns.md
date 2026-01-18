# Chapter 22C: Testing Patterns — The Safety Net 🕸️

<!--
METADATA
Phase: Python Bridge Module 3 (PBM-3)
Time: 2.5 hours (60 minutes reading + 90 minutes hands-on)
Difficulty: ⭐⭐⭐
Type: Concept / Implementation
Prerequisites: Chapter 22A (Patterns), Chapter 22B (Optimization)
Builds Toward: Chapter 13 (Embeddings), Chapter 39 (Evaluation)
Correctness Properties: [P1, P3, P12, P18]

NAVIGATION
→ Quick Reference: #quick-reference
→ Verification: #verification
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

Imagine you're a trapeze artist in a circus. 🎪 

You've spent weeks practicing a complex triple-flip. It's beautiful, fast, and exciting. But would you try it 30 feet in the air without a **safety net**? Probably not. Even the best performers make mistakes, and the net is what keeps a mistake from being a catastrophe.

**Testing is the safety net for your code.** 🕸️

As we move into **RAG** and **Multi-Agent Systems**, your code will become complex. One small change in how you process a PDF might break how the AI summarizes it. Without tests, you have to manually check everything. With tests, you push a button, and the computer tells you "Everything is still perfect!"

**By the end of this chapter**, you'll know how to:
- Use **Pytest** to run hundreds of checks in seconds.
- Create **Fixtures** to set up your test data automatically.
- Use **Mocking** to simulate the OpenAI API (saving you money and time!).
- Test **Async code** without pulling your hair out.
- Follow **TDD (Test-Driven Development)** to write bug-free code from the start.

Let's build your safety net! 🚀

---

## Prerequisites Check

Let's install the tools of the trade:

```bash
pip install pytest pytest-asyncio pytest-mock
```

**You should feel comfortable with**:
- **Protocols & Interfaces** (Chapter 22A): These make mocking MUCH easier.
- **Async/Await** (Chapter 12A): We'll be testing async functions today.

*Testing isn't about finding bugs; it's about the confidence to move fast.* 😊

---

## What You Already Know 🧩

You've been "testing" manually this whole time:

<table>
<tr>
<th>Manual Testing (The Slow Way)</th>
<th>Automated Testing (The Pro Way)</th>
</tr>
<tr>
<td>Running `python main.py` and looking at output</td>
<td>Running `pytest` and seeing green dots</td>
</tr>
<tr>
<td>Hardcoding API keys and spending money</td>
<td>**Mocking** responses for free, instant tests</td>
</tr>
<tr>
<td>Checking one case at a time</td>
<td>**Parametrization** (testing 10 cases at once)</td>
</tr>
</table>

---

## Part 1: Pytest Basics (The Engine) 🏎️

Pytest is the most popular testing framework for Python. It's simple, powerful, and fun to use.

### Your First Test

Create a file named `test_math.py`:

```python
# test_math.py
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
```

Run it:
```bash
pytest test_math.py
```

**Analogy: The Quality Inspector** 🧐
Pytest is like an inspector at a factory. It looks for any function starting with `test_`, runs it, and checks if the `assert` is true. If it's true, you get a green dot `.`. If it's false, you get a red `F`.

---

### 🔬 Try This! (Hands-On Practice #1)

**Challenge**: Write a test for a function `multiply(a, b)`. Include a case for multiplying by zero.

<details>
<summary>✅ Solution</summary>

```python
def test_multiply():
    assert multiply(10, 2) == 20
    assert multiply(5, 0) == 0
```
</details>

---

## Part 2: Fixtures (The "Ready-to-Go" Data) 📦

Often, you need to set up an object (like a Pydantic model or a Client) before you can test it. Instead of copy-pasting that setup into every test, we use **Fixtures**.

**Analogy: The Prepped Kitchen** 🔪
A chef doesn't chop onions *during* every recipe. They have a "prep" stage where everything is ready in small bowls. Fixtures are those bowls of prepped data.

```python
import pytest
from pydantic import BaseModel

class User(BaseModel):
    name: str

@pytest.fixture
def sample_user():
    return User(name="Ahmed")

def test_user_name(sample_user): # Just "ask" for it in the arguments!
    assert sample_user.name == "Ahmed"
```

---

## Part 3: Mocking (The "Stunt Double") 🎭

This is the most important skill for AI Engineering. We don't want to call the real OpenAI API every time we run a test. It's slow, expensive, and requires internet.

**Analogy: The Stunt Double** 🏃‍♂️
In an action movie, the lead actor doesn't jump off the building. A stunt double who *looks* like them does the jump. A **Mock** is a stunt double for your LLM Client.

### Mocking with `pytest-mock`

```python
# src/logic.py
async def get_ai_greeting(client):
    response = await client.generate("Say hello")
    return response.upper()

# tests/test_logic.py
@pytest.mark.asyncio
async def test_greeting_logic(mocker):
    # 1. Create a "Stunt Double" (Mock)
    mock_client = mocker.Mock()
    
    # 2. Tell the double what to say (The "Return Value")
    # Since generate is async, we use AsyncMock patterns or just return a future
    mock_client.generate = mocker.AsyncMock(return_value="hello")

    # 3. Run the logic
    result = await get_ai_greeting(mock_client)

    # 4. Verify
    assert result == "HELLO"
    mock_client.generate.assert_called_once_with("Say hello")
```

---

### 🔬 Try This! (Hands-On Practice #2)

**Challenge**: Mock a failure. Tell your mock to raise an `openai.RateLimitError` and test that your code handles it correctly (doesn't crash).

<details>
<summary>✅ Solution</summary>

```python
@pytest.mark.asyncio
async def test_rate_limit_handling(mocker):
    mock_client = mocker.AsyncMock()
    mock_client.generate.side_effect = Exception("Rate Limit!") # Simulate error
    
    # Assert that your function handles the error or raises your custom exception
    with pytest.raises(Exception):
        await get_ai_greeting(mock_client)
```
</details>

---

## Part 4: Testing Async Code ⏳

Testing async code requires the `@pytest.mark.asyncio` decorator. This tells pytest to run the test inside an event loop.

**Rule of Thumb**: If the function you're testing has `await`, your test must have `async def` and the `@pytest.mark.asyncio` decorator.

---

## Part 5: TDD (Test-Driven Development) 🛠️

TDD is a workflow: **Red → Green → Refactor**.

1. **Red**: Write a test for a feature that doesn't exist yet. Run it and watch it fail.
2. **Green**: Write the minimum code to make the test pass.
3. **Refactor**: Clean up the code, knowing the test has your back.

### 🔬 Try This! (Hands-On Practice #3)

**Challenge**: Use TDD to create a function `is_valid_email(email)`.
1. Write `test_email_validation` with cases for "valid@test.com" (True) and "bad-email" (False).
2. Run pytest (It will fail/error because the function doesn't exist).
3. Implement `is_valid_email` using a simple string check.
4. Run pytest again (Watch it turn green!).

---

## Bringing It All Together: The ProjectPulse Test Suite

Let's write a professional test suite for our `ProjectPulse` tool.

```python
# examples/mastery-check-project-pulse/tests/test_core.py
import pytest
from ..src.main import ProviderFactory, LogEntry

def test_factory_returns_mock():
    client = ProviderFactory.create("mock")
    assert client.__class__.__name__ == "MockLLMClient"

def test_log_entry_validation():
    data = {
        "author": "Ahmed",
        "role": "Backend",
        "day": "Monday",
        "blockers": [],
        "risks": [],
        "wins": ["Wrote tests!"]
    }
    entry = LogEntry(**data)
    assert entry.author == "Ahmed"

@pytest.mark.asyncio
async def test_orchestrator_run(mocker):
    # Mocking the client to avoid 0.5s sleep in MockClient
    mock_client = mocker.AsyncMock()
    mock_client.generate.return_value = '{"author": "Test", "role": "Team", "day": "Mon", "blockers":[], "risks":[], "wins":[]}'
    
    # ... logic to test the orchestrator ...
    pass
```

---

## Common Mistakes (Learn from Others!) 🚫

### Mistake #1: Testing the Library, Not Your Code
Don't write a test to see if `OpenAI` works. OpenAI tests their own code.
**Fix**: Mock the library and test **your logic** that uses the result.

### Mistake #2: Brittle Tests
If your test fails every time you change a comma in a prompt, it's too brittle.
**Fix**: Test for the *existence* of data or the *structure*, not the exact string (unless that's the goal).

### Mistake #3: Leaking Secrets
Never put real API keys in your tests!
**Fix**: Use Mocks or environment variables that are empty in the test environment.

---

## Quick Reference Card 🃏

| Command/Snippet | Purpose |
|-----------------|---------|
| `pytest` | Run all tests in the current folder |
| `@pytest.fixture` | Create reusable setup data |
| `mocker.AsyncMock()` | Create a stunt double for an async function |
| `with pytest.raises(Error):` | Verify that code correctly raises an error |
| `@pytest.mark.asyncio` | Required for testing `async def` functions |

---

## Assessment

**1. What is a "Fixture" in Pytest?**
a) A light bulb in the testing room.
b) A reusable piece of setup code/data for tests.
c) A bug that is permanently fixed.

**2. Why do we "Mock" the OpenAI client?**
a) To make the AI feel bad.
b) To save money, run tests faster, and work offline.
c) Because OpenAI requires it for testing.

**3. What does "Red → Green → Refactor" mean?**
a) Traffic light patterns.
b) The TDD workflow of failing test, passing code, then cleaning up.
c) The colors used in the Pytest console.

<details>
<summary>💡 Answers</summary>
1. b
2. b
3. b
</details>

---

## Summary

**Testing** is what separates "scripts" from "software."
- **Pytest** runs the checks.
- **Fixtures** prep the data.
- **Mocks** fake the expensive parts.
- **Asyncio** marks the time-sensitive tests.

**You have officially completed the Python Bridge!** 🏆🎉

You now have the structural, performance, and reliability skills of a professional Python developer. You are ready for the most exciting part of the journey.

---

**Next: [Milestone 3: RAG Fundamentals → Chapter 13: Understanding Embeddings](chapter-13-embeddings.md)** 🧠🚀

*Great job! You've built an incredible foundation. Now let's make your AI remember everything.* 💪
