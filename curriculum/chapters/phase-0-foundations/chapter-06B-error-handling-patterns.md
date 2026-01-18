# Chapter 6B: Error Handling Patterns — Making Your Code Bulletproof

<!--
METADATA
Phase: Python Bridge Module 1 (PBM-1)
Time: 1.5 hours (30 minutes reading + 60 minutes hands-on)
Difficulty: ⭐⭐
Type: Foundation (Python Intermediate)
Prerequisites: Chapters 1-6, 6A (Decorators, Basic try/except)
Builds Toward: Chapters 7-12 (LLM error handling), 39-40 (Testing & Production)
Correctness Properties: Error propagation, Graceful degradation

NAVIGATION
→ Quick Reference: #quick-reference
→ Verification: #verification
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

> **Imagine this**: You're building an AI chatbot for a coffee shop. A customer asks for recommendations, and your app calls an LLM API... but the API is down. 💥
>
> Should your entire app crash with a cryptic error message? Should it silently fail and confuse the customer? Or should it gracefully say "Sorry, recommendations are temporarily unavailable. Here's our menu instead!"?
>
> The difference is professional error handling - and it's what separates amateur code from production-ready systems.
>
> **By the end of this chapter**, you'll build robust error handling that makes your code self-healing, informative when things go wrong, and trustworthy for production use.

---

## Prerequisites Check

Let's make sure you're ready:

```bash
python -c "try: x = 1/0\nexcept ZeroDivisionError as e: print(f'✓ Caught error: {e}')"
```

**If this prints "✓ Caught error: division by zero"**, you're good to go! ✅

**If it fails**, review Chapter 5 on basic error handling.

