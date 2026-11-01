import pytest
import os
from src.retrieval import LexicalRetriever
from src.semantic_chunker import Chunk, SemanticChunker
from src.document_loader import Document, DocumentLoader
from src.retrieval_interface import RetrievalService


def test_vector_store_document_loader():
    """Test that DocumentLoader works correctly with various file types."""
    # Test TXT file
    txt_content = "This is a test text file."
    with open("test.txt", "w") as f:
        f.write(txt_content)

    doc = DocumentLoader.load_file("test.txt")
    assert doc.content == txt_content
    assert doc.metadata["filename"] == "test.txt"
    assert doc.metadata["file_type"] == ".txt"

    os.unlink("test.txt")


def test_vector_store_semantic_chunker():
    """Test that SemanticChunker produces correct structure."""
    content = "# Header\n\nThis is a test document with multiple sections.\n\n## Subheader\nMore content here."
    doc = Document(content=content, metadata={"filename": "test.md"})

    chunker = SemanticChunker(max_chunk_size=200)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) > 0
    for chunk in chunks:
        assert isinstance(chunk, Chunk)
        assert len(chunk.content.strip()) > 0
        assert "filename" in chunk.metadata
        assert "section_header" in chunk.metadata


def test_vector_store_retrieval_stats():
    """Test that retriever stats are calculated correctly."""
    service = RetrievalService()

    # Index some test chunks
    chunks = [
        Chunk(
            content="First chunk content",
            metadata={"filename": "doc1.txt", "source": "doc1.txt", "page_number": 1}
        ),
        Chunk(
            content="Second chunk content",
            metadata={"filename": "doc1.txt", "source": "doc1.txt", "page_number": 2}
        ),
        Chunk(
            content="Third chunk content",
            metadata={"filename": "doc2.txt", "source": "doc2.txt", "page_number": 1}
        )
    ]

    service.index_document_chunks(chunks)

    # Test get_retriever_stats
    stats = service.get_retriever_stats()
    assert "total_chunks" in stats
    assert "unique_sources" in stats
    assert stats["total_chunks"] == 3
    assert stats["unique_sources"] == 2


def test_vector_store_empty_index():
    """Test that empty retriever returns appropriate results."""
    service = RetrievalService()

    stats = service.get_retriever_stats()
    assert stats["total_chunks"] == 0
    assert stats["unique_sources"] == 0

    results = service.search("test query", top_k=3)
    assert results == []


def test_vector_store_chunk_ids():
    """Test that chunk IDs are stable and unique."""
    retriever = LexicalRetriever()

    chunks = [
        Chunk(
            content="Unique content 1",
            metadata={"source": "doc1.txt", "page_number": 1}
        ),
        Chunk(
            content="Unique content 2",
            metadata={"source": "doc2.txt", "page_number": 1}
        )
    ]

    retriever.index(chunks)

    # Verify all chunks have IDs
    for chunk in chunks:
        assert "id" in chunk.metadata
        assert chunk.metadata["id"].startswith("chunk_")

    # Verify IDs are unique
    ids = [chunk.metadata["id"] for chunk in chunks]
    assert len(ids) == len(set(ids))


def test_vector_store_duplicate_sources():
    """Test that duplicate sources from same file are deduplicated."""
    retriever = LexicalRetriever()

    chunks = [
        Chunk(
            content="First chunk",
            metadata={"source": "doc1.txt", "page_number": 1}
        ),
        Chunk(
            content="Second chunk",
            metadata={"source": "doc1.txt", "page_number": 2}
        )
    ]

    retriever.index(chunks)
    assert len(retriever) == 2

    # Index same chunks again
    retriever.index(chunks)

    # Should still have the same number of chunks (duplicates ignored)
    assert len(retriever) == 2


def test_vector_store_search_results():
    """Test that search returns correctly formatted results."""
    retriever = LexicalRetriever()

    chunks = [
        Chunk(
            content="Password requirements: at least 12 characters",
            metadata={"source": "security.txt", "page_number": 1}
        ),
        Chunk(
            content="Access control based on role and need-to-know",
            metadata={"source": "security.txt", "page_number": 2}
        )
    ]

    retriever.index(chunks)

    # Search for password requirements
    results = retriever.retrieve("password requirements", top_k=1)
    assert len(results) == 1
    assert "password" in results[0]["content"].lower()
    assert results[0]["score"] > 0.0

    # Search for access control
    results = retriever.retrieve("access control", top_k=1)
    assert len(results) == 1
    assert "access" in results[0]["content"].lower()


def test_vector_store_clear_functionality():
    """Test that clear() properly resets the retriever."""
    retriever = LexicalRetriever()

    chunks = [
        Chunk(
            content="Some content",
            metadata={"source": "test.txt"}
        )
    ]

    retriever.index(chunks)
    assert len(retriever) == 1

    # Clear and verify
    retriever.clear()
    assert len(retriever) == 0
    assert retriever.retrieve("test") == []