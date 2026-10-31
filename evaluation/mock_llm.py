import json
from typing import Optional
from src.llm_client import LLMClient

class ValidatingFakeLLMClient(LLMClient):
    """Fake client that returns a valid JSON answer based on content."""
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # Check if the prompt contains expected evidence

        # Need to find the actual chunk ID from the prompt which looks like:
        # <source_document id="chunk_...">
        import re
        chunk_match = re.search(r'<source_document id="(chunk_[a-f0-9]+)">', prompt)
        chunk_id = chunk_match.group(1) if chunk_match else "chunk_0"

        if "12 characters" in prompt:
            text = "Users must create passwords with at least 12 characters, including special characters, upper and lower case letters."
            citations = [{"chunk_id": chunk_id, "snippet": "at least 12 characters"}]
        elif "role and need-to-know" in prompt:
            text = "Access is granted based on role and need-to-know principles."
            citations = [{"chunk_id": chunk_id, "snippet": "role and need-to-know"}]
        elif "regular reviews" in prompt:
            text = "Audit procedures involve regular reviews of system logs and audits."
            citations = [{"chunk_id": chunk_id, "snippet": "regular reviews"}]
        else:
            text = "Evidence is insufficient."
            citations = []

        return json.dumps({
            "text": text,
            "citations": citations,
            "confidence": 0.99,
            "is_sufficient": len(citations) > 0
        })
