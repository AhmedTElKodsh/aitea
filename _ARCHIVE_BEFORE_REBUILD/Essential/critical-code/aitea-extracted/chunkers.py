"""Chunking strategies for document processing.

This module provides various chunking strategies for splitting documents
into smaller pieces suitable for embedding and retrieval in RAG systems.

Chunking Strategies:
- FixedSizeChunker: Split by character count with configurable overlap
- RecursiveChunker: Hierarchically split using multiple separators
- SemanticChunker: Split based on embedding similarity between sentences
- SentenceChunker: Split by sentences using NLP libraries
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import re
import uuid

from .models import Chunk, ChunkMetadata, Document


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies.
    
    Chunking strategies are responsible for splitting documents into
    smaller chunks suitable for embedding and retrieval. Different
    strategies optimize for different use cases:
    
    - FixedSizeChunker: Simple, predictable chunk sizes
    - RecursiveChunker: Respects document structure (paragraphs, sentences)
    - SemanticChunker: Groups semantically similar content
    - SentenceChunker: Preserves sentence boundaries
    
    Subclasses must implement the chunk() method to handle their
    specific splitting logic.
    
    Attributes:
        chunk_size: Target size for each chunk (in characters)
        chunk_overlap: Number of characters to overlap between chunks
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        """Initialize the chunking strategy.
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            
        Raises:
            ValueError: If chunk_size <= 0 or chunk_overlap >= chunk_size
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        """Split a document into chunks.
        
        Args:
            document: The document to split
            
        Returns:
            List of Chunk objects created from the document
        """
        ...
    
    def chunk_text(self, text: str, source: str = "unknown") -> List[Chunk]:
        """Split raw text into chunks.
        
        Convenience method for chunking text without a Document wrapper.
        
        Args:
            text: The text to split
            source: Source identifier for metadata
            
        Returns:
            List of Chunk objects
        """
        from .models import DocumentMetadata
        doc = Document(
            content=text,
            metadata=DocumentMetadata(source=source)
        )
        return self.chunk(doc)
    
    def _create_chunk(
        self,
        content: str,
        source: str,
        chunk_index: int,
        start_char: int,
        end_char: int,
        total_chunks: Optional[int] = None,
        page_number: Optional[int] = None,
        section: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Chunk:
        """Create a Chunk with proper metadata.
        
        Args:
            content: The chunk text content
            source: Source document identifier
            chunk_index: Index of this chunk
            start_char: Starting character position
            end_char: Ending character position
            total_chunks: Total number of chunks (if known)
            page_number: Page number from source document
            section: Section heading this chunk belongs to
            extra: Additional metadata
            
        Returns:
            A new Chunk instance
        """
        metadata = ChunkMetadata(
            source=source,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            start_char=start_char,
            end_char=end_char,
            page_number=page_number,
            section=section,
            extra=extra or {},
        )
        return Chunk(
            content=content,
            metadata=metadata,
            id=str(uuid.uuid4()),
        )


class FixedSizeChunker(ChunkingStrategy):
    """Split documents into fixed-size chunks with configurable overlap.
    
    This is the simplest chunking strategy. It splits text into chunks
    of approximately equal size, with optional overlap between chunks
    to maintain context across chunk boundaries.
    
    Best for:
    - Simple documents without clear structure
    - When consistent chunk sizes are important
    - Quick prototyping
    
    Attributes:
        chunk_size: Target size for each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        strip_whitespace: Whether to strip leading/trailing whitespace
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        strip_whitespace: bool = True,
    ) -> None:
        """Initialize the fixed-size chunker.
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            strip_whitespace: Whether to strip whitespace from chunks
        """
        super().__init__(chunk_size, chunk_overlap)
        self.strip_whitespace = strip_whitespace
    
    def chunk(self, document: Document) -> List[Chunk]:
        """Split document into fixed-size chunks.
        
        Args:
            document: The document to split
            
        Returns:
            List of Chunk objects
        """
        text = document.content
        source = document.metadata.source
        page_number = document.metadata.page_number
        
        if not text:
            return []
        
        chunks: List[Chunk] = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))
            
            # Extract chunk content
            chunk_content = text[start:end]
            
            if self.strip_whitespace:
                chunk_content = chunk_content.strip()
            
            # Only add non-empty chunks
            if chunk_content:
                chunk = self._create_chunk(
                    content=chunk_content,
                    source=source,
                    chunk_index=chunk_index,
                    start_char=start,
                    end_char=end,
                    page_number=page_number,
                    extra={"strategy": "fixed_size"},
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # If we've reached the end of the text, break out
            if end >= len(text):
                break
            
            # Move to next position with overlap
            start = end - self.chunk_overlap
            
            # Prevent infinite loop if overlap equals or exceeds chunk size
            if start <= 0 or start >= end:
                start = end
        
        # Update total_chunks in all chunk metadata
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)
        
        return chunks


class RecursiveChunker(ChunkingStrategy):
    """Split documents recursively using hierarchical separators.
    
    This strategy attempts to split text at natural boundaries
    (paragraphs, sentences, words) in order of preference. It tries
    the first separator, and if chunks are still too large, recursively
    splits using the next separator.
    
    Default separator hierarchy:
    1. Double newlines (paragraphs)
    2. Single newlines
    3. Periods followed by space (sentences)
    4. Spaces (words)
    
    Best for:
    - Documents with clear paragraph/sentence structure
    - When preserving semantic boundaries is important
    - General-purpose chunking
    
    Attributes:
        separators: List of separators to try, in order of preference
        keep_separator: Whether to keep the separator in the chunk
    """
    
    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " "]
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
        keep_separator: bool = True,
    ) -> None:
        """Initialize the recursive chunker.
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use (default: paragraphs, lines, sentences, words)
            keep_separator: Whether to keep separators in the output
        """
        super().__init__(chunk_size, chunk_overlap)
        self.separators = separators or self.DEFAULT_SEPARATORS.copy()
        self.keep_separator = keep_separator
    
    def chunk(self, document: Document) -> List[Chunk]:
        """Split document recursively using separators.
        
        Args:
            document: The document to split
            
        Returns:
            List of Chunk objects
        """
        text = document.content
        source = document.metadata.source
        page_number = document.metadata.page_number
        
        if not text:
            return []
        
        # Recursively split the text
        split_texts = self._split_text(text, self.separators)
        
        # Merge small chunks and create Chunk objects
        chunks: List[Chunk] = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        char_position = 0
        
        for split_text in split_texts:
            # If adding this text would exceed chunk_size, save current chunk
            if current_chunk and len(current_chunk) + len(split_text) > self.chunk_size:
                chunk = self._create_chunk(
                    content=current_chunk.strip(),
                    source=source,
                    chunk_index=chunk_index,
                    start_char=current_start,
                    end_char=current_start + len(current_chunk),
                    page_number=page_number,
                    extra={"strategy": "recursive"},
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_start = char_position - len(overlap_text)
                current_chunk = overlap_text
            
            current_chunk += split_text
            char_position += len(split_text)
        
        # Add the last chunk
        if current_chunk.strip():
            chunk = self._create_chunk(
                content=current_chunk.strip(),
                source=source,
                chunk_index=chunk_index,
                start_char=current_start,
                end_char=current_start + len(current_chunk),
                page_number=page_number,
                extra={"strategy": "recursive"},
            )
            chunks.append(chunk)
        
        # Update total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)
        
        return chunks
    
    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separators.
        
        Args:
            text: Text to split
            separators: Remaining separators to try
            
        Returns:
            List of text segments
        """
        if not separators:
            # No more separators, return text as-is
            return [text] if text else []
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        # Split by current separator
        if separator in text:
            splits = text.split(separator)
            result: List[str] = []
            
            for i, split in enumerate(splits):
                # Add separator back if keeping it (except for last split)
                if self.keep_separator and i < len(splits) - 1:
                    split = split + separator
                
                # If split is still too large, recursively split
                if len(split) > self.chunk_size and remaining_separators:
                    result.extend(self._split_text(split, remaining_separators))
                elif split:
                    result.append(split)
            
            return result
        else:
            # Separator not found, try next one
            return self._split_text(text, remaining_separators)
    
    def _get_overlap_text(self, text: str) -> str:
        """Get the overlap portion from the end of text.
        
        Args:
            text: Text to get overlap from
            
        Returns:
            The last chunk_overlap characters, or empty string if overlap is 0
        """
        if self.chunk_overlap == 0:
            return ""
        if len(text) <= self.chunk_overlap:
            return text
        return text[-self.chunk_overlap:]



class SemanticChunker(ChunkingStrategy):
    """Split documents based on semantic similarity between sentences.
    
    This strategy uses embeddings to measure semantic similarity between
    consecutive sentences. When similarity drops below a threshold,
    a new chunk boundary is created. This groups semantically related
    content together.
    
    Requires an embedding function to compute sentence embeddings.
    Can use OpenAI, sentence-transformers, or any custom embedding function.
    
    Best for:
    - Documents where topic shifts are important boundaries
    - When semantic coherence within chunks is critical
    - RAG applications requiring high-quality retrieval
    
    Attributes:
        embedding_function: Function that takes text and returns embedding vector
        similarity_threshold: Minimum similarity to keep sentences together (0-1)
        min_chunk_size: Minimum chunk size before considering a split
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_function: Optional[Callable[[str], List[float]]] = None,
        similarity_threshold: float = 0.5,
        min_chunk_size: int = 100,
    ) -> None:
        """Initialize the semantic chunker.
        
        Args:
            chunk_size: Maximum size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            embedding_function: Function to compute embeddings (text -> vector)
            similarity_threshold: Similarity threshold for chunk boundaries (0-1)
            min_chunk_size: Minimum characters before considering a split
        """
        super().__init__(chunk_size, chunk_overlap)
        self.embedding_function = embedding_function
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
    
    def chunk(self, document: Document) -> List[Chunk]:
        """Split document based on semantic similarity.
        
        Args:
            document: The document to split
            
        Returns:
            List of Chunk objects
            
        Raises:
            ValueError: If no embedding function is provided
        """
        if self.embedding_function is None:
            raise ValueError(
                "SemanticChunker requires an embedding_function. "
                "Provide a function that takes text and returns an embedding vector."
            )
        
        text = document.content
        source = document.metadata.source
        page_number = document.metadata.page_number
        
        if not text:
            return []
        
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return []
        
        if len(sentences) == 1:
            # Single sentence, return as one chunk
            return [self._create_chunk(
                content=sentences[0],
                source=source,
                chunk_index=0,
                start_char=0,
                end_char=len(sentences[0]),
                total_chunks=1,
                page_number=page_number,
                extra={"strategy": "semantic"},
            )]
        
        # Compute embeddings for all sentences
        embeddings = [self.embedding_function(s) for s in sentences]
        
        # Find chunk boundaries based on similarity
        chunks: List[Chunk] = []
        current_sentences: List[str] = [sentences[0]]
        current_start = 0
        char_position = len(sentences[0])
        chunk_index = 0
        
        for i in range(1, len(sentences)):
            # Compute similarity between current and previous sentence
            similarity = self._cosine_similarity(embeddings[i-1], embeddings[i])
            
            current_chunk_text = " ".join(current_sentences)
            
            # Check if we should start a new chunk
            should_split = (
                similarity < self.similarity_threshold and
                len(current_chunk_text) >= self.min_chunk_size
            ) or len(current_chunk_text) + len(sentences[i]) > self.chunk_size
            
            if should_split:
                # Save current chunk
                chunk = self._create_chunk(
                    content=current_chunk_text,
                    source=source,
                    chunk_index=chunk_index,
                    start_char=current_start,
                    end_char=char_position,
                    page_number=page_number,
                    extra={"strategy": "semantic", "split_similarity": similarity},
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Start new chunk (with overlap if possible)
                overlap_sentences = self._get_overlap_sentences(
                    current_sentences, self.chunk_overlap
                )
                current_sentences = overlap_sentences + [sentences[i]]
                current_start = char_position - sum(len(s) + 1 for s in overlap_sentences)
            else:
                current_sentences.append(sentences[i])
            
            char_position += len(sentences[i]) + 1  # +1 for space
        
        # Add the last chunk
        if current_sentences:
            chunk = self._create_chunk(
                content=" ".join(current_sentences),
                source=source,
                chunk_index=chunk_index,
                start_char=current_start,
                end_char=char_position,
                page_number=page_number,
                extra={"strategy": "semantic"},
            )
            chunks.append(chunk)
        
        # Update total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting regex
        # Handles periods, exclamation marks, question marks
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (0-1)
        """
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _get_overlap_sentences(
        self, sentences: List[str], target_overlap: int
    ) -> List[str]:
        """Get sentences from the end that fit within overlap size.
        
        Args:
            sentences: List of sentences
            target_overlap: Target overlap size in characters
            
        Returns:
            List of sentences that fit within overlap
        """
        result: List[str] = []
        total_length = 0
        
        for sentence in reversed(sentences):
            if total_length + len(sentence) + 1 <= target_overlap:
                result.insert(0, sentence)
                total_length += len(sentence) + 1
            else:
                break
        
        return result


class SentenceChunker(ChunkingStrategy):
    """Split documents by sentences using NLP libraries.
    
    This strategy uses spaCy or NLTK for accurate sentence boundary
    detection. It groups sentences together until the chunk size
    limit is reached, ensuring chunks always end at sentence boundaries.
    
    Falls back to regex-based splitting if NLP libraries are not available.
    
    Best for:
    - Documents where sentence integrity is important
    - Legal, medical, or technical documents
    - When accurate sentence boundaries are critical
    
    Attributes:
        use_spacy: Whether to use spaCy for sentence detection
        use_nltk: Whether to use NLTK for sentence detection
        spacy_model: spaCy model name to use
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        use_spacy: bool = True,
        use_nltk: bool = True,
        spacy_model: str = "en_core_web_sm",
    ) -> None:
        """Initialize the sentence chunker.
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            use_spacy: Whether to try using spaCy first
            use_nltk: Whether to try using NLTK as fallback
            spacy_model: spaCy model to load
        """
        super().__init__(chunk_size, chunk_overlap)
        self.use_spacy = use_spacy
        self.use_nltk = use_nltk
        self.spacy_model = spacy_model
        self._nlp = None
        self._nltk_tokenizer = None
    
    def chunk(self, document: Document) -> List[Chunk]:
        """Split document by sentences.
        
        Args:
            document: The document to split
            
        Returns:
            List of Chunk objects
        """
        text = document.content
        source = document.metadata.source
        page_number = document.metadata.page_number
        
        if not text:
            return []
        
        # Get sentences using available NLP library
        sentences = self._get_sentences(text)
        
        if not sentences:
            return []
        
        # Group sentences into chunks
        chunks: List[Chunk] = []
        current_sentences: List[str] = []
        current_length = 0
        current_start = 0
        char_position = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            # Check if adding this sentence would exceed chunk_size
            if current_length + sentence_len > self.chunk_size and current_sentences:
                # Save current chunk
                chunk_content = " ".join(current_sentences)
                chunk = self._create_chunk(
                    content=chunk_content,
                    source=source,
                    chunk_index=chunk_index,
                    start_char=current_start,
                    end_char=char_position,
                    page_number=page_number,
                    extra={"strategy": "sentence", "sentence_count": len(current_sentences)},
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(
                    current_sentences, self.chunk_overlap
                )
                current_sentences = overlap_sentences
                current_length = sum(len(s) + 1 for s in overlap_sentences)
                current_start = char_position - current_length
            
            current_sentences.append(sentence)
            current_length += sentence_len + 1  # +1 for space
            char_position += sentence_len + 1
        
        # Add the last chunk
        if current_sentences:
            chunk_content = " ".join(current_sentences)
            chunk = self._create_chunk(
                content=chunk_content,
                source=source,
                chunk_index=chunk_index,
                start_char=current_start,
                end_char=char_position,
                page_number=page_number,
                extra={"strategy": "sentence", "sentence_count": len(current_sentences)},
            )
            chunks.append(chunk)
        
        # Update total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)
        
        return chunks
    
    def _get_sentences(self, text: str) -> List[str]:
        """Get sentences using available NLP library.
        
        Tries spaCy first, then NLTK, then falls back to regex.
        
        Args:
            text: Text to split into sentences
            
        Returns:
            List of sentences
        """
        # Try spaCy
        if self.use_spacy:
            try:
                sentences = self._get_sentences_spacy(text)
                if sentences:
                    return sentences
            except ImportError:
                pass
        
        # Try NLTK
        if self.use_nltk:
            try:
                sentences = self._get_sentences_nltk(text)
                if sentences:
                    return sentences
            except ImportError:
                pass
        
        # Fallback to regex
        return self._get_sentences_regex(text)
    
    def _get_sentences_spacy(self, text: str) -> List[str]:
        """Get sentences using spaCy.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
            
        Raises:
            ImportError: If spaCy is not installed
        """
        try:
            import spacy
        except ImportError:
            raise ImportError(
                "spaCy is required for sentence detection. "
                "Install it with: pip install spacy && python -m spacy download en_core_web_sm"
            )
        
        if self._nlp is None:
            try:
                self._nlp = spacy.load(self.spacy_model)
            except OSError:
                raise ImportError(
                    f"spaCy model '{self.spacy_model}' not found. "
                    f"Download it with: python -m spacy download {self.spacy_model}"
                )
        
        doc = self._nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    def _get_sentences_nltk(self, text: str) -> List[str]:
        """Get sentences using NLTK.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
            
        Raises:
            ImportError: If NLTK is not installed
        """
        try:
            import nltk
            from nltk.tokenize import sent_tokenize
        except ImportError:
            raise ImportError(
                "NLTK is required for sentence detection. "
                "Install it with: pip install nltk"
            )
        
        # Ensure punkt tokenizer is downloaded
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        # Also try punkt_tab for newer NLTK versions
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            try:
                nltk.download('punkt_tab', quiet=True)
            except Exception:
                pass  # Older NLTK versions don't have punkt_tab
        
        sentences = sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_sentences_regex(self, text: str) -> List[str]:
        """Get sentences using regex fallback.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Split on sentence-ending punctuation followed by space or newline
        pattern = r'(?<=[.!?])\s+'
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_sentences(
        self, sentences: List[str], target_overlap: int
    ) -> List[str]:
        """Get sentences from the end that fit within overlap size.
        
        Args:
            sentences: List of sentences
            target_overlap: Target overlap size in characters
            
        Returns:
            List of sentences that fit within overlap
        """
        result: List[str] = []
        total_length = 0
        
        for sentence in reversed(sentences):
            if total_length + len(sentence) + 1 <= target_overlap:
                result.insert(0, sentence)
                total_length += len(sentence) + 1
            else:
                break
        
        return result
