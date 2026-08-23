import os

import gradio as gr
from stock.stock_data import get_stock_data
from stock.llm_client import generate_analysis
from rag.loader import loadpdf_and_chunks
from rag.indexer import initialize_vector_store
from rag.rag_chain import answer_question

RELIANCE_PDF_PATHS = [
    "data/Reliance/QuarterlyConcall.pdf",
    "data/Reliance/QuarterlyResultPPT.pdf",
]

# Build the in-memory RAG index once at startup (no persistent disk dependency).
# Wrapped so a RAG failure doesn't take down the unrelated Stock Analysis feature.
_vector_store = None
try:
    print("Building RAG index for Ask the Filing...")
    _rag_chunks = loadpdf_and_chunks(RELIANCE_PDF_PATHS)
    _vector_store = initialize_vector_store(_rag_chunks)
    print("RAG index ready.")
except Exception as e:
    print(f"Error building RAG index at startup — Ask the Filing will be unavailable: {e}")

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


def ask_filing(question: str) -> str:
    if _vector_store is None:
        return "Ask the Filing is temporarily unavailable. Please try again later."

    result = answer_question(_vector_store, question)

    sources_text = "\n".join(
        f"- {s.get('source', 'unknown')}, Page {s.get('page', 'unknown')}"
        for s in result["sources"]
    )
    return f"{result['answer']}\n\nRetrieved from:\n{sources_text}"


with gr.Blocks(title="GroqStockScriptAI") as demo:
    gr.Markdown("## GroqStockScriptAI")

    with gr.Tabs():
        with gr.Tab("Stock Analysis"):
            ticker_input = gr.Dropdown(
                label="Stock",
                choices=list(STOCK_OPTIONS.items()),
                value="RELIANCE.NS",
            )
            submit_btn = gr.Button("Analyze")
            output_box = gr.Textbox(label="Analysis", lines=10, interactive=False)

            submit_btn.click(fn=analyze_stock, inputs=[ticker_input], outputs=[output_box])
            ticker_input.change(fn=analyze_stock, inputs=[ticker_input], outputs=[output_box])

        with gr.Tab("Ask the Filing"):
            gr.Markdown("Ask a question about Reliance's latest quarterly concall and investor presentation.")
            question_input = gr.Textbox(label="Your question", placeholder="e.g. What was the revenue growth this quarter?")
            ask_btn = gr.Button("Ask")
            answer_box = gr.Textbox(label="Answer", lines=10, interactive=False)

            ask_btn.click(fn=ask_filing, inputs=[question_input], outputs=[answer_box])
            question_input.submit(fn=ask_filing, inputs=[question_input], outputs=[answer_box])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
