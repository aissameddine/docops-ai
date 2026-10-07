# DocOps AI — Devlog

Daily journal, oldest entry first. The README holds the polished summary.

---

## Day 1 — Project skeleton (2026-10-01)

**Goal:** a reproducible repo with tooling, tests and a GitHub remote, so every later day starts from a clean base.

**Done:**
- Installed `git`, `gh`, `make` (dnf) and `uv` (official installer) on Fedora
- Git identity, default branch `main`, `pull.rebase true`; ed25519 SSH key; `gh` authenticated over SSH
- Project created with `uv init --package`, Python pinned to 3.12
- Dev tools: `pytest`, `ruff`, `pre-commit`
- `src/docops_ai/` layout: ingestion, chunking, embeddings, retrieval, generation, api
- Ruff (rules `E F I B UP`, line length 100) and pytest configured in `pyproject.toml`
- Smoke test, `Makefile` (`make check`, `make test`), `.gitignore`, `.env.example`, `README.md`, pre-commit hook
- First push with `gh repo create docops-ai --private --source=. --push`
- Verified from a fresh clone: `uv sync && make check && make test` all green

**Decisions (and why):**
- **GitHub as primary remote:** the roadmap uses GitHub Actions, and it is the portfolio recruiters see.
- **uv over pip + venv:** one tool for Python versions, environment, dependencies and a lockfile (`uv.lock`).
- **`src/` layout:** tests import the installed package, which avoids import bugs that only show up in CI.
- **ruff for lint and format:** one fast tool instead of flake8 + black + isort.

**Problems / fixes:**
- Package name: the project is `docops-ai` but the importable package is `docops_ai` (hyphens are invalid in Python names). Caught before the first commit.
- `gh auth login` already uploads the SSH key, so a separate `gh ssh-key add` is redundant.

**Learned:** public/private key authentication; why the lockfile is committed; Git does not track empty folders (hence `.gitkeep`); a fresh clone is the real test of "it works".

---

## Day 2 — PDF ingestion (2026-10-01)

**Goal:** one validated record per PDF page (text, page number, source, metadata), clean enough for chunking and embedding.

**Done:**
- `PageContent` Pydantic model; `ingest_pdf()` with PyMuPDF
- `doc_id` = SHA-256 of the file bytes (truncated), so the same file always gets the same ID
- One `IngestionError` for missing, non-PDF, corrupt and password-protected files, each tested
- `clean_text()`: Unicode NFC normalisation, invisible characters removed, whitespace tidied
- `strip_page_furniture()`: repeated headers, footers and page numbers removed at document level
- Tests generate their own PDFs, so no binaries are committed
- Tried on four real French PDFs (a course handout, a lab report, two job postings): no empty pages, so no OCR needed for now

**Decisions (and why):**
- **Pydantic model:** later stages can trust validated data.
- **Header/footer filter is conservative:** a line is removed only if it repeats at the edge of at least half the pages of a document with 3+ pages; page numbers only when they follow a consistent offset from the PDF page index. Short documents are left untouched.
- **Removed lines are kept as metadata** (`stripped_edge_lines`) instead of being discarded.

**Problems / fixes:**
- Zero-width spaces (U+200B) from Word-to-PDF conversion sat inside the text; they break exact matching -> removed in `clean_text`.
- Every page of the lab report repeated the same header and ended with a page number -> layout filter.
- Review found the filter had erased the course name (it only appeared in the running header) -> saved in metadata.
- `make check && make test` stops at the first failure: a formatting error meant the tests never ran. Run them separately when debugging.

**Learned:** test on real documents early (both defects were invisible in synthetic tests); when a cleaning step deletes something, ask whether it should be moved instead.

---

## Day 3 — Chunking (2026-10-07)

**Goal:** page-aware chunks with configurable size and overlap, and a default chosen from evidence.

**Done:**
- `Chunk` and `ChunkingConfig` models (overlap must be smaller than size)
- Splitter: a window of `chunk_size` characters, cut at the best separator inside it (paragraph, line, sentence, word), overlap snapped to a word start, hard cut for very long words
- Chunks never span pages; deterministic IDs `{doc_id}-p{page}-c{index}`; character offsets into the page text are kept and tested
- `scripts/chunk_stats.py`: sizes 300/500/800/1200 x overlap 0/10/20%, reporting tiny chunks and chunks dominated by bare numbers
- Three more cleaning steps found by running on real documents (below)
- 43 tests passing

**Problems found on real documents:**
- **Ligatures** (U+FB01 etc.) in extracted text break exact matching -> expanded to plain letters. Targeted map instead of NFKC, which would also rewrite characters such as `º`.
- **Words cut by line-end hyphens** (`structu-` / `relles`) -> re-joined when both sides are lowercase letters. Known trade-off: a real compound such as `peut-` / `être` becomes `peutêtre`.
- **Source-code line numbers** in the lab report: 42-57% of chunks were mostly bare numbers -> conservative run detector (4+ consecutive numbers, mostly alone on their line, with code between them). Result: 7-14%. Section numbers, equation numbers and numeric columns are kept.
- **Known limits, not fixed:** accents lost in code-font comments (the glyph is missing from the PDF itself), and math formulas come out scattered.

**Results (lab report, 15 pages):**

| size/overlap | chunks | %tiny | %numeric before | %numeric after |
|---|---|---|---|---|
| 800/0 | 28 | 7.1 | 50.0 | 14.3 |
| 800/80 | 29 | 3.4 | 48.3 | 13.8 |
| 800/160 | 29 | 0.0 | 51.7 | 13.8 |

**Decision:** default 800 characters / 100 overlap. Overlap above 0 removes tail fragments (smallest chunk 8 -> 85 characters) at almost no cost in chunk count. Overlap 100 vs 160 and chunk size will be compared on retrieval quality in Week 3.

**Learned:** the metric (share of numeric chunks) turned a vague worry into a before/after number; real PDFs hide many extraction defects that clean test data never shows.

**Next:** Day 4 — embeddings. Compare multilingual models and check each model's maximum sequence length against our chunk sizes.
