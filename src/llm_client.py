import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

system_prompt = (
    "You are the world's best stock market analyst. Analyse the stock for the given ticker and its data. "
    "Base your analysis strictly on the numeric data provided (price, volume, P/E, recent history trend) "
    "and avoid asserting specific real-world events/news you weren't given, while still being allowed to "
    "describe general patterns (e.g., 'the stock shows a declining trend over the past week, potentially "
    "reflecting reduced investor confidence' is fine — 'this dropped because of the Q3 earnings miss' is "
    "not, unless that data was actually provided)."
)

def generate_analysis(stock_data:dict):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages= [
            {"role":"system", "content": system_prompt},
            {"role":"user", "content": f"Analyze the stock: {stock_data}"}
        ],
        temperature= 0.2
    )
    return response.choices[0].message.content
