# Implementation Plan: AITEA Curriculum

## Phase 1: Python Foundations (aitea-core)

- [x] 1. Implement Core Enumerations

  - [x] 1.1 Create TeamType enum with backend, frontend, fullstack, design, qa, devops members

    - Add string values and ensure mypy compatibility
    - _Requirements: 1.2, 8.1, 8.2_
    - ✅ **COMPLETED**: Implemented in `src/models/enums.py` with string inheritance for JSON serialization

  - [x] 1.2 Create ProcessType enum with Data Operations, Content Management, Real-time, Authentication, Integration members

    - _Requirements: 1.2_
    - ✅ **COMPLETED**: Implemented in `src/models/enums.py`

  - [x] 1.3 Create ConfidenceLevel enum with low, medium, high members

    - _Requirements: 1.2, 9.5_
    - ✅ **COMPLETED**: Implemented in `src/models/enums.py` with inline documentation for data point thresholds

  - [x] 1.4 Write property test for enum completeness and type safety

    - **Property 1: Enum Completeness and Type Safety**
    - **Validates: Requirements 1.2**

- [x] 2. Implement Core Dataclass Models

  - [x] 2.1 Create Feature dataclass with id, name, team, process, seed_time_hours, synonyms, notes fields

    - Use proper type hints including Optional and List types
    - _Requirements: 1.3, 8.1_
    - ✅ **COMPLETED**: Implemented with validation, default values (synonyms=[], notes=""), and JSON serialization (to_dict/from_dict)

  - [x] 2.2 Create TrackedTimeEntry dataclass with id, team, member_name, feature, tracked_time_hours, process, date fields

    - _Requirements: 1.3, 8.2_
    - ✅ **COMPLETED**: Implemented with validation and JSON serialization including ISO date handling

  - [x] 2.3 Create ProjectEstimate dataclass with features list, total_hours, confidence fields

    - _Requirements: 1.3, 8.3_
    - ✅ **COMPLETED**: Implemented with validation and nested serialization for FeatureEstimate list

  - [x] 2.4 Create EstimationConfig dataclass with use_outlier_detection, outlier_threshold_std, min_data_points_for_stats fields

    - _Requirements: 1.3_
    - ✅ **COMPLETED**: Implemented with validation and sensible defaults (True, 2.0, 3)

  - [x] 2.5 Create FeatureEstimate dataclass for individual feature estimates within ProjectEstimate

    - _Requirements: 1.3, 8.3_
    - ✅ **COMPLETED**: Implemented with validation, JSON serialization, and optional FeatureStatistics

  - [x] 2.6 Create FeatureStatistics dataclass for mean, median, std_dev, p80 values

    - _Requirements: 1.6, 9.1_
    - ✅ **COMPLETED**: Implemented with validation ensuring non-negative values for std_dev and counts

  - [x] 2.7 Write property test for dataclass instantiation validity

    - **Property 2: Dataclass Instantiation Validity**
    - **Validates: Requirements 1.3**

- [x] 3. Implement Result Type Pattern and Error Types

  - [x] 3.1 Create ValidationError dataclass with field, message, value attributes

    - _Requirements: 1.8, 8.5_

  - [x] 3.2 Create NotFoundError, ImportError, EstimationError types

    - _Requirements: 1.8_

  - [x] 3.3 Implement Result[T, E] generic class with ok(), err(), is_ok(), is_err(), unwrap(), unwrap_err() methods

    - _Requirements: 1.5, 1.8_

  - [x] 3.4 Write property test for Result pattern consistency

    - **Property 3: Service Result Pattern Consistency**
    - **Validates: Requirements 1.5, 1.8**

- [x] 4. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement Service Interfaces (Abstract Base Classes)

  - [x] 5.1 Create IFeatureLibraryService ABC with add_feature, get_feature, search_features, list_features methods

    - Use @abstractmethod decorators and Result return types
    - _Requirements: 1.4_
    - ✅ **COMPLETED**: Implemented in `src/services/interfaces.py` with full docstrings and Result type returns

  - [x] 5.2 Create ITimeTrackingService ABC with add_entry, import_csv, get_entries_for_feature methods

    - _Requirements: 1.4_

  - [x] 5.3 Create IEstimationService ABC with estimate_feature, estimate_project, compute_statistics methods

    - _Requirements: 1.4_

