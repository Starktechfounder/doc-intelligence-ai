import re
from typing import List, Dict, Any
from .document_loader import Document

class Chunk:
    """Represents a chunk of text with rich metadata for LLM citation."""
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata

    def __repr__(self):
        return f"Chunk(content_len={len(self.content)}, metadata={self.metadata})"

class SemanticChunker:
    """
    Splits documents into semantic chunks respecting paragraph/section boundaries
    and attaching rich metadata (filename, section header, page number).
    """
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: Document) -> List[Chunk]:
        """Splits a Document into semantic chunks with metadata."""
        text = doc.content
        base_meta = doc.metadata.copy()

        # Split text by section headers or double newlines (paragraphs)
        # We look for markdown headers (#, ##, ###) or page separators (--- Page X ---)
        sections = self._split_into_sections(text)

        chunks = []
        for section_header, section_text in sections:
            # Update metadata with current section header
            section_meta = base_meta.copy()
            if section_header:
                section_meta["section_header"] = section_header

            # Now chunk the section text into pieces fitting max_chunk_size
            section_chunks = self._chunk_text(section_text, self.max_chunk_size, self.overlap)

            for chunk_idx, chunk_text in enumerate(section_chunks):
                chunk_text = chunk_text.strip()
                if not chunk_text:
                    continue

                # Try to detect page number if present in text/metadata (e.g. from PDF loader)
                page_num = self._detect_page_number(chunk_text)
                final_meta = section_meta.copy()
                if page_num is not None:
                    final_meta["page_number"] = page_num

                final_meta["chunk_index"] = len(chunks)

                chunks.append(Chunk(content=chunk_text, metadata=final_meta))

        return chunks

    def _split_into_sections(self, text: str) -> List[tuple]:
        """Splits text by markdown headers or page markers."""
        # Regex to match Markdown headers or PDF page markers
        pattern = r'(^(?:#{1,6}\s+.+|--- Page \d+ ---))'
        parts = re.split(pattern, text, flags=re.MULTILINE)

        sections = []
        current_header = "Introduction"
        current_text_parts = []

        for part in parts:
            if not part.strip():
                continue
            if re.match(r'^(#{1,6}\s+.+|--- Page \d+ ---)', part.strip()):
                # If we have accumulated text for the previous header, save it
                if current_text_parts:
                    sections.append((current_header, "\n".join(current_text_parts)))
                    current_text_parts = []
                current_header = part.strip()
            else:
                current_text_parts.append(part)

        if current_text_parts or current_header:
            sections.append((current_header, "\n".join(current_text_parts)))

        if not sections:
            sections = [("Document Root", text)]

        return sections

    def _chunk_text(self, text: str, max_size: int, overlap: int) -> List[str]:
        """Splits text by paragraphs first, then combines or splits to fit max_size."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_len = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_len = len(para)
            if current_len + para_len + 2 <= max_size:
                current_chunk.append(para)
                current_len += para_len + 2
            else:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                # If single paragraph is larger than max_size, split by sentences or characters
                if para_len > max_size:
                    sub_chunks = self._split_large_paragraph(para, max_size, overlap)
                    chunks.extend(sub_chunks)
                    current_chunk = []
                    current_len = 0
                else:
                    current_chunk = [para]
                    current_len = para_len

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def _split_large_paragraph(self, paragraph: str, max_size: int, overlap: int) -> List[str]:
        """Splits a massive paragraph into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(paragraph):
            end = min(start + max_size, len(paragraph))
            chunks.append(paragraph[start:end])
            start += max_size - overlap
        return chunks

    def _detect_page_number(self, text: str) -> Optional[int]:
        """Detects page number from PDF page markers if present."""
        match = re.search(r'--- Page (\d+) ---', text)
        if match:
            return int(match.group(1))
        return None
