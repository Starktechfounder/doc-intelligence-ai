# Doc Intelligence AI

A production-ready Enterprise Document Intelligence & Policy Q&A system.

## Setup
1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`

## Environment Configuration
Copy `.env.example` to `.env` and configure your API keys and environment variables.

## Usage Example: Document Loading, Chunking & Retrieval

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
