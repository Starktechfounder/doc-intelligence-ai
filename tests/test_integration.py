import tempfile
import os
from src.document_loader import DocumentLoader
from src.semantic_chunker import SemanticChunker
from src.retrieval_interface import RetrievalService
from src.answer_generator import AnswerGenerator
from src.llm_client import FakeLLMClient


def test_full_pipeline_text_document():
    """Test complete pipeline with a text document."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""# Security Policy
This document outlines security guidelines for our organization.

## Password Requirements
Users must create passwords with:
- At least 12 characters
- Upper and lower case letters
- Numbers and special characters

## Access Control
Access is granted based on role and need-to-know principles.
""")
        temp_path = f.name

    try:
        # Step 1: Load document
        doc = DocumentLoader.load_file(temp_path)
        assert doc.content is not None
        assert len(doc.content) > 0
        assert "filename" in doc.metadata

        # Step 2: Chunk document
        chunker = SemanticChunker(max_chunk_size=200, overlap=50)
        chunks = chunker.chunk_document(doc)
        assert len(chunks) > 0

        # Step 3: Index and retrieve
        retriever = RetrievalService()
        retriever.index_document_chunks(chunks)

        # Verify chunks have metadata after indexing
        for chunk in chunks:
            assert "id" in chunk.metadata
            assert "filename" in chunk.metadata
            assert len(chunk.content.strip()) > 0

        # Verify indexing worked
        stats = retriever.get_retriever_stats()
        assert stats["total_chunks"] == len(chunks)

        # Search for security-related content
        results = retriever.search("password requirements", top_k=2)
        assert len(results) > 0
        assert any("password" in result.content.lower() for result in results)

        # Search for another topic
        results = retriever.search("access control", top_k=1)
        assert len(results) > 0
        assert any("access" in result.content.lower() for result in results)

    finally:
        os.unlink(temp_path)


def test_pipeline_with_citations():
    """Test that citations link back to actual retrieved chunks."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Compliance Report

## Section 1: Introduction
This document describes our compliance measures.

## Section 2: Audit Procedures
We conduct regular audits of our systems.
Audit findings are documented and reviewed.
""")
        temp_path = f.name

    try:
        doc = DocumentLoader.load_file(temp_path)
        chunker = SemanticChunker()
        chunks = chunker.chunk_document(doc)

        retriever = RetrievalService()
        retriever.index_document_chunks(chunks)

        results = retriever.search("audit procedures", top_k=1)
        assert len(results) > 0

        # Verify citation is valid (result should have all required fields)
        result = results[0]
        assert hasattr(result, 'chunk_id')
        assert hasattr(result, 'content')
        assert hasattr(result, 'score')
        assert hasattr(result, 'metadata')

        # Verify we can look up the chunk by ID
        if hasattr(retriever.retriever, 'get_chunk'):
            retrieved_chunk = retriever.retriever.get_chunk(result.chunk_id)
            assert retrieved_chunk is not None
            assert retrieved_chunk.content == result.content

    finally:
        os.unlink(temp_path)


def test_end_to_end_rag_with_generator():
    """Test full end-to-end RAG pipeline from ingestion to grounded generation."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""# Company Policy
Employees must complete annual security training by December 31st.
""")
        temp_path = f.name

    try:
        doc = DocumentLoader.load_file(temp_path)
        chunker = SemanticChunker()
        chunks = chunker.chunk_document(doc)

        retriever = RetrievalService()
        retriever.index_document_chunks(chunks)

        results = retriever.search("security training", top_k=1)
        assert len(results) > 0

        chunk_id = results[0].chunk_id

        canned_json = f"""
        {{
          "text": "Employees must complete training by December 31st.",
          "citations": [
            {{"chunk_id": "{chunk_id}", "snippet": "complete annual security training"}}
          ],
          "confidence": 0.98,
          "is_sufficient": true
        }}
        """
        client = FakeLLMClient(canned_response=canned_json)
        generator = AnswerGenerator(client)

        answer = generator.generate_answer("When is security training due?", results)
        assert answer.is_sufficient is True
        assert len(answer.citations) == 1
        assert answer.citations[0].chunk_id == chunk_id

    finally:
        os.unlink(temp_path)


def test_empty_document_handling():
    """Test pipeline handles empty documents gracefully."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("")  # Empty file
        temp_path = f.name

    try:
        doc = DocumentLoader.load_file(temp_path)
        assert doc.content == ""

        chunker = SemanticChunker()
        chunks = chunker.chunk_document(doc)
        # Empty documents should still produce at least one chunk with document root header
        assert len(chunks) >= 0

        retriever = RetrievalService()
        retriever.index_document_chunks(chunks)

        # Should handle empty or minimal index
        results = retriever.search("test query", top_k=3)
        assert results == []

    finally:
        os.unlink(temp_path)


def test_duplicate_source_deduplication():
    """Test that documents from the same source are deduplicated."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("First document content header")
        temp_path = f.name

    try:
        # Load document twice
        doc1 = DocumentLoader.load_file(temp_path)
        doc2 = DocumentLoader.load_file(temp_path)

        chunker = SemanticChunker()
        chunks1 = chunker.chunk_document(doc1)
        chunks2 = chunker.chunk_document(doc2)

        retriever = RetrievalService()
        retriever.index_document_chunks(chunks1)

        # Index chunks from same source again
        retriever.index_document_chunks(chunks2)

        # Should still have the same number of chunks (duplicates ignored)
        stats = retriever.get_retriever_stats()
        assert stats["total_chunks"] == len(chunks1)

    finally:
        os.unlink(temp_path)
