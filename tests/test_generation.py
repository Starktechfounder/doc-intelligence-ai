import pytest
from src.answer_generator import AnswerGenerator
from src.llm_client import FakeLLMClient
from src.retrieval_interface import RetrievalResult

def test_answer_generator_insufficient_evidence():
    client = FakeLLMClient()
    generator = AnswerGenerator(client)

    answer = generator.generate_answer("What is the security policy?", [])
    assert answer.is_sufficient is False
    assert "sufficient evidence" in answer.text.lower()
    assert len(answer.citations) == 0

def test_answer_generator_valid_citation():
    canned_json = """
    {
      "text": "Passwords must be at least 12 characters long.",
      "citations": [
        {"chunk_id": "chunk_123", "snippet": "At least 12 characters"}
      ],
      "confidence": 0.95,
      "is_sufficient": true
    }
    """
    client = FakeLLMClient(canned_response=canned_json)
    generator = AnswerGenerator(client)

    results = [
        RetrievalResult(
            chunk_id="chunk_123",
            content="Users must create passwords with at least 12 characters.",
            score=0.9,
            metadata={"filename": "security.md"}
        )
    ]

    answer = generator.generate_answer("What are password requirements?", results)
    assert answer.is_sufficient is True
    assert len(answer.citations) == 1
    assert answer.citations[0].chunk_id == "chunk_123"

def test_answer_generator_rejects_hallucinated_citation():
    canned_json = """
    {
      "text": "Passwords must be secure.",
      "citations": [
        {"chunk_id": "chunk_fake_999", "snippet": "Secure passwords"}
      ],
      "confidence": 0.9,
      "is_sufficient": true
    }
    """
    client = FakeLLMClient(canned_response=canned_json)
    generator = AnswerGenerator(client)

    results = [
        RetrievalResult(
            chunk_id="chunk_123",
            content="Users must create passwords.",
            score=0.9,
            metadata={"filename": "security.md"}
        )
    ]

    answer = generator.generate_answer("What are password requirements?", results)
    # Hallucinated citation chunk_fake_999 should be filtered out
    assert len(answer.citations) == 0
