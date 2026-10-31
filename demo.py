"""
Demo script for Doc Intelligence AI Pipeline.
Demonstrates document loading, semantic chunking, indexing, retrieval, and grounded answer generation.
"""

import tempfile
import os
from src.document_loader import DocumentLoader
from src.semantic_chunker import SemanticChunker
from src.retrieval_interface import RetrievalService
from src.answer_generator import AnswerGenerator
from src.llm_client import FakeLLMClient

def main():
    print("=" * 60)
    print("Doc Intelligence AI - Pipeline Demonstration")
    print("=" * 60)

    # 1. Create a sample policy document
    sample_content = """# Corporate Security Policy

## 1. Password Management
All employees must use strong passwords for corporate accounts.
Passwords must meet the following criteria:
- Minimum length of 12 characters
- Must contain uppercase and lowercase letters
- Must contain at least one number and one special character
- Must be changed every 90 days

## 2. Multi-Factor Authentication (MFA)
MFA is mandatory for all access to production systems, staging environments,
and internal corporate portals. Hardware tokens or authenticator apps are required.

## 3. Incident Response
Any security incident or suspected breach must be reported to the security team
within 24 hours via the internal #security-incident Slack channel or emergency hotline.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(sample_content)
        temp_path = f.name

    try:
        print(f"\n[1] Loading sample document from temporary file: {temp_path}")
        doc = DocumentLoader.load_file(temp_path)
        print(f"    - Loaded document successfully. Characters: {len(doc.content)}")
        print(f"    - Metadata: {doc.metadata}")

        print("\n[2] Chunking document semantically...")
        chunker = SemanticChunker(max_chunk_size=300, overlap=50)
        chunks = chunker.chunk_document(doc)
        print(f"    - Generated {len(chunks)} chunks.")
        for i, chunk in enumerate(chunks):
            print(f"      Chunk {i+1} [ID: {chunk.metadata.get('id', 'N/A')}]: {chunk.content[:60]}...")

        print("\n[3] Indexing chunks in Retrieval Service...")
        retriever = RetrievalService()
        retriever.index_document_chunks(chunks)
        stats = retriever.get_retriever_stats()
        print(f"    - Index stats: {stats}")

        print("\n[4] Performing Retrieval Searches...")
        queries = [
            "What are the password requirements?",
            "When is MFA mandatory?",
            "How do I report a security incident?"
        ]

        for query in queries:
            print(f"\n    Query: \"{query}\"")
            results = retriever.search(query, top_k=2)
            for j, res in enumerate(results):
                print(f"      [{j+1}] Score: {res.score:.4f} | Source: {res.metadata.get('filename')}")
                print(f"          Snippet: {res.content.strip().replace(chr(10), ' ')}")

        print("\n[5] Generating Grounded Answer with Citations (RAG)...")
        query = "What are the rules for passwords and MFA?"
        results = retriever.search(query, top_k=2)

        chunk_id = results[0].chunk_id if results else "unknown"
        canned_json = f"""
        {{
          "text": "Corporate policy requires passwords to be at least 12 characters long with mixed case, numbers, and special characters, changed every 90 days. Additionally, Multi-Factor Authentication (MFA) is mandatory for all production systems, staging, and internal portals.",
          "citations": [
            {{"chunk_id": "{chunk_id}", "snippet": "Minimum length of 12 characters"}}
          ],
          "confidence": 0.95,
          "is_sufficient": true
        }}
        """
        client = FakeLLMClient(canned_response=canned_json)
        generator = AnswerGenerator(client)

        answer = generator.generate_answer(query, results)
        print(f"    Query: {query}")
        print(f"    Answer: {answer.text}")
        print(f"    Confidence: {answer.confidence}")
        print(f"    Sufficient: {answer.is_sufficient}")
        print("    Citations:")
        for cit in answer.citations:
            print(f"      - Chunk ID: {cit.chunk_id}")
            print(f"        Snippet: \"{cit.snippet}\"")

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    main()
