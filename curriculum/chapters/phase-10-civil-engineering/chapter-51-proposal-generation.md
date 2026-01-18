# Chapter 51: Proposal Generation System — Winning the Bid

<!--
METADATA
Phase: 10 - Civil Engineering Application
Time: 1.5 hours (30 min reading + 60 min hands-on)
Difficulty: ⭐⭐⭐
Type: Application
Prerequisites: Chapter 50 (Contracts), Chapter 44 (CrewAI)
Builds Toward: Complete System (Ch 54)
Correctness Properties: P71 (Structure Validation), P73 (Requirement Coverage)
Project Thread: Business Growth

NAVIGATION
→ Quick Reference: #quick-reference-card
→ Verification: #verification-required-section
→ What's Next: #whats-next
-->

---

## ☕ Coffee Shop Intro

**Imagine this**: You are at a job interview.
Interviewer: "Can you handle high pressure?"
You (Contract Style): "I agree to perform duties under pressure pursuant to Section 4.1." 😐
You (Proposal Style): "Absolutely. In my last project, I managed a crisis that saved $50k. Here is how I will do the same for you." 🚀

Contracts are about **Compliance**. Proposals are about **Persuasion**.
A boring proposal loses the bid. A proposal that misses a requirement loses the bid.
We need an AI that is both **Creative** (to sell the vision) and **Meticulous** (to answer every question in the RFP).

**By the end of this chapter**, you will build a system that reads an RFP and generates a winning proposal, mapping every client need to a technical solution. 🏆

---

## Prerequisites Check

Ensure you have your `domain_models.py` from Chapter 49.

```bash
# Check file existence
ls domain_models.py
```

---

## The Story: The "Unanswered Question"

### The Problem (Disqualification)

The RFP asked: "Describe your safety protocol for hazardous waste."
You wrote 50 pages about your amazing bridge design. You forgot the waste protocol.
**Result**: Disqualified immediately.

### The Solution (Requirement Mapping)

1.  **Extract**: List every single question/requirement in the RFP.
2.  **Retrieve**: Find our company's "Standard Operating Procedure" for that topic.
3.  **Generate**: Write a custom answer linking our SOP to their requirement.
4.  **Verify**: Check that we answered 100% of requirements.

---

## Part 1: Requirement Extraction

First, we need to know what they are asking for.

### 🔬 Try This! (Hands-On Practice #1)

**Create `req_extractor.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

# Mock RFP
rfp_text = """
SECTION 4: REQUIREMENTS
4.1 The contractor must have 10 years of experience.
4.2 The bridge must withstand Category 5 hurricanes.
4.3 A safety officer must be on-site 24/7.
"""

# 1. Setup
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = JsonOutputParser()

# 2. Prompt
prompt = ChatPromptTemplate.from_template(
    """
    Extract all requirements from the RFP text.
    Return a JSON list of strings.
    Example: ["10 years experience", "Hurricane proof"]
    
    RFP:
    {rfp}
    """
)

chain = prompt | model | parser

# 3. Extract
print("📝 Extracting Requirements...")
requirements = chain.invoke({"rfp": rfp_text})

for i, req in enumerate(requirements):
    print(f"{i+1}. {req}")
```

**Run it**.
You should get a clean list of 3 items.

---

## Part 2: The Solution Mapper (RAG)

Now we answer each requirement. We need a "Company Knowledge Base" (simulated).

### 🔬 Try This! (Hands-On Practice #2)

**Create `solution_mapper.py`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Company Knowledge (Simulated Vector Store retrieval)
knowledge_base = {
    "experience": "We have been in business since 1990 (34 years).",
    "hurricane": "Our bridges use reinforced concrete rated for 200mph winds.",
    "safety": "We deploy OSHA-certified officers to every site."
}

def retrieve_knowledge(req):
    # Simple keyword match for demo
    if "experience" in req: return knowledge_base["experience"]
    if "hurricane" in req: return knowledge_base["hurricane"]
    if "safety" in req: return knowledge_base["safety"]
    return "We will comply with all standards."

# 2. The Writer
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7) # Creative!
prompt = ChatPromptTemplate.from_template(
    """
    Write a proposal section addressing this requirement.
    Requirement: {req}
    Our Capability: {capability}
    
    Be persuasive but professional.
    """
)
writer = prompt | model | StrOutputParser()

# 3. Generate Sections
requirements = [
    "The contractor must have 10 years of experience.",
    "The bridge must withstand Category 5 hurricanes."
]

print("🏗️ Generating Technical Approach...")
technical_approach = []

