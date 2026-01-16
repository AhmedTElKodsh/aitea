# Chapter 1: Environment & Project Setup

## Header

- **Phase**: 0 - Shared Foundation
- **Time Estimate**: 1 hour
- **Difficulty**: Beginner
- **Prerequisites**: None
- **Builds**: Project structure, `config.py`, `.env` configuration
- **Requirements**: Req 1, 2, 8, 9

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. **Set up** a Python virtual environment using your preferred tool (venv, UV, or Conda)
2. **Explain** why environment isolation matters for AI/ML projects
3. **Configure** environment variables using `.env` files and `python-dotenv`
4. **Implement** type-safe configuration using Python dataclasses (manual approach)
5. **Implement** type-safe configuration using Pydantic Settings (industry standard)
6. **Compare** dataclass vs Pydantic Settings approaches and choose appropriately
7. **Debug** common environment setup issues

---

## Key Concepts

### 1. Virtual Environments: Why They Matter

**Concrete Example First:**

Imagine you're working on two projects:

- Project A needs `langchain==0.1.0`
- Project B needs `langchain==0.2.0`

Without virtual environments, installing one version breaks the other. Virtual environments solve this by creating isolated Python installations for each project.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    YOUR COMPUTER                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐                       │
│  │  Project A       │    │  Project B       │                       │
│  │  ┌────────────┐  │    │  ┌────────────┐  │                       │
│  │  │ venv/      │  │    │  │ venv/      │  │                       │
│  │  │ Python 3.11│  │    │  │ Python 3.11│  │                       │
│  │  │ langchain  │  │    │  │ langchain  │  │                       │
│  │  │ ==0.1.0    │  │    │  │ ==0.2.0    │  │                       │
│  │  └────────────┘  │    │  └────────────┘  │                       │
│  └──────────────────┘    └──────────────────┘                       │
│                                                                      │
│  Each project has its own isolated Python + packages                │
└─────────────────────────────────────────────────────────────────────┘
```

**Intuition:**
Think of virtual environments like separate apartments in a building. Each apartment (project) has its own furniture (packages) without affecting neighbors.

**Formal Definition:**
A virtual environment is an isolated Python runtime with its own site-packages directory, allowing project-specific dependency management.

---

### 2. Environment Variables: Keeping Secrets Safe

**Concrete Example First:**

```python
# ❌ BAD: Hardcoded API key (will be in git history forever!)
api_key = "sk-abc123secret456"

# ✅ GOOD: Load from environment
import os
api_key = os.getenv("OLLAMA_API_KEY")
```

**Why This Matters for AI Projects:**

- API keys for OpenAI, Anthropic, cloud services
- Database connection strings
- Model configuration (which model to use, timeouts)
- Different settings for development vs production

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENVIRONMENT VARIABLE FLOW                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  .env file (NOT in git)     python-dotenv        Your Code          │
│  ┌──────────────────┐       ┌──────────┐       ┌──────────────┐    │
│  │ OLLAMA_API_KEY=  │       │          │       │              │    │
│  │ sk-abc123...     │ ───▶  │ load_    │ ───▶  │ os.getenv()  │    │
│  │                  │       │ dotenv() │       │              │    │
│  │ OLLAMA_MODEL=    │       │          │       │ Returns      │    │
│  │ llama2           │       └──────────┘       │ values       │    │
│  └──────────────────┘                          └──────────────┘    │
│                                                                      │
│  .env.example (IN git)                                              │
│  ┌──────────────────┐                                               │
│  │ OLLAMA_API_KEY=  │  ◀── Template showing what vars are needed   │
│  │ your_key_here    │                                               │
│  └──────────────────┘                                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 3. Pydantic Settings: Type-Safe Configuration with Auto-Loading

**Concrete Example First:**

```python
# ❌ BAD: Dictionary config (no type hints, easy to typo keys)
config = {
    "ollama_url": "http://localhost:11434",
    "timout": 30,  # Typo! No error until runtime
}

# ✅ GOOD: Pydantic Settings (type hints, IDE autocomplete, auto-loading)
from pydantic_settings import BaseSettings, SettingsConfigDict

class OllamaConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OLLAMA_")

    url: str = "http://localhost:11434"
    timeout: int = 30  # IDE catches typos, auto-loads from OLLAMA_TIMEOUT
```

###

in a dataclass it’s a typed attribute, not a dict key. So yes—the
timeout: int = 30
annotation makes the field’s type explicit, which enables IDE autocomplete, static type checking, and earlier errors for typos. With a plain dict,
"timeout": 30
is just a string key/value, so typos slip through until runtime.

###

**Why Pydantic Settings for Configuration:**

| Feature                | Dict | Dataclass | Pydantic Settings |
| ---------------------- | ---- | --------- | ----------------- |
| Type hints             | ❌   | ✅        | ✅                |
| IDE autocomplete       | ❌   | ✅        | ✅                |
| Automatic `__init__`   | ❌   | ✅        | ✅                |
| Automatic `__repr__`   | ❌   | ✅        | ✅                |
| Auto env var loading   | ❌   | ❌        | ✅                |
| Auto type conversion   | ❌   | ❌        | ✅                |
| Declarative validation | ❌   | ❌        | ✅                |
| Industry standard      | ❌   | ❌        | ✅                |

---

## Project Structure

Before we dive into the code, let's understand the project structure we're building:

```
ai-contract-generator/
├── .env                    # Your actual secrets (NOT in git)
├── .env.example            # Template showing required variables
├── .gitignore              # Excludes .env, __pycache__, etc.
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
│
├── curriculum/
│   └── chapters/           # Where you are now!
│       └── chapter-01-environment-setup.md
│
├── shared/                 # Phase 0: Foundation (Chapters 2-8)
│   ├── models/             # Data models (Ch 2-3)
│   ├── stores/             # Data stores (Ch 5, 8)
│   └── utils/              # Utilities (Ch 4, 7)
│
├── v1_fundamentals/        # Phase 1: Manual implementation (Ch 9-17)
├── v2_langchain/           # Phase 2: Framework-based (Ch 18-25)
├── v3_hybrid/              # Phase 3: Best of both (Ch 26-31)
│
└── tests/                  # Test files
    └── properties/         # Property-based tests (Ch 6)
