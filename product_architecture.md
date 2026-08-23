# Product Architecture: GroqStockScriptAI

## High-Level Overview

GroqStockScriptAI is an open-source application that helps users summarize a stock's recent market behavior. It fetches live market data for a curated set of stocks via `yfinance`, then passes that structured data to Groq's Llama 3.3 70B model to generate a data-grounded, analyst-style summary. The result is displayed in a Gradio web UI.

## System Architecture / Data Flow

```
[User selects stock from dropdown]
              │
              ▼
   [stock/stock_data.py: yfinance]
   fetches price, volume, P/E ratio,
   and recent daily history
              │
              ▼
   [Structured dict: Context Injection]
              │
              ▼
  [stock/llm_client.py: Groq API]
  Llama 3.3 70B via OpenAI-compatible
  client, temperature = 0.2
              │
              ▼
   [Gradio App UI: output display]
```

## Module Breakdown

| Module | Responsibility |
|---|---|
| `app.py` | UI layout, event wiring, entry point; also binds to Render's dynamic `PORT`/host for deployment |
| `stock/stock_data.py` | Pure data-ingestion layer — calls yfinance, returns a structured dict, isolated from UI/LLM concerns |
| `stock/llm_client.py` | LLM client setup and prompt construction — isolated so the model/provider can be swapped independently of the rest of the app |

Keeping these three concerns in separate files means each can be tested, debugged, or replaced independently — e.g., swapping the LLM provider only touches `llm_client.py`, and swapping the data source only touches `stock_data.py`.

## Key Architectural Decisions

- **OpenAI-compatible client for Groq**: Groq exposes an OpenAI-compatible API, so the app uses the `openai` SDK pointed at Groq's `base_url` instead of the `groq` package directly. This makes the LLM provider swappable (a different OpenAI-compatible endpoint) by changing only `api_key`/`base_url`, not application code.
- **Low temperature (0.2)**: Chosen to minimize creative variance and keep the model's output closely grounded in the numeric data provided, rather than generating overly speculative language.
- **Prompt guardrail against fabrication**: yfinance provides only numeric data (price, volume, P/E, recent history) — no news or event context. The system prompt explicitly instructs the model to reason only from the numeric trend provided and avoid asserting specific real-world causes (e.g., earnings, news events) it was never given. This was a deliberate choice to protect output credibility, since an LLM without this guardrail will readily fabricate plausible-sounding but false causes.
- **Curated stock list instead of free-text ticker input**: Rather than accepting arbitrary ticker strings (which requires validation, exchange-suffix correction, and error handling for invalid tickers), the app restricts input to a hardcoded dropdown of known-good tickers (5 NSE + 4 US). This eliminates an entire class of input-validation problems and was a deliberate scope decision to prioritize a working, reliable demo over open-ended input handling.
- **Environment-variable credential handling**: `GROQ_API_KEY` is loaded via `python-dotenv` from a local `.env` file (excluded from git via `.gitignore`) and read through `os.getenv`, never hardcoded. `.env.example` documents the required variable without exposing a real value. In deployment, the same variable is set via Render's Environment Variables dashboard.
- **Dynamic host/port binding for deployment**: `demo.launch()` binds to `server_name="0.0.0.0"` and reads `server_port` from the `PORT` environment variable (falling back to `7860` locally). Cloud hosts like Render assign the listening port dynamically at runtime, so the app must read it rather than hardcode a port.

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Gradio (`Blocks` declarative layout) |
| Data ingestion | yfinance |
| Inference | Groq Cloud API — Llama 3.3 70B (via OpenAI-compatible client) |
| Secrets | python-dotenv (local), Render Environment Variables (deployed) |
| Deployment | Render (free web service tier) |

## Known Limitations

- Only 9 stocks are supported (5 NSE, 4 US) — hardcoded, not dynamically searchable.
- No live ticker autosuggest/search — a deliberate scope cut for this version.
- The model has no access to real news/events; its analysis is limited to what numeric data can support.
- No automated tests currently cover `stock_data.py` or `llm_client.py`.
- `yfinance` is an unofficial Yahoo Finance client, not a stable public API. Yahoo occasionally rate-limits requests from shared cloud-hosting IP ranges (observed on Render), causing intermittent "Couldn't fetch data" failures unrelated to application logic. No caching or retry mitigation is implemented for this in the current version — accepted as an external dependency risk rather than engineered around, given the project's demo scope.