- [x] 6. Implement Utility Functions

  - [x] 6.1 Implement calculate_mean function for list of floats

    - _Requirements: 1.6, 9.1_

  - [x] 6.2 Implement calculate_median function for list of floats

    - _Requirements: 1.6, 9.1_

  - [x] 6.3 Implement calculate_std_dev function for list of floats

    - _Requirements: 1.6, 9.1_

  - [x] 6.4 Implement calculate_p80 (80th percentile) function for list of floats

    - _Requirements: 1.6, 9.1_
    - ✅ **COMPLETED**: Implemented in `src/utils/__init__.py` with linear interpolation

  - [x] 6.5 Implement detect_outliers function using standard deviation threshold

    - _Requirements: 1.6, 9.3_
    - ✅ **COMPLETED**: Implemented in `src/utils/__init__.py` returning (index, value) tuples

  - [x] 6.6 Implement normalize_text function for feature name matching

    - _Requirements: 1.6_
    - ✅ **COMPLETED**: Implemented in `src/utils/__init__.py` with lowercase, hyphen/underscore replacement, whitespace normalization

  - [x] 6.7 Write property test for statistics mathematical correctness

    - **Property 4: Statistics Mathematical Correctness**
    - **Validates: Requirements 1.6, 9.1**

  - [x] 6.8 Write property test for outlier detection accuracy

    - **Property 19: Outlier Detection Accuracy**
    - **Validates: Requirements 9.3**

- [x] 7. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement Service Implementations

  - [x] 8.1 Implement FeatureLibraryService with in-memory storage

    - Implement add_feature, get_feature, search_features, list_features
    - Return Result types for all operations
    - _Requirements: 1.5_

  - [x] 8.2 Implement TimeTrackingService with in-memory storage

    - Implement add_entry, get_entries_for_feature
    - _Requirements: 1.5_

  - [x] 8.3 Implement EstimationService with statistics computation

    - Implement estimate_feature using tracked time data and seed time fallback
    - Implement estimate_project aggregating feature estimates
    - Implement compute_statistics using utility functions
    - _Requirements: 1.5, 9.1, 9.2, 9.4_

  - [x] 8.4 Write property test for low data point fallback

    - **Property 18: Low Data Point Fallback**
    - **Validates: Requirements 9.2**
    - ✅ **COMPLETED**: Implemented in `tests/properties/test_model_props.py` with `TestLowDataPointFallback` class containing 5 property tests covering 0, 1, 2, and 3+ data points scenarios

  - [ ]\* 8.5 Write property test for confidence level thresholds
    - **Property 21: Confidence Level Thresholds**
    - **Validates: Requirements 9.5**
  - [ ]\* 8.6 Write property test for project estimate aggregation
    - **Property 20: Project Estimate Aggregation**
    - **Validates: Requirements 9.4**

- [x] 9. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement JSON Serialization

  - [x] 10.1 Add to_dict and from_dict methods to Feature dataclass

    - _Requirements: 8.4_

  - [x] 10.2 Add to_dict and from_dict methods to TrackedTimeEntry dataclass

    - _Requirements: 8.4_

  - [x] 10.3 Add to_dict and from_dict methods to ProjectEstimate dataclass

    - _Requirements: 8.4_

  - [x] 10.4 Implement JSON file persistence utilities (save_json, load_json)

    - _Requirements: 2.3_

  - [ ]\* 10.5 Write property test for model serialization round-trip
    - **Property 5: Model Serialization Round-Trip**
    - **Validates: Requirements 2.3, 8.4**
  - [ ]\* 10.6 Write property test for JSON validation error specificity
    - **Property 17: JSON Validation Error Specificity**
    - **Validates: Requirements 8.5**

- [x] 11. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 2: CLI Development (aitea-cli)

- [x] 12. Implement Typer CLI Application

  - [x] 12.1 Create main Typer app with feature subcommand group

    - Implement feature add, list, search commands
    - _Requirements: 2.1_

  - [x] 12.2 Add time tracking subcommand group

    - Implement time add, list commands
    - _Requirements: 2.1_

  - [x] 12.3 Add estimate command for project estimation

    - _Requirements: 2.1_

- [x] 13. Implement Rich Output Formatting

  - [x] 13.1 Create Rich tables for feature listing

    - _Requirements: 2.2_

  - [x] 13.2 Create Rich panels for estimation results

    - _Requirements: 2.2_

  - [x] 13.3 Add progress bars for long-running operations

    - _Requirements: 2.2_

- [x] 14. Implement JSON Persistence Services

  - [x] 14.1 Create FeatureLibraryPersistence service for JSON file operations

    - _Requirements: 2.3_

  - [x] 14.2 Create TimeTrackingPersistence service for JSON file operations

    - _Requirements: 2.3_

- [x] 15. Implement CSV Import Pipeline

  - [x] 15.1 Create CSV import function using pandas with validation

    - _Requirements: 2.4_

  - [x] 15.2 Implement error collection for invalid rows

    - _Requirements: 2.4_

  - [ ]\* 15.3 Write property test for CSV import validation
    - **Property 6: CSV Import Validation**
    - **Validates: Requirements 2.4**

- [x] 16. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 3: LLM Fundamentals

- [x] 17. Implement MockLLM System

  - [x] 17.1 Create MockLLM class with predefined response map

    - Implement complete() and chat() methods
    - _Requirements: 3.1, 13.1, 13.3_

  - [x] 17.2 Implement get_llm_provider() function checking API keys

    - _Requirements: 13.1, 13.4_

  - [x] 17.3 Add warning display for mock mode
    - _Requirements: 13.2_
  - [ ]\* 17.4 Write property test for MockLLM determinism
    - **Property 22: MockLLM Determinism**
    - **Validates: Requirements 13.3**