```

---

## Implementation

### Step 1: Choose Your Virtual Environment Tool

We support three options. Choose based on your preference:

#### Option A: venv (Built-in Python)

```bash
# WHY: venv is built into Python 3.3+, no extra installation needed
# WHAT: Creates an isolated Python environment in the .venv folder
# HOW: Uses Python's venv module to create a copy of the interpreter

# Create virtual environment
python -m venv .venv

# Activate it (Windows CMD)
.venv\Scripts\activate

# Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate it (macOS/Linux)
source .venv/bin/activate

# You should see (.venv) in your terminal prompt
```

#### Option B: UV (Fast, Modern)

```bash
# WHY: UV is 10-100x faster than pip, written in Rust
# WHAT: Modern Python package manager with built-in venv support
# HOW: Install UV first, then use it to create environments

# Install UV (if not already installed)
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
# Then activate as shown in Option A
```

#### Option C: Conda (Data Science Focus)

```bash
# WHY: Conda manages both Python AND non-Python dependencies (CUDA, etc.)
# WHAT: Creates isolated environments with full dependency resolution
# HOW: Uses conda's environment management system

# Create environment with Python 3.11
conda create -n ai-contract python=3.11

# Activate it
conda activate ai-contract
```

---

### Step 2: Install Dependencies

```bash
# WHY: Install all required packages into your virtual environment
# WHAT: Reads requirements.txt and installs each package
# HOW: pip resolves dependencies and downloads from PyPI

# Using pip (works with venv or conda)
pip install -r requirements.txt

# Using UV (faster alternative)
uv pip install -r requirements.txt
```

**Current `requirements.txt`:**

```txt
# Core Python utilities
python-dotenv==1.0.0        # Load environment variables from .env files
pydantic>=2.5.2             # Data validation using type hints
pydantic-settings==2.1.0    # Settings management with env var support

# Will add more dependencies in later chapters:
# - sentence-transformers (Ch 10)
# - numpy (Ch 11)
# - ollama (Ch 9)
# - langchain (Ch 21)
# - llama-index (Ch 26)
# - streamlit (Ch 32)
# - hypothesis (Ch 6)
```

---

### Step 3: Create Your `.env` File

```bash
# WHY: Copy the template to create your actual config file
# WHAT: .env contains your real values, .env.example is the template
# HOW: Copy and edit with your actual values

# Windows CMD
copy .env.example .env

# Windows PowerShell / macOS / Linux
cp .env.example .env
```

**Edit `.env` with your values:**

```bash
# Ollama Configuration
OLLAMA_CLOUD_URL=https://api.ollama.ai
OLLAMA_LOCAL_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# API Keys (add your actual keys!)
OLLAMA_API_KEY=your_actual_api_key_here

# Ollama Connection Settings
OLLAMA_TIMEOUT=30
OLLAMA_MAX_RETRIES=3

# Application Settings
LOG_LEVEL=INFO
CACHE_DIR=.cache
```

---

### Step 4: Understanding `config.py` - The Dataclass Approach (Educational)

Before we look at the actual Pydantic Settings implementation, let's understand the **manual dataclass approach**. This helps you appreciate what Pydantic does "under the hood."

> **Note:** The actual `config.py` in this project uses **Pydantic Settings** (shown later in this chapter). This section shows the dataclass approach for educational purposes.

Here's how you would implement configuration using only dataclasses:

```python
"""
Configuration management for AI Contract Generator.

WHY: Centralized configuration prevents scattered os.getenv() calls
WHAT: Provides type-safe access to all configuration values
HOW: Uses dataclasses + python-dotenv for clean, validated config
"""

# WHY: Standard library imports first (PEP 8 style)
# WHAT: os for environment variables, dataclass for config classes
# HOW: Python's import system loads these modules
import os
from dataclasses import dataclass, field
from typing import Optional

# WHY: Third-party imports after standard library
# WHAT: python-dotenv loads .env file into environment
# HOW: Reads .env file and calls os.environ for each line
from dotenv import load_dotenv

# WHY: Load .env file at module import time so config is ready immediately
# WHAT: Reads .env file and populates os.environ
# HOW: load_dotenv() searches for .env in current directory and parents
# NOTE: This runs ONCE when the module is first imported
load_dotenv()


