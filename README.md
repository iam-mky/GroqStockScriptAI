# GroqStockScriptAI

An AI-powered stock research dashboard. Select a stock from a curated list of NSE and US tickers, and get an AI-generated market summary built from live data pulled via `yfinance` and analyzed by Llama 3.3 70B (served via the Groq API).

## How it works

1. User selects a stock from the dropdown (5 NSE + 4 US tickers).
2. `src/stock_data.py` fetches live price, volume, P/E ratio, and recent daily history via `yfinance`.
3. That structured data is injected into a prompt sent to Groq's Llama 3.3 70B model (accessed through the OpenAI-compatible API) in `src/llm_client.py`.
4. The model returns a data-grounded market summary, displayed in the Gradio UI.

See [product_architecture.md](product_architecture.md) for the full system design and architectural decisions.

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your own Groq API key (get one at https://console.groq.com/keys):

```
GROQ_API_KEY=your_key_here
```

Then run:

```bash
python app.py
```

## Deployment

Deployed on [Render](https://render.com) as a free web service, connected directly to this GitHub repo. Render auto-redeploys on every push to `main`.

- **Build command**: `pip install -r requirements.txt`
- **Start command**: `python app.py`
- **Environment variable**: `GROQ_API_KEY` set via Render's dashboard (Environment tab), never committed to source

## Disclaimer

This project is an independent, personal, open-source project built for educational and portfolio purposes. It is not affiliated with, endorsed by, or connected to Groq, Hugging Face, Yahoo Finance, or any company whose stock ticker data may appear in this application. All market data is sourced from publicly available APIs. This tool does not constitute financial advice.

## Author

Manoj Kumar Yadav

## License

MIT — see [LICENSE](LICENSE).