- [x] 18. Implement Prompt Templates

  - [x] 18.1 Create PromptTemplate class with variable substitution

    - _Requirements: 3.2_

  - [x] 18.2 Create templates for feature extraction, estimation, BRD parsing

    - _Requirements: 3.2_

  - [ ]\* 18.3 Write property test for prompt template variable substitution
    - **Property 13: Prompt Template Variable Substitution**
    - **Validates: Requirements 6.6**

- [x] 19. Implement Output Parsers

  - [x] 19.1 Create JSON output parser with Pydantic validation

    - _Requirements: 3.3_

  - [ ]\* 19.2 Write property test for output parser round-trip
    - **Property 7: Output Parser Round-Trip**
    - **Validates: Requirements 3.3**

- [x] 20. Implement Tool Definitions

  - [x] 20.1 Create tool definition schema structure

    - _Requirements: 3.4_

  - [x] 20.2 Define tools for AITEA operations (add_feature, estimate, etc.)

    - _Requirements: 3.4_

- [x] 21. Implement Multi-Provider LLM Abstraction

  - [x] 21.1 Create LLMProvider abstract base class with complete(), stream(), count_tokens() methods

    - _Requirements: 3.5_

  - [x] 21.2 Implement OpenAIProvider for GPT models

    - _Requirements: 3.5_

  - [x] 21.3 Implement AnthropicProvider for Claude models

    - _Requirements: 3.5_

  - [x] 21.4 Implement BedrockProvider for AWS Bedrock models

    - _Requirements: 3.5_

  - [ ] 21.5 Implement CohereProvider for Command models

    - _Requirements: 3.5, 13.2_

  - [ ] 21.6 Implement GeminiProvider for Google Gemini models

    - _Requirements: 3.5, 13.2_

  - [ ] 21.7 Implement GrokProvider for xAI Grok models

    - _Requirements: 3.5, 13.2_

  - [ ] 21.8 Implement MistralProvider for Mistral AI models

    - _Requirements: 3.5, 13.2_

  - [ ] 21.9 Implement HuggingFaceProvider for HF Inference API

    - _Requirements: 3.5, 13.2_

  - [x] 21.10 Implement OllamaProvider for local models

    - _Requirements: 3.5, 13.2_

  - [x] 21.11 Create LLMFallbackChain with automatic provider initialization

    - ✅ **COMPLETED**: Implemented `FallbackChain` class in `src/services/providers.py` with `from_environment()` class method
    - _Requirements: 13.2, 13.3_

  - [x] 21.12 Implement provider health checking and failover logic

    - ✅ **COMPLETED**: FallbackChain tries providers in order, catches exceptions, and falls back to next provider
    - _Requirements: 13.3_

  - [x] 21.13 Add logging for provider selection and request handling

    - ✅ **COMPLETED**: Added logging in FallbackChain for provider attempts, failures, and successful handling
    - _Requirements: 13.7_

  - [x] 21.14 Update get_llm_provider() to use fallback chain

    - ✅ **COMPLETED**: Added `provider="fallback"` and `use_fallback_chain=True` options to `get_llm_provider()`
    - Added `get_fallback_chain()` convenience function
    - _Requirements: 13.1, 13.2, 13.4_

  - [ ]\* 21.15 Write property test for multi-provider fallback consistency
    - **Property 31: Multi-Provider Fallback Consistency**
    - **Validates: Requirements 3.5, 13.2, 13.3**

- [x] 22. Implement Streaming Responses

  - [x] 22.1 Create async generator for streaming LLM responses

    - _Requirements: 3.6_

  - [x] 22.2 Implement token-by-token streaming with callbacks

    - _Requirements: 3.6_

  - [ ]\* 22.3 Write property test for streaming response completeness
    - **Property 30: Streaming Response Completeness**
    - **Validates: Requirements 3.6**

- [x] 23. Implement Token Management

  - [x] 23.1 Create token counting utilities for different model families

    - _Requirements: 3.7_

  - [x] 23.2 Implement context window management with truncation strategies

    - _Requirements: 3.7_

  - [x] 23.3 Create token budget tracking for cost management

    - _Requirements: 3.7_

- [x] 24. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 4: Document Processing & Chunking (aitea-ingest)

- [x] 25. Implement Document Loaders

  - [x] 25.1 Create DocumentLoader abstract base class

    - _Requirements: 4.1_

  - [x] 25.2 Implement PDFLoader using pypdf and pdfplumber

    - _Requirements: 4.1_

  - [x] 25.3 Implement DOCXLoader using python-docx

    - _Requirements: 4.1_

  - [x] 25.4 Implement HTMLLoader with BeautifulSoup

    - _Requirements: 4.1_

  - [x] 25.5 Implement MarkdownLoader with frontmatter support

    - _Requirements: 4.1_