for req in requirements:
    cap = retrieve_knowledge(req)
    section = writer.invoke({"req": req, "capability": cap})
    technical_approach.append(section)
    print(f"\n---" Addressing: {req} ---
{section}")
```

**Run it**.
Notice how it weaves the "Knowledge" into a persuasive answer.

---

## Part 3: The Full Proposal

Now we assemble the Pydantic model (`TechnicalProposal`).

### 🔬 Try This! (Hands-On Practice #3)

**Create `proposal_assembler.py`**:

```python
from domain_models import TechnicalProposal, TeamMember
from datetime import datetime

# 1. Gather Data (Simulated from Part 1 & 2)
tech_approach_text = [
    "We bring 34 years of experience...",
    "Our Category 5 rated concrete..."
]

# 2. Create Model
print("📄 Assembling Proposal...")
try:
    proposal = TechnicalProposal(
        rfp_reference="RFP-2025-X",
        executive_summary="We are the best choice for this bridge.",
        technical_approach=tech_approach_text,
        team=[
            TeamMember(name="Alice", role="Project Manager", license_number="PE-999"),
            TeamMember(name="Bob", role="Safety Officer")
        ],
        estimated_cost=4500000.00
    )
    
    print("✅ Proposal Created Successfully!")
    print(f"Cost: ${proposal.estimated_cost:,.2f}")
    print(f"Team: {len(proposal.team)} members")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

**Run it**.
It validates that we have a PE (Alice) and the cost is a float.

---

## Common Mistakes

### Mistake #1: Ignoring the "Tone"
RFP responses can sound robotic.
**Fix**: Add "Tone Instructions" to your prompt: *"Use active voice. Be confident. Focus on value."*

### Mistake #2: Missing the "Win Theme"
A proposal needs a central argument ("We are the fastest" or "We are the safest").
**Fix**: Pass a `win_theme` variable to every writer call.

### Mistake #3: Hallucinating Capabilities
If you don't have a matching capability in the Vector Store, the AI might make one up.
**Fix**: Use the "I don't know" guardrail (Ch 17) and flag it for human review.

---

## Quick Reference Card

### Proposal Flow

```
RFP -> [Extract Requirements] -> List[Req]
       ⬇
For each Req: [Retrieve Capability] -> [Write Section]
       ⬇
[Assemble] -> TechnicalProposal Model
```

---

## Verification (REQUIRED SECTION)

We need to verify **P73 (Requirement Coverage)**.

**Create `verify_proposal.py`**:

```python
"""
Verification script for Chapter 51.
Property P73: Requirement Coverage.
"""
from domain_models import TechnicalProposal, TeamMember
import sys

print("🧪 Running Proposal Verification...\n")

# P73: Coverage
# We verify that the number of technical approach sections matches requirements
requirements = ["Req A", "Req B", "Req C"]
generated_sections = ["Answer A", "Answer B", "Answer C"]

print("Test 1: Coverage Check...")
if len(generated_sections) == len(requirements):
    print("✅ P73 Passed: Addressed all requirements.")
else:
    print(f"❌ Failed: Missed requirements. {len(generated_sections)} vs {len(requirements)}")
    sys.exit(1)

# P71: Structure (Re-verify PE check)
print("Test 2: Validation...")
try:
    TechnicalProposal(
        rfp_reference="Test",
        executive_summary="Sum",
        technical_approach=generated_sections,
        team=[TeamMember(name="Intern", role="Intern")], # No PE
        estimated_cost=100
    )
    print("❌ Failed: Should have rejected team without PE.")
    sys.exit(1)
except ValueError:
    print("✅ P71 Passed: Validation logic holds.")

print("\n🎉 Chapter 51 Complete! You are ready to bid.")
```

**Run it:** `python verify_proposal.py`

---

## Summary

**What you learned:**

1. ✅ **Persuasion vs Compliance**: Contracts constrain; Proposals sell.
2. ✅ **Requirement Extraction**: Breaking a massive doc into a checklist.
3. ✅ **Knowledge Mapping**: Linking "What they want" to "What we have".
4. ✅ **Section Generation**: Writing targeted technical content.
5. ✅ **Team Validation**: Ensuring we have the right people on the job.

**Key Takeaway**: A winning proposal is just a series of good answers to specific questions. AI excels at this granular mapping.

**Skills unlocked**: 🎯
- Proposal Engineering
- Requirement Analysis
- Content Strategy

**Looking ahead**: We have the Contract. We have the Proposal. Now we need to actually *do the work*.
In **Chapter 52**, we will build the **Technical Report Generation System** to automate the daily grind of engineering reports.

---

**Next**: [Chapter 52: Technical Report Generation System →](chapter-52-report-generation.md)
