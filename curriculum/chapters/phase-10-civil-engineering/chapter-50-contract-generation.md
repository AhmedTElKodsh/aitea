# Chapter 50: Contract Generation System — The Automated Lawyer

<!--
METADATA
Phase: 10 - Civil Engineering Application
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Application
Prerequisites: Chapter 49 (Models), Chapter 6 (Templates), Chapter 17 (RAG)
Builds Toward: Complete System (Ch 54)
Correctness Properties: P70 (Completeness), P72 (Clause Consistency)
Project Thread: Core Application

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: A client sends you a 50-page RFP (Request for Proposal).
They want a contract by Friday.
You have to:
1. Read the RFP.
2. Find the budget (`$5M`), deadline (`Dec 2025`), and insurance requirements (`$2M`).
3. Find your "Standard Engineering Agreement" Word doc.
4. Ctrl+F, replace old values, paste in new values.
5. Pray you didn't miss anything.

**Today, we automate this.**
We will build a system that reads the RFP (using RAG), understands it (using Agents), and fills out the Pydantic Model (Chapter 49) automatically.
It's like having a lawyer who works at light speed. ⚡

---

## Prerequisites Check

Ensure you have your `domain_models.py` from Chapter 49.

```bash
# Check file existence
ls domain_models.py
```

---

## The Story: The "Copy-Paste" Error

### The Problem (Human Error)

You copied the contract from the "Project Alpha" folder to use for "Project Beta".
You changed the name. You changed the price.
But you forgot to change the **Location**.
Now you have a contract for a bridge in New York, but the project is in Texas.
The client laughs at you. You lose the bid. 📉

### The Solution (Generative Filling)

We don't copy-paste. We **Generate**.
We take a Template (from Chapter 6) and inject data extracted directly from the RFP.
If the RFP says "Texas", the contract says "Texas". No copy-paste errors allowed.

---

## Part 1: The RFP Processor (Reading)

First, we need to extract facts from the RFP.

### 🔬 Try This! (Hands-On Practice #1)

**Create `rfp_processor.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from domain_models import EngineeringContract # From Ch 49
from dotenv import load_dotenv

load_dotenv()

# 1. Mock RFP Text (In real life, load this from PDF)
rfp_text = """
REQUEST FOR PROPOSAL
Project: Skyway Bridge
ID: ENG-2025-001
Client: Metropolis City Council
Scope: Design and build a pedestrian bridge over I-95.
Budget: $4,500,000 USD
Timeline: Start Jan 1, 2025. End Dec 31, 2025.
Terms: Engineer must indemnify Client against all claims.
       Either party may terminate with 30 days notice.
"""

# 2. Setup Extraction
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = PydanticOutputParser(pydantic_object=EngineeringContract)

prompt = ChatPromptTemplate.from_template(
    """
    You are a Contract Administrator. Extract terms from the RFP. 
    
    RFP Text:
    {rfp}
    
    {format_instructions}
    """
)

chain = prompt | model | parser

# 3. Extract
print("📝 Reading RFP...")
try:
    contract = chain.invoke({
        "rfp": rfp_text,
        "format_instructions": parser.get_format_instructions()
    })
    print("✅ Extraction Successful!")
    print(f"Project: {contract.project_name}")
    print(f"Budget: ${contract.budget:,.2f}")
    print(f"Indemnification: {contract.indemnification_clause[:50]}...")
except Exception as e:
    print(f"❌ Extraction Failed: {e}")
```

**Run it**.
It fills the complex Pydantic model instantly.

---

## Part 2: Dynamic Clause Generation

Sometimes the RFP has weird requirements. "Must use blue steel."
We need to generate specific clauses for that.

### 🔬 Try This! (Hands-On Practice #2)

Let's build a specialized agent for writing clauses.

**Create `clause_generator.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7) # Slightly creative

clause_prompt = ChatPromptTemplate.from_template(
    """
    Write a legal contract clause for the following requirement.
    Use formal, professional engineering contract language.
    
    Requirement: {requirement}
    """
)

clause_chain = clause_prompt | model | StrOutputParser()

# Test
req = "The bridge must be painted 'Sky Blue' using weather-resistant paint."
print(f"Requirement: {req}")
clause = clause_chain.invoke({"requirement": req})
print(f"\nGenerated Clause:\n{clause}")
```

**Run it**.
It turns a simple requirement into legalese ("The Contractor shall ensure...").

---

## Part 3: The Template Merger (Ch 6 Integration)

Remember Chapter 6? We have `TemplateStore`.
Now we combine Extracted Data + Template = Final Document.

### 🔬 Try This! (Hands-On Practice #3)

