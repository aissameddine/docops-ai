# DocOps AI

**Ask questions about your documents in plain language and get answers backed by citations** (document name and page number).

DocOps AI is an end-to-end RAG project (retrieval-augmented generation), built step by step with engineering practices from the start: tests, linting, reproducible setup, and measured decisions.

> **Work in progress.** The document-processing half of the pipeline (reading PDFs, cleaning them, splitting them into chunks) is built and tested. Search, answer generation, evaluation and deployment come next. Every step is logged in [docs/devlog.md](docs/devlog.md).

## The problem

Language models write fluent answers, but they can invent facts and they know nothing about your private documents. **RAG** fixes both: first *find* the passages of your documents that are relevant to a question, then let the model answer using only those passages, and show where the answer came from.

Doing this well is mostly an engineering problem: PDFs are messy, search quality has to be measured rather than assumed, and the whole thing has to be reproducible. That is what this project focuses on.

## What it will do

*Illustrative example of the target behaviour (not implemented yet):*

```
Question:  Which MPI call starts a send without waiting for it to finish?
Answer:    MPI_Isend starts the send and returns immediately; completion is
           checked later with MPI_Wait or MPI_Waitall.
Sources:   lab_report.pdf, page 6
```

## How it works

| Stage | What it does | Status |
|---|---|---|
| 1. Parse | Read each PDF page by page: text, page number, metadata | Done |
| 2. Clean | Fix defects found in real PDFs (see below) | Done |
| 3. Chunk | Cut pages into overlapping passages of controlled size | Done |
| 4. Embed | Turn each passage into a vector that captures its meaning | Planned |
| 5. Index and search | Store vectors in Qdrant, retrieve the closest passages to a question | Planned |
| 6. Answer | Give the passages to an LLM, require a cited answer | Planned |
| 7. Evaluate | Score retrieval and answers on a 100-question benchmark | Planned |
| 8. Ship | API, Docker, CI/CD, experiment tracking, monitoring | Planned |

## What is built so far

- **PDF ingestion.** One validated record per page, with page number, source file and a stable document ID (a hash of the file), so re-processing the same file never creates duplicates. Missing, corrupt and password-protected files raise one clear error, each covered by a test.
- **Cleaning of real-world defects**, found by running the code on real French PDFs (course material, lab reports, administrative documents) rather than clean samples:
  - invisible characters and typographic ligatures (`ﬁ` stored as one character), which break search;
  - words split by hyphens at line ends (`structu-` / `relles`);
  - repeated headers, footers and page numbers, removed at document level and kept in metadata rather than discarded;
  - source-code line numbers, which made 42-57% of a lab report's chunks mostly bare numbers. After the fix: 7-14%.
- **Page-aware chunking.** Configurable size and overlap; a chunk never crosses a page break, so every citation points to one exact page. Each chunk keeps its character offsets in the page text.
- **A measured default.** A small script compares chunk sizes and overlaps on real documents. Overlap removed tiny leftover fragments (smallest chunk went from 8 to 85 characters) at almost no cost, so the default is 800 characters with 100 overlap, to be re-checked on retrieval quality later.
- **Engineering base.** Reproducible environment (`uv` and a lockfile), automated tests (`pytest`), linting and formatting (`ruff`), pre-commit hooks, and work done through pull requests.

## Skills demonstrated

| Skill | Evidence in this repo | Status |
|---|---|---|
| Document processing and data cleaning | Ingestion, cleaning, layout handling | Built |
| Software engineering practices | Tests, linting, pre-commit, pull requests, reproducible setup | Built |
| Evidence-based decisions | Stats script, results tables in the devlog | Built |
| RAG: embeddings, vector search, cited answers | Qdrant, multilingual embedding models, LLM generation | Planned |
| Evaluation | 100-question benchmark, retrieval and answer metrics | Planned |
| MLOps | Docker, GitHub Actions CI, MLflow experiment tracking | Planned |
| Agentic AI and safety | Structured outputs, tool calling, guardrails, prompt-injection tests | Planned |

## Roadmap

- [x] Project skeleton, tooling, first push
- [x] PDF ingestion: text, page number, metadata
- [x] Text cleaning and chunking, compared on real documents
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

pages = ingest_pdf("data/raw/report.pdf")   # your own PDF (data/raw is git-ignored)
chunks = chunk_pages(pages, ChunkingConfig(chunk_size=800, overlap=100))
print(len(pages), "pages ->", len(chunks), "chunks")
print(chunks[0].source, "page", chunks[0].page_number)
```

<details>
<summary><b>Glossary for non-specialists</b></summary>

- **RAG (retrieval-augmented generation):** search your documents first, then let an AI model answer using only what was found.
- **Chunk:** a short passage of a document (here around 800 characters), the unit that gets searched.
- **Embedding:** a list of numbers representing the meaning of a text, so that similar texts end up close together.
- **Vector database (Qdrant):** a database that finds the closest embeddings to a question quickly.
- **Evaluation benchmark:** a fixed set of questions with known answers, used to measure whether a change really improves the system.
- **MLOps:** the practices that make an ML system reproducible, tested and deployable.

</details>

## Tech stack

Python 3.12 · PyMuPDF · Pydantic · pytest · ruff · uv
Planned: sentence-transformers · Qdrant · FastAPI · PostgreSQL · MLflow · Docker · GitHub Actions · AWS

## Author

Aissam Eddine Boukhelkhal, Master 2 Data Science, looking for an AI / ML engineering internship starting early 2027.
[LinkedIn](www.linkedin.com/in/aissam-eddine-boukhelkhal-769162192) · aissam-eddine.boukhelkhal@etu.univ-lyon1.fr
