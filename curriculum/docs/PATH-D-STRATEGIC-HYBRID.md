# Path D: Strategic Hybrid Curriculum
## The Optimal Zero-to-Hero AI Engineering Learning Path

**Created**: 2026-01-16
**Status**: ✅ APPROVED
**Student**: Ahmed
**Skill Level**: Beginner Python
**Goal**: Build AI Civil Engineering Document Generation System
**Timeline**: 12 weeks core + flexible enhancement

---

## 🎯 Executive Summary

Path D is a **three-track learning system** that delivers:

- **12-week core track** → Working Civil Engineering AI system (35 chapters, 52 hours)
- **Enhancement track** → Optional depth modules (18 chapters, 27 hours) - take anytime after prerequisites
- **Mastery track** → Advanced frameworks (10 chapters, 24 hours) - future learning after project complete

**Total Curriculum**: 63 chapters, 103 hours of content, zero-to-hero progression

---

## 🏗️ Architecture Principles

### 1. Progressive Disclosure
Complexity revealed only when foundations support it. Like building a house - foundation first, then walls, then roof.

### 2. Critical Path Isolation
35 essential chapters identified as the MINIMUM required to build the final system. Everything else enhances but isn't blocking.

### 3. Flexible Enhancement
Enhancement chapters can be taken:
- In parallel with core track (if Ahmed progresses quickly)
- After completing core track (to add features)
- Never (if time-constrained, though not recommended)

### 4. Acceptable Technical Debt
"Lite" chapters (12-Lite, 25-Lite) teach simplified versions. Full versions in Enhancement track allow refactoring later. This is intentional - MVP first, polish later.

### 5. Continuous Validation
Assessments at every chapter and milestone gate ensure gaps caught early.

---

## 📊 The Three Tracks Explained

### **Track 1: CRITICAL PATH** (Core Curriculum)
**Purpose**: Fastest path to working Civil Engineering application
**Chapters**: 35 total
**Time**: 52 hours of content (~12 weeks at 4-5 hours/week)
**Output**: Fully functional AI document generation system

**Must Complete**: Sequential, no skipping

### **Track 2: ENHANCEMENT PATH** (Parallel Learning)
**Purpose**: Add depth, production features, advanced patterns
**Chapters**: 18 total
**Time**: 27 hours of content (~3-4 weeks if done sequentially)
**Output**: Production-grade system with advanced features

**Can Complete**: Anytime after prerequisites met, flexible ordering

### **Track 3: MASTERY PATH** (Future Learning)
**Purpose**: Master advanced frameworks, multi-agent systems
**Chapters**: 10 total
**Time**: 24 hours of content (~6-8 weeks)
**Output**: Expert-level AI engineering skills

**Should Complete**: After finishing Civil Engineering project

---

## 🛤️ Track 1: CRITICAL PATH (Week-by-Week)

### **Milestone 1: Foundations & Python Essentials** (Weeks 1-2.5)
**Goal**: Master Python fundamentals required for AI development

| Week | Chapter | Title | Hours | Deliverable |
|------|---------|-------|-------|-------------|
| 1 | 1 | Environment Setup & Project Initialization | 1.5 | Dev environment ready |
| 1 | 2 | Enums & Type Hints | 1.5 | Type-safe code |
| 1-2 | 3 | Pydantic Models (Core) | 2.0 | Data validation |
| 2 | 4 | Pydantic Advanced & Structured Output | 2.0 | Nested models |
| 2 | 5 | Validation Utilities | 1.5 | Validation library |
| 2 | 6 | Template System | 1.5 | YAML templates |
| 2-3 | 6A | 🆕 Decorators & Context Managers | 1.5 | Function enhancement |
| 3 | 6B | 🆕 Error Handling Patterns | 1.5 | Robust error handling |
| 3 | 6C | 🆕 OOP Intermediate | 1.5 | Inheritance, abstractions |

**Mini-Project**: Configuration Manager (uses decorators, context managers, error handling)
**Assessment**: Can create validated Pydantic models with proper error handling
**Total**: 14.5 hours

---

### **Milestone 2: LLM Core Skills** (Weeks 3-4.5)
**Goal**: Master LLM API calls and structured output

| Week | Chapter | Title | Hours | Deliverable |
|------|---------|-------|-------|-------------|
| 3-4 | 7 | Your First LLM Call | 1.5 | Simple chatbot |
| 4 | 8 | Multi-Provider LLM Client | 2.0 | Provider abstraction |
| 4 | 9 | Prompt Engineering Basics | 1.5 | Prompt templates |
| 4 | 11 | Structured Output with Pydantic | 1.5 | JSON extraction |
| 4-5 | 12-Lite | 🆕 Error Handling for LLMs (simplified) | 1.0 | Basic retry logic |