**Create `contract_assembler.py`**:

```python
# We simulate the TemplateStore for this exercise
# In full app, import it: from stores.template_store import TemplateStore

class MockTemplateStore:
    def get_template(self, type):
        return """
        CONTRACT AGREEMENT
        Project: {{project_name}}
        Budget: {{budget}}
        
        1. SCOPE
        {{scope_of_work}}
        
        2. SPECIAL PROVISIONS
        {{special_clauses}}
        """

# 1. Setup
store = MockTemplateStore()
template = store.get_template("engineering")

# 2. Data (From Part 1)
# We assume 'contract' object exists or create a dummy one
data = {
    "project_name": "Skyway Bridge",
    "budget": "$4,500,000",
    "scope_of_work": "Design and build...",
    "special_clauses": "All steel shall be Sky Blue per standard X."
}

# 3. Assemble
print("🏗️ Assembling Contract...")
final_doc = template
for key, value in data.items():
    final_doc = final_doc.replace(f"{{{{{key}}}}}", str(value))

print(final_doc)
```

**Run it**.
You now have a filled contract text ready for PDF export (Ch 54).

---

## Common Mistakes

### Mistake #1: Ignoring Date Formats
RFP: "Jan 1st". Model expects `date` object. Pydantic parser handles this well, but sometimes fails on ambiguous dates ("10/11/12").
**Fix**: Add "Format dates as YYYY-MM-DD" to system prompt.

### Mistake #2: Losing Context
If the RFP is 50 pages, it won't fit in the prompt.
**Fix**: Use RAG (Chapter 17) to find the "Budget" section, then extract. Don't shove the whole PDF into the extractor.

### Mistake #3: Blind Trust
Never send the AI contract to a client without review.
**Fix**: Add a "Human-in-the-Loop" step (Chapter 33) before finalizing.

---

## Quick Reference Card

### Architecture

```
RFP (PDF) -> [RAG] -> Relevant Chunks
       ⬇
[Extraction Chain] -> Pydantic Model (Data)
       ⬇
[Template Store] -> Template String
       ⬇
[Assembler] -> Final Contract
```

---

## Verification (REQUIRED SECTION)

We need to verify **P72 (Clause Consistency)**. The extracted budget must match the RFP.

**Create `verify_generation.py`**:

```python
"""
Verification script for Chapter 50.
Property P72: Extraction Consistency.
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from domain_models import EngineeringContract
import sys

print("🧪 Running Generator Verification...\n")

# Mock RFP with tricky budget formatting
rfp_content = "The total allocated funds for Project Beta are 5.2 Million US Dollars."

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = PydanticOutputParser(pydantic_object=EngineeringContract)
prompt = ChatPromptTemplate.from_template(
    "Extract info. Use dummy values for missing fields to satisfy validation.\n{rfp}\n{format_instructions}"
)
chain = prompt | model | parser

print("Test 1: Budget Extraction...")
try:
    # We expect the model to convert "5.2 Million" to 5200000.0
    result = chain.invoke({
        "rfp": rfp_content, 
        "format_instructions": parser.get_format_instructions()
    })
    
    if result.budget == 5200000.0:
        print("✅ P72 Passed: Extracted and normalized budget correctly.")
    else:
        print(f"❌ Failed: Expected 5,200,000. Got {result.budget}")
        sys.exit(1)
        
except Exception as e:
    # If validation fails due to missing fields (which we told it to fake), 
    # we just want to check if the logic worked at all.
    # But ideally, we want a clean pass.
    print(f"❌ Error during extraction: {e}")
    sys.exit(1)

print("\n🎉 Chapter 50 Complete! You are a Legal Engineer.")
```

**Run it:** `python verify_generation.py`

---

## Summary

**What you learned:**

1. ✅ **Automated Ingestion**: Turning unstructured RFPs into structured Models.
2. ✅ **Pydantic Power**: Ensuring the extracted data is valid (dates, numbers).
3. ✅ **Clause Generation**: Using AI to write specific legal text.
4. ✅ **Template Assembly**: Merging data with structure.
5. ✅ **End-to-End Flow**: From PDF to Contract.

**Key Takeaway**: AI doesn't replace the lawyer. It drafts the paperwork so the lawyer can focus on strategy.

**Skills unlocked**: 🎯
- Legal Engineering
- Document Automation
- Complex Data Extraction

**Looking ahead**: We can build contracts. What about **Proposals**? A proposal is more than data—it's persuasion. It requires strategy and technical writing.
In **Chapter 51**, we will build the **Proposal Generation System**.

---

**Next**: [Chapter 51: Proposal Generation System →](chapter-51-proposal-generation.md)
