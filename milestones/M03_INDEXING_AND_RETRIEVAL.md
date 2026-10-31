# M03 --- Indexing and Retrieval

## Objective

Turn chunks into searchable records and retrieve the most relevant evidence for a user question.

## Scope

-   Stable chunk identifiers
-   A simple lexical baseline (for example TF-IDF or BM25, depending on dependencies)
-   Optional embedding/vector-store adapter only if justified
-   Top-k retrieval with source metadata and scores
-   Deterministic relevance tests

## Tasks

1.  Inspect the chunk schema and select a stable ID strategy.
2.  Define a small retriever interface independent of a specific backend.
3.  Implement a lexical baseline and document tokenization/normalization behavior.
4.  If embeddings are considered, compare complexity, local/API cost, privacy, and measurable retrieval gains before selecting a provider.
5.  Return chunk text, source metadata, stable ID, and a score from retrieval.
6.  Define behavior for empty query, empty index, duplicate ingestion, and no useful matches.
7.  Create a small test corpus with questions and expected relevant sources.
8.  Add tests for ranking, metadata preservation, top-k limits, and empty states.
9.  Measure baseline results and record limitations.

## Acceptance criteria

-   [ ] Chunks can be indexed and queried through a stable interface.
-   [ ] Results are ranked and include source metadata.
-   [ ] Empty/invalid queries and empty indexes are handled predictably.
-   [ ] Duplicate-ingestion behavior is defined and tested.
-   [ ] Relevance tests demonstrate that known relevant chunks rank appropriately.
-   [ ] Tests do not require a live model API.
-   [ ] The chosen design and trade-offs are recorded.

## Deliverables

Indexer, retriever interface, baseline implementation, retrieval tests, and a small evaluation dataset.

## Evidence to record

Example query, top retrieved chunks, source IDs, scores, and measured baseline results.

## Risks

Lexical search misses semantic paraphrases; vector search adds dependency, latency, and cost. Do not choose a more complex backend without evidence.

## Status note

Previously reported complete; verify current implementation before moving on.