**Mini-Project**: Multi-Provider Chatbot with Structured Output
**Assessment**: Can build LLM client that extracts structured data reliably
**Total**: 7.5 hours

**Skipped for Now**:
- Ch 10: Streaming Responses → Enhancement Track
- Ch 12 (Full): Advanced error handling → Enhancement Track

---

### **Milestone 3: RAG Fundamentals** (Weeks 5-6.5)
**Goal**: Build semantic search and retrieval systems

| Week | Chapter | Title | Hours | Deliverable |
|------|---------|-------|-------|-------------|
| 5 | 13 | Understanding Embeddings | 1.5 | Semantic search |
| 5 | 14 | Vector Stores with Chroma | 1.5 | Persistent vectors |
| 5-6 | 15 | Chunking Strategies | 1.5 | Document chunking |
| 6 | 16 | Document Loaders | 1.5 | Multi-format loading |
| 6 | 17 | Your First RAG System | 2.0 | End-to-end RAG |
| 6-7 | 18 | LCEL Chains | 1.5 | LangChain basics |

**Mini-Project**: FAQ Search Engine (semantic search over documents)
**Assessment**: Can build end-to-end RAG pipeline with proper chunking
**Total**: 9.5 hours

**Skipped for Now**:
- Ch 19-22: Advanced RAG (retrieval strategies, query expansion, evaluation, optimization) → Enhancement Track

---

### **Milestone 4: LangChain Essentials** (Weeks 7-8)
**Goal**: Master LangChain for document processing

| Week | Chapter | Title | Hours | Deliverable |
|------|---------|-------|-------|-------------|
| 7 | 23 | LangChain Loaders & Text Splitters | 1.5 | LangChain integration |
| 7 | 24 | LangChain Structured Output | 1.5 | Chain-based extraction |
| 7-8 | 25-Lite | 🆕 Simple Memory (simplified) | 1.0 | Conversation memory |

**Mini-Project**: Memory-Enabled Document QA System
**Assessment**: Can build LangChain pipeline with memory
**Total**: 4.0 hours

**Skipped for Now**:
- Ch 25 (Full): Callbacks & Advanced Memory → Enhancement Track
- Ch 26-30: Full Agent Systems (ReAct, OTAR, tools) → Enhancement Track

---

### **Milestone 5: Production Basics** (Week 9)
**Goal**: Learn to test and evaluate AI systems

| Week | Chapter | Title | Hours | Deliverable |
|------|---------|-------|-------|-------------|
| 9 | 39 | Testing LLM Applications | 1.5 | Test suite |
| 9 | 40 | Evaluation & Metrics | 1.5 | Eval framework |

**Mini-Project**: Test & Evaluate RAG System
**Assessment**: Can write comprehensive tests for LLM applications
**Total**: 3.0 hours

**Skipped for Now**:
- Ch 41: Security & Privacy → Enhancement Track
- Ch 42: Cost Optimization → Mastery Track

---

### **Milestone 6: 🏗️ Civil Engineering Application** (Weeks 10-12)
**Goal**: Build complete Civil Engineering Document Generation System

| Week | Chapter | Title | Hours | Deliverable |
|------|---------|-------|-------|-------------|
| 10 | 49 | Civil Engineering Domain Models | 2.0 | Contract/Proposal models |
| 10 | 50 | Contract Generation System | 2.0 | Contract generator |
| 11 | 51 | Proposal Generation System | 2.0 | Proposal generator |
| 11 | 52 | Technical Report Generation | 2.0 | Report generator |
| 11-12 | 53 | Compliance Validation | 1.5 | Compliance checker |
| 12 | 54 | End-to-End Document System | 2.0 | Integrated system |

**FINAL PROJECT**: Complete Civil Engineering Document Generation System (8 hours)
**Assessment**: Fully functional AI system for civil engineering documents
**Total**: 11.5 hours

---

## **✅ Track 1 Summary**

**Total Chapters**: 35
**Total Hours**: 52 hours
**Timeline**: 12 weeks at 4-5 hours/week
**Outcome**: Working Civil Engineering AI Document System

---

## 🔄 Track 2: ENHANCEMENT PATH (Flexible Timing)

### **Purpose**
Add depth, production features, and advanced patterns to your Civil Engineering system. These chapters ENHANCE the core system but aren't blocking.

### **When to Take Enhancement Chapters**

