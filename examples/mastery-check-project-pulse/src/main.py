"""
PROJECT PULSE - Mastery Verification Tool
-----------------------------------------
Demonstrates skills from Chapters 1-12.

Scenario:
    Reads raw status logs, uses AI to extract structured data,
    and compiles a Weekly Executive Report.
"""

import asyncio
import os
import time
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Literal
from contextlib import contextmanager
from datetime import datetime

from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# --- 1. CONFIGURATION & TYPES (Ch 1-2, 12B) ---

load_dotenv()

# Custom Exception Hierarchy (Ch 6B)
class ProjectPulseError(Exception):
    """Base exception for the tool."""
    pass

class DataIngestionError(ProjectPulseError):
    """Failed to read input data."""
    pass

class ProcessingError(ProjectPulseError):
    """Failed to process data with LLM."""
    pass

# --- 2. DATA MODELS (Ch 3-5) ---

class LogEntry(BaseModel):
    """Represents a single extracted update."""
    author: str = Field(..., description="Name of the person")
    role: Literal["Frontend", "Backend", "DevOps", "Product", "Team"]
    day: str
    blockers: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    wins: List[str] = Field(default_factory=list)

class ExecutiveReport(BaseModel):
    """Final aggregated report."""
    generated_at: datetime = Field(default_factory=datetime.now)
    total_updates_processed: int
    high_priority_risks: List[str]
    key_achievements: List[str]
    team_sentiment_score: float = Field(..., ge=0, le=10, description="1-10 Score")
    summary_markdown: str

# --- 3. INFRASTRUCTURE & OOP (Ch 6C, 8) ---

class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(self, system: str, user: str) -> str:
        pass

class OpenAIClient(BaseLLMClient):
    """Production client using real OpenAI API."""
    def __init__(self, api_key: str):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(self, system: str, user: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise ProcessingError(f"OpenAI API failed: {e}")

class MockLLMClient(BaseLLMClient):
    """Simulation client for testing without tokens."""
    async def generate(self, system: str, user: str) -> str:
        # Simulate network latency (Async!)
        await asyncio.sleep(0.5) 
        
        # Deterministic mock response based on input
        if "SARAH" in user.upper():
            return '''
            {
                "author": "Sarah",
                "role": "Frontend",
                "day": "Monday",
                "blockers": ["Missing Auth API"],
                "risks": ["UI freeze deadline"],
                "wins": ["Login screen component done"]
            }
            '''
        elif "MIKE" in user.upper():
            return '''
            {
                "author": "Mike",
                "role": "Backend",
                "day": "Tuesday",
                "blockers": [],
                "risks": ["Slow search query"],
                "wins": ["DB Migration success"]
            }
            '''
        else:
            # Fallback for "All Team"
            return '''
            {
                "author": "Team",
                "role": "Team",
                "day": "Friday",
                "blockers": [],
                "risks": ["Search optimization needed"],
                "wins": ["End-to-end prototype working"]
            }
            '''

# --- 4. UTILITIES (Ch 6A) ---

@contextmanager
def operation_timer(name: str):
    """Timing context manager."""
    start = time.perf_counter()
    print(f"[TIMER] Starting {name}...")
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"[TIMER] {name} completed in {elapsed:.2f}s")

# --- 5. BUSINESS LOGIC (Ch 12A - Async) ---

async def parse_log_chunk(client: BaseLLMClient, text_chunk: str) -> LogEntry:
    # Uses LLM to parse unstructured text into a Pydantic model.
    # Note: In a real app, we would use Structured Outputs.
    system_prompt = "You are a JSON extractor. Extract status data."
    
    json_str = await client.generate(system_prompt, text_chunk)
    
    try:
        return LogEntry.model_validate_json(json_str)
    except ValidationError as e:
        print(f"[WARN] Validation warning: {e}")
        return LogEntry(author="Unknown", role="Team", day="Unknown")

async def analyze_project_health(log_file: str, use_mock: bool = True) -> ExecutiveReport:
    # Main Async Pipeline
    
    # 1. Setup Client
    if use_mock or not os.getenv("OPENAI_API_KEY"):
        print("[INFO] Using MOCK LLM Client")
        client = MockLLMClient()
    else:
        print("[INFO] Using REAL OpenAI Client")
        client = OpenAIClient(os.getenv("OPENAI_API_KEY"))

    # 2. Read Data
    if not os.path.exists(log_file):
        raise DataIngestionError(f"File not found: {log_file}")
    
    with open(log_file, 'r') as f:
        content = f.read()

    # 3. Split content
    chunks = [c.strip() for c in content.split('\n\n') if c.strip()]
    print(f"[INFO] Found {len(chunks)} log entries to process.")

    # 4. Concurrent Processing
    tasks = [parse_log_chunk(client, chunk) for chunk in chunks]
    results: List[LogEntry] = await asyncio.gather(*tasks)

    # 5. Aggregate
    all_risks = [r for res in results for r in res.risks]
    all_wins = [w for res in results for w in res.wins]
    
    summary_md = f"# Weekly Report\n\n"
    summary_md += f"**Processed:** {len(results)} updates.\n"
    summary_md += "## Risks\n" + "\n".join(f"- {r}" for r in all_risks)
    
    return ExecutiveReport(
        total_updates_processed=len(results),
        high_priority_risks=all_risks,
        key_achievements=all_wins,
        team_sentiment_score=8.5,
        summary_markdown=summary_md
    )

# --- 6. CLI ENTRY POINT ---

async def main():
    data_path = "examples/mastery-check-project-pulse/data/week_24_logs.txt"
    
    print("ProjectPulse: Initializing...")
    
    try:
        with operation_timer("Weekly Analysis"):
            report = await analyze_project_health(data_path, use_mock=True)
            
        print("\n" + "="*40)
        print("EXECUTIVE SUMMARY GENERATED")
        print("="*40)
        print(report.summary_markdown)
        print("\nJSON Dump (Pydantic):")
        print(report.model_dump_json(indent=2))
        
    except ProjectPulseError as e:
        print(f"Fatal Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())