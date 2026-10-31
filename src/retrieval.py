"""
Retrieval module for document intelligence system.

Provides a stable retriever interface for querying indexed document chunks
and retrieving relevant evidence with metadata and scores.
"""
from typing import List, Dict, Any, Optional
from uuid import uuid4
from src.semantic_chunker import Chunk


class Retriever:
    """
    Abstract interface for document retrieval systems.

    Defines the contract for querying indexed chunks and returning
    relevant results with source metadata and relevance scores.
    """

    def index(self, chunks: List[Chunk]) -> None:
        """
        Index chunks for retrieval.

        Args:
            chunks: List of Chunk objects to be indexed
        """
        raise NotImplementedError("Subclasses must implement index method")

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant chunks for a query.

        Args:
            query: The search query string
            top_k: Maximum number of results to return (default: 3)
            min_score: Minimum relevance score threshold (default: 0.0)

        Returns:
            List of result dictionaries, each containing:
                - content: The chunk text
                - score: Relevance score (0.0 to 1.0)
                - metadata: Source metadata including filename, page number, etc.
                - id: Stable unique identifier for the chunk
        """
        raise NotImplementedError("Subclasses must implement retrieve method")

    def clear(self) -> None:
        """Clear all indexed data."""
        raise NotImplementedError("Subclasses must implement clear method")


class LexicalRetriever(Retriever):
    """
    Lexical retrieval implementation using TF-IDF and cosine similarity.

    Provides baseline retrieval functionality without requiring external
    APIs or embeddings. Suitable for portfolio projects and initial
    development.
    """

    def __init__(
        self,
        stop_words: Optional[List[str]] = "english",
        min_df: float = 1,
        max_df: float = 1.0
    ):
        """
        Initialize lexical retriever with TF-IDF parameters.

        Args:
            stop_words: List of stop words to use (default: English stop words)
            min_df: Minimum document frequency for term inclusion (int or float)
            max_df: Maximum document frequency for term inclusion (float: 0.0-1.0)
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        self.vectorizer = TfidfVectorizer(
            stop_words=stop_words,
            min_df=min_df,
            max_df=max_df,
            token_pattern=r"(?u)\b\w\w+\b"
        )
        self.chunks: List[Chunk] = []
        self.tfidf_matrix = None
        self.chunk_ids: Dict[str, str] = {}  # content_id -> chunk_id
        self.indexed_sources = set()

    def _generate_chunk_id(self, chunk: Chunk) -> str:
        """
        Generate a stable, unique ID for a chunk.

        Uses content hash for stability, falls back to UUID if hashing fails.

        Args:
            chunk: The chunk to generate ID for

        Returns:
            Stable unique identifier for the chunk
        """
        import hashlib
        # Create a stable hash from chunk content and key metadata fields
        hash_input = (
            chunk.content +
            chunk.metadata.get("source", "") +
            str(chunk.metadata.get("page_number", 0)) +
            str(chunk.metadata.get("chunk_index", 0))
        )
        content_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        return f"chunk_{content_hash}"

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for lexical retrieval.

        Args:
            text: Input text to normalize

        Returns:
            Normalized text (lowercase, stripped)
        """
        import re
        # Convert to lowercase and strip extra whitespace
        text = text.lower().strip()
        # Normalize whitespace (multiple spaces/newlines to single space)
        text = re.sub(r'\s+', ' ', text)
        return text

    def index(self, chunks: List[Chunk]) -> None:
        """
        Index chunks for retrieval with deduplication and stable IDs.

        Args:
            chunks: List of Chunk objects to index
        """
        if not chunks:
            return

        # Generate stable IDs for new chunks
        for chunk in chunks:
            chunk_id = self._generate_chunk_id(chunk)
            self.chunk_ids[id(chunk)] = chunk_id
            chunk.metadata["id"] = chunk_id

        # Check for duplicate sources (same source file)
        new_chunks = []
        for chunk in chunks:
            source = chunk.metadata.get("source")
            if source and source in self.indexed_sources:
                continue  # Skip already indexed sources
            new_chunks.append(chunk)

        if not new_chunks:
            return

        # Track indexed sources for deduplication
        for chunk in new_chunks:
            source = chunk.metadata.get("source")
            if source:
                self.indexed_sources.add(source)

        # Add new chunks to our collection
        self.chunks.extend(new_chunks)

        # Rebuild TF-IDF matrix for all chunks
        corpus = [c.content for c in self.chunks]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant chunks using TF-IDF and cosine similarity.

        Args:
            query: Search query string
            top_k: Maximum number of results to return
            min_score: Minimum relevance score threshold

        Returns:
            List of result dictionaries with content, score, and metadata
        """
        if not self.chunks or self.tfidf_matrix is None or not query.strip():
            return []

        # Normalize query
        normalized_query = self._normalize_text(query)

        # Transform query to TF-IDF space
        query_vector = self.vectorizer.transform([normalized_query])

        # Calculate cosine similarities
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        if len(similarities) == 0:
            return []

        # Get top indices sorted by similarity score descending
        top_indices = similarities.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score < min_score:
                continue  # Skip results below minimum score

            chunk = self.chunks[idx]
            chunk_id = self.chunk_ids.get(id(chunk), f"chunk_{idx}")

            results.append({
                "id": chunk_id,
                "content": chunk.content,
                "score": score,
                "metadata": chunk.metadata
            })

        return results

    def clear(self) -> None:
        """Clear all indexed chunks and reset the retriever."""
        self.chunks = []
        self.tfidf_matrix = None
        self.chunk_ids.clear()
        self.indexed_sources.clear()

    def __len__(self) -> int:
        """Return the number of indexed chunks."""
        return len(self.chunks)

    def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        """
        Retrieve a specific chunk by its ID.

        Args:
            chunk_id: The stable ID of the chunk to retrieve

        Returns:
            The Chunk object if found, None otherwise
        """
        for chunk in self.chunks:
            if chunk.metadata.get("id") == chunk_id:
                return chunk
        return None