"""
Configuration management for AI Contract Generator.

This module provides centralized configuration loading from environment
variables with type safety and validation using Pydantic Settings.

WHY: Pydantic Settings provides automatic env var mapping and validation
WHAT: Type-safe configuration with minimal boilerplate
HOW: BaseSettings automatically loads from environment variables
"""

# WHY: Standard library imports first (PEP 8 style)
import os
import warnings
from typing import Optional

# WHY: Third-party imports after standard library
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# WHY: Load .env file at module import time so config is ready immediately
# WHAT: Reads .env file and populates os.environ
# HOW: load_dotenv() searches for .env in current directory and parents
load_dotenv()


class OllamaConfig(BaseSettings):
    """
    Configuration for Ollama LLM connections using Pydantic Settings.

    WHY: BaseSettings automatically loads from environment variables
    WHAT: Stores URLs and credentials for Ollama API access
    HOW: Pydantic maps OLLAMA_* env vars to fields automatically

    Example:
        >>> config = OllamaConfig()
        >>> print(config.local_url)
        http://localhost:11434
    
    MAGIC EXPLAINED:
        - env_prefix="OLLAMA_" means Pydantic looks for OLLAMA_CLOUD_URL, OLLAMA_LOCAL_URL, etc.
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
    
    # WHY: Type hints enable automatic validation and IDE autocomplete
    # WHAT: Cloud Ollama API endpoint (fallback option)
    # HOW: Pydantic looks for OLLAMA_CLOUD_URL env var, uses default if not found
    # NOTE: No field(default_factory=...) needed - Pydantic handles it!
    cloud_url: str = "https://api.ollama.ai"
    
    # WHAT: Local Ollama instance (primary option for privacy)
    # WHY: Local-first approach keeps data on your machine
    local_url: str = "http://localhost:11434"
    
    # WHAT: Default LLM model to use
    # NOTE: Can be overridden per-request in later chapters
    model: str = "llama2"
    
    # WHAT: API key for cloud Ollama (optional for local)
    # WHY: Optional[str] means it can be None
    # NOTE: Required only when using cloud_url
    api_key: Optional[str] = None
    
    # WHAT: Request timeout in seconds
    # HOW: Pydantic automatically converts string "30" from env to int
    # WHY: Prevents hanging on slow/dead connections
    timeout: int = 30
    
    # WHAT: Number of retry attempts for failed requests
    # WHY: Improves reliability for transient network issues
    max_retries: int = 3


    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """
        Validate timeout is positive.
        
        WHY: Pydantic validators run automatically during instantiation
        WHAT: Checks timeout > 0
        HOW: Raises ValueError if invalid
        
        NOTE: @field_validator is Pydantic's way of adding custom validation
        """
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
        # WHY: Validate at least one URL is provided for fallback chain
        # NOTE: Fallback chain is Cloud → Local → ST-Only
        if not (self.cloud_url or self.local_url):
            raise ValueError(
                "At least one of OLLAMA_CLOUD_URL or OLLAMA_LOCAL_URL must be set"
            )
        
        # WHY: Warn if fallback chain is incomplete (production best practice)
        # WHAT: Full fallback chain provides maximum reliability
        # HOW: Non-blocking warning allows development flexibility
        if not self.cloud_url:
            warnings.warn(
                "OLLAMA_CLOUD_URL not set. Fallback chain incomplete: Local → ST-Only. "
                "For production, consider setting both cloud and local URLs.",
                UserWarning,
                stacklevel=2
            )
        elif not self.local_url:
            warnings.warn(
                "OLLAMA_LOCAL_URL not set. Fallback chain incomplete: Cloud → ST-Only. "
                "For production, consider setting both cloud and local URLs.",
                UserWarning,
                stacklevel=2
            )


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
        headers = {"Content-Type": "application/json"}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

class AppConfig(BaseSettings):
    """
    Application-wide configuration using Pydantic Settings.

    WHY: Single source of truth for all config
    WHAT: Aggregates all configuration sections
    HOW: Composes other Pydantic Settings classes

    Example:
        >>> from config import get_config
        >>> cfg = get_config()
        >>> print(cfg.ollama.model)
        llama2
    
    MAGIC EXPLAINED:
        - No env_prefix here, so looks for exact env var names (LOG_LEVEL, CACHE_DIR)
        - Nested OllamaConfig is automatically instantiated
        - All validation happens automatically
    """
    
    # WHAT: Ollama LLM configuration
    # HOW: Pydantic automatically instantiates OllamaConfig
    # NOTE: No field(default_factory=...) needed!
    ollama: OllamaConfig = OllamaConfig()
    
    # WHAT: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
    # WHY: Control how much output we see
    log_level: str = "INFO"
    
    # WHAT: Directory for caching embeddings and models
    # WHY: Avoid re-downloading models every run
    # NOTE: Will be used in Chapter 10 (Sentence Transformers)
    cache_dir: str = ".cache"
    

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """
        Validate log level is recognized.
        
        WHY: Catch invalid log levels early
        WHAT: Checks against valid Python logging levels
        HOW: Raises ValueError if invalid
        """
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(
                f"LOG_LEVEL must be one of {valid_levels}, got {v}"
            )
        return v.upper()  # Normalize to uppercase
    
    def model_post_init(self, __context) -> None:
        """
        Initialize application configuration after validation.
        
        WHY: Ensure cache directory exists
        WHAT: Creates cache_dir if missing
        HOW: Uses os.makedirs with exist_ok=True
        """
        os.makedirs(self.cache_dir, exist_ok=True)


config = AppConfig()


def get_config() -> AppConfig:
    """
    Retrieve the application configuration.

    Returns:
        AppConfig instance with all nested configurations

    WHY: Provides a centralized way to access the application config
    WHAT: Returns the singleton AppConfig instance
    HOW: Uses the global config variable

    Example:
        >>> from config import get_config
        >>> cfg = get_config()
        >>> print(cfg.ollama.model)
        llama2
    """
    return config


# WHY: When run directly, show configuration for debugging
# WHAT: Displays all config values (hiding sensitive data)
# HOW: Only runs when script is executed directly (not imported)
if __name__ == "__main__":
    print("=" * 60)
    print("Configuration Loaded Successfully!")
    print("=" * 60)
    print(f"\n📡 Ollama Configuration:")
    print(f"  Cloud URL: {config.ollama.cloud_url}")
    print(f"  Local URL: {config.ollama.local_url}")
    print(f"  Model: {config.ollama.model}")
    print(f"  API Key: {'✓ Set' if config.ollama.api_key else '✗ Not Set'}")
    print(f"  Timeout: {config.ollama.timeout}s")
    print(f"  Max Retries: {config.ollama.max_retries}")
    
    print(f"\n⚙️  Application Configuration:")
    print(f"  Log Level: {config.log_level}")
    print(f"  Cache Dir: {config.cache_dir}")
    
    print(f"\n🔑 Headers (for API requests):")
    headers = config.ollama.get_headers()
    for key, value in headers.items():
        if key == "Authorization":
            print(f"  {key}: Bearer ***hidden***")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ All configuration validated and ready to use!")
    print("=" * 60)