@dataclass
class OllamaConfig:
    """
    Configuration for Ollama LLM connections.

    WHY: Dataclass automatically generates __init__, __repr__, __eq__
    WHAT: Stores URLs and credentials for Ollama API access
    HOW: Loads from environment variables with sensible defaults

    Example:
        >>> config = OllamaConfig()
        >>> print(config.local_url)
        http://localhost:11434
    """

    # WHY: Type hints enable IDE autocomplete and type checking
    # WHAT: Cloud Ollama API endpoint (fallback option)
    # HOW: Uses field(default_factory=...) to call function at instantiation
    # NOTE: default_factory is needed because we're calling a function
    cloud_url: str = field(
        default_factory=lambda: os.getenv(
            "OLLAMA_CLOUD_URL",
            "https://api.ollama.ai"
        )
    )

    # WHAT: Local Ollama instance (primary option for privacy)
    # WHY: Local-first approach keeps data on your machine
    local_url: str = field(
        default_factory=lambda: os.getenv(
            "OLLAMA_LOCAL_URL",
            "http://localhost:11434"
        )
    )

    # WHAT: Default LLM model to use
    # NOTE: Can be overridden per-request in later chapters
    model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama2")
    )

    # WHAT: API key for cloud Ollama (optional for local)
    # WHY: Optional[str] means it can be None
    # NOTE: Required only when using cloud_url
    api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OLLAMA_API_KEY")
    )

    # WHAT: Request timeout in seconds
    # HOW: Convert string from env var to int
    # WHY: Prevents hanging on slow/dead connections
    timeout: int = field(
        default_factory=lambda: int(os.getenv("OLLAMA_TIMEOUT", "30"))
    )

    # WHAT: Number of retry attempts for failed requests
    # WHY: Improves reliability for transient network issues
    max_retries: int = field(
        default_factory=lambda: int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
    )

    def __post_init__(self):
        """
        Validate configuration after initialization.

        WHY: Dataclass __post_init__ runs after __init__
        WHAT: Checks that required values are present and warns about incomplete fallback chain
        HOW: Raises ValueError if validation fails, warns if fallback chain incomplete

        PITFALL: Without validation, bad config causes cryptic errors later
        """
        import warnings

        # WHY: Validate at least one URL is provided for fallback chain
        # NOTE: Fallback chain is Cloud → Local → ST-Only
        # We need at least one of cloud_url or local_url to attempt LLM calls
        if not (self.cloud_url or self.local_url):
            raise ValueError(
                "At least one of OLLAMA_CLOUD_URL or OLLAMA_LOCAL_URL must be set"
            )

        # WHY: Warn if fallback chain is incomplete (production best practice)
        # WHAT: Full fallback chain (Cloud → Local → ST-Only) provides maximum reliability
        # HOW: Non-blocking warning allows development flexibility while encouraging best practice
        # NOTE: This is especially important for production deployments
        if not self.cloud_url:
            warnings.warn(
                "OLLAMA_CLOUD_URL not set. Fallback chain incomplete: Local → ST-Only. "
                "For production, consider setting both cloud and local URLs for maximum reliability.",
                UserWarning,
                stacklevel=2
            )
        elif not self.local_url:
            warnings.warn(
                "OLLAMA_LOCAL_URL not set. Fallback chain incomplete: Cloud → ST-Only. "
                "For production, consider setting both cloud and local URLs for maximum reliability.",
                UserWarning,
                stacklevel=2
            )

        # WHY: Validate model name is specified
        if not self.model:
            raise ValueError("OLLAMA_MODEL must be set")

        # WHY: Validate timeout is positive
        if self.timeout <= 0:
            raise ValueError("OLLAMA_TIMEOUT must be positive")

        # WHY: Validate retries is non-negative
        if self.max_retries < 0:
            raise ValueError("OLLAMA_MAX_RETRIES must be non-negative")

    def get_headers(self) -> dict[str, str]:
        """
        Generate HTTP headers for Ollama API requests.

        Returns:
            Dictionary of headers including auth if API key present

        WHY: Centralizes header generation logic
        WHAT: Adds Authorization header when api_key is set
        HOW: Returns dict suitable for requests library

        Example:
            >>> config = OllamaConfig()
            >>> headers = config.get_headers()
            >>> print(headers)
            {'Content-Type': 'application/json'}
        """
        headers = {
            "Content-Type": "application/json",
        }

        # WHY: Only add auth header if we have an API key
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers


@dataclass
class AppConfig:
    """
    Application-wide configuration.

    WHY: Single source of truth for all config
    WHAT: Aggregates all configuration sections
    HOW: Composes other config dataclasses

    Example:
        >>> from config import get_config
        >>> cfg = get_config()
        >>> print(cfg.ollama.model)
        llama2
    """

    # WHAT: Ollama LLM configuration
    # HOW: Automatically instantiates OllamaConfig
    ollama: OllamaConfig = field(default_factory=OllamaConfig)

    # WHAT: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
    # WHY: Control how much output we see
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )

    # WHAT: Directory for caching embeddings and models
    # WHY: Avoid re-downloading models every run
    # NOTE: Will be used in Chapter 10 (Sentence Transformers)
    cache_dir: str = field(
        default_factory=lambda: os.getenv("CACHE_DIR", ".cache")
    )

    def __post_init__(self):
        """
        Validate and initialize application configuration.

        WHY: Ensure cache directory exists
        WHAT: Creates cache_dir if missing
        HOW: Uses os.makedirs with exist_ok=True
        """
        # WHY: Create cache directory if it doesn't exist
        # WHAT: Makes the directory and any parent directories
        # HOW: exist_ok=True prevents error if directory exists
        os.makedirs(self.cache_dir, exist_ok=True)

        # WHY: Validate log level is recognized
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_levels:
            raise ValueError(
                f"LOG_LEVEL must be one of {valid_levels}, "
                f"got {self.log_level}"
            )


# WHY: Create singleton instance at module level
# WHAT: Single config object used throughout application
# HOW: Instantiated when module is imported
# NOTE: This is the "module as singleton" pattern
# ALTERNATIVE: Could use a class with @classmethod, but this is simpler
config = AppConfig()


# WHY: Convenience function for getting config
# WHAT: Returns the singleton config instance
# HOW: Simple getter function
def get_config() -> AppConfig:
    """
    Get the application configuration.

    Returns:
        The singleton AppConfig instance

    Example:
        >>> from config import get_config
        >>> cfg = get_config()
        >>> print(cfg.ollama.model)
        llama2
    """
    return config
