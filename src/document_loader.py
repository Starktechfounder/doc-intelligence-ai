import os
from typing import List, Dict, Any, Optional
from pypdf import PdfReader

class Document:
    """Represents a loaded document with text content and metadata."""
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata

class DocumentLoader:
    """Robust utility to read files (.txt, .md, .pdf)."""

    @staticmethod
    def load_file(file_path: str) -> Document:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".txt", ".md"]:
            return DocumentLoader._load_text(file_path)
        elif ext == ".pdf":
            return DocumentLoader._load_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    @staticmethod
    def _load_text(file_path: str) -> Document:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        filename = os.path.basename(file_path)
        return Document(
            content=content,
            metadata={
                "filename": filename,
                "source": file_path,
                "file_type": os.path.splitext(file_path)[1].lower()
            }
        )

    @staticmethod
    def _load_pdf(file_path: str) -> Document:
        reader = PdfReader(file_path)
        text_parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text_parts.append(f"--- Page {i + 1} ---\n{page_text}")

        content = "\n\n".join(text_parts)
        filename = os.path.basename(file_path)
        return Document(
            content=content,
            metadata={
                "filename": filename,
                "source": file_path,
                "file_type": ".pdf",
                "total_pages": len(reader.pages)
            }
        )
