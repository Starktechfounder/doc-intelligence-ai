# Doc Intelligence AI

A production-ready Enterprise Document Intelligence & Policy Q&A system.

## Problem Statement & Architecture

Enterprise organizations possess vast amounts of unstructured policies, SOPs, and compliance documents. Searching through these manually is slow, error-prone, and inefficient. 

**Doc Intelligence AI** provides an end-to-end Retrieval-Augmented Generation (RAG) platform that ingests unstructured files (`.txt`, `.md`, `.pdf`), semantically chunks content preserving section headers and metadata, and serves grounded Q&A with strict source citation verification.

```
┌─────────────────┐      ┌─────────────────────────┐      ┌────────────────────────┐
│  React Frontend │ ───> │  FastAPI Backend Service │ ───> │ Lexical Vector Store   │
│  (Vite + TS)    │ <─── │  (Ingestion & Retrieval)│ <─── │ (TF-IDF + Cosine Sim)  │
└─────────────────┘      └─────────────────────────┘      └────────────────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │ Grounded Answer Generator│
                         │ (Citation Verification)  │
                         └──────────────────────────┘
```

## Features & Verification

- **Multi-Format Document Ingestion**: Ingests Markdown, plain text, and PDF files.
- **Semantic Chunking**: Splits documents respecting paragraph and section header boundaries.
- **Lexical Vector Search**: TF-IDF similarity search with source deduplication and stable chunk hashing.
- **Grounded Q&A Generation**: LLM-generated responses with citation validation to eliminate hallucinations.
- **Interactive UI**: Modern React frontend with document management, adjustable retrieval parameters, and citation inspector.
- **Containerized Deployment**: Docker and Docker Compose configuration for easy reproducible deployment.

## Deployment with Docker

Run the complete stack via Docker Compose:

```bash
docker-compose up --build
```

- **Frontend**: Accessible at `http://localhost:5173`
- **Backend API**: Accessible at `http://localhost:8000`
- **API Docs**: Available at `http://localhost:8000/docs`

## Manual Local Setup

1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
3. Install dependencies: `pip install -r requirements.txt`
4. Setup environment variables: `cp .env.example .env`
5. Run the backend API: `uvicorn src.main:app --reload`
6. Run the frontend: `cd frontend && npm install && npm run dev`

## Evaluation Suite

Run the baseline quality evaluation suite:

```bash
python -m evaluation.run_eval
```

Sample evaluation outcomes:
- **Retrieval Accuracy**: 100.0%
- **Average Keyword Match**: ~33.3%
- **Average Latency**: <1ms

## Security & Reliability Controls

- **Upload Limits**: 10MB maximum file size limit enforced.
- **Path Traversal Defenses**: Strips path separators from filenames.
- **Safe Exception Handling**: Global exception interceptor to avoid credential leaks.
- **Citation Verification**: Filters out hallucinated chunk IDs automatically.

## Running Tests

Run all unit and integration tests using pytest:

```bash
python -m pytest
```