You can take enhancement chapters:
1. **In Parallel** - If progressing quickly through core track
2. **After Milestone Completion** - Add features to each milestone's project
3. **After Track 1 Complete** - Polish the final system
4. **As Needed** - When you encounter limitations

### **Enhancement Chapter Catalog**

| After Milestone | Chapter | Title | Hours | Adds To System |
|----------------|---------|-------|-------|----------------|
| M1 | 6D | Testing with pytest | 1.5 | Comprehensive test suite |
| M2 | 10 | Streaming Responses | 1.5 | Real-time UX like ChatGPT |
| M2 | 12 | Full Error Handling & Retries | 1.5 | Production reliability |
| M3 | 12A | Generators & Iterators | 1.5 | Efficient data processing |
| M3 | 12B | Async/Await Fundamentals | 1.5 | Concurrent LLM calls |
| M3 | 19 | Retrieval Strategies | 1.5 | Better RAG quality |
| M3 | 20 | Query Expansion & Reranking | 1.5 | Improved search |
| M3 | 21 | RAG Evaluation | 1.5 | Measure RAG performance |
| M3 | 22 | RAG Optimization | 1.5 | Production RAG |
| M4 | 22A | Strategy & Factory Patterns | 1.5 | Better architecture |
| M4 | 22B | Observer & Chain Patterns | 1.5 | Event-driven design |
| M4 | 25 | Full Callbacks & Memory | 1.5 | Advanced LangChain |
| M4 | 26 | Understanding Agents | 1.5 | Autonomous systems |
| M4 | 27 | ReAct Pattern | 1.5 | Reasoning agents |
| M4 | 28 | Tools & Tool Calling | 1.5 | Agent capabilities |
| M4 | 29 | Agent Memory Strategies | 1.5 | Stateful agents |
| M4 | 30 | OTAR Pattern | 1.5 | Advanced agents |
| M5 | 41 | Security & Privacy | 1.5 | Secure production system |

**Total Enhancement**: 18 chapters, 27 hours

---

## 🚀 Track 3: MASTERY PATH (Future Learning)

### **Purpose**
Master advanced frameworks and build cutting-edge multi-agent systems. Take AFTER completing Civil Engineering project.

### **Mastery Chapter Catalog**

| Chapter | Title | Hours | Skills Gained |
|---------|-------|-------|---------------|
| 22C | State Machines Basics | 1.5 | FSM fundamentals |
| 31 | LangGraph Introduction | 1.5 | Graph-based workflows |
| 32 | LangGraph State Management | 1.5 | Complex state machines |
| 33 | LangGraph Conditional Routing | 1.5 | Dynamic workflows |
| 34 | LangGraph Production Patterns | 1.5 | Production workflows |
| 35 | LlamaIndex Introduction | 1.5 | Alternative framework |
| 36 | LlamaIndex Query Engines | 1.5 | Advanced querying |
| 37 | LlamaIndex Indexing Strategies | 1.5 | Optimized indexing |
| 38 | LlamaIndex Production Patterns | 1.5 | Production LlamaIndex |
| 42 | Cost Optimization | 1.5 | Optimize LLM costs |
| 43 | Multi-Agent Systems Intro | 1.5 | Agent coordination |
| 44 | CrewAI Framework | 1.5 | CrewAI patterns |
| 45 | AutoGen Framework | 1.5 | AutoGen patterns |
| 46 | Agent Communication Patterns | 1.5 | Inter-agent protocols |
| 47 | Multi-Agent Coordination | 1.5 | Complex coordination |
| 48 | Production Multi-Agent Systems | 1.5 | Production multi-agent |

**Total Mastery**: 16 chapters, 24 hours

---

## 📚 Assessment Framework

### **Per-Chapter Assessments**

Every chapter includes:

1. **Quick Check** (5 questions, 5 min)
   - Multiple choice or short answer
   - Verify concept understanding
   - Pass: 4/5 correct

2. **Coding Challenge** (1-2 problems, 20-30 min)
   - Apply chapter concepts
   - Auto-gradable with tests
   - Pass: All tests green

3. **Chapter Mini-Project** (30-45 min)
   - Small standalone project
   - Example: Ch 7 → "Movie Chatbot", Ch 11 → "Recipe Extractor"
   - Pass: Project runs and meets requirements

### **Milestone Assessments**

At end of each milestone:

1. **Capstone Mini-Project** (2-4 hours)
   - Integrates all milestone concepts
   - See mini-project table below

2. **Self-Assessment Checklist**
   - "Can I do X without looking at docs?"
   - Identifies gaps before proceeding

