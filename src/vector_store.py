from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.semantic_chunker import Chunk
from src.retrieval import Retriever

class VectorStore(Retriever):
    """
    A lightweight local vector / retrieval store using TF-IDF and cosine similarity,
    suitable for student portfolio projects without heavy C++ extension overhead.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.chunks: List[Chunk] = []
        self.tfidf_matrix = None
        self.indexed_sources = set()

    def index(self, chunks: List[Chunk]) -> None:
        """
        Indexes a list of chunks. Prevents duplicate indexing of the same source file.

        This method implements the Retriever interface and provides stable chunk IDs.
        """
        if not chunks:
            return

        # Generate stable IDs for new chunks
        for chunk in chunks:
            chunk_id = self._generate_chunk_id(chunk)
            chunk.metadata["id"] = chunk_id

        # Check source uniqueness to prevent duplicate indexing
        new_chunks = []
        for chunk in chunks:
            source = chunk.metadata.get("source")
            if source and source in self.indexed_sources:
                # Skip already indexed sources to make it repeatable without duplicates
                continue
            new_chunks.append(chunk)

        if not new_chunks:
            return

        for chunk in new_chunks:
            source = chunk.metadata.get("source")
            if source:
                self.indexed_sources.add(source)

        self.chunks.extend(new_chunks)

        # Rebuild TF-IDF matrix over all chunks
        corpus = [c.content for c in self.chunks]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def index_chunks(self, chunks: List[Chunk]) -> None:
        """
        Backward compatibility method. Delegates to index().

        This method exists for backward compatibility and delegates to the new
        Retriever interface method.
        """
        self.index(chunks)

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieves the top_k most relevant chunks for a query, preserving metadata.

        This method implements the Retriever interface and adds score filtering.
        """
        if not self.chunks or self.tfidf_matrix is None or not query.strip():
            return []

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        if len(similarities) == 0:
            return []

        # Get top indices sorted by similarity score descending
        top_indices = similarities.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            # Skip irrelevant results (score <= 0) or below minimum threshold
            if score <= 0.0 or score < min_score:
                continue
            chunk = self.chunks[idx]
            results.append({
                "id": chunk.metadata.get("id", f"chunk_{idx}"),
                "content": chunk.content,
                "score": score,
                "metadata": chunk.metadata
            })

        return results

    def clear(self) -> None:
        """Clear all indexed data."""
        self.chunks = []
        self.tfidf_matrix = None
        self.indexed_sources.clear()

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
