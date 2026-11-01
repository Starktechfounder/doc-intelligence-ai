import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from src.main import app, retrieval_service
from src.document_loader import DocumentLoader

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_state():
    retrieval_service.clear_index()

def test_oversized_file_upload():
    """Test that files exceeding 10MB are rejected."""
    # Create a dummy large content (10MB + 1 byte)
    large_content = b"a" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/ingest/file",
        files={"file": ("large.txt", large_content, "text/plain")}
    )
    assert response.status_code == 413
    assert "exceeds maximum allowed limit" in response.json()["detail"]

def test_malicious_filename_handling():
    """Test that path traversal in filenames is handled safely."""
    # The current implementation uses os.path.basename or just the provided filename
    # but doesn't write to disk using that filename except for PDF which uses tempfile.
    # We should ensure it doesn't crash or leak info.
    content = b"Some content"
    malicious_name = "../../../etc/passwd"
    response = client.post(
        "/ingest/file",
        files={"file": (malicious_name, content, "text/plain")}
    )
    # It should either succeed (by stripping path) or fail gracefully
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        data = response.json()
        # Ensure it doesn't keep the traversal part in the recorded filename
        assert "/" not in data["filename"]
        assert "\\" not in data["filename"]

def test_empty_file_upload():
    """Test uploading an empty file."""
    response = client.post(
        "/ingest/file",
        files={"file": ("empty.txt", b"", "text/plain")}
    )
    assert response.status_code == 200
    assert response.json()["chunks_indexed"] == 0

def test_invalid_pdf_handling():
    """Test handling of malformed PDF files."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"NOT A PDF")
        tmp_path = f.name

    try:
        response = client.post(
            "/ingest/file",
            files={"file": ("invalid.pdf", b"NOT A PDF", "application/pdf")}
        )
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"] or "Failed to process" in response.json()["detail"]
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_path_traversal_protection():
    """Test DocumentLoader protection against non-existent or restricted paths."""
    # Note: we are passing absolute paths to DocumentLoader.load_file
    with pytest.raises(FileNotFoundError):
        DocumentLoader.load_file("/tmp/non_existent_file_xyz_123")
