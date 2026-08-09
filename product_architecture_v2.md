# Product Architecture v2: "Ask the Filing" — RAG Extension

This document extends [product_architecture.md](product_architecture.md) (v1). v1's modules (`app.py`, `src/stock_data.py`, `src/llm_client.py`) are unchanged and continue to serve the stock-summary feature. This document covers the new `rag/` package only.

## High-Level Overview

"Ask the Filing" is a retrieval-augmented generation (RAG) feature bolted onto the existing GroqStockScriptAI app. It answers user questions about Reliance's quarterly concall and investor presentation by retrieving relevant document chunks and grounding the LLM's answer in them, with a citation back to the source.

## System Architecture / Data Flow

```
[App startup]
      │
      ▼
[rag/loader.py: load PDFs, split into chunks]
      │
      ▼
[rag/indexer.py: embed chunks, build in-memory vector index]
      │
      ▼
[Index held in memory, ready for queries]

[User asks a question in the Gradio UI]
      │
      ▼
[rag/retriever.py: embed question, retrieve top-3 chunks from index]
      │
      ▼
[rag/rag_chain.py: stuff chunks + question into prompt, call Groq]
      │
      ▼
[Answer + source citation returned to Gradio UI]
```

## Module Breakdown

| Module | Responsibility |
|---|---|
| `rag/loader.py` | Loads the bundled PDFs and splits them into chunks (500 chars, 50 char overlap) |
| `rag/indexer.py` | Embeds chunks and builds the in-memory vector index; runs once at app startup |
| `rag/retriever.py` | Embeds an incoming question and retrieves the top-3 most similar chunks from the index |
| `rag/rag_chain.py` | Assembles the retrieved chunks + question into a prompt, calls the existing Groq client, returns answer + citation |
| `app.py` (extended) | Adds a new UI section/tab wiring user questions to `rag_chain.py`, alongside the existing stock-summary feature |

Same separation-of-concerns principle as v1: loading, indexing, retrieval, and generation are each isolated, so any one piece (e.g., swapping the embedding model, or the vector store) can change without touching the others.

## Key Architectural Decisions

See [ADR-001: RAG Extension Design Decisions](adr_001_rag_extension.md) for the detailed tradeoffs behind embedding choice, vector store choice, and chunking parameters.

## Constraints Carried From v1

* Credentials (`GROQ_API_KEY`) continue to be read via `os.getenv`, never hardcoded — same pattern, no new secret-handling approach introduced
* Must remain deployable on Render's free tier

## Known Limitations (v2 additions)

* Index is rebuilt from scratch on every app restart/redeploy — no persistence, so startup takes slightly longer
* Limited to 2 pre-bundled documents for 1 company — not a general-purpose document Q&A tool in this iteration
* No conversation memory — each question is answered independently, with no awareness of prior questions in the session