**You should be comfortable with**:
- Basic try/except blocks
- Raising exceptions
- Understanding stack traces
- Decorators from Chapter 6A (we'll use them!)

*Don't worry if you're rusty - we'll reinforce everything as we go!* 😊

---

## What You Already Know 🧩

### 📌 From Previous Chapters

Think of this chapter as leveling up your error handling skills:

<table>
<tr>
<th>Concept You Know</th>
<th>How We'll Level It Up</th>
</tr>
<tr>
<td>Basic try/except (Ch 5)</td>
<td>We'll create custom exceptions that carry context and meaning</td>
</tr>
<tr>
<td>Decorators (Ch 6A)</td>
<td>We'll use decorators to add error handling automatically</td>
</tr>
<tr>
<td>Type hints (Ch 2)</td>
<td>We'll use types to represent Success/Failure explicitly</td>
</tr>
</table>

### 🔮 Where This Leads

You'll use these skills in:
- **Chapter 7-12**: LLM API calls fail - your code handles it gracefully
- **Chapter 17-22**: RAG systems need robust error recovery
- **Chapter 39-40**: Production systems require comprehensive error handling
- **Final Project (Ch 54)**: Your Civil Engineering app handles errors professionally

*Error handling is what makes your code production-ready!* 💪

---

## The Story: Why Better Error Handling Matters

### The Problem (When Errors Go Wrong)

Okay, picture this. You're building an LLM-powered document generator. A simple function that calls OpenAI:

```python
def generate_summary(text: str) -> str:
    """Generate summary using OpenAI"""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Summarize: {text}"}]
    )
    return response.choices[0].message.content
```

Looks simple, right? Now watch what happens when things go wrong:

**Scenario 1**: API key is invalid
```python
generate_summary("Long document...")
# 💥 openai.AuthenticationError: Incorrect API key provided
# Stack trace: 50 lines of cryptic error messages
# User sees: Complete crash, no idea what happened
```

**Scenario 2**: Rate limit exceeded
```python
generate_summary("Another document...")
# 💥 openai.RateLimitError: Rate limit exceeded
# App crashes, user loses all unsaved work
```

**Scenario 3**: Network timeout
```python
generate_summary("Yet another document...")
# 💥 requests.exceptions.Timeout: Request timed out
# User waits forever, then app freezes
```

**The pain points**:
- ❌ Every error crashes the entire application
- ❌ Error messages are technical gibberish for users
- ❌ No way to recover or retry
- ❌ No logging - you can't debug what went wrong
- ❌ Each error type requires different handling, but code doesn't distinguish

*If this makes you cringe, you're not alone! Let's fix it!*

---

### The Naive Solution

> "Let's just wrap everything in try/except!"

```python
def generate_summary(text: str) -> str:
    try:
        response = openai.chat.completions.create(...)
        return response.choices[0].message.content
    except:  # Catch EVERYTHING
        return "Error occurred"  # 😱 What error? Why?
```

**Why This Breaks**:
- ❌ Catches ALL exceptions (even KeyboardInterrupt!)
- ❌ User sees "Error occurred" - completely unhelpful
- ❌ No logging - you have no idea what went wrong
- ❌ Can't retry or handle different errors differently
- ❌ Hides bugs instead of fixing them

---

### The Elegant Solution (Professional Error Handling)

Alright, let me show you how professionals handle errors:

```python
from typing import Union
from dataclasses import dataclass
import logging

# Custom exception for domain-specific errors
class DocumentGenerationError(Exception):
    """Base exception for document generation failures"""
    pass

# Result type - explicitly represents success or failure
@dataclass
class Result:
    success: bool
    data: any = None
    error: str = None
    error_type: str = None

def generate_summary(text: str) -> Result:
    """Generate summary with robust error handling"""
    try:
        response = openai.chat.completions.create(...)
        return Result(
            success=True,
            data=response.choices[0].message.content
        )

    except openai.AuthenticationError as e:
        logging.error(f"API auth failed: {e}")
        return Result(
            success=False,
            error="Invalid API credentials. Please check configuration.",
            error_type="auth"
        )

    except openai.RateLimitError as e:
        logging.warning(f"Rate limit hit: {e}")
        return Result(
            success=False,
            error="Service temporarily busy. Please try again in a moment.",
            error_type="rate_limit"
        )

    except Exception as e:
        logging.exception("Unexpected error in generate_summary")
        return Result(
            success=False,
            error=f"Generation failed: {str(e)}",
            error_type="unexpected"
        )

# Using it
result = generate_summary("Long document...")
if result.success:
    print(f"Summary: {result.data}")
else:
    print(f"Error: {result.error}")
    if result.error_type == "rate_limit":
        # Could retry after delay
        pass
```

**Look at the benefits!** 🤩
- ✅ Specific exception handling (auth vs rate limit vs other)
- ✅ User-friendly error messages
- ✅ Detailed logging for debugging
- ✅ Explicit success/failure in return type
- ✅ Caller can decide how to handle each error type
- ✅ No crashes - graceful degradation

> **The Big Insight**:
> - **Custom Exceptions** = Domain-specific, meaningful errors
> - **Result Type** = Explicit success/failure (no guessing!)
> - **Specific Handling** = Different recovery for different errors
> - **Logging** = Debugging and monitoring
>
> Professional error handling turns crashes into conversations with your code.

*Now let's learn how to build this! Don't worry, we'll start simple.* 😊

---

## Part 1: Custom Exception Classes (Making Errors Meaningful)

### What's a Custom Exception, Really?

Okay, let's start with an analogy.

**Analogy: Error Messages at a Hospital** 🏥

Generic Exception:
> "Something went wrong in the building"

Custom Exception:
> "Patient needs X-ray in Radiology, Room 204"

Which one helps you fix the problem? The specific one! Custom exceptions give errors context and meaning.

**In Python terms**:
- **Generic** `Exception` = "Something broke somewhere"
- **Custom** `InvalidAPIKeyError` = "API authentication failed, check credentials"

*Let's create our first custom exception...*

---

### Your First Custom Exception: Hello Error World

Let's create a custom exception for document processing:

```python
class DocumentError(Exception):
    """Base exception for document-related errors"""
    pass

class DocumentTooLargeError(DocumentError):
    """Raised when document exceeds size limit"""
    pass

class DocumentFormatError(DocumentError):
    """Raised when document format is invalid"""
    pass

# Using them
def process_document(doc: str, max_size: int = 1000):
    if len(doc) > max_size:
        raise DocumentTooLargeError(
            f"Document is {len(doc)} chars, max is {max_size}"
        )

    if not doc.strip():
        raise DocumentFormatError("Document is empty")

    return f"Processed: {doc[:50]}..."

# Try it
try:
    process_document("a" * 2000)  # Too large!
except DocumentTooLargeError as e:
    print(f"❌ Size error: {e}")
except DocumentFormatError as e:
    print(f"❌ Format error: {e}")
```

**Output**:
```
❌ Size error: Document is 2000 chars, max is 1000
```

**Let's break down what just happened**:

1. We created a **base exception** `DocumentError` (like a family name)
2. We created **specific exceptions** that inherit from it
3. When we raise them, we include **helpful context** (actual vs max size)
4. When we catch them, we can handle **each type differently**

*See? Now errors tell a story!*

---

### Exception Hierarchy (The Family Tree)

Think of exceptions like a family tree:

```
Exception (Python's base)
  ↓
DocumentError (Your base)
  ├── DocumentTooLargeError
  ├── DocumentFormatError
  └── DocumentNotFoundError
```

**Why this matters**:

```python
try:
    process_document(...)
except DocumentError as e:
    # Catches ALL document errors (any child class)
    print(f"Document error: {e}")
```

vs

```python
try:
    process_document(...)
except DocumentTooLargeError as e:
    # Only catches size errors - more specific handling
    print(f"Split document and try again: {e}")
except DocumentFormatError as e:
    # Only catches format errors
    print(f"Fix format: {e}")
```

**Rule of thumb**: Catch **specific exceptions** when you can handle them specifically, catch **base exceptions** when you want to handle them all the same way.

---

### 🔬 Try This! (Hands-On Practice #1)

Let's practice creating custom exceptions!

**Challenge**: Create a custom exception hierarchy for API errors.

**Starter code**:
```python
class APIError(Exception):
    """Base exception for API-related errors"""
    pass

# Your code: Create 3 specific exceptions that inherit from APIError
# 1. APIAuthenticationError - for auth failures
# 2. APIRateLimitError - for rate limits
# 3. APITimeoutError - for timeouts

def call_api(endpoint: str, has_auth: bool = True):
    if not has_auth:
        # Raise APIAuthenticationError
        pass

    # Test your exceptions
    raise APIAuthenticationError("Invalid API key")

# Test it
try:
    call_api("/data", has_auth=False)
except APIAuthenticationError as e:
    print(f"Auth failed: {e}")
```

<details>
<summary>💡 Hint</summary>

Create classes that inherit from `APIError`:
```python
class APIAuthenticationError(APIError):
    pass
```

</details>

<details>
<summary>✅ Solution</summary>

```python
class APIError(Exception):
    """Base exception for API-related errors"""
    pass

class APIAuthenticationError(APIError):
    """Raised when API authentication fails"""
    pass

class APIRateLimitError(APIError):
    """Raised when API rate limit is exceeded"""
    pass

class APITimeoutError(APIError):
    """Raised when API request times out"""
    pass

def call_api(endpoint: str, has_auth: bool = True):
    if not has_auth:
        raise APIAuthenticationError("Invalid API key provided")

    return {"data": "success"}

# Test it
try:
    call_api("/data", has_auth=False)
except APIAuthenticationError as e:
    print(f"Auth failed: {e}")
```

</details>

*Try creating these yourself before looking! Making mistakes helps you learn.* 🧠

---

### Adding Context to Exceptions

Let's make exceptions even more useful by adding context:

```python
class APIError(Exception):
    """Base API exception with context"""

    def __init__(self, message: str, status_code: int = None, endpoint: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.endpoint = endpoint
        self.timestamp = datetime.now()

    def __str__(self):
        parts = [self.message]
        if self.endpoint:
            parts.append(f"Endpoint: {self.endpoint}")
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        return " | ".join(parts)

# Using it
raise APIError(
    message="Rate limit exceeded",
    status_code=429,
    endpoint="/api/generate"
)

# When caught:
# APIError: Rate limit exceeded | Endpoint: /api/generate | Status: 429
```

**Now errors carry all the context you need for debugging!** 🎯

---

## Transition: From Custom Exceptions to Result Types

Okay, you've learned to create meaningful exceptions! Give yourself a high-five. 🙌

Now let's tackle a different problem: **How do you know if a function might fail?**

**The setup**: With exceptions, you can't tell from the function signature:

```python
def generate_summary(text: str) -> str:
    # Might return a string... or raise 5 different exceptions?
    # Caller has no idea!
```

You have to read the docs (or the code) to know what can go wrong.

**What if the function signature told you**: *"This function might succeed with a string, or fail with an error"*?

That's where the **Result type pattern** comes in! Let's dive in...

---

## Part 2: The Result Type Pattern (Explicit Success/Failure)

### What's a Result Type, Really?

Let me paint you a picture with an analogy.

**Analogy: Opening a Treasure Chest** 🎁

Traditional approach (exceptions):
> You try to open the chest. Either treasure pops out, or it explodes (exception thrown!). You don't know until you try.

Result type approach:
> The chest has a label: "CONTAINS: Treasure" or "CONTAINS: Trap". You know what you're getting BEFORE you open it.

**In Python terms**:
- **Traditional**: Function returns value OR raises exception (surprise!)
- **Result type**: Function ALWAYS returns Result object that says "success + data" or "failure + error"

*Let's build this pattern...*

---

### Building a Simple Result Type

Let's start with the basics:

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

T = TypeVar('T')  # Generic type for the data

@dataclass
class Result(Generic[T]):
    """Represents either success with data, or failure with error"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

    @staticmethod
    def ok(data: T) -> 'Result[T]':
        """Create a successful result"""
        return Result(success=True, data=data)

    @staticmethod
    def fail(error: str) -> 'Result[T]':
        """Create a failed result"""
        return Result(success=False, error=error)

    def unwrap(self) -> T:
        """Get the data (raises if failure)"""
        if not self.success:
            raise ValueError(f"Called unwrap() on failed Result: {self.error}")
        return self.data

    def unwrap_or(self, default: T) -> T:
        """Get the data, or default if failure"""
        return self.data if self.success else default

# Using it
def divide(a: int, b: int) -> Result[float]:
    if b == 0:
        return Result.fail("Division by zero")
    return Result.ok(a / b)

# Success case
result = divide(10, 2)
if result.success:
    print(f"Result: {result.data}")  # Result: 5.0

# Failure case
result = divide(10, 0)
if result.success:
    print(f"Result: {result.data}")
else:
    print(f"Error: {result.error}")  # Error: Division by zero

# Or use helper methods
value = divide(10, 2).unwrap()  # Gets 5.0
value = divide(10, 0).unwrap_or(0.0)  # Gets 0.0 (default)
```

**See the power?** 🤩
- ✅ Function signature says "might fail" (returns Result)
- ✅ No surprise exceptions
- ✅ Caller MUST check success before using data
- ✅ Clear, explicit error handling

---

### 🔬 Try This! (Hands-On Practice #2)

Let's practice using the Result type!

**Challenge**: Create a function that validates email addresses using Result.

**Starter code**:
```python
import re

def validate_email(email: str) -> Result[str]:
    """Validate email address, return Result"""
    # Your code:
    # 1. Check if email contains @ symbol
    # 2. Check if email matches basic pattern (has @ and .)
    # 3. Return Result.ok(email) if valid
    # 4. Return Result.fail("reason") if invalid
    pass

# Test it
result = validate_email("user@example.com")
if result.success:
    print(f"✓ Valid: {result.data}")
else:
    print(f"✗ Invalid: {result.error}")

result = validate_email("invalid-email")
if result.success:
    print(f"✓ Valid: {result.data}")
else:
    print(f"✗ Invalid: {result.error}")
```

<details>
<summary>💡 Hint</summary>

1. Check for @ first: `if '@' not in email:`
2. Use regex: `re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)`
3. Return `Result.ok(email)` or `Result.fail("message")`

</details>

<details>
<summary>✅ Solution</summary>

```python
import re

def validate_email(email: str) -> Result[str]:
    """Validate email address, return Result"""

    if not email:
        return Result.fail("Email is empty")

    if '@' not in email:
        return Result.fail("Email must contain @ symbol")

    # Basic email regex
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        return Result.fail("Email format is invalid")

    return Result.ok(email)

# Test it
result = validate_email("user@example.com")
print(f"✓ Valid: {result.data}" if result.success else f"✗ Invalid: {result.error}")
# Output: ✓ Valid: user@example.com

result = validate_email("invalid-email")
print(f"✓ Valid: {result.data}" if result.success else f"✗ Invalid: {result.error}")
# Output: ✗ Invalid: Email must contain @ symbol
```

</details>

*Try this before looking! The practice makes it stick.* 💪

---

### Real-World Example: LLM API Call with Result

Let's apply this to actual LLM code:

```python
from typing import Dict, Any
import logging

@dataclass
class Result(Generic[T]):
    # ... (Result class from above)

    @property
    def is_ok(self) -> bool:
        """Alias for success check"""
        return self.success

    @property
    def is_err(self) -> bool:
        """Check if result is an error"""
        return not self.success

def call_llm(
    prompt: str,
    model: str = "gpt-4",
    max_retries: int = 3
) -> Result[str]:
    """
    Call LLM API with proper error handling

    Returns:
        Result[str]: Success with response text, or failure with error message
    """

    if not prompt.strip():
        return Result.fail("Prompt cannot be empty")

    for attempt in range(max_retries):
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.choices[0].message.content
            logging.info(f"LLM call succeeded (attempt {attempt + 1})")
            return Result.ok(content)

        except openai.AuthenticationError as e:
            logging.error(f"Auth error: {e}")
            return Result.fail("Invalid API credentials")

        except openai.RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logging.warning(f"Rate limit hit, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                logging.error("Rate limit exceeded after retries")
                return Result.fail("Service is busy, please try again later")

        except Exception as e:
            logging.exception(f"Unexpected error on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                continue
            else:
                return Result.fail(f"Request failed: {str(e)}")

    return Result.fail("All retry attempts exhausted")

# Using it
result = call_llm("Explain quantum physics in one sentence")

if result.is_ok:
    print(f"Response: {result.data}")
    # Use the response...
elif result.error == "Invalid API credentials":
    print("Please configure API key")
elif result.error.startswith("Service is busy"):
    print("Try again in a few minutes")
else:
    print(f"Error: {result.error}")
```

**This is production-ready error handling!** Look at the benefits:
- ✅ Clear return type: `Result[str]`
- ✅ Retry logic built-in
- ✅ Specific error handling (auth vs rate limit)
- ✅ Comprehensive logging
- ✅ Caller can handle errors appropriately
- ✅ No surprise exceptions

*This is the code you'll write in Chapters 7-12!* 🎯

---

## Part 3: Error Propagation Strategies

Alright, now let's talk about a common problem: **What do you do when a function you call fails?**

Should you:
1. Handle it immediately?
2. Pass the error up to your caller?
3. Convert it to a different error type?
4. Log and continue?

Let's explore each strategy...

---

### Strategy 1: Handle Immediately (Catch and Recover)

**When to use**: You can fix the problem locally

```python
def load_config(file_path: str) -> Dict:
    """Load config, use defaults if file missing"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Can recover! Use defaults
        logging.warning(f"Config not found at {file_path}, using defaults")
        return {"host": "localhost", "port": 8080}
    except json.JSONDecodeError as e:
        # Can't recover - re-raise with context
        raise ConfigError(f"Invalid config file: {e}")
```

---

### Strategy 2: Propagate Up (Let Caller Handle)

**When to use**: Caller is better positioned to handle the error

```python
def fetch_user_data(user_id: int) -> Result[Dict]:
    """Fetch user data - caller decides what to do on failure"""
    result = call_api(f"/users/{user_id}")

    if result.is_err:
        # Propagate the error up
        return Result.fail(f"Failed to fetch user {user_id}: {result.error}")

    return Result.ok(result.data)

# Caller decides what to do
result = fetch_user_data(123)
if result.is_err:
    # Maybe show cached data? Retry? Show error to user?
    # Caller has the context to decide
    pass
```

---

### Strategy 3: Convert Error Type (Re-wrap)

**When to use**: Low-level error needs to become domain-specific

```python
def save_document(doc: Document) -> Result[str]:
    """Save document to database"""
    try:
        db.insert(doc.to_dict())
        return Result.ok(doc.id)

    except DatabaseConnectionError as e:
        # Convert low-level DB error to domain error
        return Result.fail("Cannot save document - database unavailable")

    except DatabaseUniqueConstraintError as e:
        # Convert to domain-specific error
        return Result.fail(f"Document {doc.id} already exists")
```

---

### Strategy 4: Log and Continue (Graceful Degradation)

**When to use**: Failure is acceptable, feature is optional

```python
def enrich_document(doc: Document) -> Document:
    """Enrich document with AI-generated summary (optional)"""
    try:
        summary_result = call_llm(f"Summarize: {doc.content}")
        if summary_result.is_ok:
            doc.summary = summary_result.data
        else:
            # Log failure but continue
            logging.warning(f"Could not generate summary: {summary_result.error}")
            doc.summary = None  # Optional feature

    except Exception as e:
        # Unexpected error - log and continue
        logging.exception("Unexpected error in enrich_document")
        doc.summary = None

    return doc  # Always return document, even if enrichment failed
```

---

### 🔬 Try This! (Hands-On Practice #3)

**Challenge**: Implement error propagation in a multi-step process.

**Scenario**: Load config → Connect to database → Fetch data

Each step can fail. Decide the best strategy for each!

**Starter code**:
```python
def load_config(path: str) -> Result[Dict]:
    # Your code: Load config, use defaults if missing
    pass

def connect_db(config: Dict) -> Result[Connection]:
    # Your code: Connect to DB, fail if can't connect
    pass

def fetch_data(conn: Connection) -> Result[List[Dict]]:
    # Your code: Fetch data, fail if query fails
    pass

def process_data() -> Result[List[Dict]]:
    """Multi-step process with error handling"""
    # Your code: Chain the above functions
    # Use proper error propagation!
    pass

# Test it
result = process_data()
if result.is_ok:
    print(f"Got {len(result.data)} records")
else:
    print(f"Failed: {result.error}")
```

<details>
<summary>✅ Solution</summary>

```python
def load_config(path: str) -> Result[Dict]:
    """Load config, use defaults if missing (Strategy 1: Handle Immediately)"""
    try:
        with open(path, 'r') as f:
            return Result.ok(json.load(f))
    except FileNotFoundError:
        # Recover with defaults
        return Result.ok({"host": "localhost", "port": 5432})
    except json.JSONDecodeError as e:
        return Result.fail(f"Invalid config: {e}")

def connect_db(config: Dict) -> Result['Connection']:
    """Connect to database (Strategy 2: Propagate failure up)"""
    try:
        conn = database.connect(**config)
        return Result.ok(conn)
    except Exception as e:
        # Can't handle here - propagate
        return Result.fail(f"Database connection failed: {e}")

def fetch_data(conn: 'Connection') -> Result[List[Dict]]:
    """Fetch data (Strategy 2: Propagate failure up)"""
    try:
        data = conn.execute("SELECT * FROM users")
        return Result.ok(data)
    except Exception as e:
        return Result.fail(f"Query failed: {e}")

def process_data() -> Result[List[Dict]]:
    """Multi-step process with proper error propagation"""

    # Step 1: Load config (handles errors internally)
    config_result = load_config("config.json")
    if config_result.is_err:
        return Result.fail(f"Config error: {config_result.error}")

    # Step 2: Connect to DB (propagates errors)
    conn_result = connect_db(config_result.data)
    if conn_result.is_err:
        return Result.fail(f"Connection error: {conn_result.error}")

    # Step 3: Fetch data (propagates errors)
    data_result = fetch_data(conn_result.data)
    if data_result.is_err:
        return Result.fail(f"Data fetch error: {data_result.error}")

    return Result.ok(data_result.data)
```

</details>

---

## Part 4: Logging Best Practices

Alright, last piece of the puzzle: **Logging!**

**The setup**: When errors happen in production, you're not there to debug. Logs are your time machine - they tell you what happened.

Let's learn to log effectively...

---

### Logging Levels (Know Your Tools)

Python's logging module has 5 levels:

```python
import logging

logging.debug("Detailed diagnostic info")      # For developers during development
logging.info("Normal operation")               # Confirm things work
logging.warning("Something unexpected happened") # Potential problem
logging.error("Error occurred")                # Serious problem
logging.critical("System is unusable")         # Emergency!
```

**When to use each**:
- **DEBUG**: Variable values, loop iterations, "entering function X"
- **INFO**: "Started processing", "Completed successfully", "User logged in"
- **WARNING**: "Using default value", "Deprecated API called", "Retrying..."
- **ERROR**: Exceptions caught, operations failed
- **CRITICAL**: System crash, data corruption, security breach

---

### Setting Up Logging Properly

```python
import logging
from datetime import datetime

# Configure logging (do this once at app startup)
logging.basicConfig(
    level=logging.INFO,  # Minimum level to log
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler(f'app_{datetime.now():%Y%m%d}.log'),  # To file
        logging.StreamHandler()  # Also to console
    ]
)

