from langchain_community.vectorstores import FAISS

def retrieve_relevant_chunks(vector_store: FAISS, query: str, k: int = 3) -> list[dict]:
    """
    Queries the FAISS index for the top-k most similar chunks to the query
    and returns them as framework-agnostic dictionaries.
    """
    results = vector_store.similarity_search(query, k=k)

    return [
        {
            "text": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in results
    ]