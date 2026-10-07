# DocOps AI

Ask questions about your PDFs and get answers with **page-level citations**.
A document-intelligence and RAG (retrieval-augmented generation) project, built step by step with engineering practices from day one.

> **Work in progress.** The ingestion layer is built and tested; retrieval, LLM answers, evaluation and MLOps are next.

## How it works

```
PDF -> parse -> clean -> chunk -> embed -> index (Qdrant) -> retrieve -> LLM answer + citations
```

## Roadmap

- [x] Project skeleton, tooling, first push
- [x] PDF ingestion: text, page number, metadata
- [x] Text cleaning: invisible characters, repeated headers, footers and page numbers
- [ ] Chunking with several sizes compared on real documents *(in progress)*
- [ ] Embeddings (multilingual model comparison)
- [ ] Qdrant setup and retrieval
- [ ] First end-to-end question returning relevant chunks (MVP)
- [ ] LLM generation with citations
- [ ] Retrieval experiments: chunk size, overlap, embedding model, top-k, reranking
- [ ] 100-question evaluation benchmark and first formal evaluation
- [ ] Service layer: FastAPI, PostgreSQL, Docker, structured logging, error handling
- [ ] MLOps: MLflow experiment tracking, GitHub Actions CI, versioned Docker image
- [ ] Security and monitoring: prompt-injection and data-leakage tests, structured outputs and guardrails
- [ ] Cloud deployment (AWS); Kubernetes only if everything else is solid

## What this project shows

- **RAG pipeline design**: every chunk keeps its source, page and character offsets, so answers can be verified.
- **Working with messy real data**: tested on French course material, lab reports and job postings, not only clean samples.
- **Evaluation mindset**: chunking, embedding and retrieval choices will be measured on a benchmark, not guessed.
- **Software engineering habits**: tests, linting, pull requests, reproducible builds.

## Try it

```bash
git clone git@github.com:aissameddine/docops-ai.git
cd docops-ai
uv sync
make test
```

```python
from docops_ai.chunking import ChunkingConfig, chunk_pages
from docops_ai.ingestion import ingest_pdf

pages = ingest_pdf("data/raw/report.pdf")  # your own PDF (data/raw is git-ignored)
chunks = chunk_pages(pages, ChunkingConfig(chunk_size=800, overlap=100))
print(len(pages), "pages ->", len(chunks), "chunks")
```

## Tech stack

Python 3.12 · PyMuPDF · Pydantic · pytest · ruff · uv
Planned: sentence-transformers · Qdrant · FastAPI · PostgreSQL · MLflow · Docker · GitHub Actions

## Author

Aissam Eddine Boukhelkhal, Master 2 Data Science, looking for an AI / ML engineering internship starting early 2027.
[LinkedIn](www.linkedin.com/in/aissam-eddine-boukhelkhal-769162192) · aissam-eddine.boukhelkhal@etu.univ-lyon1.fr