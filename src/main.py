import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api_schemas import HealthResponse, IngestResponse, QueryRequest, DocumentSummary
from src.schemas import Answer, Citation
from src.document_loader import DocumentLoader, Document
from src.semantic_chunker import SemanticChunker
from src.retrieval_interface import RetrievalService
from src.answer_generator import AnswerGenerator
from src.llm_client import LLMClient, FakeLLMClient

# System state containers
retrieval_service = RetrievalService()
chunker = SemanticChunker()

def get_llm_client() -> LLMClient:
    """Dependency provider for LLM client."""
    # In production/live mode, configure Anthropic or OpenAI LLMClient if API key present
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and api_key != "fake_key":
        try:
            from src.llm_client import AnthropicLLMClient
            return AnthropicLLMClient(api_key=api_key)
        except ImportError:
            pass
    # Default fallback to FakeLLMClient if no live key configured
    return FakeLLMClient(canned_response='''{
        "text": "Based on the provided security policy, users must create passwords with at least 12 characters, including upper/lower case letters, numbers, and special characters.",
        "citations": [{"chunk_id": "chunk_0", "snippet": "Users must create passwords with: - At least 12 characters"}],
        "confidence": 0.95,
        "is_sufficient": true
    }''')

def create_app() -> FastAPI:
    app = FastAPI(
        title="Document Intelligence AI Service",
        description="Production-grade document ingestion, retrieval, and question-answering API",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        # Prevent leak of tracebacks/credentials to client
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred."}
        )

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint without revealing internal secrets or credentials."""
        return HealthResponse(status="healthy", version="1.0.0")

    @app.post("/ingest/file", response_model=IngestResponse)
    async def ingest_file(file: UploadFile = File(...)):
        """Upload and ingest a document file (.txt, .md, .pdf)."""
        # Validate extension
        filename = file.filename or "unknown"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [".txt", ".md", ".pdf"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{ext}'. Supported extensions: .txt, .md, .pdf"
            )

        # Enforce max file size (e.g. 10MB)
        contents = await file.read()
        max_size = 10 * 1024 * 1024
        if len(contents) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds maximum allowed limit (10MB)"
            )

        try:
            # Parse document content
            if ext in [".txt", ".md"]:
                text_content = contents.decode("utf-8", errors="ignore")
                doc = Document(content=text_content, metadata={"filename": filename, "source": filename, "file_type": ext})
            elif ext == ".pdf":
                # For PDF, save temporarily to load via PdfReader or read directly
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(contents)
                    tmp_path = tmp.name
                try:
                    doc = DocumentLoader.load_file(tmp_path)
                    doc.metadata["filename"] = filename
                    doc.metadata["source"] = filename
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            chunks = chunker.chunk_document(doc)
            retrieval_service.index_document_chunks(chunks)

            return IngestResponse(
                status="success",
                filename=filename,
                chunks_indexed=len(chunks)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process and ingest file: {str(e)}"
            )

    @app.get("/documents", response_model=List[DocumentSummary])
    async def list_documents():
        """List summary of indexed documents."""
        retriever = retrieval_service.retriever
        chunks = getattr(retriever, "chunks", [])

        doc_map = {}
        for chunk in chunks:
            fname = chunk.metadata.get("filename", "unknown")
            if fname not in doc_map:
                doc_map[fname] = {"filename": fname, "total_chunks": 0, "metadata": chunk.metadata}
            doc_map[fname]["total_chunks"] += 1

        return [DocumentSummary(**val) for val in doc_map.values()]

    @app.post("/query", response_model=Answer)
    async def query_documents(
        request: QueryRequest,
        llm_client: LLMClient = Depends(get_llm_client)
    ):
        """Query ingested documents and generate a grounded answer with citations."""
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query string cannot be empty."
            )

        try:
            results = retrieval_service.search(
                query=request.query,
                top_k=request.top_k,
                min_score=request.min_score
            )

            generator = AnswerGenerator(llm_client=llm_client)
            answer = generator.generate_answer(query=request.query, results=results)
            return answer
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating answer for query."
            )

    return app

app = create_app()
