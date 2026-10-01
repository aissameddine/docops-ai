# DocOps AI

Production-grade document intelligence + RAG platform: PDF ingestion, retrieval,
grounded answers with citations, evaluation benchmark, and an MLOps layer.

Status: early development (week 1, building the ingestion and retrieval MVP).

## Setup

```bash
uv sync
make check
make test
```

## Structure

`src/docops_ai/` holds ingestion, chunking, embeddings, retrieval, generation and api.
