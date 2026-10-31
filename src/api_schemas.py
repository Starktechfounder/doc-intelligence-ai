from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="Service version")

class IngestRequest(BaseModel):
    file_path: Optional[str] = Field(None, description="Local path to file to ingest")
    # Alternatively, content and filename could be provided
    content: Optional[str] = Field(None, description="Raw text content to ingest")
    filename: Optional[str] = Field(None, description="Filename for raw text ingestion")

class IngestResponse(BaseModel):
    status: str = Field(..., description="Ingestion status")
    filename: str = Field(..., description="Name of ingested file")
    chunks_indexed: int = Field(..., description="Number of chunks indexed")

class QueryRequest(BaseModel):
    query: str = Field(..., description="Question to ask the document collection")
    top_k: int = Field(3, ge=1, le=10, description="Number of top chunks to retrieve")
    min_score: float = Field(0.0, ge=0.0, le=1.0, description="Minimum relevance score threshold")

class DocumentSummary(BaseModel):
    filename: str
    total_chunks: int
    metadata: Dict[str, Any]
