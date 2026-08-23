# Building "Ask the Filing": A RAG Extension to GroqStockScriptAI

## What I set out to build

GroqStockScriptAI already gave users an AI-generated summary of a stock's recent price and volume behavior. I wanted to go one level deeper: let a user ask a real question — "what did management say about margins this quarter?" — and get an answer grounded in an actual company document, not the model's general knowledge. That's a fundamentally different problem from the original feature. It's not "summarize this data," it's "find the right needle in a document, and prove where you found it." That's what RAG (Retrieval-Augmented Generation) is for, and this was my first hands-on build of one.

The scope was deliberately narrow: one company (Reliance Industries), two documents (the latest quarterly concall transcript and investor presentation), answers grounded strictly in those documents, with a citation back to the source page.

## Step 1: Turning PDFs into searchable pieces

A PDF isn't something an AI model can search directly — it first has to become small, comparable pieces of text. `loader.py` reads each PDF page by page, and splits each page's text into chunks of 500 characters, with a 50-character overlap between consecutive chunks.

The overlap isn't a nice-to-have. A fact or sentence sitting right at a chunk boundary would otherwise get split in half — half the meaning ends up in one chunk, half in the next, and neither chunk alone captures it well. The 50-character overlap means boundary content shows up whole in at least one chunk.

Since Render's free hosting tier has no persistent disk, this loading-and-chunking step runs fresh every time the app starts — a few seconds of work, traded for zero infrastructure to maintain.

## Step 2: Turning text into vectors — and hitting a real production failure

Each chunk of text becomes a numerical vector — an "embedding" — via an embedding model, so that a user's question can later be compared mathematically against every chunk to find the closest matches.

I started with `sentence-transformers` running locally, per my own architecture decision log: test the simplest approach first, and only pivot if it actually failed. It failed. On Render's free tier, the app crashed on every deploy with:

```
No open ports detected, continuing to scan...
Exited with status 137
```

Exit code 137 means the operating system killed the process with SIGKILL — almost always an out-of-memory kill. The app never even reached the point of starting its own web server ("no open ports detected" because the app died before it got that far). The culprit: `sentence-transformers` depends on `torch`, a large library, and Render's free tier caps memory around 512MB — nowhere near enough room to load it alongside everything else.

The fix: instead of loading the embedding model locally, I switched to Hugging Face's **hosted Inference API** (`HuggingFaceEndpointEmbeddings`). Same model, same output — but the actual computation now happens on Hugging Face's servers, and my app just sends text and receives vectors back over the network. No `torch`, no local model weights, a fraction of the memory footprint.

The real lesson here isn't about embeddings specifically — it's that **I'd already written down this exact risk before building anything**, with a fallback already planned. That's why the fix took minutes once the crash happened, instead of an open-ended debugging session. Naming your assumptions in advance turns a scary production crash into a checklist.

## Step 3: Where the vectors live — choosing FAISS over Chroma

Once you have embeddings, you need somewhere to store and search them — a vector store. I chose FAISS over the more commonly-recommended Chroma specifically because of the same memory constraint from Step 2: Chroma pulls in extra dependencies (a SQLite backend, an ONNX runtime) that add weight I couldn't afford. FAISS, used in pure in-memory mode, does exactly what this project needs — fast similarity search over a small, session-lived set of vectors — without the extra baggage.

This is a good example of a decision that looks small in the code but is really about *fitting the tool to the constraint*, not "which vector store is objectively best."

## Step 4: Retrieval — turning a question into the right chunks

When a user asks a question, it goes through the same embedding process as the document chunks did, and FAISS finds the top 3 chunks whose vectors are closest to the question's vector — meaning, semantically, the most relevant pieces of the document.

