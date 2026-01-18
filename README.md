# 🏗️ AI Engineering Curriculum: Zero to Production RAG Systems

**A comprehensive 54-chapter hands-on curriculum that teaches you to build production-ready AI systems through real-world Civil Engineering applications.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Progress](https://img.shields.io/badge/chapters-19%2F54%20complete-orange.svg)](PROGRESS-SUMMARY.md)
[![Template](https://img.shields.io/badge/template-v2.1-green.svg)](curriculum/templates/)

## 🎯 What You'll Build

By the end of this curriculum, you'll have built a **complete AI-powered Civil Engineering Document System** that:

- 📄 **Processes Technical Documents**: Contracts, proposals, structural analysis reports, geotechnical investigations
- 🤖 **Uses Multiple AI Frameworks**: LangChain, LangGraph, LlamaIndex, CrewAI, AutoGen
- 🔍 **Implements Advanced RAG**: Hybrid search, semantic chunking, query rewriting, contextual compression
- 👥 **Orchestrates Multi-Agent Systems**: Supervisor patterns, team-based workflows, iterative refinement
- ✅ **Production-Ready**: Property-based testing, error handling, cost tracking, security best practices

## 🚀 Why This Curriculum?

**Learn by Building Real Systems** - Not just theory. Every chapter includes working code, automated verification, and hands-on exercises.

**Zero to Hero in 71 Hours** - Start with Python basics, end with production multi-agent systems. No AI experience required.

**Industry-Proven Patterns** - Learn from real projects: AITEA's multi-provider LLM system and Contract Generator's pedagogical approach.

**Civil Engineering Focus** - Apply AI to real-world problems: analyzing bridge load calculations, processing geotechnical reports, generating RFP responses.

## 📚 Learning Approach

### Progressive Mastery

- **Foundations First** (Ch 1-6): Python, Pydantic, type hints, configuration
- **Universal Examples** (Ch 7-30): Learn with movies, restaurants, FAQs
- **Domain Application** (Ch 31-54): Apply to Civil Engineering projects
- **Component Evolution**: Each mini-project builds toward the final system

### Pedagogical Features

- ☕ **Cafe-Style Teaching**: Conversational language with real-world analogies
- 🔨 **Modified Scaffold**: Example patterns + starter code, you complete the TODOs
- ✅ **Automated Verification**: Every chapter includes 3-5 test scripts with expected outputs
- 🧪 **Property-Based Testing**: 40+ correctness properties using Hypothesis
- 🎯 **Hands-On Exercises**: Minimum 2 "Try This!" challenges per chapter

## 📖 Curriculum Structure (54 Chapters, 10 Phases)

| Phase        | Chapters | Hours | Focus                                                |
| ------------ | -------- | ----- | ---------------------------------------------------- |
| **Phase 0**  | 1-6      | 9h    | 🔧 Foundations: Python, Pydantic, Config             |
| **Phase 1**  | 7-12     | 9h    | 🤖 LLM Fundamentals: Multi-provider clients, prompts |
| **Phase 2**  | 13-16    | 6h    | 🔍 Embeddings & Vectors: Transformers, Chroma        |
| **Phase 3**  | 17-22    | 9h    | 📚 RAG Fundamentals: Retrieval + Generation          |
| **Phase 4**  | 23-25    | 4.5h  | ⛓️ LangChain Core: Loaders, memory, callbacks        |
| **Phase 5**  | 26-30    | 7.5h  | 🎯 Agents: ReAct, OTAR, tool calling                 |
| **Phase 6**  | 31-34    | 6h    | 🕸️ LangGraph: State graphs, workflows                |
| **Phase 7**  | 35-38    | 6h    | 🦙 LlamaIndex: Query engines, hybrid search          |
| **Phase 8**  | 39-42    | 6h    | 🚀 Production: Evaluation, security, optimization    |
| **Phase 9**  | 43-48    | 9h    | 👥 Multi-Agent: CrewAI, AutoGen, teams               |
| **Phase 10** | 49-54    | 9h    | 🏗️ Civil Engineering: Complete system                |

**Total: 54 chapters, 71 hours** | **Current Progress: 19/54 chapters (30.1%)** ✅

## ✨ Key Features

### 🤖 Multi-Provider LLM Support

```python
# Seamlessly switch between providers with fallback chains
client = MultiProviderLLMClient(
    providers=[OpenAI(), Anthropic(), Groq(), Ollama()],
    fallback_strategy="graceful_degradation"
)
```

- OpenAI (GPT-3.5, GPT-4), Anthropic (Claude 3), Groq (Fast inference)
- Ollama (Local models), MockLLM (Testing)
- Automatic fallback with cost tracking

### 🔍 Advanced RAG Patterns

- **4 Chunking Strategies**: FixedSize, Recursive, Semantic, Sentence
- **Hybrid Search**: Dense (embeddings) + Sparse (BM25)
- **Query Enhancement**: Rewriting, expansion, contextual compression
- **Document Loaders**: PDF, DOCX, HTML, Markdown, CAD annotations

### 👥 Agent Frameworks

- **OTAR Loop**: Observe-Think-Act-Reflect pattern
- **ReAct**: Reasoning and Acting agents
- **LangGraph**: Complex workflows with state management
- **CrewAI**: Team-based multi-agent systems
- **AutoGen**: Iterative refinement agents

### ✅ Production-Ready

- **Testing**: Property-based testing with Hypothesis (40+ properties)
- **Reliability**: Error handling, retries, graceful degradation
- **Monitoring**: Token counting, cost tracking, LangSmith evaluation
- **Performance**: Streaming responses, async/await patterns
- **Security**: Input validation, prompt injection prevention

## 🚀 Getting Started

### Prerequisites

- Python 3.10+ installed
- Basic Python knowledge (variables, functions, classes)
- Text editor or IDE (VS Code recommended)
- 1-2 hours per chapter for learning and exercises

### Quick Start (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/AhmedTElKodsh/aitea.git
cd aitea

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (OpenAI, Anthropic, etc.)

# 5. Start with Chapter 1
# Open: curriculum/chapters/phase-0-foundations/chapter-01-environment-setup.md
```

### Learning Path

1. **📖 Read the Chapter**: Understand concepts with cafe-style explanations
2. **💻 Complete the Code**: Fill in TODOs in the starter code
3. **✅ Run Verification**: Execute automated test scripts to verify your work
4. **🎯 Try Exercises**: Complete 2+ hands-on challenges
5. **🔄 Iterate**: Each chapter builds on previous ones

**See [QUICKSTART.md](QUICKSTART.md) for detailed guidance.**

## 🎓 Learning Paths

Choose the path that fits your goals:

### 🏃 Path 1: Rapid Implementation (4-6 weeks)

**Goal**: Build a working RAG system quickly

- Complete Ch 1-30 (Foundations → Agents)
- Jump to Ch 49-54 (Civil Engineering Application)
- **Best for**: Developers who need results fast

### 🎯 Path 2: Comprehensive Mastery (8-10 weeks)

**Goal**: Deep understanding of all AI frameworks

- Complete all 54 chapters sequentially
- Master LangChain, LangGraph, LlamaIndex, Multi-Agent systems
- **Best for**: AI Engineers building production systems

### 🔧 Path 3: Framework Focus

**Goal**: Specialize in specific frameworks

- **LangChain**: Ch 1-30
- **LangGraph**: Ch 31-34
- **LlamaIndex**: Ch 35-38
- **Multi-Agent**: Ch 43-48
- **Best for**: Developers with specific framework needs

## 🛠️ Technology Stack

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

### Testing & Quality

- **pytest**: Unit and integration tests
- **Hypothesis**: Property-based testing
- **LangSmith**: Evaluation and monitoring

### Multi-Agent Frameworks

- **CrewAI**: Team-based workflows
- **AutoGen**: Iterative agent conversations

## 📂 Project Structure

```
aitea/
├── curriculum/
│   ├── chapters/          # 54 chapter markdown files
│   │   ├── phase-0-foundations/
│   │   ├── phase-1-llm-fundamentals/
│   │   └── phase-2-embeddings-vectors/
│   ├── templates/         # Chapter templates (v2.1)
│   ├── reference/         # PROJECT-THREAD.md, ce-contexts.md
│   └── docs/              # Roadmap, session summaries
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
└── requirements.txt       # Python dependencies
```

## 📊 Current Status

**Progress**: 19/54 chapters complete (30.1%) ✅  
**Latest**: Chapter 14 - Vector Stores with Chroma  
**Template**: v2.1 (100% compliance on updated chapters)  
**Quality**: All chapters include automated verification scripts

See [PROGRESS-SUMMARY.md](PROGRESS-SUMMARY.md) for detailed progress tracking.

## 🤝 Contributing

This is an active learning project. Contributions welcome!

**How to contribute:**

1. 🐛 **Report Issues**: Document errors with chapter reference
2. 💡 **Suggest Improvements**: Propose enhancements with code examples
3. ✅ **Add Tests**: Contribute property-based tests
4. 📝 **Improve Documentation**: Clarify explanations or add examples

**Quality Standards:**

- All chapters must follow [Template v2.1](curriculum/templates/MASTER-CHAPTER-TEMPLATE-V2.md)
- Include automated verification scripts
- Provide working code examples
- Test with property-based testing (Hypothesis)

## 📜 License

MIT License - See [LICENSE](LICENSE) for details

## 🙏 Credits

This curriculum merges best practices from:

- **AITEA Project**: Multi-provider LLM system, property-based testing, OTAR agent pattern
- **Contract Generator Project**: Pedagogical approach, Pydantic models, Civil Engineering templates

Built with ❤️ for the AI Engineering community.

## 📞 Support & Resources

- 📖 **Documentation**: [QUICKSTART.md](QUICKSTART.md) | [PROGRESS-SUMMARY.md](PROGRESS-SUMMARY.md)
- 🔗 **Component Evolution**: [PROJECT-THREAD.md](curriculum/reference/PROJECT-THREAD.md)
- 🏗️ **CE Examples**: [ce-contexts.md](curriculum/reference/ce-contexts.md)
- 🗺️ **Curriculum Structure**: [roadmap-v6.md](curriculum/docs/roadmap-v6.md)

## ⭐ Star This Repo

If you find this curriculum helpful, please star the repository to help others discover it!

---

<div align="center">

**🚀 Ready to start your AI Engineering journey?**

[Begin with Chapter 1](curriculum/chapters/phase-0-foundations/chapter-01-environment-setup.md) | [View Progress](PROGRESS-SUMMARY.md) | [Quick Start](QUICKSTART.md)

</div>