```

**Key Design Decisions Explained:**

| Decision                     | Why                                                               |
| ---------------------------- | ----------------------------------------------------------------- |
| `field(default_factory=...)` | Allows calling functions (like `os.getenv`) at instantiation time |
| `__post_init__` validation   | Catches config errors early, before they cause cryptic failures   |
| `__post_init__` warnings     | Encourages production best practices without blocking development |
| Module-level singleton       | Simple pattern - config is ready when you import it               |
| Nested dataclasses           | Groups related config (all Ollama settings together)              |
| Type hints everywhere        | IDE autocomplete, type checking, self-documenting code            |

**Fallback Chain Philosophy:**

The configuration uses **warnings instead of errors** for incomplete fallback chains:

```python
# ✅ ALLOWED: Cloud only (warns about missing local)
OLLAMA_CLOUD_URL=https://api.ollama.ai
OLLAMA_API_KEY=your_key
# Warning: "Fallback chain incomplete: Cloud → ST-Only"

# ✅ ALLOWED: Local only (warns about missing cloud)
OLLAMA_LOCAL_URL=http://localhost:11434
# Warning: "Fallback chain incomplete: Local → ST-Only"

# ✅ RECOMMENDED: Both (full fallback chain, no warnings)
OLLAMA_CLOUD_URL=https://api.ollama.ai
OLLAMA_LOCAL_URL=http://localhost:11434
OLLAMA_API_KEY=your_key
# No warnings - full Cloud → Local → ST-Only chain

# ❌ ERROR: Neither (cannot attempt LLM calls)
# (both commented out or empty)
# ValueError: "At least one of OLLAMA_CLOUD_URL or OLLAMA_LOCAL_URL must be set"
```

**Why This Design?**

- **Development Flexibility**: Learners can start with just local Ollama or just cloud
- **Production Guidance**: Warnings encourage setting up full fallback chain for reliability
- **Graceful Degradation**: System always has ST-Only mode as final fallback
- **Non-Blocking**: Warnings don't stop the application from running

---

## From Scratch vs With Framework: A Deep Comparison

Understanding both approaches helps you appreciate what Pydantic Settings does "under the hood" and when to use each approach.

### Manual Approach (Dataclass + os.getenv)

```python
# Manual: Full control, explicit, educational
import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class OllamaConfig:
    # WHY: default_factory needed because os.getenv() is a function call
    # WHAT: Each field manually loads from environment
    # HOW: Lambda defers execution until instantiation
    cloud_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_CLOUD_URL", "https://api.ollama.ai")
    )
    local_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_LOCAL_URL", "http://localhost:11434")
    )
    model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama2")
    )
    api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OLLAMA_API_KEY")
    )
    # WHY: Manual type conversion from string to int
    timeout: int = field(
        default_factory=lambda: int(os.getenv("OLLAMA_TIMEOUT", "30"))
    )
    max_retries: int = field(
        default_factory=lambda: int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
    )

    def __post_init__(self):
        """Manual validation - must write all checks yourself."""
        if self.timeout <= 0:
            raise ValueError("OLLAMA_TIMEOUT must be positive")
        if self.max_retries < 0:
            raise ValueError("OLLAMA_MAX_RETRIES must be non-negative")
        if not self.model:
            raise ValueError("OLLAMA_MODEL must be set")
```

**Pros:**

- ✅ No extra dependencies (dataclasses are built-in)
- ✅ Full understanding of what's happening
- ✅ Easy to debug - no "magic"
- ✅ Good for learning Python fundamentals

**Cons:**

- ❌ More boilerplate (every field needs `field(default_factory=lambda: ...)`)
- ❌ Manual type conversion (`int(os.getenv(...))`)
- ❌ Manual validation logic in `__post_init__`
- ❌ Easy to forget validation for new fields

---

### Framework Approach (Pydantic Settings) - What We Actually Use

```python
# Pydantic: Less code, more features, industry standard
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class OllamaConfig(BaseSettings):
    # WHY: SettingsConfigDict configures automatic env var mapping
    # WHAT: env_prefix="OLLAMA_" means cloud_url → OLLAMA_CLOUD_URL
    # HOW: Pydantic automatically looks up OLLAMA_CLOUD_URL when instantiated
    model_config = SettingsConfigDict(env_prefix="OLLAMA_")

    # WHY: Just declare the field with type and default - Pydantic handles the rest!
    # WHAT: No field(default_factory=...) needed
    # HOW: Pydantic automatically loads from OLLAMA_CLOUD_URL env var
    cloud_url: str = "https://api.ollama.ai"
    local_url: str = "http://localhost:11434"
    model: str = "llama2"
    api_key: Optional[str] = None

    # WHY: Pydantic automatically converts string "30" to int 30
    # WHAT: Type conversion happens based on the type hint
    # HOW: Pydantic's type coercion system
    timeout: int = 30
    max_retries: int = 3

    # WHY: Declarative validation is cleaner than imperative
    # WHAT: @field_validator runs automatically during instantiation
    # HOW: Pydantic calls this before the object is fully created
    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("OLLAMA_TIMEOUT must be positive")
        return v
```

**Pros:**

- ✅ Much less boilerplate
- ✅ Automatic env var mapping with `env_prefix`
- ✅ Automatic type conversion (string → int, string → bool, etc.)
- ✅ Declarative validation with `@field_validator`
- ✅ Industry standard (FastAPI, LangChain, LlamaIndex all use it)
- ✅ Built-in JSON serialization
- ✅ Excellent error messages

**Cons:**

- ❌ Extra dependency (`pydantic-settings`)
- ❌ "Magic" behavior can be confusing at first
- ❌ Need to understand Pydantic's validation system

---

## Rewriting config.py: Dataclass → Pydantic Settings

Let's walk through the transformation step-by-step. This is what the actual `config.py` in this project uses.

### Step 1: Change Imports

```python
# ❌ BEFORE (Dataclass approach)
import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# ✅ AFTER (Pydantic Settings approach)
import os
import warnings
from typing import Optional
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
```

**What Changed:**

- Removed `dataclass` and `field` imports
- Added `BaseSettings` and `SettingsConfigDict` from `pydantic_settings`
- Added `field_validator` from `pydantic` for custom validation

---

### Step 2: Transform OllamaConfig

```python
# ❌ BEFORE (Dataclass)
@dataclass
class OllamaConfig:
    cloud_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_CLOUD_URL", "https://api.ollama.ai")
    )
    timeout: int = field(
        default_factory=lambda: int(os.getenv("OLLAMA_TIMEOUT", "30"))
    )

    def __post_init__(self):
        if self.timeout <= 0:
            raise ValueError("OLLAMA_TIMEOUT must be positive")

