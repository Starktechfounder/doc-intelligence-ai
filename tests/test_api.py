import pytest
from fastapi.testclient import TestClient
from src.main import app, retrieval_service, get_llm_client
from src.llm_client import FakeLLMClient
import os
import json

client = TestClient(app)

# Mock LLM response for testing where chunk_id matches the generated chunk ID
class FakeLLMForAPI(FakeLLMClient):
    def generate(self, prompt, system_prompt=None):
        # Extract chunk_id from prompt if possible, or use a general mock
        # When results are empty (empty index), AnswerGenerator handles it directly without calling LLM.
        # When results are present, we inspect the prompt or return a valid chunk ID.
        # Let's inspect prompt for chunk_
        import re
        match = re.search(r'<source_document id="(chunk_[a-f0-9]+)">', prompt)
        chunk_id = match.group(1) if match else "chunk_0"

        mock_answer = {
            "text": "The audit procedures include regular reviews of system logs.",
            "citations": [{"chunk_id": chunk_id, "snippet": "regular reviews of system logs"}],
            "confidence": 0.9,
            "is_sufficient": True
        }
        return json.dumps(mock_answer)

def override_get_llm_client():
    return FakeLLMForAPI()

app.dependency_overrides[get_llm_client] = override_get_llm_client

@pytest.fixture(autouse=True)
def clear_state():
    """Clear retrieval index before each test."""
    retrieval_service.clear_index()

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}

def test_ingest_file_txt():
    content = b"Security Policy content here."
    response = client.post(
        "/ingest/file",
        files={"file": ("security.txt", content, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["filename"] == "security.txt"
    assert data["chunks_indexed"] > 0

def test_ingest_unsupported_file():
    response = client.post(
        "/ingest/file",
        files={"file": ("script.py", b"print('hello')", "text/x-python")}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_query_flow():
    # 1. Ingest a document
    client.post(
        "/ingest/file",
        files={"file": ("audit.txt", b"Audit procedures: regular reviews of system logs.", "text/plain")}
    )

    # 2. Query
    response = client.post(
        "/query",
        json={"query": "what are the audit procedures?", "top_k": 2}
    )
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "citations" in data
    assert data["is_sufficient"] is True
    assert len(data["citations"]) > 0

def test_query_empty_index():
    response = client.post(
        "/query",
        json={"query": "anything?", "top_k": 2}
    )
    assert response.status_code == 200
    data = response.json()
    # Should return "insufficient evidence" response from AnswerGenerator
    assert data["is_sufficient"] is False
    assert "could not find" in data["text"].lower()

def test_list_documents():
    client.post(
        "/ingest/file",
        files={"file": ("doc1.txt", b"Content 1", "text/plain")}
    )
    client.post(
        "/ingest/file",
        files={"file": ("doc2.txt", b"Content 2", "text/plain")}
    )

    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    filenames = [d["filename"] for d in data]
    assert "doc1.txt" in filenames
    assert "doc2.txt" in filenames
