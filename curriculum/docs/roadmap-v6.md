# AI Knowledge Base Curriculum Roadmap v6
## Zero-to-Hero: 54 Chapters, 10 Phases, 71 Hours

**Last Updated**: 2026-01-16
**Version**: 6.0
**Teaching Style**: Cafe-style casual with progressive complexity
**Implementation Approach**: Modified scaffold (examples + starter code)

---

## Overview

This curriculum takes you from basic Python knowledge to building production-ready AI systems. You'll learn by creating a **Civil Engineering Document System** that generates Contracts, Proposals, and Technical Reports.

### Learning Progression
- **Chapters 1-30**: Universal examples (movies, restaurants, FAQs, chatbots)
- **Chapters 31-54**: Apply to Civil Engineering (contracts, proposals, reports)

### Teaching Philosophy
- Start with **why** before **how**
- Progressive complexity (simplest → advanced)
- Hands-on with runnable code at every step
- Property-based testing for correctness
- Real-world patterns over toy examples

---

## Phase 0: Foundations (Chapters 1-6) 🏗️
**Time**: 9 hours total | **Status**: ✅ PRESERVED from Contract project

### Chapter 1: Environment Setup & Project Initialization
**Time**: 1.5 hours | **Type**: Foundation | **Difficulty**: ⭐

**What You'll Build**: A properly configured Python development environment with virtual environments, dependency management, and VS Code integration.

**Learning Objectives**:
- Set up Python 3.10+ with virtual environments
- Configure VS Code for Python development
- Install and manage dependencies with pip
- Understand project structure best practices
- Set up git version control

**Prerequisites**: None (absolute beginner)

**Builds Toward**: Every subsequent chapter

**Key Concepts**: Virtual environments, requirements.txt, .env files, .gitignore

---

### Chapter 2: Enums & Type Hints
**Time**: 1.5 hours | **Type**: Foundation | **Difficulty**: ⭐

**What You'll Build**: A type-safe document classification system using Python's type hints and Enums.

**Learning Objectives**:
- Master Python type hints (str, int, List, Dict, Optional, Union)
- Create and use Enum classes for constrained choices
- Understand type safety benefits
- Use mypy for type checking
- Apply Literal types

**Prerequisites**: Chapter 1

**Builds Toward**: Pydantic models (Ch 3-4), all type-safe code

**Key Concepts**: Type annotations, Enum, Literal, type checking, IDE autocomplete

---

### Chapter 3: Pydantic Models (Core)
**Time**: 2 hours | **Type**: Foundation | **Difficulty**: ⭐⭐

**What You'll Build**: Data models for a movie review system with automatic validation.

**Learning Objectives**:
- Create Pydantic BaseModel classes
- Implement automatic validation
- Use Field() for constraints and metadata
- Understand model_dump() and model_dump_json()
- Handle validation errors gracefully

**Prerequisites**: Chapter 2 (type hints, enums)

**Builds Toward**: All data modeling, LLM structured output (Ch 11, 24)

**Key Concepts**: BaseModel, Field, validators, data serialization

---

### Chapter 4: Pydantic Advanced & Structured Output
**Time**: 2 hours | **Type**: Foundation | **Difficulty**: ⭐⭐

**What You'll Build**: Complex nested data models for a restaurant menu system with custom validators.

**Learning Objectives**:
- Create nested Pydantic models
- Implement custom validators (@field_validator, @model_validator)
- Use computed fields (@computed_field)
- Configure model behavior with ConfigDict
- Parse JSON into models

**Prerequisites**: Chapter 3 (Pydantic core)

**Builds Toward**: LLM structured output (Ch 11), complex domain models

**Key Concepts**: Nested models, validators, computed fields, JSON parsing

---

### Chapter 5: Validation Utilities
**Time**: 1.5 hours | **Type**: Foundation | **Difficulty**: ⭐⭐

**What You'll Build**: Reusable validation functions for common patterns (emails, URLs, dates, file paths).

**Learning Objectives**:
- Create custom validation functions
- Use regex for pattern matching
- Validate file paths and URLs
- Handle validation errors with Result type
- Build a validation utility library

**Prerequisites**: Chapter 3-4 (Pydantic)

**Builds Toward**: All input validation, error handling (Ch 40)

**Key Concepts**: Regex, validation patterns, error handling, utility functions

---

### Chapter 6: Template System
**Time**: 1.5 hours | **Type**: Foundation | **Difficulty**: ⭐⭐

**What You'll Build**: A YAML-based template system for generating documents with variable substitution.

**Learning Objectives**:
- Load and parse YAML templates
- Implement variable substitution
- Create a template registry
- Validate template structure
- Generate documents from templates

**Prerequisites**: Chapters 3-5 (Pydantic, validation)

**Builds Toward**: Document generation (Ch 24, 49-54)

**Key Concepts**: YAML, Jinja2 templates, template engines, placeholders

---

## Phase 1: LLM Fundamentals (Chapters 7-12) 🤖
**Time**: 9 hours total | **Status**: 🆕 NEW - To be created

### Chapter 7: Your First LLM Call
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐

**What You'll Build**: A simple chatbot that answers questions about movies using OpenAI's API.

**Learning Objectives**:
- Make your first LLM API call
- Understand prompts, completions, and tokens
- Handle API keys securely with .env
- Parse LLM responses
- Understand temperature and max_tokens parameters

**Prerequisites**: Chapter 1 (environment setup)

**Builds Toward**: All LLM-powered features