# Create logger for your module
logger = logging.getLogger(__name__)

# Use it
logger.info("Application started")
logger.warning("Config file not found, using defaults")
logger.error("Failed to connect to database")
```

**Output**:
```
2026-01-16 10:30:45 | INFO     | __main__ | Application started
2026-01-16 10:30:45 | WARNING  | __main__ | Config file not found, using defaults
2026-01-16 10:30:46 | ERROR    | __main__ | Failed to connect to database
```

---

### Logging in Error Handling

Here's how to combine logging with error handling:

```python
def call_external_api(endpoint: str) -> Result[Dict]:
    """Call external API with logging"""
    logger.info(f"Calling API: {endpoint}")

    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()

        logger.info(f"API call succeeded: {endpoint}")
        return Result.ok(response.json())

    except requests.Timeout:
        logger.warning(f"API timeout: {endpoint}")
        return Result.fail("Request timed out")

    except requests.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning(f"Rate limit hit: {endpoint}")
            return Result.fail("Rate limit exceeded")
        else:
            logger.error(f"HTTP error {e.response.status_code}: {endpoint}")
            return Result.fail(f"API error: {e.response.status_code}")

    except Exception as e:
        # Use .exception() to include stack trace
        logger.exception(f"Unexpected error calling {endpoint}")
        return Result.fail(f"Unexpected error: {str(e)}")
