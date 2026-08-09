# Technical Learning Log — "Ask the Filing" (RAG Extension)

Write this manually as you build, in your own words. This is your source material for a future LinkedIn post/article — capture what you actually did, what broke, what you learned, and why you made each call. Don't skip the messy parts; those are the most useful ones to write about later.

---

## What I set out to build

<!-- One or two sentences: what is this feature, why did I want to build it -->

## Step 1: Loading and chunking the PDFs

<!-- What did loader.py end up doing? What did I learn about PDF text extraction (e.g., messy text, page breaks, tables)? -->

## Step 2: Embeddings

Started with local `sentence-transformers` (`all-MiniLM-L6-v2`) via LangChain's `HuggingFaceEmbeddings`, per the original ADR decision — deliberately chosen to test locally-first rather than assume it would fail.

Deployed to Render's free tier staging service. It crashed on every deploy:

```
No open ports detected, continuing to scan...
Exited with status 137
```

Exit code 137 = killed by SIGKILL, almost always Render's out-of-memory killer. The app was dying *during startup*, while loading the embedding model — before it ever reached the line that starts the Gradio server (which is exactly why "no open ports detected" showed up: the app never got that far). `sentence-transformers` pulls in `torch`, which is a heavy dependency, and Render's free tier caps around 512MB RAM — not enough headroom.

This was the exact risk flagged in the ADR before writing any code, with an explicit fallback already planned: switch to a hosted embedding API if local didn't fit. Swapped `HuggingFaceEmbeddings` for `HuggingFaceEndpointEmbeddings` — same model, but the embedding computation now runs on Hugging Face's hosted Inference API instead of loading the model locally. Removed `sentence-transformers` from `requirements.txt` entirely, added a new `HF_TOKEN` secret (handled the same way as `GROQ_API_KEY` — environment variable, never committed).

**Takeaway**: the fix was fast because the risk was already written down and reasoned about in advance, with a fallback plan ready to execute — not because the bug was easy. Writing the ADR before building turned a confusing crash into a five-minute diagnosis.

## Step 3: Building the vector index

<!-- FAISS or Chroma — which did I pick and why, in my own words? What surprised me about how vector search actually works? -->

## Step 4: Retrieval

<!-- Did top-3 chunks work well? Any cases where the right answer wasn't retrieved? What would I tune if I had more time? -->

## Step 5: Grounded answers + citations

<!-- How did I get the model to cite its source? Did it ever try to answer from outside the documents despite instructions — how did I catch/fix that? -->

## Step 6: Wiring it into the existing app

<!-- Any friction integrating this into the v1 Gradio app? -->

## Step 7: Deploying to Render

<!-- Did it work first try? What broke, if anything (memory, build time, dependencies)? -->

## What I'd do differently next time

<!-- Honest reflection — this is often the most valuable section for a reader -->

## Key takeaways (for the LinkedIn/article version)

<!-- 2-4 bullet points, the "if you only read one thing" summary -->