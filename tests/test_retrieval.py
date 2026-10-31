import pytest
from src.retrieval import LexicalRetriever, Retriever
from src.semantic_chunker import Chunk
from src.retrieval_interface import RetrievalResult


def test_retriever_interface():
    """Test that LexicalRetriever implements Retriever interface."""
    retriever = LexicalRetriever()
    assert isinstance(retriever, Retriever)

    # Test that required methods exist
    assert hasattr(retriever, 'index')
    assert hasattr(retriever, 'retrieve')
    assert hasattr(retriever, 'clear')


def test_lexical_retriever_stable_ids():
    """Test that chunk IDs are stable across retrievals."""
    retriever = LexicalRetriever()

    chunk1 = Chunk(
        content="Test content 1",
        metadata={"source": "doc1.txt", "page_number": 1}
    )
    chunk2 = Chunk(
        content="Test content 2",
        metadata={"source": "doc2.txt", "page_number": 2}
    )

    # Index chunks
    retriever.index([chunk1, chunk2])

    # Generate IDs
    id1_first = chunk1.metadata.get("id")
    id2_first = chunk2.metadata.get("id")

    # Clear and re-index with same chunks
    retriever.clear()
    retriever.index([chunk1, chunk2])

    id1_second = chunk1.metadata.get("id")
    id2_second = chunk2.metadata.get("id")

    # IDs should be stable
    assert id1_first == id1_second
    assert id2_first == id2_second


def test_lexical_retriever_deduplication():
    """Test that retriever prevents duplicate source indexing."""
    retriever = LexicalRetriever()

    # Create chunks from same source
    chunk1 = Chunk(
        content="First chunk",
        metadata={"source": "doc1.txt", "page_number": 1}
    )
    chunk2 = Chunk(
        content="Second chunk",
        metadata={"source": "doc1.txt", "page_number": 2}
    )

    # Index first batch
    retriever.index([chunk1, chunk2])
    assert len(retriever) == 2

    # Index same chunks again (should be ignored due to source deduplication)
    retriever.index([chunk1, chunk2])
    # Should still have only 2 chunks (duplicates ignored)
    assert len(retriever) == 2


def test_lexical_retriever_empty_query():
    """Test that empty queries return no results."""
    retriever = LexicalRetriever()

    chunk = Chunk(
        content="Some content",
        metadata={"source": "doc1.txt"}
    )
    retriever.index([chunk])

    # Empty query
    results = retriever.retrieve("", top_k=3)
    assert results == []

    # Whitespace-only query
    results = retriever.retrieve("   \n\t  ", top_k=3)
    assert results == []


def test_lexical_retriever_min_score():
    """Test minimum score threshold functionality."""
    retriever = LexicalRetriever(min_df=0.0, max_df=1.0)

    chunk1 = Chunk(
        content="Exact match query text",
        metadata={"source": "doc1.txt"}
    )
    chunk2 = Chunk(
        content="Different unrelated content",
        metadata={"source": "doc2.txt"}
    )

    retriever.index([chunk1, chunk2])

    # Query with min_score 1.0 should only return exact matches
    results = retriever.retrieve("Exact match query text", top_k=10, min_score=1.0)
    assert len(results) == 1
    assert "Exact match" in results[0]["content"]


def test_lexical_retriever_empty_index():
    """Test retrieval with empty index."""
    retriever = LexicalRetriever()

    # Search without indexing anything
    results = retriever.retrieve("some query", top_k=3)
    assert results == []

    # Clear index and search
    chunk = Chunk(
        content="Test",
        metadata={"source": "test.txt"}
    )
    retriever.index([chunk])
    retriever.clear()

    results = retriever.retrieve("test", top_k=3)
    assert results == []


def test_lexical_retriever_top_k():
    """Test top_k parameter functionality."""
    retriever = LexicalRetriever()

    chunks = [
        Chunk(content="Content 1 with query keywords", metadata={"source": "doc1.txt"}),
        Chunk(content="Content 2 with query keywords", metadata={"source": "doc2.txt"}),
        Chunk(content="Content 3 with query keywords", metadata={"source": "doc3.txt"}),
        Chunk(content="Content 4 without keywords", metadata={"source": "doc4.txt"}),
    ]

    retriever.index(chunks)

    # Request top 2 results
    results = retriever.retrieve("query keywords", top_k=2)
    assert len(results) == 2

    # Request more results than available
    results = retriever.retrieve("keywords", top_k=10)
    assert len(results) <= 4  # All chunks have keywords


def test_retrieval_result_class():
    """Test RetrievalResult class functionality."""
    result = RetrievalResult(
        chunk_id="test_id",
        content="Test content",
        score=0.85,
        metadata={"source": "test.txt"}
    )

    assert result.chunk_id == "test_id"
    assert result.content == "Test content"
    assert result.score == 0.85
    assert result.metadata["source"] == "test.txt"

    # Test to_dict method
    result_dict = result.to_dict()
    assert result_dict["id"] == "test_id"
    assert result_dict["content"] == "Test content"
    assert result_dict["score"] == 0.85
    assert result_dict["metadata"]["source"] == "test.txt"


def test_retrieval_interface_clear():
    """Test that retriever.clear() works properly."""
    retriever = LexicalRetriever()

    chunk = Chunk(
        content="Test",
        metadata={"source": "test.txt"}
    )
    retriever.index([chunk])
    assert len(retriever) > 0

    retriever.clear()
    assert len(retriever) == 0
    assert retriever.retrieve("test") == []