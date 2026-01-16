# AI Knowledge Base - Civil Engineering Document System

**A comprehensive zero-to-hero AI Engineering curriculum teaching AI agents, RAG, and multi-agent systems through building a Civil Engineering Document System.**

## Project Overview

This project provides a **54-chapter hands-on curriculum** (60-65 hours) that takes you from basic Python knowledge to building production-ready AI systems. You'll learn by creating a real-world Civil Engineering Document System that handles:

- **Contracts** (engineering, consulting, governmental, military)
- **Proposals** (RFP/RFQ responses, technical approaches, pricing)
- **Technical Reports** (engineering analysis, calculations, visualizations)

## Learning Approach

- **Zero-to-Hero Progression**: Start with foundations, build up to advanced multi-agent systems
- **Cafe-Style Teaching**: Casual conversational language with real-world analogies
- **Modified Scaffold**: Example patterns + starter code, you fill in the TODOs
- **Universal Examples First**: Chapters 1-30 use movies, restaurants, FAQs
- **Civil Engineering Application**: Chapters 31-54 apply concepts to real projects
- **Property-Based Testing**: 40+ correctness properties using Hypothesis

## Curriculum Structure (54 Chapters, 10 Phases)

### Phase 0: Foundations (Ch 1-6) - 9 hours
Environment setup, Python type hints, Pydantic models, validation, template systems

### Phase 1: LLM Fundamentals (Ch 7-12) - 9 hours
Multi-provider LLM clients, prompts, structured output, streaming, error handling

### Phase 2: Embeddings & Vectors (Ch 13-16) - 6 hours
Sentence transformers, vector stores, similarity search, chunking strategies

### Phase 3: RAG Fundamentals (Ch 17-22) - 9 hours
Retrieval-augmented generation, LCEL chains, advanced RAG patterns

### Phase 4: LangChain Core (Ch 23-25) - 4.5 hours
Document loaders, text splitting, memory, callbacks

### Phase 5: Agents (Ch 26-30) - 7.5 hours
ReAct pattern, OTAR loop, tool calling, agent memory

### Phase 6: LangGraph (Ch 31-34) - 6 hours
State graphs, conditional routing, human-in-the-loop, persistence

### Phase 7: LlamaIndex (Ch 35-38) - 6 hours
Query engines, response synthesis, advanced indexing, hybrid search

### Phase 8: Production (Ch 39-42) - 6 hours
Evaluation, LangSmith, error handling, security, cost optimization

### Phase 9: Multi-Agent (Ch 43-48) - 9 hours
CrewAI, AutoGen, supervisor patterns, agent communication

### Phase 10: Civil Engineering Application (Ch 49-54) - 9 hours
Apply everything to build Contracts, Proposals, Reports system

**Total: 54 chapters, 71 hours**

## Key Features

### Multi-Provider LLM Support
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude 3)
- Groq (Fast inference)
- Ollama (Local models)
- MockLLM (Testing)
- Fallback chains with graceful degradation

### Advanced RAG Patterns
- 4 chunking strategies (FixedSize, Recursive, Semantic, Sentence)
- Hybrid search (dense + sparse)
- Query rewriting and expansion
- Contextual compression
- Document loaders (PDF, DOCX, HTML, Markdown)

### Agent Frameworks
- **OTAR Loop**: Observe-Think-Act-Reflect pattern
- **ReAct**: Reasoning and Acting agents
- **LangGraph**: Complex workflows with state management
- **CrewAI**: Team-based multi-agent systems
- **AutoGen**: Iterative refinement agents

### Production-Ready
- Property-based testing (Hypothesis)
- Error handling and retries
- Token counting and cost tracking
- Streaming responses
- LangSmith evaluation
- Security best practices

## Project Structure

```
AI-Knowledge-Base/
├── curriculum/
│   ├── chapters/          # 54 chapter markdown files
│   ├── templates/         # Chapter templates for authors
│   ├── prompts/           # Master curriculum prompt
│   └── references/        # Reference materials from AITEA and Contract projects
├── shared/
│   ├── models/            # Pydantic models (contracts, proposals, reports)
│   ├── infrastructure/    # LLM clients, providers, streaming
│   ├── ingest/            # Document loaders and chunkers
│   └── data/templates/    # YAML templates for documents
├── examples/              # Working code examples from curriculum
├── tests/
│   ├── properties/        # Property-based tests
│   ├── unit/
│   └── integration/
└── _ARCHIVE_BEFORE_REBUILD/  # Complete backup of original projects
```

## Getting Started

### Prerequisites

- Python 3.10+
- Basic Python knowledge (variables, functions, classes)
- Text editor or IDE (VS Code recommended)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd AI-Knowledge-Base

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Start Learning

1. **Begin with Chapter 1**: `curriculum/chapters/phase-0-foundations/chapter-01-environment-setup.md`
2. **Follow the progression**: Each chapter builds on previous ones
3. **Complete the exercises**: Hands-on practice is essential
4. **Run the tests**: Verify your understanding with property-based tests
5. **Build incrementally**: By Chapter 54, you'll have a complete system

## Technology Stack

### Core Frameworks
- **LangChain**: Chains, agents, memory, callbacks
- **LangGraph**: Stateful workflows and complex agent systems
- **LlamaIndex**: Advanced indexing and query engines
- **Pydantic**: Data validation and settings management

### AI/ML Libraries
- **OpenAI**: GPT models
- **Anthropic**: Claude models
- **Sentence Transformers**: Embeddings
- **Chroma**: Vector store
- **Ollama**: Local model serving

### Testing
- **pytest**: Unit and integration tests
- **Hypothesis**: Property-based testing

### Multi-Agent Frameworks
- **CrewAI**: Team-based workflows
- **AutoGen**: Iterative agent conversations

## Learning Paths

### Path 1: Rapid Implementation (4-6 weeks)
Follow chapters 1-30, then jump to chapters 49-54 for Civil Engineering application.

### Path 2: Comprehensive (8-10 weeks)
Complete all 54 chapters sequentially for deep understanding.

### Path 3: Framework Focus
- LangChain: Ch 1-30
- LangGraph: Ch 31-34
- LlamaIndex: Ch 35-38
- Multi-Agent: Ch 43-48

## Project Phases (Part 2 - Parallel Waves)

After completing the curriculum structure, implementation follows in 5 waves:

**Wave 1**: Ch 7-12 (LLM Fundamentals)
**Wave 2**: Ch 13-22 (Embeddings & RAG)
**Wave 3**: Ch 23-30 (LangChain & Agents)
**Wave 4**: Ch 31-42 (Advanced Topics)
**Wave 5**: Ch 43-54 (Multi-Agent & Civil Engineering)

Each wave: Write chapters → Implement examples → Verify learning

## Contributing

This is a learning project. If you find errors or have suggestions:
1. Document the issue with chapter reference
2. Propose improvements with code examples
3. Test your changes with property-based tests

## Credits

This curriculum merges best practices from:
- **AITEA Project**: Multi-provider LLM system, property-based testing, OTAR agent pattern
- **Contract Generator Project**: Excellent pedagogical approach, Pydantic models, Civil Engineering templates

## License

[To be determined]

## Support

For questions or feedback about the curriculum:
- Review the chapter's "Troubleshooting FAQ" section
- Check `curriculum/references/` for additional materials
- Run property tests to verify your understanding

---

**Ready to start your AI Engineering journey? Begin with Chapter 1!** 🚀
