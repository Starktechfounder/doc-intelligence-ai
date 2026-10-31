from pydantic import BaseModel, Field
from typing import List, Optional

class Citation(BaseModel):
    chunk_id: str = Field(..., description="The unique ID of the chunk used as source evidence.")
    snippet: str = Field(..., description="The specific snippet from the chunk that supports the claim.")

class Answer(BaseModel):
    text: str = Field(..., description="The generated answer based on the provided evidence.")
    citations: List[Citation] = Field(default_factory=list, description="List of citations linking claims to source chunks.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the answer.")
    is_sufficient: bool = Field(..., description="Whether the provided evidence was sufficient to answer the question.")
