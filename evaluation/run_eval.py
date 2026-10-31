import time
import json
import os
from typing import List, Dict, Any
from src.document_loader import Document
from src.semantic_chunker import SemanticChunker
from src.retrieval_interface import RetrievalService
from src.answer_generator import AnswerGenerator
from src.llm_client import FakeLLMClient
from evaluation.mock_llm import ValidatingFakeLLMClient

class Evaluator:
    def __init__(self, retrieval_service: RetrievalService, llm_client=None):
        self.retrieval_service = retrieval_service
        self.llm_client = llm_client or FakeLLMClient()
        self.generator = AnswerGenerator(self.llm_client)

    def run_evaluation(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        total_latency = 0

        for item in dataset:
            start_time = time.time()

            # 1. Retrieval
            retrieval_results = self.retrieval_service.search(item["query"], top_k=5)

            # 2. Answer Generation
            answer = self.generator.generate_answer(item["query"], retrieval_results)

            latency = time.time() - start_time
            total_latency += latency

            # 3. Simple Metrics
            # Retrieval success: Was the expected document found in the top results?
            retrieval_success = any(
                item["expected_document"].lower() in res.metadata.get("filename", "").lower()
                for res in retrieval_results
            )

            # Answer faithfulness (keyword check)
            matched_keywords = []
            for kw in item["expected_keywords"]:
                if kw.lower() in answer.text.lower():
                    matched_keywords.append(kw)

            keyword_score = len(matched_keywords) / len(item["expected_keywords"]) if item["expected_keywords"] else 1.0

            # Citation validity
            valid_citations = 0
            retrieved_ids = {res.chunk_id for res in retrieval_results}
            for cit in answer.citations:
                if cit.chunk_id in retrieved_ids:
                    valid_citations += 1

            results.append({
                "id": item["id"],
                "query": item["query"],
                "retrieval_success": retrieval_success,
                "keyword_score": keyword_score,
                "matched_keywords": matched_keywords,
                "citation_count": len(answer.citations),
                "valid_citations": valid_citations,
                "latency": latency,
                "is_sufficient": answer.is_sufficient
            })

        # Summary metrics
        count = len(results)
        summary = {
            "total_queries": count,
            "avg_latency": total_latency / count if count > 0 else 0,
            "retrieval_accuracy": sum(r["retrieval_success"] for r in results) / count if count > 0 else 0,
            "avg_keyword_score": sum(r["keyword_score"] for r in results) / count if count > 0 else 0,
            "results": results
        }

        return summary

if __name__ == "__main__":
    # Setup mock environment for evaluation
    rs = RetrievalService()
    chunker = SemanticChunker()

    # Ingest mock documents
    docs = [
        Document("Users must create passwords with at least 12 characters, including special characters, upper and lower case letters.", {"filename": "security_policy.txt"}),
        Document("Access is granted based on role and need-to-know principles.", {"filename": "security_policy.txt"}),
        Document("We conduct regular reviews of system logs and audits.", {"filename": "compliance_report.md"})
    ]

    for doc in docs:
        rs.index_document_chunks(chunker.chunk_document(doc))

    # Load dataset
    dataset_path = os.path.join("evaluation", "data", "eval_dataset.json")
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    evaluator = Evaluator(rs, llm_client=ValidatingFakeLLMClient())
    report = evaluator.run_evaluation(dataset)

    # Save report
    report_dir = os.path.join("evaluation", "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"baseline_{int(time.time())}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Evaluation complete. Report saved to {report_path}")
    print(f"Retrieval Accuracy: {report['retrieval_accuracy']:.2%}")
    print(f"Avg Keyword Score: {report['avg_keyword_score']:.2%}")
    print(f"Avg Latency: {report['avg_latency']:.4f}s")