**Key Concepts**: API calls, prompts, completions, tokens, parameters

**Correctness Properties**: [P1: API credentials validation]

---

### Chapter 8: Multi-Provider LLM Client
**Time**: 2 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: An LLM client that works with OpenAI, Anthropic, Groq, and Ollama using a unified interface.

**Learning Objectives**:
- Create a provider abstraction layer
- Implement the Strategy pattern
- Support multiple LLM providers
- Add fallback logic (OpenAI → Groq → Ollama)
- Handle provider-specific errors

**Prerequisites**: Chapter 7 (first LLM call)

**Builds Toward**: Production LLM systems (Ch 40-42)

**Key Concepts**: Abstraction, Strategy pattern, fallback chains, error handling

**Correctness Properties**: [P2: Provider fallback correctness, P3: Response format consistency]

---

### Chapter 9: Prompt Engineering Basics
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: A prompt template system with variable substitution and few-shot examples.

**Learning Objectives**:
- Structure effective prompts
- Use system/user/assistant message roles
- Implement few-shot learning
- Create reusable prompt templates
- Understand prompt engineering best practices

**Prerequisites**: Chapter 7-8 (LLM basics)

**Builds Toward**: All LLM applications, agents (Ch 26-30)

**Key Concepts**: Prompt engineering, few-shot learning, message roles, templates

**Correctness Properties**: [P4: Prompt template variable substitution]

---

### Chapter 10: Streaming Responses
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: A streaming chatbot that displays responses word-by-word like ChatGPT.

**Learning Objectives**:
- Understand streaming vs non-streaming APIs
- Implement streaming response handlers
- Create progress indicators
- Handle streaming errors
- Build a streaming CLI interface

**Prerequisites**: Chapter 8 (multi-provider client)

**Builds Toward**: Interactive UIs (Ch 45-47), real-time applications

**Key Concepts**: Streaming, generators, callbacks, async/await

**Correctness Properties**: [P5: Stream chunk ordering, P6: Complete response reconstruction]

---

### Chapter 11: Structured Output with Pydantic
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: An LLM that extracts structured data (restaurant info) from unstructured text.

**Learning Objectives**:
- Extract structured data from LLM responses
- Use JSON mode and function calling
- Validate LLM output with Pydantic
- Handle extraction failures
- Implement retry logic for malformed outputs

**Prerequisites**: Chapter 4 (Pydantic advanced), Chapter 8 (LLM client)

**Builds Toward**: Document generation (Ch 24), extraction chains (Ch 18-19)

**Key Concepts**: Structured output, JSON mode, function calling, output validation

**Correctness Properties**: [P7: Schema adherence, P8: Required field extraction]

---

### Chapter 12: Error Handling & Retries
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: Robust error handling for LLM calls with exponential backoff and circuit breakers.

**Learning Objectives**:
- Handle common LLM API errors (rate limits, timeouts, invalid requests)
- Implement exponential backoff
- Use the Result type for error handling
- Add circuit breakers
- Log errors effectively

**Prerequisites**: Chapter 5 (validation), Chapter 8 (LLM client)

**Builds Toward**: Production systems (Ch 40-42)

**Key Concepts**: Error handling, retries, exponential backoff, circuit breakers, logging

**Correctness Properties**: [P9: Retry count limits, P10: Circuit breaker state transitions]

---

## Phase 2: Embeddings & Vectors (Chapters 13-16) 📊
**Time**: 6 hours total | **Status**: 🆕 NEW

### Chapter 13: Understanding Embeddings
**Time**: 1.5 hours | **Type**: Concept + Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: A semantic search system for movie descriptions using embeddings.

**Learning Objectives**:
- Understand what embeddings are (vectors representing meaning)
- Generate embeddings with OpenAI and Sentence Transformers
- Calculate cosine similarity
- Perform semantic search
- Visualize embeddings (optional: t-SNE/UMAP)

**Prerequisites**: Chapter 8 (LLM client)

**Builds Toward**: Vector stores (Ch 14), RAG (Ch 17-22)

**Key Concepts**: Embeddings, vectors, cosine similarity, semantic search

**Correctness Properties**: [P11: Embedding dimension consistency, P12: Similarity symmetry]

---

### Chapter 14: Vector Stores with Chroma
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: A persistent vector store for searching through a movie database.

**Learning Objectives**:
- Set up ChromaDB
- Store documents with embeddings
- Perform similarity search
- Add metadata filtering
- Persist vector stores to disk

**Prerequisites**: Chapter 13 (embeddings)

**Builds Toward**: RAG systems (Ch 17-22)

**Key Concepts**: Vector databases, ChromaDB, persistence, metadata filtering

**Correctness Properties**: [P13: Retrieval relevance, P14: Persistence correctness]

---

### Chapter 15: Chunking Strategies
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: Four different document chunking strategies (FixedSize, Recursive, Semantic, Sentence).

**Learning Objectives**:
- Understand why chunking matters
- Implement FixedSize chunking
- Implement RecursiveCharacterTextSplitter
- Implement Semantic chunking
- Implement Sentence-based chunking
- Compare strategies with examples

**Prerequisites**: Chapter 13-14 (embeddings, vectors)

**Builds Toward**: RAG optimization (Ch 21-22)

**Key Concepts**: Chunking, token limits, context windows, chunk overlap

**Correctness Properties**: [P15: Chunk size limits, P16: Overlap correctness]

---

