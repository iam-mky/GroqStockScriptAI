# Technical Learning Log — "Ask the Filing" (RAG Extension)

Write this manually as you build, in your own words. This is your source material for a future LinkedIn post/article — capture what you actually did, what broke, what you learned, and why you made each call. Don't skip the messy parts; those are the most useful ones to write about later.

---

## What I set out to build

<!-- One or two sentences: what is this feature, why did I want to build it -->

## Step 1: Loading and chunking the PDFs

<!-- What did loader.py end up doing? What did I learn about PDF text extraction (e.g., messy text, page breaks, tables)? -->

## Step 2: Embeddings

<!-- Which approach did I actually end up using (local sentence-transformers or hosted API)? Did Render's free tier handle it, or did I have to pivot? What happened when I tried? -->

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