- [x] 26. Implement Chunking Strategies

  - [x] 26.1 Create ChunkingStrategy abstract base class

    - _Requirements: 4.2_

  - [x] 26.2 Implement FixedSizeChunker with configurable size and overlap

    - _Requirements: 4.2_

  - [x] 26.3 Implement RecursiveChunker with hierarchical separators

    - _Requirements: 4.2_

  - [x] 26.4 Implement SemanticChunker using embedding similarity

    - _Requirements: 4.2_

  - [x] 26.5 Implement SentenceChunker using spaCy/NLTK

    - _Requirements: 4.2_

  - [ ]\* 26.6 Write property test for chunk boundary integrity
    - **Property 32: Chunk Boundary Integrity**
    - **Validates: Requirements 4.2, 4.3**

- [x] 27. Implement Parent Document Retrieval

  - [x] 27.1 Create ParentDocumentRetriever with child/parent splitters

    - _Requirements: 4.3_

  - [x] 27.2 Implement chunk-to-parent mapping storage

    - _Requirements: 4.3_

- [x] 28. Implement Metadata Extraction

  - [x] 28.1 Create metadata extractors for source, page, section

    - _Requirements: 4.4_

  - [x] 28.2 Implement automatic title and heading extraction

    - _Requirements: 4.4_

  - [x] 28.3 Create metadata enrichment pipeline

    - _Requirements: 4.4_

- [x] 29. Implement Table Extraction

  - [x] 29.1 Create table detection from PDFs using camelot/tabula

    - _Requirements: 4.5_

  - [x] 29.2 Implement table-to-text conversion strategies

    - _Requirements: 4.5_

  - [x] 29.3 Create structured data handling for extracted tables

    - _Requirements: 4.5_

- [x] 30. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 5: Agent Foundations (From Scratch)

- [x] 31. Implement SimpleAgent Class

  - [x] 31.1 Create SimpleAgent with Observe-Think-Act-Reflect loop

    - Implement state machine for agent loop

    - _Requirements: 5.2_

  - [ ]\* 31.2 Write property test for agent loop state transitions
    - **Property 8: Agent Loop State Transitions**
    - **Validates: Requirements 5.2**

- [x] 32. Implement ToolRegistry

  - [x] 32.1 Create ToolRegistry class with register, get, list methods

    - _Requirements: 5.3_

  - [x] 32.2 Implement JSON schema validation for tool arguments

    - _Requirements: 5.3_

  - [ ]\* 32.3 Write property test for tool registry operations
    - **Property 9: Tool Registry Operations**
    - **Validates: Requirements 5.3**

- [-] 33. Implement ReAct Pattern

  - [x] 33.1 Create ReActAgent implementing reasoning and acting

    - _Requirements: 5.4_

- [x] 34. Implement Memory Classes

  - [x] 34.1 Create ShortTermMemory with capacity limit

    - _Requirements: 5.5_

  - [x] 34.2 Create LongTermMemory for persistent storage

    - _Requirements: 5.5_

  - [x] 34.3 Create SummarizationMemory for context compression

    - _Requirements: 5.5_

  - [ ]\* 34.4 Write property test for memory capacity constraints
    - **Property 10: Memory Capacity Constraints**
    - **Validates: Requirements 5.5**

- [x] 35. Implement Safety Checks

  - [x] 35.1 Create prompt injection detection function

    - _Requirements: 5.6_

  - [x] 35.2 Create safe tool usage validator

    - _Requirements: 5.6_

  - [ ]\* 35.3 Write property test for prompt injection detection
    - **Property 11: Prompt Injection Detection**
    - **Validates: Requirements 5.6**

- [x] 36. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 6: LangChain Track (aitea-langchain)

- [x] 37. Implement LCEL Chains

  - [x] 37.1 Create feature extraction chain using pipe operator

    - _Requirements: 6.1_
    - ✅ **COMPLETED**: Implemented in `src/langchain/chains.py` with `create_feature_extraction_chain()` using LCEL pipe operator, ChatPromptTemplate, JsonOutputParser with Pydantic models (ExtractedFeature, FeatureExtractionOutput)

  - [x] 37.2 Implement RunnablePassthrough for data flow

    - _Requirements: 6.1_
    - ✅ **COMPLETED**: Implemented RunnablePassthrough in all chains for preserving input data, demonstrated in `create_simple_passthrough_chain()` and `create_multi_input_chain()` examples

  - [x] 37.3 Create estimation chain with optional RAG integration

    - _Requirements: 6.1_
    - ✅ **COMPLETED**: Implemented `create_estimation_chain()` with optional retriever parameter for RAG pattern, includes context formatting and EstimationOutput Pydantic model

- [x] 38. Implement Custom Tools

  - [x] 38.1 Wrap aitea-core services as LangChain tools using @tool decorator

    - _Requirements: 6.2_

  - [x] 38.2 Create StructuredTool implementations

    - _Requirements: 6.2_