### Chapter 16: Document Loaders
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: Loaders for PDF, DOCX, HTML, and Markdown documents.

**Learning Objectives**:
- Load PDFs with PyPDF
- Extract text from DOCX files
- Parse HTML with BeautifulSoup
- Load Markdown files
- Handle encoding issues
- Extract metadata from documents

**Prerequisites**: Chapter 15 (chunking)

**Builds Toward**: RAG with real documents (Ch 17-22)

**Key Concepts**: Document parsing, metadata extraction, encoding

**Correctness Properties**: [P17: Text extraction completeness, P18: Metadata preservation]

---

## Phase 3: RAG Fundamentals (Chapters 17-22) 🔍
**Time**: 9 hours total | **Status**: 🆕 NEW

### Chapter 17: Your First RAG System
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: A simple RAG chatbot that answers questions about a movie knowledge base.

**Learning Objectives**:
- Understand the RAG pattern (Retrieve → Augment → Generate)
- Build a basic RAG pipeline
- Combine retrieval with LLM generation
- Handle "I don't know" cases
- Cite sources in responses

**Prerequisites**: Chapter 14 (vector stores), Chapter 8 (LLM client)

**Builds Toward**: Advanced RAG (Ch 19-22)

**Key Concepts**: RAG pattern, retrieval, context augmentation, citations

**Correctness Properties**: [P19: Source citation accuracy, P20: Retrieval-generation consistency]

---

### Chapter 18: LangChain Expression Language (LCEL)
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: RAG chains using LCEL's pipe operator for composable workflows.

**Learning Objectives**:
- Understand LCEL syntax and philosophy
- Chain components with pipe operator
- Use RunnablePassthrough for data flow
- Implement parallel execution
- Add fallback chains

**Prerequisites**: Chapter 17 (RAG basics)

**Builds Toward**: Complex chains (Ch 19-22)

**Key Concepts**: LCEL, Runnables, chaining, composition

**Correctness Properties**: [P21: Chain execution order, P22: Data passthrough correctness]

---

### Chapter 19: Retrieval Strategies
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Advanced retrievers (MultiQueryRetriever, ContextualCompressionRetriever, EnsembleRetriever).

**Learning Objectives**:
- Generate multiple query variations
- Compress retrieved context
- Combine dense and sparse retrieval (hybrid search)
- Rerank results
- Optimize retrieval for different use cases

**Prerequisites**: Chapter 17-18 (RAG, LCEL)

**Builds Toward**: Production RAG (Ch 21-22)

**Key Concepts**: Query expansion, contextual compression, hybrid search, reranking

**Correctness Properties**: [P23: Query variation diversity, P24: Compression retention]

---

### Chapter 20: Conversational RAG
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: A chatbot that remembers conversation history and uses it for retrieval.

**Learning Objectives**:
- Implement conversation memory
- Rewrite follow-up questions with context
- Build a conversational retrieval chain
- Handle pronoun resolution
- Manage conversation history

**Prerequisites**: Chapter 18 (LCEL)

**Builds Toward**: Multi-turn agents (Ch 26-30)

**Key Concepts**: Conversation memory, context tracking, query rewriting

**Correctness Properties**: [P25: Context continuity, P26: Pronoun resolution]

---

### Chapter 21: RAG Evaluation
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: An evaluation framework for RAG systems measuring retrieval quality and generation faithfulness.

**Learning Objectives**:
- Measure retrieval recall and precision
- Evaluate answer faithfulness
- Detect hallucinations
- Use RAGAS framework
- Create evaluation datasets

**Prerequisites**: Chapter 17-20 (RAG systems)

**Builds Toward**: Production evaluation (Ch 40)

**Key Concepts**: Retrieval metrics, faithfulness, hallucination detection, RAGAS

**Correctness Properties**: [P27: Metric calculation correctness, P28: Faithfulness scoring]

---

### Chapter 22: Advanced RAG Patterns
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Parent Document Retriever, Auto-merging Retriever, and Multi-vector Retriever.

**Learning Objectives**:
- Retrieve parent documents for better context
- Auto-merge related chunks
- Store multiple embeddings per document
- Implement hypothetical document embeddings (HyDE)
- Choose patterns for different use cases

**Prerequisites**: Chapter 19 (retrieval strategies)

**Builds Toward**: LlamaIndex advanced patterns (Ch 36-38)

**Key Concepts**: Parent retriever, auto-merging, multi-vector, HyDE

**Correctness Properties**: [P29: Parent-child relationship integrity, P30: Merge boundary detection]

---

## Phase 4: LangChain Core (Chapters 23-25) ⛓️
**Time**: 4.5 hours total | **Status**: 🆕 NEW

### Chapter 23: LangChain Document Loaders & Text Splitters
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: LangChain-based document processing pipeline with various loaders and splitters.

**Learning Objectives**:
- Use LangChain's built-in document loaders
- Compare text splitters (Character, Recursive, Token-based)
- Handle metadata in documents
- Build a preprocessing pipeline
- Benchmark splitter performance

**Prerequisites**: Chapter 16 (document loaders), Chapter 15 (chunking)

**Builds Toward**: RAG workflows (Ch 17-22)

**Key Concepts**: LangChain loaders, text splitters, document transformers

**Correctness Properties**: [P16: Overlap correctness, P31: Metadata propagation]

---

### Chapter 24: Memory & Callbacks
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: Conversation memory systems and custom callbacks for logging/monitoring.

