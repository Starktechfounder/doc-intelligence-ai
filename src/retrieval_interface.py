"""
Retrieval interface abstraction for document intelligence system.

Provides a clean abstraction layer between the core application and
the underlying retrieval implementation, supporting multiple backends.
"""
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from src.semantic_chunker import Chunk


class RetrievalResult:
    """
    Standardized result format for retrieval operations.

    Ensures consistent result structure across different retrieval backends.
    """

    def __init__(
        self,
        chunk_id: str,
        content: str,
        score: float,
        metadata: Dict[str, Any]
    ):
        self.chunk_id = chunk_id
        self.content = content
        self.score = score
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "id": self.chunk_id,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata
        }


class RetrievalService:
    """
    High-level retrieval service that manages chunk indexing and querying.

    Provides a clean interface for the application layer and supports
    multiple retrieval backends through composition.
    """

    def __init__(self, retriever: Any = None):
        """
        Initialize retrieval service with optional retriever backend.

        Args:
            retriever: Retriever instance (defaults to LexicalRetriever)
        """
        if retriever is None:
            from src.retrieval import LexicalRetriever
            self.retriever = LexicalRetriever()
        else:
            self.retriever = retriever

    def index_document_chunks(self, chunks: List[Chunk]) -> None:
        """
        Index document chunks for retrieval.

        Args:
            chunks: List of Chunk objects to index
        """
        self.retriever.index(chunks)

    def search(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.0
    ) -> List[RetrievalResult]:
        """
        Search for relevant chunks using the configured retriever.

        Args:
            query: Search query string
            top_k: Maximum number of results to return
            min_score: Minimum relevance score threshold

        Returns:
            List of RetrievalResult objects sorted by relevance
        """
        raw_results = self.retriever.retrieve(query, top_k, min_score)
        return [
            RetrievalResult(
                chunk_id=result["id"],
                content=result["content"],
                score=result["score"],
                metadata=result["metadata"]
            )
            for result in raw_results
        ]

    def clear_index(self) -> None:
        """Clear all indexed data."""
        self.retriever.clear()

    def get_retriever_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current index.

        Returns:
            Dictionary containing index statistics
        """
        if hasattr(self.retriever, "__len__"):
            return {
                "total_chunks": len(self.retriever),
                "unique_sources": len(self.retriever.indexed_sources) if hasattr(self.retriever, "indexed_sources") else 0
            }
        return {"total_chunks": 0, "unique_sources": 0}