# ✅ AFTER (Pydantic Settings)
class OllamaConfig(BaseSettings):
    """
    Configuration for Ollama LLM connections using Pydantic Settings.

    MAGIC EXPLAINED:
        - env_prefix="OLLAMA_" means Pydantic looks for OLLAMA_CLOUD_URL, etc.
        - Default values are used if env var not found
        - Type conversion (str to int) happens automatically
        - Validation runs automatically on instantiation
    """

    # WHY: SettingsConfigDict configures how Pydantic loads settings
    # WHAT: env_prefix adds "OLLAMA_" to all field names when looking for env vars
    # HOW: Pydantic automatically converts cloud_url → OLLAMA_CLOUD_URL
    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        case_sensitive=False,  # OLLAMA_cloud_url and OLLAMA_CLOUD_URL both work
    )

    # WHY: Just declare type and default - no field(default_factory=...) needed!
    # WHAT: Pydantic automatically loads from OLLAMA_CLOUD_URL
    # HOW: BaseSettings overrides __init__ to check env vars first
    cloud_url: str = "https://api.ollama.ai"
    local_url: str = "http://localhost:11434"
    model: str = "llama2"
    api_key: Optional[str] = None

    # WHY: Pydantic automatically converts string "30" from env to int
    # WHAT: No manual int() conversion needed
    # HOW: Pydantic's type coercion based on type hint
    timeout: int = 30
    max_retries: int = 3

    # WHY: @field_validator replaces __post_init__ validation
    # WHAT: Runs automatically during instantiation
    # HOW: Pydantic calls validators before object is fully created
    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("OLLAMA_TIMEOUT must be positive")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Validate max_retries is non-negative."""
        if v < 0:
            raise ValueError("OLLAMA_MAX_RETRIES must be non-negative")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model name is not empty."""
        if not v or not v.strip():
            raise ValueError("OLLAMA_MODEL must be set")
        return v

    def model_post_init(self, __context) -> None:
        """
        Additional validation after model initialization.

        WHY: Pydantic's model_post_init is like dataclass __post_init__
        WHAT: Checks fallback chain completeness
        HOW: Warns if only one URL is configured

        NOTE: This runs AFTER all field validators
        """
        if not (self.cloud_url or self.local_url):
            raise ValueError(
                "At least one of OLLAMA_CLOUD_URL or OLLAMA_LOCAL_URL must be set"
            )
```

**Key Transformations:**

| Dataclass                                    | Pydantic Settings                 |
| -------------------------------------------- | --------------------------------- |
| `@dataclass`                                 | `class X(BaseSettings):`          |
| `field(default_factory=lambda: os.getenv())` | Just `field: type = default`      |
| `int(os.getenv("X", "30"))`                  | `field: int = 30` (auto-converts) |
| `__post_init__` validation                   | `@field_validator` decorators     |
| Manual env var names                         | `env_prefix` auto-generates names |

---

### Step 3: Transform AppConfig

```python
# ❌ BEFORE (Dataclass)
@dataclass
class AppConfig:
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    cache_dir: str = field(
        default_factory=lambda: os.getenv("CACHE_DIR", ".cache")
    )

    def __post_init__(self):
        os.makedirs(self.cache_dir, exist_ok=True)
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")

# ✅ AFTER (Pydantic Settings)
class AppConfig(BaseSettings):
    """
    Application-wide configuration using Pydantic Settings.

    MAGIC EXPLAINED:
        - No env_prefix here, so looks for exact env var names (LOG_LEVEL, CACHE_DIR)
        - Nested OllamaConfig is automatically instantiated
        - All validation happens automatically
    """

    # WHAT: Nested config - Pydantic automatically instantiates OllamaConfig
    # WHY: No field(default_factory=...) needed!
    ollama: OllamaConfig = OllamaConfig()

    # WHAT: Direct env var mapping (no prefix)
    log_level: str = "INFO"
    cache_dir: str = ".cache"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate and normalize log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}, got {v}")
        return v.upper()  # Normalize to uppercase

    def model_post_init(self, __context) -> None:
        """Create cache directory after validation."""
        os.makedirs(self.cache_dir, exist_ok=True)
```

---

### The Complete Pydantic Settings config.py

Here's the full implementation that's actually used in this project:

```python
"""
Configuration management for AI Contract Generator.

This module provides centralized configuration loading from environment
variables with type safety and validation using Pydantic Settings.

WHY: Pydantic Settings provides automatic env var mapping and validation
WHAT: Type-safe configuration with minimal boilerplate
HOW: BaseSettings automatically loads from environment variables
"""

import os
import warnings
from typing import Optional

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file at module import time
load_dotenv()