**Learning Objectives**:
- Implement ConversationBufferMemory
- Use ConversationSummaryMemory
- Create custom callbacks
- Track token usage
- Build a conversation logger

**Prerequisites**: Chapter 20 (conversational RAG)

**Builds Toward**: Agents (Ch 26-30), observability (Ch 41)

**Key Concepts**: Memory types, callbacks, event handlers, token tracking

**Correctness Properties**: [P25: Context continuity, P32: Callback execution order]

---

### Chapter 25: Output Parsers
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: Custom output parsers for structured data extraction from LLM responses.

**Learning Objectives**:
- Use PydanticOutputParser
- Implement StructuredOutputParser
- Create custom output parsers
- Handle parsing errors
- Combine parsers with LCEL chains

**Prerequisites**: Chapter 4 (Pydantic advanced), Chapter 11 (structured output)

**Builds Toward**: Agents (Ch 26-30), document generation (Ch 49-54)

**Key Concepts**: Output parsing, format instructions, error handling

**Correctness Properties**: [P7: Schema adherence, P33: Parse error recovery]

---

## Phase 5: Agents (Chapters 26-30) 🤖
**Time**: 7.5 hours total | **Status**: 🆕 NEW

### Chapter 26: Introduction to Agents
**Time**: 1.5 hours | **Type**: Concept + Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: Your first agent that uses tools to answer questions (calculator, search).

**Learning Objectives**:
- Understand what agents are (LLMs with tools)
- Create simple tools
- Build a zero-shot agent
- Understand the agent loop (reason → act → observe)
- Handle agent errors

**Prerequisites**: Chapter 18 (LCEL)

**Builds Toward**: ReAct (Ch 27), complex agents (Ch 28-30)

**Key Concepts**: Agents, tools, agent loop, zero-shot reasoning

**Correctness Properties**: [P34: Tool call validity, P35: Agent loop termination]

---

### Chapter 27: ReAct Pattern
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: A ReAct agent that reasons about which tools to use and interprets results.

**Learning Objectives**:
- Understand ReAct (Reasoning + Acting)
- Implement the ReAct loop
- Create a ReAct prompt template
- Parse thought/action/observation
- Build a debugging agent

**Prerequisites**: Chapter 26 (agents intro)

**Builds Toward**: Complex workflows (Ch 31-34)

**Key Concepts**: ReAct, thought/action/observation, reasoning traces

**Correctness Properties**: [P36: Reasoning trace completeness, P37: Action validity]

---

### Chapter 28: OTAR Loop Pattern
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: An Observe-Think-Act-Reflect agent for iterative problem solving.

**Learning Objectives**:
- Understand the OTAR pattern
- Implement state transitions
- Add reflection for learning
- Track agent state history
- Build a self-improving agent

**Prerequisites**: Chapter 27 (ReAct)

**Builds Toward**: Complex agent systems (Ch 43-48)

**Key Concepts**: OTAR, state machines, reflection, iterative improvement

**Correctness Properties**: [P38: State transition validity, P39: Reflection integration]

---

### Chapter 29: Tool Calling & Function Calling
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: A tool registry with function calling support for GPT-4 and Claude.

**Learning Objectives**:
- Understand tool/function calling APIs
- Create tool schemas
- Implement tool execution
- Handle tool errors
- Build a tool registry pattern

**Prerequisites**: Chapter 26 (agents intro)

**Builds Toward**: Multi-tool agents (Ch 43-48)

**Key Concepts**: Function calling, tool schemas, JSON schemas, tool registry

**Correctness Properties**: [P34: Tool call validity, P40: Schema validation]

---

### Chapter 30: Agent Memory & Context Management
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Agents with long-term memory and context pruning strategies.

**Learning Objectives**:
- Implement agent memory
- Prune context to fit token limits
- Use vector store for long-term memory
- Implement relevance-based retrieval
- Build a memory-augmented agent

**Prerequisites**: Chapter 24 (memory), Chapter 26-27 (agents)

**Builds Toward**: Complex agents (Ch 43-48)

**Key Concepts**: Agent memory, context pruning, long-term memory, retrieval

**Correctness Properties**: [P25: Context continuity, P41: Memory retrieval relevance]

---

## Phase 6: LangGraph (Chapters 31-34) 📈
**Time**: 6 hours total | **Status**: 🆕 NEW

### Chapter 31: LangGraph State Machines
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: A state graph for a document review workflow with multiple steps.

**Learning Objectives**:
- Understand LangGraph's state graph model
- Define states and transitions
- Create nodes and edges
- Compile and run graphs
- Visualize workflows

**Prerequisites**: Chapter 27-28 (ReAct, OTAR)

**Builds Toward**: Complex workflows (Ch 32-34)

**Key Concepts**: State graphs, nodes, edges, state management

**Correctness Properties**: [P38: State transition validity, P42: Graph execution correctness]

---

### Chapter 32: Conditional Routing
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Dynamic workflows that route based on conditions (if quality score > 0.8, approve; else, revise).

**Learning Objectives**:
- Implement conditional edges
- Route based on state
- Handle branching logic
- Create decision nodes
- Build a quality control workflow

**Prerequisites**: Chapter 31 (LangGraph basics)

**Builds Toward**: Complex agent systems (Ch 43-48)

**Key Concepts**: Conditional routing, branching, decision logic

**Correctness Properties**: [P43: Routing condition evaluation, P44: Branch coverage]

---

### Chapter 33: Human-in-the-Loop Workflows
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Workflows that pause for human approval before critical actions.