3. **Readiness Gate**
   - Pass milestone assessment → Proceed to next milestone
   - Gaps identified → Take relevant enhancement chapters

### **Milestone Capstone Projects**

| Milestone | Project | Hours | Skills Validated |
|-----------|---------|-------|------------------|
| M1 | Configuration Manager | 2 | Pydantic, decorators, error handling |
| M2 | Multi-Provider Streaming Chatbot | 3 | LLM calls, providers, structured output |
| M3 | FAQ Search Engine | 4 | Embeddings, RAG, chunking, retrieval |
| M4 | Memory-Enabled Document QA | 3 | LangChain, chains, memory |
| M5 | Tested RAG System | 2 | Testing, evaluation, metrics |
| M6 | 🏗️ Civil Engineering System | 8 | ALL SKILLS - Final Project |

---

## 🎯 Success Criteria

### **By End of Track 1 (Week 12)**

Ahmed will be able to:

✅ Build multi-provider LLM applications with structured output
✅ Create RAG systems with embeddings and vector stores
✅ Implement document processing pipelines with LangChain
✅ Generate civil engineering documents (contracts, proposals, reports)
✅ Validate compliance and structure of generated documents
✅ Test and evaluate LLM application quality
✅ Deploy working AI system with proper error handling

### **By End of Track 2 (Enhancement Complete)**

Ahmed will additionally be able to:

✅ Build production-grade systems with streaming, async, and advanced error handling
✅ Implement agent systems with ReAct and OTAR patterns
✅ Optimize RAG quality with advanced retrieval strategies
✅ Apply software design patterns to AI systems
✅ Secure AI applications for production deployment

### **By End of Track 3 (Mastery Complete)**

Ahmed will additionally be able to:

✅ Build complex workflows with LangGraph
✅ Master LlamaIndex for advanced querying
✅ Create multi-agent systems with CrewAI and AutoGen
✅ Optimize costs and performance of LLM applications
✅ Deploy enterprise-grade AI systems

---

## 🛠️ Technical Architecture Decisions

### **"Lite" Chapters Explained**

**Ch 12-Lite: Error Handling for LLMs**
- **Teaches**: Try/except, basic retry with exponential backoff, Result type
- **Skips**: Circuit breakers, advanced retry strategies, monitoring
- **Rationale**: Enough to build reliable chatbot, not production system
- **Enhancement Path**: Full Ch 12 adds production patterns

**Ch 25-Lite: Simple Memory**
- **Teaches**: Conversation history buffer, basic memory integration
- **Skips**: Callbacks, advanced memory strategies (summary, entity, knowledge graph)
- **Rationale**: Enough for document QA, not complex agents
- **Enhancement Path**: Full Ch 25 adds callbacks and advanced memory

### **Technical Debt Management**

Path D intentionally creates technical debt in the core track:
- Simplified error handling (12-Lite)
- Basic memory (25-Lite)
- No streaming (Ch 10 skipped)
- No async (Ch 12A-12B skipped)

**This is GOOD technical debt** because:
1. Ahmed ships working system in 12 weeks
2. Debt is documented and tracked
3. Enhancement chapters provide refactoring path
4. Debt doesn't block final project completion

**Refactoring Timeline**:
- After M6: System works but has technical debt
- Weeks 13-16: Take enhancement chapters, refactor system
- Result: Production-ready system with all advanced features

---

## 📅 Weekly Time Commitment

### **Core Track (Weeks 1-12)**

**Recommended**: 4-5 hours/week
- 3-4 hours: Chapter content + coding
- 1 hour: Assessment + mini-project

**Flexible Options**:
- **Intensive**: 8-10 hours/week → Finish in 6-7 weeks
- **Relaxed**: 2-3 hours/week → Finish in 20-24 weeks

### **Enhancement Track (Weeks 13-16)**

**Recommended**: 6-8 hours/week
- Take 4-5 enhancement chapters/week
- Refactor Civil Engineering system with new skills

### **Mastery Track (Future)**

**Recommended**: 3-4 hours/week over 6-8 weeks
- Learn at comfortable pace
- No pressure - this is career development

---

## 🚦 Checkpoint Gates

### **Gate 1: After Chapter 6C (End of Week 3)**
**Question**: "Are Python fundamentals solid?"

**Pass Criteria**:
- ✅ Decorators make sense
- ✅ Error handling feels natural
- ✅ OOP concepts clear

**If Pass**: Proceed to Milestone 2 (LLM Core Skills)
**If Fail**: Take Ch 6D (Testing), practice more Python

---

### **Gate 2: After Chapter 12-Lite (End of Week 5)**
**Question**: "Can I build LLM applications?"

