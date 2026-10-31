# Doc Intelligence AI

A production-ready Enterprise Document Intelligence & Policy Q&A system.

## Setup
1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`

## Environment Configuration
Copy `.env.example` to `.env` and configure your API keys and environment variables.

## Running the API Service

Start the FastAPI application with Uvicorn:

```bash
uvicorn src.main:app --reload
```

Interactive API documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

### Key Endpoints

- **`GET /health`**: Returns service health status without exposing credentials or internal state.
- **`POST /ingest/file`**: Upload and ingest document files (`.txt`, `.md`, `.pdf`).
- **`GET /documents`**: List summary of currently indexed documents.
- **`POST /query`**: Submit a natural language question and receive grounded answers with citations.

#### Example Query Payload:
```json
{
  "query": "What are the password length requirements?",
  "top_k": 3,
  "min_score": 0.1
}
```

#### Example Answer Response:
```json
{
  "text": "Passwords must contain at least 12 characters including uppercase, lowercase, numbers, and special characters.",
  "citations": [
    {
      "chunk_id": "chunk_a1b2c3d4",
      "snippet": "At least 12 characters"
    }
  ],
  "confidence": 0.95,
  "is_sufficient": true
}
```

## Running Tests

Run all unit and integration tests using pytest:

```bash
python -m pytest
```

## Python SDK / Core Module Usage Example

```python
from src.document_loader import DocumentLoader
from src.semantic_chunker import SemanticChunker
from src.vector_store import VectorStore

# 1. Load a document (.txt, .md, or .pdf)
doc = DocumentLoader.load_file("path/to/policy.pdf")

# 2. Chunk the document semantically preserving metadata
chunker = SemanticChunker(max_chunk_size=500, overlap=50)
chunks = chunker.chunk_document(doc)

# 3. Index chunks in the vector store
vector_store = VectorStore()
vector_store.index_chunks(chunks)

# 4. Retrieve relevant chunks for a query
results = vector_store.retrieve("security compliance guidelines", top_k=3)
for res in results:
    print(f"Score: {res['score']}")
    print(f"Source: {res['metadata']['filename']} (Page {res['metadata'].get('page_number', 'N/A')})")
    print(f"Content: {res['content']}\n")
```
