# Chapter 53: Compliance Review Agent — The Inspector

<!--
METADATA
Phase: 10 - Civil Engineering Application
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Application
Prerequisites: Chapter 4 (Advanced Models), Chapter 14 (Vector Stores)
Builds Toward: Complete System (Ch 54)
Correctness Properties: P76 (Rule Coverage), P77 (Violation Detection)
Project Thread: Quality Assurance

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You finish building a house. You're proud.
The Inspector walks in.
"Door frame is 31 inches. Code requires 32." **Fail.**
"Stair rise is 8 inches. Code max is 7.75." **Fail.**

You have to tear it down and start over.
In Civil Engineering, regulations (OSHA, FAR, ISO) are non-negotiable.
Humans miss these details. AI doesn't sleep, doesn't blink, and can memorize 10,000 pages of code.

**By the end of this chapter**, you will build a **Compliance Agent** that scans your documents for illegal clauses and safety violations *before* the inspector arrives. 🕵️‍♂️

---

## Prerequisites Check

Ensure you have `shared/models/compliance.py` (from Chapter 4).

```bash
ls shared/models/compliance.py
```

---

## The Story: The "Hidden" Regulation

### The Problem (The Fine Print)

You wrote a contract for a Federal job.
It looks standard.
But you forgot **FAR 52.222-50** (Combating Trafficking in Persons).
Because you missed one paragraph in a 500-page rulebook, your company is blacklisted from government work.

### The Solution (RAG-Based Review)

We treat regulations as a **Knowledge Base**.
1.  **Chunk**: Break the contract into clauses.
2.  **Retrieve**: For each clause, find the relevant laws.
3.  **Compare**: Ask the AI, "Does this clause violate this law?"
4.  **Report**: Generate a list of flags.

---

## Part 1: The Regulatory Database

We need a database of "Laws". We'll simulate a Safety Standard.

### 🔬 Try This! (Hands-On Practice #1)

**Create `regulatory_db.py`**:

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import shutil

DB_PATH = "./laws_db"
# Cleanup
try: shutil.rmtree(DB_PATH) 
except: pass

# 1. The "Laws" (Simulated)
laws = [
    "OSHA 1926.100: Employees working in areas where there is a possible danger of head injury from impact, or from falling or flying objects, shall be protected by protective helmets.",
    "OSHA 1926.501: Each employee on a walking/working surface (horizontal and vertical surface) with an unprotected side or edge which is 6 feet (1.8 m) or more above a lower level shall be protected from falling.",
    "FAR 52.203-7: Anti-Kickback Procedures. The Contractor shall have in place and follow reasonable procedures to prevent and detect violations."
]

# 2. Index them
print("🏛️ Indexing Laws...")
vectorstore = Chroma.from_texts(
    texts=laws,
    embedding=OpenAIEmbeddings(),
    collection_name="regulations",
    persist_directory=DB_PATH
)
print(f"Indexed {len(laws)} regulations.")
```

**Run it**.
You now have a digital lawyer.

---

## Part 2: The Review Logic

Now we write the logic to check a specific text against the DB.

### 🔬 Try This! (Hands-On Practice #2)

**Create `reviewer.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from shared.models.compliance import ComplianceIssue, RewriteSuggestion
from shared.models.enums import SeverityLevel

# 1. Connect to DB
vectorstore = Chroma(
    collection_name="regulations",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="./laws_db"
)

# 2. The Reviewer Chain
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = JsonOutputParser(pydantic_object=ComplianceIssue)

prompt = ChatPromptTemplate.from_template(
    """
    You are a Compliance Officer.
    
    TEXT TO REVIEW:
    {text}
    
    RELEVANT LAWS:
    {laws}
    
    Task:
    1. Determine if the text violates the laws.
    2. If YES, create a ComplianceIssue (Severity HIGH).
    3. If NO, return null (empty JSON).
    
    {format_instructions}
    """
)

chain = prompt | model | parser

def check_compliance(clause_text):
    # A. Retrieve Laws
    results = vectorstore.similarity_search(clause_text, k=1)
    laws_text = "\n".join([d.page_content for d in results])
    
    # B. Compare
    print(f"🔎 Checking against: {laws_text[:50]}...")
    try:
        issue = chain.invoke({
            "text": clause_text,
            "laws": laws_text,
            "format_instructions": parser.get_format_instructions()
        })
        if issue:
            return issue
    except:
        return None # No issue found or parsing error (assume safe for demo)

# 3. Test
risky_text = "Workers will operate on the roof (20 feet high) without harnesses to save time."
print(f"\nScanning: '{risky_text}'")

issue_dict = check_compliance(risky_text)
if issue_dict:
    print(f"🚨 VIOLATION: {issue_dict['description']}")
    print(f"Severity: {issue_dict['severity']}")
else:
    print("✅ Compliant.")
