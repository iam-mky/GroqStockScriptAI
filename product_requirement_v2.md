## Product Requirements Document (PRD) v2: "Ask the Filing" — RAG Extension

This document extends [product_requirement.md](product_requirement.md) (v1). v1's scope and requirements remain unchanged; this covers the new RAG feature only.

## 1. Overview

"Ask the Filing" adds a document question-answering feature to GroqStockScriptAI. A user can ask natural-language questions about Reliance's latest quarterly concall transcript and investor presentation, and receive answers grounded strictly in those documents, with a source citation. This is a retrieval-augmented generation (RAG) pipeline, distinct from and additive to v1's structured-data stock summary feature.

## 2. Locked Scope

* **1 company**: Reliance Industries
* **2 documents**: latest quarterly concall transcript (PDF) + investor presentation (PDF)
* **In-memory vector index**, rebuilt on every app startup — no persistent disk dependency, to stay compatible with Render's free tier
* Answers must be grounded in the source documents, with a page/section citation
* Questions outside the scope of the documents must be explicitly flagged as unanswerable from the source material — never answered from the model's general knowledge

This scope is locked for this iteration. No additional companies, documents, or persistence layers until this version is working and deployed.

## 3. Pipeline

```
Load PDF → Chunk text (500 chars, 50 char overlap) → Embed chunks → Store in in-memory vector index
                                                                              ↓
User question → Embed question → Retrieve top-3 similar chunks
                                                                              ↓
Stuff chunks into prompt → Groq LLM answers → Return answer + source citation
```

## 4. Technical Stack (additions to v1)

* PDF loading: `pypdf`
* Chunking: LangChain's `RecursiveCharacterTextSplitter`, 500 char chunks, 50 char overlap
* Embeddings: `all-MiniLM-L6-v2`, via Hugging Face's hosted Inference API (`HuggingFaceEndpointEmbeddings`) — pivoted from a local `sentence-transformers` model after that approach caused an out-of-memory crash on Render's free tier (see ADR-001, Decision 2, addendum)
* Vector store: FAISS, in-memory, cosine similarity (see ADR-001, Decision 3)
* LLM: existing Groq (Llama 3.3) client from v1, reused as-is
* UI: extend the existing Gradio app with a new "Ask the Filing" tab

## 5. Constraints

* Must remain deployable on Render's free tier (RAM and build-size limits apply)
* Startup indexing (PDF load → chunk → embed → store) must complete in a reasonable time for a single-document set — no background job infrastructure for this scope
* No new paid services introduced without an explicit decision recorded in the ADR

## 6. Out of Scope (this iteration)

* Multiple companies or documents
* Persistent/disk-backed vector storage
* User-uploaded documents
* Conversation memory across questions