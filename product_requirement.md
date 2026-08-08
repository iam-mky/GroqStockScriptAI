## Product Requirements Document (PRD): GroqStockScriptAI

## 1. Project Overview & Architecture

GroqStockScriptAI is a financial research dashboard that demonstrates practical AI engineering and modern software architecture. A user selects a stock, and the application fetches real-time market data and generates an AI-written summary. It also serves as a personal learning project and portfolio piece.

## System Architecture Pipeline

```
[User selects stock] ──► [yfinance Data Fetch] ──► [Context Injection] ──► [Groq API (Llama 3.3 70B)]
                                                                                    │
                                                                                    ▼
                                                                          [Structured Output]
                                                                                    │
                                                                                    ▼
                                                                          [Gradio App UI]
                                                                                    │
                                                                                    ▼
                                                                      [Hugging Face Spaces (Live Hosting)]
```

------------------------------

## 2. Technical Stack & Governance

### Core Infrastructure

* User Interface: Gradio (`gr.Blocks()` declarative layout)
* Inference Engine: Groq Cloud API (`llama-3.3-70b-versatile`, accessed via an OpenAI-compatible client, low temperature for factual consistency)
* Data Ingestion Layer: `yfinance` Python library (live NSE and US market data)
* Deployment Environment: Hugging Face Spaces (free, permanent cloud hosting with encrypted secret injection)

### Legal, Security & IP Compliance

* No proprietary or confidential data is used — only public market data via `yfinance`.
* Credentials are never hardcoded; all secrets are read from environment variables and injected via Hugging Face Repository Secrets in production.
* Open Source Licensing: MIT License, with a non-affiliation disclaimer in `README.md`.

------------------------------

## 3. Implementation Phases

**Phase 1: Foundational Layout** — Gradio UI skeleton with input, submit action, and output display, wired end-to-end with placeholder logic.

**Phase 2: Live Ingestion & Inference** — Connect `yfinance` to fetch price, volume, and P/E ratio for a curated set of tickers; inject that structured data into a Groq prompt to generate an analyst-style summary, with an explicit guardrail against the model fabricating real-world causes it wasn't given data for.

**Phase 3: Cloud Security & Configuration** — Abstract all credentials via environment variables (`python-dotenv` locally), generate `requirements.txt`, and enforce a strict `.gitignore` to prevent accidental secret exposure.

**Phase 4: Distribution** — Publish to GitHub, deploy to Hugging Face Spaces with the Groq API key stored as a Repository Secret, and document the project via `product_architecture.md` and `README.md`.

------------------------------

## 4. Distribution & Content Plan

| Channel | Purpose |
|---|---|
| GitHub | Source-of-truth repository showcasing code and documentation |
| Hugging Face Spaces | Live, permanently hosted demo |
| LinkedIn / Medium / Substack | Articles explaining the build process and architecture decisions (to be linked from the app once published) |