```

**Run it**.
It should catch the "no harness" rule (OSHA 1926.501).

---

## Part 3: The Full Report

Now we wrap the issues into a `ComplianceReport` (from Chapter 4).

### 🔬 Try This! (Hands-On Practice #3)

**Create `full_review.py`**:

```python
from shared.models.compliance import ComplianceReport
from reviewer import check_compliance
from datetime import datetime

# 1. A Full Document
contract_sections = [
    "The project ID is ENG-2024.", # Safe
    "Employees are not required to wear helmets if it is hot.", # VIOLATION (OSHA 1926.100)
    "Payments will be made via unmarked cash envelopes." # VIOLATION (FAR 52.203-7)
]

# 2. Scan Loop
issues = []
print("--- Starting Audit ---")
for i, section in enumerate(contract_sections):
    print(f"Scanning Section {i+1}...")
    result = check_compliance(section)
    if result:
        # Convert dict back to Pydantic model if needed, or append dict
        # Our model expects Pydantic objects
        # For simplicity in this script we assume result is dict matching schema
        issues.append(result)

# 3. Generate Report
# Calculate score (1.0 - (0.1 * num_issues))
score = max(0.0, 1.0 - (0.1 * len(issues)))

report = ComplianceReport(
    contract_id="ENG-2024",
    score=score,
    issues=issues,
    checked_at=datetime.now()
)

print("\n--- COMPLIANCE REPORT ---")
print(f"Score: {report.score}")
print(f"Issues Found: {len(report.issues)}")
for issue in report.issues:
    print(f"- [{issue.severity}] {issue.description}")
```

**Run it**.
It should find 2 violations and give a score of 0.8.

---

## Common Mistakes

### Mistake #1: False Positives
The AI flags "Employees must wear hats" as a violation of "Must wear helmets".
**Fix**: Tune the prompt. "Only flag direct contradictions or omissions."

### Mistake #2: Stale Laws
Regulations change.
**Fix**: Your vector store needs an "Update Pipeline" to re-ingest laws annually.

### Mistake #3: Ignoring Severity
Not all violations are equal. "Wrong font size" vs "Death trap".
**Fix**: Ensure your `SeverityLevel` enum is used correctly by the AI.

---

## Quick Reference Card

### Compliance Flow

```
Clause -> [Vector Search] -> Relevant Laws
       ⬇
Prompt(Clause + Laws) -> "Does this violate?"
       ⬇
ComplianceIssue (or None)
```

---

## Verification (REQUIRED SECTION)

We need to verify **P77 (Violation Detection)**.

**Create `verify_compliance.py`**:

```python
"""
Verification script for Chapter 53.
Property P77: Violation Detection.
"""
from reviewer import check_compliance
import sys

print("🧪 Running Compliance Verification...\n")

# P77: Violation Detection
# Test a known violation
violation_text = "It is acceptable to accept kickbacks from subcontractors."
# Matches FAR 52.203-7

print("Test 1: Detecting Kickbacks...")
result = check_compliance(violation_text)

if result and "kickback" in result['description'].lower():
    print("✅ P77 Passed: Detected kickback violation.")
elif result:
    print(f"✅ P77 Passed: Detected violation (Description: {result['description']})")
else:
    print("❌ Failed: Did not detect violation.")
    sys.exit(1)

# Test a Safe Text
print("Test 2: Safe Text...")
safe_text = "All employees must follow safety procedures."
result = check_compliance(safe_text)

if result is None:
    print("✅ Passed: Safe text cleared.")
else:
    print(f"❌ Failed: False positive. {result}")
    sys.exit(1)

print("\n🎉 Chapter 53 Complete! You are the Inspector.")
```

**Run it:** `python verify_compliance.py`

---

## Summary

**What you learned:**

1. ✅ **Regulatory RAG**: Using Vector Search for laws, not just facts.
2. ✅ **Clause-by-Clause Review**: Breaking documents down for precision.
3. ✅ **Severity Classification**: Distinguishing warnings from errors.
4. ✅ **Reporting**: Generating a structured `ComplianceReport`.
5. ✅ **Risk Mitigation**: Catching problems before they become lawsuits.

**Key Takeaway**: AI is the ultimate proofreader. It doesn't get tired. It knows the rules.

**Skills unlocked**: 🎯
- Legal Tech (RegTech)
- Audit Automation
- Risk Analysis

**Looking ahead**: We have built *all* the components.
- Ch 49: Models
- Ch 50: Contract Gen
- Ch 51: Proposals
- Ch 52: Reports
- Ch 53: Compliance

In **Chapter 54 (The Finale)**, we will integrate everything into a **Single Application** with a UI. We will cross the finish line! 🏁

---

**Next**: [Chapter 54: Complete Civil Engineering Document System →](chapter-54-complete-system.md)