```

**Key practices**:
- ✅ Log before risky operations ("Calling API...")
- ✅ Log successful outcomes ("API call succeeded")
- ✅ Use appropriate levels (warning for retryable, error for failures)
- ✅ Use `logger.exception()` for unexpected errors (includes stack trace)
- ✅ Include context (endpoint, parameters, etc.)

---

## Bringing It All Together: Robust Document Processor

Alright, let's build a comprehensive example using everything you've learned!

**What it will do**:
- Custom exceptions for domain errors
- Result type for explicit success/failure
- Proper error propagation
- Comprehensive logging

This is production-ready code!

---

### Step 1: Create `exceptions.py`

```python
"""Custom exceptions for document processing"""

class DocumentError(Exception):
    """Base exception for document processing"""
    pass

class DocumentTooLargeError(DocumentError):
    """Document exceeds size limit"""
    def __init__(self, size: int, max_size: int):
        self.size = size
        self.max_size = max_size
        super().__init__(f"Document size {size} exceeds limit {max_size}")

class DocumentFormatError(DocumentError):
    """Invalid document format"""
    pass

class ProcessingError(DocumentError):
    """Error during document processing"""
    pass
```

---

### Step 2: Create `result.py`

```python
"""Result type for explicit success/failure"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Callable

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    """Represents either success or failure"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

    @staticmethod
    def ok(data: T) -> 'Result[T]':
        """Create successful result"""
        return Result(success=True, data=data)

    @staticmethod
    def fail(error: str) -> 'Result[T]':
        """Create failed result"""
        return Result(success=False, error=error)

    def map(self, func: Callable[[T], any]) -> 'Result':
        """Transform data if success, otherwise propagate error"""
        if self.success:
            try:
                return Result.ok(func(self.data))
            except Exception as e:
                return Result.fail(str(e))
        return self

    def and_then(self, func: Callable[[T], 'Result']) -> 'Result':
        """Chain operations, short-circuit on failure"""
        if self.success:
            return func(self.data)
        return self

    @property
    def is_ok(self) -> bool:
        return self.success

    @property
    def is_err(self) -> bool:
        return not self.success