**Learning Objectives**:
- Implement interrupt points
- Save and resume workflow state
- Get human feedback
- Implement approval gates
- Build a contract review workflow

**Prerequisites**: Chapter 31-32 (LangGraph)

**Builds Toward**: Production workflows (Ch 49-54)

**Key Concepts**: Human-in-the-loop, interrupts, state persistence, approval gates

**Correctness Properties**: [P45: State persistence across interrupts, P46: Resume correctness]

---

### Chapter 34: Persistent State with Checkpoints
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Workflows that save checkpoints and can recover from failures.

**Learning Objectives**:
- Implement checkpoint persistence
- Save to disk/database
- Recover from failures
- Time-travel debugging
- Build a resilient workflow

**Prerequisites**: Chapter 33 (human-in-the-loop)

**Builds Toward**: Production systems (Ch 40-42)

**Key Concepts**: Checkpointing, persistence, failure recovery, time-travel

**Correctness Properties**: [P45: State persistence, P47: Recovery completeness]

---

## Phase 7: LlamaIndex (Chapters 35-38) 🦙
**Time**: 6 hours total | **Status**: 🆕 NEW

### Chapter 35: LlamaIndex Fundamentals
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐

**What You'll Build**: A LlamaIndex-based Q&A system over documents.

**Learning Objectives**:
- Understand LlamaIndex architecture
- Create Document and Node objects
- Build a VectorStoreIndex
- Query the index
- Compare with LangChain

**Prerequisites**: Chapter 14 (vector stores), Chapter 17 (RAG)

**Builds Toward**: Advanced indexing (Ch 36-38)

**Key Concepts**: LlamaIndex, Documents, Nodes, VectorStoreIndex

**Correctness Properties**: [P48: Index construction correctness, P49: Query response relevance]

---

### Chapter 36: Query Engines & Response Synthesis
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Custom query engines with different response synthesis modes.

**Learning Objectives**:
- Use different query engines (VectorIndex, Summary, Tree, Keyword)
- Implement response synthesis modes (compact, refine, tree_summarize)
- Add query transformations
- Implement streaming responses
- Build a multi-modal query engine

**Prerequisites**: Chapter 35 (LlamaIndex basics)

**Builds Toward**: Advanced RAG (Ch 37-38)

**Key Concepts**: Query engines, response synthesis, query transformations

**Correctness Properties**: [P50: Synthesis mode correctness, P51: Query transformation accuracy]

---

### Chapter 37: Advanced Indexing
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Multi-index systems (Summary Index, Tree Index, Knowledge Graph).

**Learning Objectives**:
- Build Summary Index for quick overviews
- Create Tree Index for hierarchical data
- Implement Knowledge Graph Index
- Combine multiple indexes
- Choose the right index for use cases

**Prerequisites**: Chapter 35-36 (LlamaIndex)

**Builds Toward**: Complex knowledge bases (Ch 49-54)

**Key Concepts**: Index types, hierarchical indexing, knowledge graphs

**Correctness Properties**: [P52: Index type appropriateness, P53: Multi-index query routing]

---

### Chapter 38: Hybrid Search & Reranking
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Hybrid search combining BM25 (keyword) and vector similarity with reranking.

**Learning Objectives**:
- Implement BM25 search
- Combine with vector search
- Add cross-encoder reranking
- Tune fusion parameters
- Benchmark retrieval quality

**Prerequisites**: Chapter 19 (retrieval strategies), Chapter 36 (query engines)

**Builds Toward**: Production RAG (Ch 40-42)

**Key Concepts**: Hybrid search, BM25, fusion, reranking, cross-encoders

**Correctness Properties**: [P23: Query variation diversity, P54: Reranking score monotonicity]

---

## Phase 8: Production (Chapters 39-42) 🚀
**Time**: 6 hours total | **Status**: 🆕 NEW

### Chapter 39: Testing AI Systems with Hypothesis
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Property-based tests for LLM systems using Hypothesis.

**Learning Objectives**:
- Understand property-based testing
- Use Hypothesis strategies
- Define correctness properties
- Test LLM systems
- Build test suites

**Prerequisites**: All previous chapters

**Builds Toward**: Quality assurance (Ch 40-42)

**Key Concepts**: Property-based testing, Hypothesis, invariants, test strategies

**Correctness Properties**: ALL 40+ properties tested

---

### Chapter 40: Evaluation with LangSmith
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Evaluation pipelines using LangSmith for LLM systems.

**Learning Objectives**:
- Set up LangSmith
- Create evaluation datasets
- Define metrics and evaluators
- Run evaluations
- Compare model versions

**Prerequisites**: Chapter 21 (RAG evaluation)

**Builds Toward**: Production monitoring (Ch 41-42)

**Key Concepts**: LangSmith, evaluation, metrics, datasets

**Correctness Properties**: [P27: Metric calculation correctness, P55: Evaluation reproducibility]

---

### Chapter 41: Error Handling, Security & Observability
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Production-grade error handling, prompt injection defense, and logging.

**Learning Objectives**:
- Implement comprehensive error handling
- Defend against prompt injection
- Add input sanitization
- Build logging and tracing
- Monitor LLM systems

**Prerequisites**: Chapter 12 (error handling)

**Builds Toward**: Production deployment (Ch 42)

**Key Concepts**: Error handling, security, prompt injection, logging, observability

**Correctness Properties**: [P9: Retry limits, P56: Security validation]

---

