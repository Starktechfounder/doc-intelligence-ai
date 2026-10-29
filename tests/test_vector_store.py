import pytest
from src.semantic_chunker import Chunk
from src.vector_store import VectorStore

def test_vector_store_indexing_and_retrieval():
    store = VectorStore()

    chunks = [
        Chunk(content="The quick brown fox jumps over the lazy dog about security compliance.", metadata={"filename": "doc1.txt", "source": "doc1.txt", "section_header": "Introduction", "page_number": 1}),
        Chunk(content="Financial policies dictate strict adherence to auditing and risk assessment guidelines.", metadata={"filename": "doc2.txt", "source": "doc2.txt", "section_header": "Finance", "page_number": 2}),
    ]

    store.index_chunks(chunks)

    # Test retrieval for security
    results = store.retrieve("security compliance", top_k=1)
    assert len(results) == 1
    assert "quick brown fox" in results[0]["content"]
    assert results[0]["metadata"]["filename"] == "doc1.txt"
    assert results[0]["metadata"]["section_header"] == "Introduction"
    assert results[0]["metadata"]["page_number"] == 1

def test_vector_store_repeatable_indexing():
    store = VectorStore()
    chunks = [
        Chunk(content="Unique text for deduplication test.", metadata={"source": "dup.txt"})
    ]

    store.index_chunks(chunks)
    assert len(store.chunks) == 1

    # Indexing same source again should be ignored
    store.index_chunks(chunks)
    assert len(store.chunks) == 1

def test_vector_store_empty_inputs():
    store = VectorStore()

    # Empty index search
    assert store.retrieve("test query") == []

    # Indexing empty list
    store.index_chunks([])
    assert len(store.chunks) == 0

def test_vector_store_unknown_query():
    store = VectorStore()
    store.index_chunks([Chunk(content="Python programming language features.", metadata={"source": "code.py"})])

    # Query unrelated to indexed content
    results = store.retrieve("quantum mechanics astrophysics", top_k=2)
    assert results == []