```

---

### Step 3: Create `document_processor.py`

```python
"""Document processor with robust error handling"""

import logging
from typing import Dict
from exceptions import *
from result import Result

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process documents with robust error handling"""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        logger.info(f"DocumentProcessor initialized (max_size={max_size})")

    def validate_document(self, content: str) -> Result[str]:
        """Validate document meets requirements"""
        logger.debug("Validating document")

        if not content or not content.strip():
            logger.warning("Empty document rejected")
            return Result.fail("Document is empty")

        if len(content) > self.max_size:
            logger.warning(f"Document too large: {len(content)} > {self.max_size}")
            return Result.fail(
                f"Document size {len(content)} exceeds limit {self.max_size}"
            )

        logger.info("Document validation passed")
        return Result.ok(content)

    def process_content(self, content: str) -> Result[Dict]:
        """Process document content"""
        logger.info("Processing document content")

        try:
            # Simulate processing
            words = content.split()
            result = {
                "word_count": len(words),
                "char_count": len(content),
                "preview": content[:100]
            }

            logger.info(f"Processing complete: {result['word_count']} words")
            return Result.ok(result)

        except Exception as e:
            logger.exception("Unexpected error during processing")
            return Result.fail(f"Processing failed: {str(e)}")

    def generate_summary(self, content: str) -> Result[str]:
        """Generate AI summary (can fail gracefully)"""
        logger.info("Generating AI summary")

        try:
            # Simulate LLM call
            summary = f"Summary of {len(content.split())} word document"
            logger.info("Summary generated successfully")
            return Result.ok(summary)

        except Exception as e:
            # Non-critical failure - log and return failure
            logger.warning(f"Summary generation failed: {e}")
            return Result.fail("Summary unavailable")

    def process_document(self, content: str) -> Result[Dict]:
        """
        Complete document processing pipeline

        Returns:
            Result[Dict]: Success with processed data, or failure with error
        """
        logger.info("=" * 60)
        logger.info("Starting document processing pipeline")

        # Step 1: Validate (critical - must succeed)
        validation_result = self.validate_document(content)
        if validation_result.is_err:
            logger.error(f"Validation failed: {validation_result.error}")
            return Result.fail(f"Validation error: {validation_result.error}")

        # Step 2: Process (critical - must succeed)
        process_result = self.process_content(validation_result.data)
        if process_result.is_err:
            logger.error(f"Processing failed: {process_result.error}")
            return Result.fail(f"Processing error: {process_result.error}")

        # Step 3: Generate summary (optional - can fail gracefully)
        summary_result = self.generate_summary(content)
        if summary_result.is_ok:
            process_result.data['summary'] = summary_result.data
        else:
            logger.warning("Continuing without summary")
            process_result.data['summary'] = None

        logger.info("Document processing complete")
        return process_result

# Example usage
def main():
    processor = DocumentProcessor(max_size=1000)

    # Test 1: Valid document
    print("\n--- Test 1: Valid Document ---")
    result = processor.process_document("This is a test document with several words.")
    if result.is_ok:
        print(f"✓ Success: {result.data}")
    else:
        print(f"✗ Failed: {result.error}")

    # Test 2: Empty document
    print("\n--- Test 2: Empty Document ---")
    result = processor.process_document("")
    if result.is_ok:
        print(f"✓ Success: {result.data}")
    else:
        print(f"✗ Failed: {result.error}")

    # Test 3: Document too large
    print("\n--- Test 3: Large Document ---")
    result = processor.process_document("word " * 500)
    if result.is_ok:
        print(f"✓ Success: {result.data}")
    else:
        print(f"✗ Failed: {result.error}")

if __name__ == '__main__':
    main()
```

---

### Step 4: Run It!

```bash
python document_processor.py
```

**Expected output**:
```
2026-01-16 10:30:00 | INFO     | DocumentProcessor initialized (max_size=1000)

--- Test 1: Valid Document ---
2026-01-16 10:30:00 | INFO     | ============================================================
2026-01-16 10:30:00 | INFO     | Starting document processing pipeline
2026-01-16 10:30:00 | INFO     | Document validation passed
2026-01-16 10:30:00 | INFO     | Processing document content
2026-01-16 10:30:00 | INFO     | Processing complete: 8 words
2026-01-16 10:30:00 | INFO     | Generating AI summary
2026-01-16 10:30:00 | INFO     | Summary generated successfully
2026-01-16 10:30:00 | INFO     | Document processing complete
✓ Success: {'word_count': 8, 'char_count': 42, 'preview': 'This is a test document with several words.', 'summary': 'Summary of 8 word document'}

--- Test 2: Empty Document ---
2026-01-16 10:30:00 | INFO     | ============================================================
2026-01-16 10:30:00 | INFO     | Starting document processing pipeline
2026-01-16 10:30:00 | WARNING  | Empty document rejected
2026-01-16 10:30:00 | ERROR    | Validation failed: Document is empty
✗ Failed: Validation error: Document is empty

--- Test 3: Large Document ---
2026-01-16 10:30:00 | INFO     | ============================================================
2026-01-16 10:30:00 | INFO     | Starting document processing pipeline
2026-01-16 10:30:00 | WARNING  | Document too large: 3000 > 1000
2026-01-16 10:30:00 | ERROR    | Validation failed: Document size 3000 exceeds limit 1000
✗ Failed: Validation error: Document size 3000 exceeds limit 1000
```

**Amazing, right?** Look at what you've built:
- ✅ Custom exceptions for domain errors
- ✅ Result type for explicit success/failure
- ✅ Multi-step pipeline with proper error propagation
- ✅ Graceful degradation (summary optional)
- ✅ Comprehensive logging at every step
- ✅ Professional error messages

*This is the code you'll write in Chapters 7-54!* 🎉

---

## Common Mistakes (Learn from Others!)

### Mistake #1: Catching All Exceptions

```python
# ❌ WRONG - Catches EVERYTHING including KeyboardInterrupt
try:
    do_something()
except:  # Bare except!
    print("Error occurred")

# ✅ CORRECT - Catch specific exceptions
try:
    do_something()
except ValueError as e:
    print(f"Value error: {e}")
except KeyError as e:
    print(f"Key error: {e}")
except Exception as e:  # Catch remaining, but not BaseException
    print(f"Unexpected: {e}")
```

**Why it matters**: Bare `except:` catches system exits, keyboard interrupts, and makes debugging impossible!

---

### Mistake #2: Swallowing Errors

```python
# ❌ WRONG - Error disappears without trace
try:
    result = call_api()
except Exception:
    pass  # Silent failure!

# ✅ CORRECT - Log the error
try:
    result = call_api()
except Exception as e:
    logger.exception("API call failed")
    return Result.fail(str(e))
```

**Why it matters**: Silent failures are debugging nightmares!

---

### Mistake #3: Not Providing Context

```python
# ❌ WRONG - What URL? What status code?
raise Exception("API call failed")

# ✅ CORRECT - Include context
raise APIError(
    message="API call failed",
    endpoint="/api/users",
    status_code=500,
    retry_count=3
)
```

---

### Mistake #4: Using Exceptions for Control Flow

```python
# ❌ WRONG - Exceptions aren't for normal flow
try:
    user = find_user(user_id)
except UserNotFoundError:
    user = create_user(user_id)  # This is normal business logic!

# ✅ CORRECT - Use explicit checks
user = find_user(user_id)
if user is None:
    user = create_user(user_id)
```

**Why it matters**: Exceptions are expensive and should be for exceptional situations!

---

## Quick Reference Card

### Custom Exception Template

```python
class MyError(Exception):
    """Base exception for my module"""

    def __init__(self, message: str, **context):
        super().__init__(message)
        self.message = message
        self.context = context

    def __str__(self):
        parts = [self.message]
        for key, value in self.context.items():
            parts.append(f"{key}={value}")
        return " | ".join(parts)
```

### Result Type Template

```python
@dataclass
class Result(Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

    @staticmethod
    def ok(data: T) -> 'Result[T]':
        return Result(success=True, data=data)

    @staticmethod
    def fail(error: str) -> 'Result[T]':
        return Result(success=False, error=error)
```

### Logging Template

```python
import logging

logger = logging.getLogger(__name__)

try:
    logger.info("Starting operation")
    result = do_something()
    logger.info("Operation completed successfully")
    return Result.ok(result)
except SpecificError as e:
    logger.warning(f"Expected error: {e}")
    return Result.fail("User-friendly message")
except Exception as e:
    logger.exception("Unexpected error")
    return Result.fail(f"Operation failed: {str(e)}")
```

---

## Verification (Test Your Knowledge!)

```python
import logging

print("🧪 Running verification tests...\n")

# Test 1: Custom exceptions work correctly
print("Test 1: Custom exceptions")
class TestError(Exception):
    pass

try:
    raise TestError("Test message")
except TestError as e:
    assert str(e) == "Test message"
    print("✅ Passed! Custom exceptions work\n")

# Test 2: Result type handles success/failure
print("Test 2: Result type")
success = Result.ok(42)
failure = Result.fail("Error message")

assert success.is_ok == True
assert success.data == 42
assert failure.is_err == True
assert failure.error == "Error message"
print("✅ Passed! Result type works correctly\n")

# Test 3: Error propagation
print("Test 3: Error propagation")
def step1() -> Result[int]:
    return Result.ok(10)

def step2(x: int) -> Result[int]:
    return Result.ok(x * 2)

def pipeline() -> Result[int]:
    result1 = step1()
    if result1.is_err:
        return result1
    return step2(result1.data)

result = pipeline()
assert result.is_ok and result.data == 20
print("✅ Passed! Error propagation works\n")

print("🎉 All tests passed! You understand error handling!")
```

---

## Assessment

### Quick Check Questions

1. **What's the benefit of custom exceptions over generic `Exception`?**

2. **What does the Result type make explicit that exceptions don't?**

3. **Name three logging levels and when to use each.**

4. **What's the difference between `logger.error()` and `logger.exception()`?**

5. **When should you catch and handle an error vs propagate it up?**

<details>
<summary>Click to see answers</summary>

1. Custom exceptions carry domain-specific context, are more specific to catch, and make code self-documenting

2. Result type makes success/failure explicit in the function signature - caller knows it might fail

3. INFO (normal operation), WARNING (potential problem), ERROR (serious problem that was handled)

4. `logger.exception()` includes the full stack trace, use it in except blocks for unexpected errors

5. Handle immediately if you can recover; propagate if caller has better context to decide what to do

</details>

---

### Coding Challenge

**Challenge**: Create a robust file reader with comprehensive error handling.

**Requirements**:
- Use custom exceptions for file errors
- Return `Result[str]` type
- Handle missing file (use default content)
- Handle permission denied (fail with clear error)
- Log all operations
- Handle unexpected errors gracefully

**Starter code**:
```python
class FileError(Exception):
    pass

class FileNotFoundError(FileError):
    pass

class FilePermissionError(FileError):
    pass

def read_file_robust(path: str, default: str = "") -> Result[str]:
    """
    Read file with robust error handling

    Args:
        path: File path to read
        default: Default content if file not found

    Returns:
        Result[str]: Success with content, or failure with error
    """
    # Your code here!
    pass

# Test it
result = read_file_robust("test.txt", default="Default content")
if result.is_ok:
    print(f"Content: {result.data}")
else:
    print(f"Error: {result.error}")
```

<details>
<summary>✅ Solution</summary>

```python
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class FileError(Exception):
    pass

class FilePermissionError(FileError):
    pass

def read_file_robust(path: str, default: str = "") -> Result[str]:
    """Read file with robust error handling"""
    logger.info(f"Reading file: {path}")

    try:
        with open(path, 'r') as f:
            content = f.read()
            logger.info(f"Successfully read {len(content)} chars from {path}")
            return Result.ok(content)

    except FileNotFoundError:
        logger.warning(f"File not found: {path}, using default")
        return Result.ok(default)

    except PermissionError:
        logger.error(f"Permission denied: {path}")
        return Result.fail(f"Cannot access file: permission denied")

    except Exception as e:
        logger.exception(f"Unexpected error reading {path}")
        return Result.fail(f"Failed to read file: {str(e)}")

# Test
result = read_file_robust("nonexistent.txt", default="Hello World")
print(f"Result: {result.data if result.is_ok else result.error}")
```

</details>

---

## What's Next?

Congratulations, Ahmed! You've mastered professional error handling! 🎉

### In Chapter 6C: OOP Intermediate, you'll learn:
- Inheritance and abstract classes
- Properties and computed fields
- Class methods vs instance methods
- When to use classes vs functions

### In Chapter 7: Your First LLM Call, you'll USE error handling for:
- API authentication failures
- Rate limiting and retries
- Network timeouts
- Invalid responses

*Everything you learned here will make your LLM code bulletproof!*

---

## Summary

**Custom Exceptions** make errors meaningful:
- **Pattern**: Create exception hierarchy (base + specific)
- **Key**: Include context (what, where, why)
- **Benefit**: Specific catching and handling

**Result Type** makes success/failure explicit:
- **Pattern**: `Result[T]` with `ok()` and `fail()` constructors
- **Key**: Function signature shows it might fail
- **Benefit**: No surprise exceptions, explicit error handling

**Error Propagation** strategies:
- **Handle immediately**: When you can recover
- **Propagate up**: When caller has better context
- **Convert type**: Transform low-level to domain error
- **Log and continue**: For optional features

**Logging** enables debugging:
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Key**: Use `logger.exception()` in except blocks
- **Benefit**: Know what happened in production

**You now have production-ready error handling skills!** 🎉

Your code will be robust, debuggable, and professional.

---

**Next**: [Chapter 6C: OOP Intermediate →](chapter-06C-oop-intermediate.md)

*Great job mastering error handling! You're becoming a professional developer!* 💪