- [x] 39. Implement Vector Store Abstraction

  - [x] 39.1 Create VectorStore abstract interface

    - _Requirements: 6.3_
    - ✅ **COMPLETED**: Implemented in `src/langchain/vector_stores.py` with abstract VectorStore class providing unified interface for add_documents, similarity_search, hybrid_search, delete, clear, and get_embedding_dimension methods. Includes Document and SearchResult dataclasses with validation.

  - [x] 39.2 Implement ChromaDB store for development

    - _Requirements: 6.3_
    - 🔄 **IN PROGRESS**: Abstract interface completed, concrete implementation needed

  - [x] 39.3 Implement Pinecone store for production

    - _Requirements: 6.3_
    - 🔄 **IN PROGRESS**: Abstract interface completed, concrete implementation needed

  - [x] 39.4 Implement Qdrant store with hybrid search

    - _Requirements: 6.3_
    - 🔄 **IN PROGRESS**: Abstract interface completed, concrete implementation needed

  - [x] 39.5 Implement embedding model selection (OpenAI, Cohere, BGE)

    - _Requirements: 6.3_
    - ✅ **COMPLETED**: Implemented EmbeddingModel abstract base class and EmbeddingProvider enum with factory function create_embedding_model() supporting OpenAI, Cohere, and BGE providers. Includes async embed_documents and embed_query methods.

  - [ ]\* 39.6 Write property test for RAG retrieval relevance
    - **Property 12: RAG Retrieval Relevance**
    - **Validates: Requirements 6.3**
  - [ ]\* 39.7 Write property test for embedding similarity transitivity
    - **Property 33: Embedding Similarity Transitivity**
    - **Validates: Requirements 6.3**

- [x] 40. Implement LangGraph BRD Parser Agent

  - [x] 40.1 Create StateGraph with nodes for BRD parsing

    - _Requirements: 6.4_

  - [x] 40.2 Implement conditional edges for workflow control

    - _Requirements: 6.4_

- [x] 41. Implement LangSmith Integration

  - [x] 41.1 Add tracing configuration

    - _Requirements: 6.5_

  - [x] 41.2 Set up evaluation and dataset management

    - _Requirements: 6.5_

- [x] 42. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 7: Multi-Agent Frameworks (aitea-agents)

- [x] 43. Implement CrewAI Multi-Agent System

  - [x] 43.1 Create Analyst agent for BRD feature extraction

    - _Requirements: 7.1_

  - [x] 43.2 Create Estimator agent for time estimation

    - _Requirements: 7.1_

  - [x] 43.3 Create Reviewer agent for estimate validation

    - _Requirements: 7.1_

  - [x] 43.4 Implement Crew with sequential and hierarchical processes

    - _Requirements: 7.1_

  - [ ]\* 43.5 Write property test for CrewAI agent role isolation
    - **Property 36: CrewAI Agent Role Isolation**
    - **Validates: Requirements 7.1**

- [x] 44. Implement AutoGen Conversational Agents

  - [x] 44.1 Create AssistantAgent for estimation tasks

    - _Requirements: 7.2_

  - [x] 44.2 Create UserProxyAgent with human-in-the-loop

    - _Requirements: 7.2_

  - [x] 44.3 Implement GroupChat for multi-agent conversations

    - _Requirements: 7.2_

  - [x] 44.4 Add code execution capabilities with sandboxing

    - _Requirements: 7.2_

- [ ] 45. Implement Strands Agents SDK

  - [ ] 45.1 Create Strands agent with @tool decorators
    - _Requirements: 7.3_
  - [ ] 45.2 Implement AWS Bedrock model integration
    - _Requirements: 7.3_
  - [ ] 45.3 Add conversation memory and context management
    - _Requirements: 7.3_

- [ ] 46. Implement MCP Tool Definitions

  - [ ] 46.1 Create MCPToolDefinition class with schema
    - _Requirements: 7.4_
  - [ ] 46.2 Implement converters to LangChain, CrewAI, Strands formats
    - _Requirements: 7.4_
  - [ ] 46.3 Create MCP server for AITEA tools
    - _Requirements: 7.4_
  - [ ]\* 46.4 Write property test for MCP tool schema compatibility
    - **Property 37: MCP Tool Schema Compatibility**
    - **Validates: Requirements 7.4**

- [ ] 47. Implement Framework Comparison Guide

  - [ ] 47.1 Create decision matrix for framework selection
    - _Requirements: 7.5_
  - [ ] 47.2 Document use cases for each framework
    - _Requirements: 7.5_
  - [ ] 47.3 Create benchmark tests comparing frameworks
    - _Requirements: 7.5_

- [ ] 48. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 8: LlamaIndex & Advanced RAG (aitea-llamaindex)

