from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.semantic_chunker import Chunk

class VectorStore:
    """
    A lightweight local vector / retrieval store using TF-IDF and cosine similarity,
    suitable for student portfolio projects without heavy C++ extension overhead.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.chunks: List[Chunk] = []
        self.tfidf_matrix = None
        self.indexed_sources = set()

    def index_chunks(self, chunks: List[Chunk]) -> None:
        """
        Indexes a list of chunks. Prevents duplicate indexing of the same source file.
        """
        if not chunks:
            return

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

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves the top_k most relevant chunks for a query, preserving metadata.
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
            if score <= 0.0:
                continue # Skip irrelevant results
            chunk = self.chunks[idx]
            results.append({
                "content": chunk.content,
                "score": score,
                "metadata": chunk.metadata
            })

        return results