class OllamaConfig(BaseSettings):
    """
    Configuration for Ollama LLM connections using Pydantic Settings.

    Example:
        >>> config = OllamaConfig()
        >>> print(config.local_url)
        http://localhost:11434
    """

    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        case_sensitive=False,
    )

    cloud_url: str = "https://api.ollama.ai"
    local_url: str = "http://localhost:11434"
    model: str = "llama2"
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("OLLAMA_TIMEOUT must be positive")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        if v < 0:
            raise ValueError("OLLAMA_MAX_RETRIES must be non-negative")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("OLLAMA_MODEL must be set")
        return v

    def model_post_init(self, __context) -> None:
        if not (self.cloud_url or self.local_url):
            raise ValueError(
                "At least one of OLLAMA_CLOUD_URL or OLLAMA_LOCAL_URL must be set"
            )

        if not self.cloud_url:
            warnings.warn(
                "OLLAMA_CLOUD_URL not set. Fallback chain incomplete.",
                UserWarning,
                stacklevel=2
            )
        elif not self.local_url:
            warnings.warn(
                "OLLAMA_LOCAL_URL not set. Fallback chain incomplete.",
                UserWarning,
                stacklevel=2
            )

    def get_headers(self) -> dict[str, str]:
        """Generate HTTP headers for Ollama API requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


class AppConfig(BaseSettings):
    """Application-wide configuration using Pydantic Settings."""

    ollama: OllamaConfig = OllamaConfig()
    log_level: str = "INFO"
    cache_dir: str = ".cache"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}, got {v}")
        return v.upper()

    def model_post_init(self, __context) -> None:
        os.makedirs(self.cache_dir, exist_ok=True)


# Singleton instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the application configuration."""
    return config
```

---

## Understanding Pydantic's "Magic"

### How env_prefix Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PYDANTIC ENV_PREFIX MAGIC                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  model_config = SettingsConfigDict(env_prefix="OLLAMA_")            │
│                                                                      │
│  Field Name        →    Environment Variable                        │
│  ─────────────────────────────────────────────────────────────────  │
│  cloud_url         →    OLLAMA_CLOUD_URL                            │
│  local_url         →    OLLAMA_LOCAL_URL                            │
│  model             →    OLLAMA_MODEL                                │
│  api_key           →    OLLAMA_API_KEY                              │
│  timeout           →    OLLAMA_TIMEOUT                              │
│  max_retries       →    OLLAMA_MAX_RETRIES                          │
│                                                                      │
│  Pydantic automatically:                                            │
│  1. Converts field_name to UPPER_CASE                               │
│  2. Prepends the env_prefix                                         │
│  3. Looks up the env var                                            │
│  4. Converts to the declared type                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### How Type Conversion Works

```python
# In .env file (everything is a string):
OLLAMA_TIMEOUT=30
OLLAMA_MAX_RETRIES=3

# Pydantic sees:
timeout: int = 30  # Type hint says int

# Pydantic automatically:
# 1. Reads "30" from OLLAMA_TIMEOUT (string)
# 2. Sees type hint is `int`
# 3. Converts "30" → 30 (integer)
# 4. Assigns to self.timeout

# This also works for:
# - str → bool ("true" → True, "false" → False)
# - str → float ("3.14" → 3.14)
# - str → list (JSON parsing)
# - str → dict (JSON parsing)
```

### How Validation Order Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PYDANTIC VALIDATION ORDER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Load values from environment variables                          │
│     ↓                                                               │
│  2. Apply type conversion (str → int, etc.)                         │
│     ↓                                                               │
│  3. Run @field_validator for each field                             │
│     ↓                                                               │
│  4. Run model_post_init() for cross-field validation                │
│     ↓                                                               │
│  5. Object is ready to use                                          │
│                                                                      │
│  If ANY step fails → ValidationError is raised                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Side-by-Side Comparison: Lines of Code

| Component               | Dataclass Approach | Pydantic Settings |
| ----------------------- | ------------------ | ----------------- |
| OllamaConfig fields     | 24 lines           | 8 lines           |
| OllamaConfig validation | 15 lines           | 18 lines          |
| AppConfig fields        | 12 lines           | 4 lines           |
| AppConfig validation    | 10 lines           | 8 lines           |
| **Total**               | **61 lines**       | **38 lines**      |

**37% less code** with Pydantic Settings, plus:

- Automatic type conversion
- Better error messages
- JSON serialization built-in
- Industry standard patterns

---

## Interactive Checkpoints

Complete these checkpoints to verify your setup:

### ✅ Checkpoint 1: Virtual Environment Active

```bash
# Run this command - you should see your venv path
python -c "import sys; print(sys.prefix)"

# Expected output (something like):
# C:\Users\YourName\ai-contract-generator\.venv
# or
# /home/yourname/ai-contract-generator/.venv
```

- [ ] I see my virtual environment path (not the system Python)

### ✅ Checkpoint 2: Dependencies Installed

```bash
# Check that python-dotenv is installed
python -c "import dotenv; print(f'python-dotenv version: {dotenv.__version__}')"

# Expected output:
# python-dotenv version: 1.0.0
```

- [ ] python-dotenv is installed and importable

### ✅ Checkpoint 3: Configuration Loads

```bash
# Run the config test
python config.py

# Expected output:
# === Configuration Test ===
# Ollama Cloud URL: https://api.ollama.ai
# Ollama Local URL: http://localhost:11434
# Ollama Model: llama2
# API Key Set: Yes (or No)
# Timeout: 30s
# Max Retries: 3
# Log Level: INFO
# Cache Dir: .cache
#
# === Headers ===
# {'Content-Type': 'application/json', ...}
#
# Configuration loaded successfully! ✓
```

- [ ] Configuration loads without errors
- [ ] Values match my `.env` file

### ✅ Checkpoint 4: Cache Directory Created

```bash
# Check that .cache directory exists
python -c "import os; print('Cache exists:', os.path.isdir('.cache'))"