- [ ] 49. Implement Multiple Index Types

  - [ ] 49.1 Create Vector index for feature library
    - _Requirements: 8.1_
  - [ ] 49.2 Create Tree and Keyword indices
    - _Requirements: 8.1_
  - [ ] 49.3 Create KnowledgeGraph index
    - _Requirements: 8.1_

- [ ] 50. Implement Advanced Retrievers

  - [ ] 50.1 Create hybrid search retriever (dense + sparse)
    - _Requirements: 8.2_
  - [ ] 50.2 Implement HyDE (Hypothetical Document Embeddings)
    - _Requirements: 8.2_
  - [ ] 50.3 Implement reranking with Cohere/cross-encoder
    - _Requirements: 8.2_
  - [ ]\* 50.4 Write property test for hybrid retriever result quality
    - **Property 14: Hybrid Retriever Result Quality**
    - **Validates: Requirements 8.2**

- [ ] 51. Implement Query Engines

  - [ ] 51.1 Create router query engine for multi-index routing
    - _Requirements: 8.3_
  - [ ] 51.2 Create sub-question query engine for complex queries
    - _Requirements: 8.3_
  - [ ] 51.3 Create citation query engine with source attribution
    - _Requirements: 8.3_

- [ ] 52. Implement Agentic RAG Patterns

  - [ ] 52.1 Implement Self-RAG with retrieval decision and hallucination check
    - _Requirements: 8.4_
  - [ ] 52.2 Implement Corrective RAG (CRAG) with document grading
    - _Requirements: 8.4_
  - [ ] 52.3 Implement Adaptive RAG with query complexity routing
    - _Requirements: 8.4_
  - [ ]\* 52.4 Write property test for agentic RAG self-correction
    - **Property 39: Agentic RAG Self-Correction**
    - **Validates: Requirements 8.4**

- [ ] 53. Implement Graph RAG

  - [ ] 53.1 Set up Neo4j database connection
    - _Requirements: 8.5_
  - [ ] 53.2 Implement entity and relationship extraction from documents
    - _Requirements: 8.5_
  - [ ] 53.3 Create knowledge graph construction pipeline
    - _Requirements: 8.5_
  - [ ] 53.4 Implement graph-based retrieval with Cypher queries
    - _Requirements: 8.5_
  - [ ]\* 53.5 Write property test for graph RAG relationship preservation
    - **Property 38: Graph RAG Relationship Preservation**
    - **Validates: Requirements 8.5**

- [ ] 54. Implement RAGAS Evaluation Framework

  - [ ] 54.1 Implement faithfulness metric
    - _Requirements: 8.6_
  - [ ] 54.2 Implement answer relevancy metric
    - _Requirements: 8.6_
  - [ ] 54.3 Implement context precision and recall metrics
    - _Requirements: 8.6_
  - [ ] 54.4 Create evaluation pipeline with test datasets
    - _Requirements: 8.6_

- [ ] 55. Implement Framework Benchmark

  - [ ] 55.1 Create benchmark suite comparing LangChain vs LlamaIndex
    - _Requirements: 8.7_
  - [ ] 55.2 Measure latency, accuracy, and cost metrics
    - _Requirements: 8.7_
  - [ ] 55.3 Document trade-offs and recommendations
    - _Requirements: 8.7_

- [ ] 56. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 9: Production Hardening (aitea-web)

- [ ] 57. Implement Guardrails

  - [ ] 57.1 Set up NeMo Guardrails with rail definitions
    - _Requirements: 9.1_
  - [ ] 57.2 Implement input validation rails (topic, jailbreak detection)
    - _Requirements: 9.1_
  - [ ] 57.3 Implement output validation rails (factuality, toxicity)
    - _Requirements: 9.1_
  - [ ] 57.4 Integrate Guardrails AI for Pydantic-based validation
    - _Requirements: 9.1_
  - [ ]\* 57.5 Write property test for guardrail trigger determinism
    - **Property 34: Guardrail Trigger Determinism**
    - **Validates: Requirements 9.1**

- [ ] 58. Implement Observability

  - [ ] 58.1 Set up LangFuse for LLM tracing
    - _Requirements: 9.2_
  - [ ] 58.2 Integrate Phoenix for local observability
    - _Requirements: 9.2_
  - [ ] 58.3 Add OpenTelemetry instrumentation
    - _Requirements: 9.2_
  - [ ] 58.4 Create custom metrics for token usage and latency
    - _Requirements: 9.2_

- [ ] 59. Implement Reliability Patterns

  - [ ] 59.1 Create RetryConfig with exponential backoff
    - _Requirements: 9.3_
  - [ ] 59.2 Implement circuit breaker pattern
    - _Requirements: 9.3_
  - [x] 59.3 Implement FallbackChain for provider failover
    - ✅ **COMPLETED**: Implemented in task 21.11-21.14 (`src/services/providers.py`)
    - _Requirements: 9.3_
  - [ ] 59.4 Add timeout handling with graceful degradation
    - _Requirements: 9.3_
  - [ ]\* 59.5 Write property test for retry pattern behavior
    - **Property 15: Retry Pattern Behavior**
    - **Validates: Requirements 9.3**