**Pass Criteria**:
- ✅ Multi-provider chatbot working
- ✅ Structured output extraction successful
- ✅ Error handling prevents crashes

**If Pass**: Proceed to Milestone 3 (RAG)
**If Fail**: Take Ch 10, Ch 12 (Full) for depth

---

### **Gate 3: After Chapter 18 (End of Week 7)**
**Question**: "Do I understand RAG?"

**Pass Criteria**:
- ✅ FAQ engine works well
- ✅ Embeddings concept clear
- ✅ Chunking strategies make sense

**If Pass**: Proceed to Milestone 4 (LangChain)
**If Fail**: Take Ch 19-22 for advanced RAG

---

### **Gate 4: After Chapter 25-Lite (End of Week 8)**
**Question**: "Ready for final project?"

**Pass Criteria**:
- ✅ LangChain comfortable
- ✅ Memory systems working
- ✅ Confident in abilities

**If Pass**: Take Ch 39-40, proceed to Milestone 6
**If Fail**: Take Ch 25-30 for agent depth

---

## 🎓 Learning Resources

### **Required Tools**
- Python 3.10+
- VS Code with Python extension
- Git for version control
- OpenAI API key (paid account recommended)
- Optional: Anthropic, Groq API keys

### **Required Python Packages**
```
openai>=1.0.0
anthropic>=0.8.0
langchain>=0.1.0
chromadb>=0.4.0
pydantic>=2.0.0
pytest>=7.0.0
python-dotenv>=1.0.0
```

### **Optional Resources**
- LangChain documentation
- OpenAI Cookbook
- Real Python (Python tutorials)
- Fast.ai (ML context)

---

## 📊 Progress Tracking

### **Track 1 Progress**

- [ ] Milestone 1: Foundations (Ch 1-6, 6A-6C) - Weeks 1-3
- [ ] Milestone 2: LLM Skills (Ch 7-9, 11, 12-Lite) - Weeks 3-5
- [ ] Milestone 3: RAG (Ch 13-18) - Weeks 5-7
- [ ] Milestone 4: LangChain (Ch 23-25-Lite) - Weeks 7-8
- [ ] Milestone 5: Production (Ch 39-40) - Week 9
- [ ] Milestone 6: 🏗️ Civil Engineering (Ch 49-54) - Weeks 10-12

### **Track 2 Progress**

- [ ] Testing & Quality (Ch 6D, 39-41)
- [ ] Advanced LLM (Ch 10, 12, 12A-12B)
- [ ] Advanced RAG (Ch 19-22)
- [ ] Design Patterns (Ch 22A-22B)
- [ ] Agent Systems (Ch 25-30)

### **Track 3 Progress**

- [ ] LangGraph (Ch 22C, 31-34)
- [ ] LlamaIndex (Ch 35-38)
- [ ] Multi-Agent (Ch 42-48)

---

## 🎯 Risk Management

### **Identified Risks**

1. **Risk: Decorators too difficult**
   - **Mitigation**: Ch 6A includes extensive examples, visual diagrams
   - **Fallback**: Online Python decorator tutorial first

2. **Risk: LLM API costs**
   - **Mitigation**: Use Ollama (free local models) for practice
   - **Fallback**: MockLLM provider for testing

3. **Risk: Falling behind schedule**
   - **Mitigation**: Flexible enhancement track
   - **Fallback**: Focus only on core track, skip enhancements

4. **Risk: Concepts not sticking**
   - **Mitigation**: Checkpoint gates catch early
   - **Fallback**: Enhancement chapters provide depth

5. **Risk: Burnout from 12-week intensity**
   - **Mitigation**: Mini-projects provide variety
   - **Fallback**: Extend to 16-20 weeks, reduce hours/week

---

## ✅ Approval & Execution

**Approved By**: Ahmed
**Approved Date**: 2026-01-16
**Execution Start**: Immediately

**First Deliverable**: Chapter 6A - Decorators & Context Managers

---

## 📞 Support & Adjustments

Path D is a LIVING PLAN. Adjustments are expected and encouraged.

**When to Adjust**:
- Checkpoint gate fails
- Schedule needs flexibility
- Ahmed discovers interest in specific topic
- Learning pace faster/slower than expected

**How to Adjust**:
- Consult with BMad Master
- Review enhancement chapter catalog
- Modify weekly hours
- Extend/compress timeline

**Remember**: The goal is Ahmed's mastery and project completion, not rigid adherence to timeline.

---

**END OF PATH D SPECIFICATION**

BMad Master will now create Chapter 6A to begin execution.