In testing, top-3 retrieval gave sensible results for straightforward questions. Where this would need more attention in a larger version of this project: questions that need information spread across many chunks (retrieving only 3 might miss part of the picture), and questions phrased very differently from how the document phrases the same idea (embedding similarity isn't perfect at bridging very different wording). Neither showed up as a problem at this project's scale — one company, two documents — but it's exactly the kind of thing that would need tuning (a higher `k`, or better chunking) if this were extended to many documents.

## Step 5: How grounded answers and citations actually happen

This is the part that's easy to wave your hands at, so here it is concretely: there's no separate "citation system." Grounding and citation both come from **what you put in the prompt** and **what metadata you carry alongside each chunk**.

Every chunk stored in the vector index carries metadata — which file it came from, which page. When a question comes in, the retrieved chunks (text + metadata) get formatted into the prompt sent to the LLM, with each chunk explicitly labeled: `[Source: <file>, Page <page>]`. The system prompt then instructs the model to answer *using only what's in that context*, and to say clearly when the answer isn't covered — rather than falling back on outside knowledge. The model doesn't have any built-in notion of "citing sources" — it's simply been given the source labels as part of its input, and told to reference them.

This mirrors a lesson from the earlier stock-summary feature: an LLM will happily sound confident about things it doesn't actually know, unless you explicitly constrain what it's allowed to claim. Here, the constraint is "answer only from this labeled context" instead of "don't invent stock news" — same underlying principle, applied to a new mechanism.

## Step 6: Wiring it into the existing app

This part was genuinely smooth — the whole point of keeping v1's `app.py`, `stock_data.py`, and `llm_client.py` untouched was so that adding a new Gradio tab and a new `rag/` package wouldn't risk breaking the working stock-analysis feature. The vector index gets built once, when the app starts, and both features run side by side.

## Step 7: Deploying to Render

The first deploy failed exactly as described in Step 2 — memory, not code, was the problem. After switching to the hosted embedding API, the app deployed cleanly: no local model to load, a much smaller memory footprint, and a fast startup.

## Step 8: A model I didn't touch stopped working

After both features were live, Stock Analysis and Ask the Filing started failing at the same time, with no code changes on my end. The cause: `llama-3.3-70b-versatile`, the model both features had been calling since v1, was no longer available on Groq. An external dependency changed underneath a working system — nothing about my code was wrong the day before.

Because I'd used an OpenAI-compatible client (a v1 decision, made for a different reason — provider flexibility) rather than Groq's own SDK, switching models was a one-line change per call site: swap the `model` string to `openai/gpt-oss-120b`. Both `llm_client.py` and `rag_chain.py` needed the same fix, since each had independently hardcoded the same model name — a small duplication that made this a two-file fix instead of a one-line one, worth cleaning up later by sharing a single model constant.

Fixing this surfaced a second, unrelated problem: Stock Analysis started failing again immediately, this time with a token-limit error — 8012 tokens requested against an 8000 cap. `generate_analysis()` builds its prompt by dropping the entire `stock_data` dict into an f-string, and `recent_history` was a full year of daily records, each one repeating full key names in its raw dict form. That's a lot of tokens spent on a granularity the summary probably didn't need. Reducing the fetch window from 1 year to 6 months (`stock_data.py`) brought the prompt comfortably under the limit — a smaller, more urgent version of a scoping decision I'd already made once before (the hardcoded ticker list in v1): send the model less, not more, when more isn't actually helping.

## What I'd do differently next time

I'd test the memory-heavy dependency against the actual free-tier hosting environment *before* building the rest of the pipeline around it, rather than after. The architecture decision log correctly predicted the risk, but I still built the full local pipeline first and only discovered the failure at deploy time. Testing that one risky piece in isolation, early, would have caught this a step sooner.

The model-name duplication I noticed here didn't stay a "next time" item — I fixed it right after: pulled `MODEL_NAME` into a single constant in `llm_client.py`, imported wherever it's needed. Cheap to fix immediately, and exactly the kind of small debt that gets expensive if it's left for "later" and the next provider change happens under real time pressure.

## Key takeaways

- RAG isn't magic — it's chunking, embedding, similarity search, and a carefully constrained prompt, in that order. Understanding each step individually makes the whole thing far less mysterious.
- Citations in a RAG system aren't a separate feature — they come from carrying metadata alongside your data from the very first step, and telling the model to use it.
- Free-tier cloud hosting has real constraints that don't show up in local development — writing down your risky assumptions before you build (not just once something breaks) is what makes debugging fast instead of stressful.
- The same anti-hallucination principle applies everywhere you use an LLM: it will confidently answer beyond what it actually knows unless you explicitly constrain what it's allowed to claim.
- Provider abstraction pays off even when you didn't build it for the reason it ends up mattering — an OpenAI-compatible client made a surprise model deprecation a one-line fix instead of a rewrite.
