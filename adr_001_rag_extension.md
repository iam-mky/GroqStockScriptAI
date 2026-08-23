# ADR-001: "Ask the Filing" RAG Extension — Design Decisions

**Context**: Extending GroqStockScriptAI with a RAG feature for document Q&A, while keeping the app deployable on Render's free tier.

---

## Decision 1: Chunk size and overlap

**Decision**: 500 character chunks, 50 character overlap (10%).

**Factors considered**:
- Chunk size trades off two failure modes: too large, and irrelevant text dilutes the embedding and gets retrieved alongside the useful part; too small, and a single chunk may not contain enough context to answer a question on its own.
- Overlap exists specifically to avoid losing meaning at chunk boundaries — a sentence or fact that straddles the cut point would otherwise be split across two chunks, weakening both chunks' embeddings.
- 10% overlap is a common starting ratio — enough to catch boundary-split content without meaningfully increasing storage/embedding cost.

**Alternatives considered**: Larger chunks (1000+ chars) — rejected for a first iteration since financial documents (concall transcripts, investor presentations) tend to have dense, locally-scoped facts (a single Q&A exchange, a single metric table row), which suits smaller chunks better.

---

## Decision 2: Embeddings — local `sentence-transformers` vs. hosted API

**Decision**: Attempt local `sentence-transformers` (`all-MiniLM-L6-v2`) first; fall back to a hosted embedding API only if Render's free tier (~512MB RAM) can't handle the model.

**Factors considered**:
- Local embeddings avoid a second external API dependency/secret, and have no per-call cost.
- `sentence-transformers` depends on `torch`, which is a heavy install — real risk of exceeding Render free tier's build size or runtime memory limits.
- A hosted embedding API avoids the memory risk entirely, but introduces a new secret to manage and an external dependency at query time (plus, for indexing, a burst of API calls at startup).

**Alternatives considered**: Hosted embedding API from the start — rejected for now in favor of testing the local approach first, since the actual failure mode (build failure vs. runtime OOM vs. works fine) isn't known until tested against Render directly. This decision may be revisited based on real deployment results — if so, that update will be logged as an addendum below, not a silent change.

**Addendum (post-deployment)**: The local `sentence-transformers` approach was tested on Render's free tier and failed — the process was killed during startup (exit code 137, an OS out-of-memory kill via SIGKILL) while loading `torch`/the embedding model, before the app ever bound a port. This confirmed the predicted risk. Switched to `HuggingFaceEndpointEmbeddings` (Hugging Face's hosted Inference API) instead of `HuggingFaceEmbeddings` (local) — same underlying model (`all-MiniLM-L6-v2`), but embedding computation now happens on Hugging Face's servers via an API call, removing the local `torch` dependency entirely. This requires a new secret, `HF_TOKEN`, handled the same way as `GROQ_API_KEY` (environment variable, never committed).

---

## Decision 3: Vector store — FAISS vs. Chroma

**Decision**: FAISS, in-memory, using `DistanceStrategy.COSINE` with normalized embeddings.

**Factors considered**:
- Chroma has cleaner LangChain integration but pulls in additional dependencies (SQLite backend, ONNX runtime for its default embedding function) that add weight — a concern given the Render free tier constraint.
- FAISS is lighter for a pure in-memory, single-session use case like this one, with no need for Chroma's persistence or client-server features.
- Implemented via LangChain's `FAISS.from_documents()`, which also solves the "FAISS has no native metadata" limitation — each vector is wrapped in a `Document` object carrying its source/page/chunk-index metadata, so retrieval results come back with citation information attached, not just raw vectors.
- Cosine similarity was chosen over the default L2 (Euclidean) distance for semantic search — requires both normalizing embeddings (`normalize_embeddings=True` at embedding time) and explicitly setting `distance_strategy=DistanceStrategy.COSINE` when building the FAISS index, since normalization alone doesn't change FAISS's default ranking metric.

---

## Decision 4: Out-of-scope question handling

**Decision**: If retrieved chunks don't contain information relevant to the question, the system must explicitly state the answer isn't covered in the source documents — never fall back to the model's general knowledge.

**Factors considered**:
- This mirrors the v1 anti-hallucination guardrail (the stock-summary prompt already avoids asserting real-world causes not present in the data). Same principle applied to a new mechanism: retrieval relevance, not just prompt instruction, should gate whether an answer is attempted.
- Financial documents carry real credibility risk if the app appears to answer confidently from outside the source — this is a explicit design constraint, not an incidental behavior.

---

## Decision 5: Documentation structure (v1 vs v2)

**Decision**: v1's PRD and architecture docs remain untouched; this extension gets its own `_v2` documents plus this ADR, rather than rewriting v1 in place.

**Factors considered**: Preserves the historical record of what v1 actually was and why those decisions were made, rather than overwriting them — useful both for the reader (shows iteration over time) and for the author (avoids losing the reasoning behind earlier, still-valid decisions).