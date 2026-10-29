import os
import pytest
from src.document_loader import Document, DocumentLoader
from src.semantic_chunker import SemanticChunker, Chunk

def tmp_file(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)

def test_document_loader_txt(tmp_path):
    path = tmp_file(tmp_path, "test.txt", "Hello world text file.")
    doc = DocumentLoader.load_file(path)
    assert doc.content == "Hello world text file."
    assert doc.metadata["filename"] == "test.txt"
    assert doc.metadata["file_type"] == ".txt"

def test_document_loader_not_found():
    with pytest.raises(FileNotFoundError):
        DocumentLoader.load_file("non_existent_file_12345.txt")

def test_document_loader_unsupported(tmp_path):
    path = tmp_file(tmp_path, "test.xyz", "unknown format")
    with pytest.raises(ValueError):
        DocumentLoader.load_file(path)

def test_semantic_chunker_basic():
    content = "# Section One\n\nThis is paragraph one of section one.\n\nThis is paragraph two of section one.\n\n## Section Two\n\nParagraph in section two."
    doc = Document(content=content, metadata={"filename": "doc.md"})

    chunker = SemanticChunker(max_chunk_size=150, overlap=20)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) > 0
    for chunk in chunks:
        assert isinstance(chunk, Chunk)
        assert len(chunk.content.strip()) > 0
        assert "filename" in chunk.metadata
        assert "section_header" in chunk.metadata

def test_semantic_chunker_no_empty_chunks():
    content = "\n\n\n   \n\n# Header\n\n   \nParagraph text here."
    doc = Document(content=content, metadata={"filename": "empty_test.txt"})
    chunker = SemanticChunker(max_chunk_size=500, overlap=50)
    chunks = chunker.chunk_document(doc)

    for chunk in chunks:
        assert chunk.content.strip() != ""