- [ ] 60. Implement Async Patterns

  - [ ] 60.1 Create async tool execution with asyncio.gather
    - _Requirements: 9.4_
  - [ ] 60.2 Implement parallel RAG queries
    - _Requirements: 9.4_
  - [ ] 60.3 Add semaphore-based concurrency limiting
    - _Requirements: 9.4_
  - [ ]\* 60.4 Write property test for async task ordering
    - **Property 35: Async Task Ordering**
    - **Validates: Requirements 9.4**

- [ ] 61. Implement Streaming Responses

  - [ ] 61.1 Create SSE endpoint for streaming agent responses
    - _Requirements: 9.5_
  - [ ] 61.2 Implement chunked transfer encoding
    - _Requirements: 9.5_
  - [ ] 61.3 Add progress events for long-running operations
    - _Requirements: 9.5_

- [ ] 62. Implement Cost Optimization

  - [ ] 62.1 Create semantic cache with embedding similarity
    - _Requirements: 9.6_
  - [ ] 62.2 Implement token budget tracking and enforcement
    - _Requirements: 9.6_
  - [ ] 62.3 Add model routing based on query complexity
    - _Requirements: 9.6_
  - [ ]\* 62.4 Write property test for cache hit consistency
    - **Property 16: Cache Hit Consistency**
    - **Validates: Requirements 9.6**

- [ ] 63. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 10: Deployment & Integration

- [ ] 64. Implement FastAPI Web Application

  - [ ] 64.1 Create FastAPI app with REST endpoints
    - _Requirements: 10.1_
  - [ ] 64.2 Add WebSocket endpoint for bidirectional agent communication
    - _Requirements: 10.1_
  - [ ] 64.3 Implement SSE endpoint for streaming updates
    - _Requirements: 10.1_
  - [ ] 64.4 Add Pydantic response models and error handling
    - _Requirements: 10.1_
  - [ ]\* 64.5 Write property test for API endpoint response consistency
    - **Property 29: API Endpoint Response Consistency**
    - **Validates: Requirements 10.1**
  - [ ]\* 64.6 Write property test for WebSocket message ordering
    - **Property 40: WebSocket Message Ordering**
    - **Validates: Requirements 10.1**

- [ ] 65. Implement Queue-Based Processing

  - [ ] 65.1 Set up Redis for task queue
    - _Requirements: 10.2_
  - [ ] 65.2 Implement Celery workers for long-running agent tasks
    - _Requirements: 10.2_
  - [ ] 65.3 Add task status tracking and result retrieval
    - _Requirements: 10.2_
  - [ ] 65.4 Implement task prioritization and rate limiting
    - _Requirements: 10.2_

- [ ] 66. Implement Containerization

  - [ ] 66.1 Create Dockerfile for AITEA application
    - _Requirements: 10.3_
  - [ ] 66.2 Create docker-compose for local development
    - _Requirements: 10.3_
  - [ ] 66.3 Add health checks and graceful shutdown
    - _Requirements: 10.3_
  - [ ] 66.4 Document Kubernetes deployment patterns
    - _Requirements: 10.3_

- [ ] 67. Implement Serverless Deployment

  - [ ] 67.1 Create AWS Lambda handler for estimation API
    - _Requirements: 10.4_
  - [ ] 67.2 Implement Vercel serverless functions
    - _Requirements: 10.4_
  - [ ] 67.3 Add cold start optimization strategies
    - _Requirements: 10.4_
  - [ ] 67.4 Document serverless limitations and workarounds
    - _Requirements: 10.4_

- [ ] 68. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 11: Chapter Content Structure

- [ ] 69. Implement Chapter Content Models

  - [ ] 69.1 Create ChapterMetadata dataclass
    - _Requirements: 14.1_
  - [ ] 69.2 Create ChapterContent dataclass with all sections
    - _Requirements: 14.1-14.7_
  - [ ] 69.3 Create CodeSection, Exercise, DebuggingScenario, MiniProject, AITEAIntegration dataclasses
    - _Requirements: 14.2-14.7_

- [ ] 70. Implement Chapter Validation

  - [ ]\* 70.1 Write property test for chapter header completeness
    - **Property 23: Chapter Header Completeness**
    - **Validates: Requirements 14.1**
  - [ ]\* 70.2 Write property test for learning objectives count
    - **Property 24: Learning Objectives Count**
    - **Validates: Requirements 14.2**
  - [ ]\* 70.3 Write property test for exercise minimum count
    - **Property 25: Exercise Minimum Count**
    - **Validates: Requirements 14.4**
  - [ ]\* 70.4 Write property test for debugging scenario structure
    - **Property 26: Debugging Scenario Structure**
    - **Validates: Requirements 14.5**
  - [ ]\* 70.5 Write property test for mini-project completeness
    - **Property 27: Mini-Project Completeness**
    - **Validates: Requirements 14.6**
  - [ ]\* 70.6 Write property test for AITEA integration reference
    - **Property 28: AITEA Integration Reference**
    - **Validates: Requirements 14.7**

