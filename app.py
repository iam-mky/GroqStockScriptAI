import os

import gradio as gr
from src.stock_data import get_stock_data
from src.llm_client import generate_analysis

# Hardcoded stock universe: 5 NSE + 4 US tickers (display name -> yfinance ticker)
STOCK_OPTIONS = {
    "Reliance (NSE)": "RELIANCE.NS",
    "TCS (NSE)": "TCS.NS",
    "Wipro (NSE)": "WIPRO.NS",
    "HDFC Bank (NSE)": "HDFCBANK.NS",
    "Axis Bank (NSE)": "AXISBANK.NS",
    "Apple (US)": "AAPL",
    "Meta (US)": "META",
    "Google (US)": "GOOGL",
    "Netflix (US)": "NFLX",
}


def analyze_stock(ticker: str) -> str:
    data = get_stock_data(ticker)
    if data is None:
        return f"Couldn't fetch data for {ticker}. Please try another stock."

    return generate_analysis(data)


with gr.Blocks(title="GroqStockScriptAI") as demo:
    gr.Markdown("## GroqStockScriptAI\nSelect a stock to get an AI-generated market summary.")
    ticker_input = gr.Dropdown(
        label="Stock",
        choices=list(STOCK_OPTIONS.items()),
        value="RELIANCE.NS",
    )
    submit_btn = gr.Button("Analyze")
    output_box = gr.Textbox(label="Analysis", lines=10, interactive=False)

    submit_btn.click(fn=analyze_stock, inputs=[ticker_input], outputs=[output_box])
    ticker_input.change(fn=analyze_stock, inputs=[ticker_input], outputs=[output_box])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
