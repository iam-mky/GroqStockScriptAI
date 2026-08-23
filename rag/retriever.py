from langchain_community.vectorstores import FAISS

def retrieve_relevant_chunks(vector_store: FAISS, query: str, k: int = 3) -> list[dict]:
    """
    Queries the FAISS index for the top-k most similar chunks to the query
    and returns them as framework-agnostic dictionaries.
    """
    try:
        results = vector_store.similarity_search(query, k=k)
    except Exception as e:
        print(f"Error during similarity search for query '{query}': {e}")
        return []

    return [
        {
            "text": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in results
    ]