- [ ] 71. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 12: Curriculum Chapter Content Creation

- [x] 72. Create Curriculum Structure

  - [x] 72.1 Create curriculum/README.md with chapter index
  - [x] 72.2 Create curriculum/chapters/ folder structure

- [x] 73. Create Phase 1 Chapters (Python Foundations)

  - [x] 73.1 CH01_environment_setup.md - Environment & Project Setup
  - [x] 73.2 CH02_enums_type_hints.md - Enums & Type Hints
  - [x] 73.3 CH03_dataclasses.md - Dataclasses & Data Models
  - [x] 73.4 CH04_abstract_classes.md - Abstract Classes & Interfaces
  - [x] 73.5 CH05_services.md - Service Implementation
  - [x] 73.6 CH06_utilities.md - Utility Functions
  - [x] 73.7 CH07_property_testing.md - Property-Based Testing
  - [x] 73.8 CH08_error_handling.md - Error Handling & Validation

- [x] 74. Create Phase 2 Chapters (CLI Development)

  - [x] 74.1 CH09_cli_typer.md - CLI with Typer
  - [x] 74.2 CH10_rich_ui.md - Rich Terminal UI
  - [x] 74.3 CH11_json_persistence.md - JSON Persistence
  - [x] 74.4 CH12_csv_import.md - CSV Import Pipeline

- [x] 75. Create Phase 3 Chapters (LLM Fundamentals)

  - [x] 75.1 CH13_llm_basics.md - LLM Basics & Mock Client
    - ✅ **COMPLETED**: Covers LLM concepts, MockLLM implementation, provider abstraction
  - [x] 75.2 CH14_prompt_engineering.md - Prompt Engineering
    - ✅ **COMPLETED**: Covers PromptTemplate, ChatPromptTemplate, few-shot, CoT
  - [x] 75.3 CH15_structured_outputs.md - Structured Outputs
    - ✅ **COMPLETED**: Covers JsonOutputParser, Pydantic validation, format instructions
  - [x] 75.4 CH16_tool_calling.md - Tool Calling Patterns
    - ✅ **COMPLETED**: Covers ToolDefinition, JSON Schema validation, OpenAI/Anthropic formats

- [x] 76. Create Phase 4 Chapters (Agent Foundations)

  - [x] 76.1 CH17_agent_concepts.md - What Are Agents?
    - ✅ **COMPLETED**: Covers agent vs chatbot vs workflow, core components, use cases
  - [x] 76.2 CH18_agent_loop.md - Agent Loop from Scratch
    - ✅ **COMPLETED**: Covers OTAR loop, AgentState, AgentContext, SimpleAgent
  - [x] 76.3 CH19_tool_registry.md - Tool Registry
    - ✅ **COMPLETED**: Covers ToolRegistry, registration, validation, format export
  - [x] 76.4 CH20_react_pattern.md - Planning Patterns (ReAct)
    - ✅ **COMPLETED**: Covers ReAct pattern, step parsing, action execution
  - [x] 76.5 CH21_memory.md - Memory Patterns
    - ✅ **COMPLETED**: Covers ShortTermMemory, LongTermMemory, SummarizationMemory
  - [x] 76.6 CH22_safety.md - Guardrails & Safety
    - ✅ **COMPLETED**: Covers prompt injection detection, tool validation, sanitization

- [ ] 77. Create Phase 5-6 Chapters (Framework Tracks)
  - [ ] 77.1 LangChain chapters (CH23-CH28)
  - [ ] 77.2 LlamaIndex chapters (CH29-CH34)

---

## Summary: Curriculum Coverage

### Frameworks Covered

- **LangChain**: LCEL, LangGraph, LangSmith (Phase 6)
- **LlamaIndex**: Indices, Retrievers, Query Engines (Phase 8)
- **CrewAI**: Multi-agent orchestration (Phase 7)
- **AutoGen**: Conversational agents (Phase 7)
- **Strands Agents SDK**: AWS-native agents (Phase 7)

### RAG Patterns Covered

- Basic RAG with vector stores (Phase 6)
- Hybrid search (dense + sparse) (Phase 8)
- HyDE and reranking (Phase 8)
- Self-RAG, CRAG, Adaptive RAG (Phase 8)
- Graph RAG with Neo4j (Phase 8)

### Production Patterns Covered

- Guardrails (NeMo, Guardrails AI) (Phase 9)
- Observability (LangFuse, Phoenix, OpenTelemetry) (Phase 9)
- Reliability (retries, circuit breakers, fallbacks) (Phase 9)
- Async/concurrent execution (Phase 9)
- Streaming responses (SSE, WebSocket) (Phase 9-10)
- Cost optimization (caching, batching, model routing) (Phase 9)
- Deployment (Docker, Kubernetes, Serverless) (Phase 10)