# Expected output:
# Cache exists: True
```

- [ ] `.cache` directory was created automatically

---

## Debugging Scenario

### The Bug

A learner reports this error when running `python config.py`:

```python
Traceback (most recent call last):
  File "config.py", line 89, in <module>
    config = AppConfig()
  File "<string>", line 6, in __init__
  File "config.py", line 85, in __post_init__
    raise ValueError(
ValueError: LOG_LEVEL must be one of {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}, got debug
```

### Your Task

1. What's causing this error?
2. How would you fix it?

<details>
<summary>💡 Click to reveal the answer</summary>

**Root Cause:**
The `.env` file has `LOG_LEVEL=debug` (lowercase), but the validation checks against uppercase values.

**The Fix:**
The validation already handles this! Look at line 85:

```python
if self.log_level.upper() not in valid_levels:
```

The `.upper()` call should handle lowercase input. But wait - the error message shows `got debug` (lowercase), which means the comparison is working but the error message is showing the original value.

**Actually, the real issue is:**
The learner's `.env` file might have extra whitespace or the value isn't being read correctly.

**Debugging Steps:**

```python
# Add this debug line temporarily
print(f"LOG_LEVEL raw value: '{os.getenv('LOG_LEVEL')}'")
print(f"LOG_LEVEL repr: {repr(os.getenv('LOG_LEVEL'))}")
```

**Common Causes:**

1. Extra whitespace: `LOG_LEVEL= debug` (space after =)
2. Quotes in .env: `LOG_LEVEL="debug"` (some parsers include quotes)
3. .env file not found (using default, but default is "INFO" so this isn't it)

**The Actual Fix:**
Check the `.env` file for:

- Extra spaces around the `=` sign
- Quotes around the value
- Trailing whitespace

Correct format:

```bash
LOG_LEVEL=INFO
```

</details>

---

## Quick Check Questions

Test your understanding with these questions:

### Question 1

Why do we use `field(default_factory=lambda: os.getenv(...))` instead of just `os.getenv(...)` as the default value?

<details>
<summary>Answer</summary>

**Answer:** Default values in dataclasses are evaluated once at class definition time, not at instantiation time. Using `default_factory` ensures `os.getenv()` is called each time a new instance is created.

```python
# ❌ BAD: os.getenv() called once when class is defined
cloud_url: str = os.getenv("OLLAMA_CLOUD_URL", "default")

# ✅ GOOD: os.getenv() called each time OllamaConfig() is created
cloud_url: str = field(default_factory=lambda: os.getenv("OLLAMA_CLOUD_URL", "default"))
```

This matters if environment variables change during runtime (rare but possible).

</details>

### Question 2

What's the purpose of `__post_init__` in a dataclass?

<details>
<summary>Answer</summary>

**Answer:** `__post_init__` is called automatically after the auto-generated `__init__` method completes. It's used for:

1. **Validation** - Check that values are valid
2. **Derived values** - Compute values based on other fields
3. **Side effects** - Create directories, open connections, etc.

```python
@dataclass
class Config:
    timeout: int = 30

    def __post_init__(self):
        # Validation
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
```

</details>

### Question 3

Why do we create a module-level `config = AppConfig()` singleton?

<details>
<summary>Answer</summary>

**Answer:** The singleton pattern ensures:

1. **Single source of truth** - All code uses the same config instance
2. **Lazy initialization** - Config is loaded once when first imported
3. **Easy access** - Just `from config import config` or `get_config()`

```python
# Any file can access the same config
from config import config
print(config.ollama.model)  # Same instance everywhere
```

**Alternative approaches:**

- Dependency injection (more flexible, more complex)
- Global function that creates new instance each time (wasteful)
- Class with `@classmethod` (more boilerplate)
</details>

### Question 4

What happens if `.env` file doesn't exist?

<details>
<summary>Answer</summary>

**Answer:** `load_dotenv()` silently does nothing if `.env` doesn't exist. The config will use default values specified in the `os.getenv()` calls.

```python
# If OLLAMA_MODEL not in environment, uses "llama2"
model: str = field(
    default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama2")
)
```

This is intentional - it allows the app to work with just environment variables (useful in Docker/production) without requiring a `.env` file.

</details>

### Question 5

Why is `.env` in `.gitignore` but `.env.example` is not?

<details>
<summary>Answer</summary>

**Answer:**

- **`.env`** contains real secrets (API keys, passwords) - NEVER commit to git
- **`.env.example`** is a template showing what variables are needed - safe to commit

```bash
# .gitignore
.env           # Real secrets - excluded
# .env.example  # Template - NOT excluded (not in .gitignore)
```

This pattern lets new developers know what environment variables they need to set up, without exposing actual secrets.

</details>

### Question 6

What does `env_prefix="OLLAMA_"` do in Pydantic Settings?

<details>
<summary>Answer</summary>

**Answer:** The `env_prefix` in `SettingsConfigDict` tells Pydantic to automatically prepend "OLLAMA_" to field names when looking for environment variables.

```python
class OllamaConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OLLAMA_")
    
    cloud_url: str = "default"  # Looks for OLLAMA_CLOUD_URL
    timeout: int = 30           # Looks for OLLAMA_TIMEOUT
```

**The transformation:**
1. Take field name: `cloud_url`
2. Convert to UPPER_CASE: `CLOUD_URL`
3. Prepend prefix: `OLLAMA_CLOUD_URL`
4. Look up in environment

This eliminates the need for manual `os.getenv("OLLAMA_CLOUD_URL")` calls!

</details>

### Question 7

What's the difference between `@field_validator` and `model_post_init` in Pydantic?

<details>
<summary>Answer</summary>

**Answer:**

**`@field_validator`** - Validates a single field:
- Runs during object creation
- Has access only to the field being validated
- Good for: type checks, range checks, format validation

```python
@field_validator("timeout")
@classmethod
def validate_timeout(cls, v: int) -> int:
    if v <= 0:
        raise ValueError("timeout must be positive")
    return v
```

**`model_post_init`** - Runs after all fields are set:
- Has access to `self` (all fields)
- Good for: cross-field validation, side effects (creating directories)

```python
def model_post_init(self, __context) -> None:
    # Can access multiple fields
    if not (self.cloud_url or self.local_url):
        raise ValueError("Need at least one URL")
    # Can perform side effects
    os.makedirs(self.cache_dir, exist_ok=True)
```

**Execution order:** `@field_validator` runs first, then `model_post_init`.

</details>

---

## Mini-Project

### Challenge: Add a New Configuration Section (Using Pydantic Settings)

Add a `SentenceTransformerConfig` class to `config.py` that will be used in Chapter 10.

**Requirements:**

1. Create a new Pydantic Settings class `SentenceTransformerConfig` with these fields:

   - `model_name: str` - default `"all-MiniLM-L6-v2"` (from env var `ST_MODEL_NAME`)
   - `cache_folder: str` - default `".cache/models"` (from env var `ST_CACHE_FOLDER`)
   - `device: str` - default `"cpu"` (from env var `ST_DEVICE`, can be "cpu" or "cuda")

2. Add validation using `@field_validator`:

   - `device` must be either "cpu" or "cuda"
   - `model_name` must not be empty

3. Add `sentence_transformer: SentenceTransformerConfig` field to `AppConfig`

4. Update `.env.example` with the new variables

**Starter Code (Pydantic Settings):**

```python
class SentenceTransformerConfig(BaseSettings):
    """
    Configuration for Sentence Transformers embedding model.

    WHY: Centralize embedding model settings for easy configuration
    WHAT: Stores model name, cache location, and compute device
    HOW: Uses Pydantic Settings with ST_ prefix for env vars
    """

    model_config = SettingsConfigDict(env_prefix="ST_")

    # TODO: Add fields here
    model_name: str = "all-MiniLM-L6-v2"
    # ... add more fields

    # TODO: Add validators
    @field_validator("device")
    @classmethod
    def validate_device(cls, v: str) -> str:
        # Your validation logic here
        pass
```

**Acceptance Criteria:**

- [ ] `SentenceTransformerConfig` class inherits from `BaseSettings`
- [ ] Uses `SettingsConfigDict(env_prefix="ST_")` for automatic env var mapping
- [ ] Each field has type hint and sensible default
- [ ] `@field_validator("device")` validates "cpu" or "cuda"
- [ ] `@field_validator("model_name")` validates not empty
- [ ] `AppConfig` includes `sentence_transformer` field
- [ ] `.env.example` updated with new variables
- [ ] Running `python config.py` still works

**Verification Command:**

```bash
# After implementing, run:
python -c "from config import get_config; cfg = get_config(); print(f'ST Model: {cfg.sentence_transformer.model_name}')"

# Expected output:
# ST Model: all-MiniLM-L6-v2
```

**Solution Hint - Field Validator Pattern:**

```python
@field_validator("device")
@classmethod
def validate_device(cls, v: str) -> str:
    valid_devices = {"cpu", "cuda"}
    if v.lower() not in valid_devices:
        raise ValueError(f"device must be one of {valid_devices}, got {v}")
    return v.lower()  # Normalize to lowercase
```

**Suggested Extensions:**

1. Add a `max_seq_length: int` field (default 256)
2. Add a method `get_model_path()` that returns the full path to the cached model
3. Add `model_post_init` to create `cache_folder` if it doesn't exist

---

## Project Integration Notes

### What We Built

In this chapter, we established the foundation for the entire AI Contract Generator project:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CHAPTER 1 DELIVERABLES                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ✅ Virtual environment (isolated Python)                           │
│  ✅ Dependencies installed (python-dotenv, pydantic)                │
│  ✅ .env configuration (secrets management)                         │
│  ✅ config.py (type-safe configuration)                             │
│                                                                      │
│  These will be used by EVERY subsequent chapter!                    │
└─────────────────────────────────────────────────────────────────────┘
```

### How It Connects to Other Chapters

| Chapter                       | Uses From Chapter 1                        |
| ----------------------------- | ------------------------------------------ |
| Ch 2-8 (Phase 0)              | `config.py` for settings                   |
| Ch 9 (Ollama Client)          | `OllamaConfig` for URLs, timeouts, API key |
| Ch 10 (Sentence Transformers) | `cache_dir` for model caching              |
| Ch 32 (Streamlit UI)          | `AppConfig` for all settings               |

### What's Next

**Chapter 2: Enums & Type Hints** will build on this foundation by:

- Creating `TemplateType` enum (engineering, consulting, military, governmental)
- Creating `SeverityLevel` enum (high, medium, low)
- Learning why enums are better than string constants

These enums will be used throughout the project for type-safe template and severity handling.

---

## Summary

In this chapter, you learned:

1. **Virtual Environments** - Isolate project dependencies
2. **Environment Variables** - Keep secrets out of code
3. **python-dotenv** - Load `.env` files automatically
4. **Dataclasses** - Type-safe configuration with manual validation (educational approach)
5. **Pydantic Settings** - Industry-standard configuration with automatic env var mapping
6. **Singleton Pattern** - Single config instance for the whole app

**Key Takeaways:**

- Always use virtual environments for Python projects
- Never commit secrets to git - use `.env` files
- **Pydantic Settings** is the industry standard for Python configuration:
  - Automatic env var mapping with `env_prefix`
  - Automatic type conversion (string → int, etc.)
  - Declarative validation with `@field_validator`
  - Used by FastAPI, LangChain, and modern Python projects
- Validate configuration early to catch errors before they cause problems

**Dataclass vs Pydantic Settings Decision Guide:**

| Use Dataclass When...          | Use Pydantic Settings When...            |
| ------------------------------ | ---------------------------------------- |
| Learning Python fundamentals   | Building production applications         |
| Minimizing dependencies        | Need automatic env var loading           |
| Full control over behavior     | Want less boilerplate                    |
| Simple config without env vars | Working with FastAPI/LangChain ecosystem |

**Next Chapter:** [Chapter 2: Enums & Type Hints](./chapter-02-enums-type-hints.md)
