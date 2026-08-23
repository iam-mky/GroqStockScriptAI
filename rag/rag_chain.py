from stock.llm_client import client, MODEL_NAME
from rag.retriever import retrieve_relevant_chunks

RAG_SYSTEM_PROMPT = (
    "You are a financial research assistant answering questions about Reliance Industries' "
    "latest quarterly concall transcript and investor presentation. Answer strictly using the "
    "provided context excerpts below — do not use outside knowledge or make assumptions beyond "
    "what the context states. If the context does not contain enough information to answer the "
    "question, say clearly that the answer is not covered in the provided documents — do not guess "
    "or fabricate an answer. When you do answer, cite the source and page number(s) you used, "
    "in the format (Source: <file>, Page <page>)."
)


def _format_context(chunks: list[dict]) -> str:
    formatted = []
    for chunk in chunks:
        source = chunk["metadata"].get("source", "unknown")
        page = chunk["metadata"].get("page", "unknown")
        formatted.append(f"[Source: {source}, Page {page}]\n{chunk['text']}")
    return "\n\n".join(formatted)


def answer_question(vector_store, question: str, k: int = 3) -> dict:
    retrieved_chunks = retrieve_relevant_chunks(vector_store, question, k=k)
    context = _format_context(retrieved_chunks)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": RAG_SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
            temperature=0.1,
        )
        return {
            "answer": response.choices[0].message.content,
            "sources": [chunk["metadata"] for chunk in retrieved_chunks],
        }
    except Exception as e:
        print(f"Error calling Groq API for Ask the Filing: {e}")
        return {
            "answer": "Sorry, the answer could not be generated right now. Please try again shortly.",
            "sources": [],
        }