### Chapter 42: Token Management & Cost Optimization
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Token counting, cost tracking, and optimization strategies.

**Learning Objectives**:
- Count tokens with tiktoken
- Track API costs
- Optimize prompts for tokens
- Implement caching strategies
- Choose cost-effective models

**Prerequisites**: Chapter 8 (multi-provider)

**Builds Toward**: Production systems (Ch 49-54)

**Key Concepts**: Token counting, cost tracking, optimization, caching

**Correctness Properties**: [P57: Token count accuracy, P58: Cost calculation correctness]

---

## Phase 9: Multi-Agent Systems (Chapters 43-48) 👥
**Time**: 9 hours total | **Status**: 🆕 NEW

### Chapter 43: Multi-Agent Fundamentals
**Time**: 1.5 hours | **Type**: Concept + Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: A two-agent system (researcher + writer) that collaborates.

**Learning Objectives**:
- Understand multi-agent patterns (Anthropic's 5 patterns)
- Implement agent communication
- Coordinate between agents
- Handle agent conflicts
- Build a basic workflow

**Prerequisites**: Chapter 26-30 (agents)

**Builds Toward**: Complex multi-agent systems (Ch 44-48)

**Key Concepts**: Multi-agent systems, communication, coordination, workflows

**Correctness Properties**: [P59: Message passing correctness, P60: Agent state consistency]

---

### Chapter 44: CrewAI for Team-Based Workflows
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: A CrewAI team (PM, researcher, analyst, writer) for document creation.

**Learning Objectives**:
- Set up CrewAI
- Define agents with roles
- Create tasks
- Assign tasks to agents
- Run crew workflows

**Prerequisites**: Chapter 43 (multi-agent basics)

**Builds Toward**: Document generation (Ch 49-54)

**Key Concepts**: CrewAI, roles, tasks, crews, delegation

**Correctness Properties**: [P61: Task assignment validity, P62: Crew execution order]

---

### Chapter 45: AutoGen for Iterative Refinement
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: AutoGen agents that iteratively refine a document through conversation.

**Learning Objectives**:
- Set up AutoGen
- Create conversable agents
- Implement group chat
- Add termination conditions
- Build refinement loops

**Prerequisites**: Chapter 43 (multi-agent basics)

**Builds Toward**: Quality assurance workflows (Ch 49-54)

**Key Concepts**: AutoGen, conversable agents, group chat, termination

**Correctness Properties**: [P63: Conversation termination, P64: Refinement convergence]

---

### Chapter 46: Supervisor Pattern
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: A supervisor agent that orchestrates worker agents.

**Learning Objectives**:
- Implement the supervisor pattern
- Route tasks to workers
- Aggregate worker results
- Handle worker failures
- Build hierarchical agent systems

**Prerequisites**: Chapter 31-34 (LangGraph), Chapter 43 (multi-agent)

**Builds Toward**: Complex workflows (Ch 49-54)

**Key Concepts**: Supervisor pattern, orchestration, hierarchies, delegation

**Correctness Properties**: [P65: Task routing correctness, P66: Result aggregation]

---

### Chapter 47: Agent Communication Protocols
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Message passing and shared memory for agent communication.

**Learning Objectives**:
- Implement message queues
- Use shared memory/state
- Add event-driven communication
- Handle asynchronous agents
- Build agent networks

**Prerequisites**: Chapter 43-46 (multi-agent patterns)

**Builds Toward**: Large-scale systems (Ch 49-54)

**Key Concepts**: Message passing, shared state, events, async

**Correctness Properties**: [P59: Message passing, P67: Shared state consistency]

---

### Chapter 48: Debugging Multi-Agent Systems
**Time**: 1.5 hours | **Type**: Implementation | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Debugging tools for multi-agent workflows (trace visualization, state inspection).

**Learning Objectives**:
- Trace agent interactions
- Visualize agent workflows
- Inspect agent state
- Debug deadlocks
- Profile performance

**Prerequisites**: Chapter 43-47 (multi-agent systems)

**Builds Toward**: Production multi-agent systems (Ch 49-54)

**Key Concepts**: Debugging, tracing, visualization, profiling

**Correctness Properties**: [P68: Trace completeness, P69: State inspection accuracy]

---

## Phase 10: Civil Engineering Application (Chapters 49-54) 🏗️
**Time**: 9 hours total | **Status**: 🆕 NEW - Apply everything to real project

### Chapter 49: Civil Engineering Document Models
**Time**: 1.5 hours | **Type**: Application | **Difficulty**: ⭐⭐

**What You'll Build**: Pydantic models for Contracts, Proposals, and Technical Reports.

**Learning Objectives**:
- Model contract structure (parties, terms, clauses, exhibits)
- Model proposal structure (executive summary, technical approach, pricing)
- Model report structure (intro, methodology, analysis, conclusions)
- Add industry-specific validation
- Create template schemas

**Prerequisites**: Chapter 3-6 (Pydantic, templates)

**Builds Toward**: Document generation (Ch 50-54)

**Key Concepts**: Domain modeling, contract structure, proposal structure, report structure

**Correctness Properties**: [P70: Contract completeness, P71: Proposal structure validation]

---

### Chapter 50: Contract Generation System
**Time**: 1.5 hours | **Type**: Application | **Difficulty**: ⭐⭐⭐

**What You'll Build**: End-to-end system generating engineering contracts from requirements.

**Learning Objectives**:
- Build contract generation pipeline
- Use templates (engineering, consulting, government, military)
- Extract requirements from RFPs
- Generate contract clauses with LLMs
- Validate contract completeness

**Prerequisites**: Chapter 6 (templates), Chapter 17-22 (RAG), Chapter 26-30 (agents)

**Builds Toward**: Complete system (Ch 54)

**Key Concepts**: Contract generation, clause generation, template population

**Correctness Properties**: [P70: Contract completeness, P72: Clause consistency]

---

### Chapter 51: Proposal Generation System
**Time**: 1.5 hours | **Type**: Application | **Difficulty**: ⭐⭐⭐

**What You'll Build**: System generating technical proposals in response to RFPs/RFQs.

**Learning Objectives**:
- Parse RFP requirements
- Generate executive summary
- Create technical approach
- Calculate pricing
- Build proposal workflow

**Prerequisites**: Chapter 44-46 (multi-agent), Chapter 50 (contract generation)

**Builds Toward**: Complete system (Ch 54)

**Key Concepts**: RFP parsing, proposal structure, technical writing, pricing

**Correctness Properties**: [P71: Proposal structure, P73: Requirement coverage]

---

### Chapter 52: Technical Report Generation System
**Time**: 1.5 hours | **Type**: Application | **Difficulty**: ⭐⭐⭐

**What You'll Build**: System generating engineering analysis reports with calculations and visualizations.

**Learning Objectives**:
- Generate report structure
- Include calculations and analysis
- Add charts and visualizations
- Cite engineering standards
- Build report workflow

**Prerequisites**: Chapter 44-46 (multi-agent), Chapter 50-51 (document generation)

**Builds Toward**: Complete system (Ch 54)

**Key Concepts**: Report structure, technical writing, calculations, visualizations

**Correctness Properties**: [P74: Calculation accuracy, P75: Visualization correctness]

---

### Chapter 53: Compliance Review Agent
**Time**: 1.5 hours | **Type**: Application | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Agent that reviews documents for regulatory compliance and standards adherence.

**Learning Objectives**:
- Build compliance checker
- Check against regulations (FAR, OSHA, ASCE standards)
- Identify missing requirements
- Generate compliance reports
- Suggest corrections

**Prerequisites**: Chapter 26-30 (agents), Chapter 50-52 (document generation)

**Builds Toward**: Complete system (Ch 54)

**Key Concepts**: Compliance checking, regulatory review, standards validation

**Correctness Properties**: [P76: Compliance rule coverage, P77: Violation detection]

---

### Chapter 54: Complete Civil Engineering Document System
**Time**: 1.5 hours | **Type**: Capstone | **Difficulty**: ⭐⭐⭐

**What You'll Build**: Integrated system with UI for generating and reviewing all document types.

**Learning Objectives**:
- Integrate all components
- Build Streamlit UI
- Add version control
- Implement export (PDF, DOCX)
- Deploy the system

**Prerequisites**: ALL previous chapters

**Builds Toward**: Real-world deployment

**Key Concepts**: System integration, UI, version control, export, deployment

**Correctness Properties**: [P78: End-to-end workflow, P79: Export format correctness]

---

## Dependency Map

```
Phase 0 (Ch 1-6) ─┐
                  ├─→ Phase 1 (Ch 7-12) ─┐
                  │                       ├─→ Phase 2 (Ch 13-16) ─┐
                  │                       │                        ├─→ Phase 3 (Ch 17-22) ─┐
                  │                       │                        │                        ├─→ Phase 4 (Ch 23-25) ─┐
                  │                       │                        │                        │                        ├─→ Phase 5 (Ch 26-30) ─┐
                  │                       │                        │                        │                        │                        ├─→ Phase 6 (Ch 31-34) ─┐
                  │                       │                        │                        │                        │                        │                        ├─→ Phase 7 (Ch 35-38) ─┐
                  │                       │                        │                        │                        │                        │                        │                        ├─→ Phase 8 (Ch 39-42) ─┐
                  │                       │                        │                        │                        │                        │                        │                        │                        ├─→ Phase 9 (Ch 43-48) ─┐
                  │                       │                        │                        │                        │                        │                        │                        │                        │                        └─→ Phase 10 (Ch 49-54)
```

---

## Property-Based Testing Coverage

**40+ Correctness Properties Validated Across Curriculum**:

| Property | Description | Chapters |
|----------|-------------|----------|
| P1 | API credentials validation | 7 |
| P2 | Provider fallback correctness | 8 |
| P3 | Response format consistency | 8 |
| P4 | Prompt template variable substitution | 9 |
| P5 | Stream chunk ordering | 10 |
| P6 | Complete response reconstruction | 10 |
| P7 | Schema adherence | 11, 25 |
| P8 | Required field extraction | 11 |
| P9 | Retry count limits | 12, 41 |
| P10 | Circuit breaker state transitions | 12 |
| P11 | Embedding dimension consistency | 13 |
| P12 | Similarity symmetry | 13 |
| P13 | Retrieval relevance | 14 |
| P14 | Persistence correctness | 14 |
| P15 | Chunk size limits | 15 |
| P16 | Overlap correctness | 15, 23 |
| P17 | Text extraction completeness | 16 |
| P18 | Metadata preservation | 16 |
| P19 | Source citation accuracy | 17 |
| P20 | Retrieval-generation consistency | 17 |
| P21 | Chain execution order | 18 |
| P22 | Data passthrough correctness | 18 |
| P23 | Query variation diversity | 19, 38 |
| P24 | Compression retention | 19 |
| P25 | Context continuity | 20, 24, 30 |
| P26 | Pronoun resolution | 20 |
| P27 | Metric calculation correctness | 21, 40 |
| P28 | Faithfulness scoring | 21 |
| P29 | Parent-child relationship integrity | 22 |
| P30 | Merge boundary detection | 22 |
| P31 | Metadata propagation | 23 |
| P32 | Callback execution order | 24 |
| P33 | Parse error recovery | 25 |
| P34 | Tool call validity | 26, 29 |
| P35 | Agent loop termination | 26 |
| P36 | Reasoning trace completeness | 27 |
| P37 | Action validity | 27 |
| P38 | State transition validity | 28, 31 |
| P39 | Reflection integration | 28 |
| P40 | Schema validation | 29 |
| P41 | Memory retrieval relevance | 30 |
| P42 | Graph execution correctness | 31 |
| P43 | Routing condition evaluation | 32 |
| P44 | Branch coverage | 32 |
| P45 | State persistence across interrupts | 33, 34 |
| P46 | Resume correctness | 33 |
| P47 | Recovery completeness | 34 |
| P48 | Index construction correctness | 35 |
| P49 | Query response relevance | 35 |
| P50 | Synthesis mode correctness | 36 |
| P51 | Query transformation accuracy | 36 |
| P52 | Index type appropriateness | 37 |
| P53 | Multi-index query routing | 37 |
| P54 | Reranking score monotonicity | 38 |
| P55 | Evaluation reproducibility | 40 |
| P56 | Security validation | 41 |
| P57 | Token count accuracy | 42 |
| P58 | Cost calculation correctness | 42 |
| P59 | Message passing correctness | 43, 47 |
| P60 | Agent state consistency | 43 |
| P61 | Task assignment validity | 44 |
| P62 | Crew execution order | 44 |
| P63 | Conversation termination | 45 |
| P64 | Refinement convergence | 45 |
| P65 | Task routing correctness | 46 |
| P66 | Result aggregation | 46 |
| P67 | Shared state consistency | 47 |
| P68 | Trace completeness | 48 |
| P69 | State inspection accuracy | 48 |
| P70 | Contract completeness | 49, 50 |
| P71 | Proposal structure validation | 49, 51 |
| P72 | Clause consistency | 50 |
| P73 | Requirement coverage | 51 |
| P74 | Calculation accuracy | 52 |
| P75 | Visualization correctness | 52 |
| P76 | Compliance rule coverage | 53 |
| P77 | Violation detection | 53 |
| P78 | End-to-end workflow | 54 |
| P79 | Export format correctness | 54 |

---

## Implementation Timeline (Part 2 - Parallel Waves)

### Wave 1: Foundations + LLM Fundamentals (Weeks 1-2)
**Write**: Chapters 7-12
**Implement**: Multi-provider LLM client, prompt templates, streaming, structured output
**Verify**: P1-P10 properties passing

### Wave 2: Embeddings + RAG (Weeks 3-4)
**Write**: Chapters 13-22
**Implement**: Embeddings, vector stores, chunking, RAG pipelines, evaluation
**Verify**: P11-P30 properties passing

### Wave 3: LangChain + Agents (Weeks 5-6)
**Write**: Chapters 23-30
**Implement**: LangChain tools, agents, ReAct, OTAR, memory
**Verify**: P31-P41 properties passing

### Wave 4: Advanced Frameworks (Weeks 7-8)
**Write**: Chapters 31-42
**Implement**: LangGraph, LlamaIndex, production tools, evaluation
**Verify**: P42-P58 properties passing

### Wave 5: Multi-Agent + Civil Engineering (Weeks 9-10)
**Write**: Chapters 43-54
**Implement**: Multi-agent systems, document generation, compliance
**Verify**: P59-P79 properties passing, end-to-end system

---

## File Naming Convention

```
curriculum/chapters/
  phase-0-foundations/
    chapter-01-environment-setup.md
    chapter-02-enums-type-hints.md
    ...
  phase-1-llm-fundamentals/
    chapter-07-first-llm-call.md
    chapter-08-multi-provider-client.md
    ...
  phase-10-civil-engineering/
    chapter-49-civil-eng-models.md
    chapter-50-contract-generation.md
    chapter-51-proposal-generation.md
    chapter-52-report-generation.md
    chapter-53-compliance-review.md
    chapter-54-complete-system.md
```

---

## Success Metrics

By the end of this curriculum, learners will be able to:

✅ Build production-ready LLM applications with multiple providers
✅ Implement RAG systems with advanced retrieval strategies
✅ Create agents using ReAct, OTAR, and custom patterns
✅ Build complex workflows with LangGraph
✅ Develop multi-agent systems with CrewAI and AutoGen
✅ Generate Civil Engineering documents (contracts, proposals, reports)
✅ Implement compliance checking and quality assurance
✅ Deploy and monitor AI systems in production
✅ Write property-based tests for correctness validation

**Total Learning Investment**: 71 hours → Career-ready AI Engineering skills

---

## Next Steps

1. ✅ Roadmap created (this document)
2. 🔄 Create chapter templates (Phase 3.2)
3. 🔄 Create curriculum prompt v6 (Phase 3.3)
4. 🔄 Git commit and verification (Phase 4)
5. 🔄 Begin Part 2: Parallel Waves implementation

**Ready to begin the journey? Let's build something amazing!** 🚀
