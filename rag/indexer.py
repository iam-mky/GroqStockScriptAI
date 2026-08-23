import os

from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.documents import Document


def initialize_vector_store(raw_chunks: list[dict]) -> FAISS :
    if not raw_chunks:
        raise ValueError("No text chunks provided")

    print("Initializing in-memory FAISS vector store..")
    # Convert dictionary into standard langchain document objects
    document = [Document(page_content=chunk["text"], metadata=chunk["metadata"])
                for chunk in raw_chunks
            ]
    # Use Hugging Face's hosted Inference API for embeddings instead of loading
    # the model locally — avoids the torch/sentence-transformers memory footprint
    # that caused an OOM kill (exit 137) on Render's free tier.
    try:
        print('Calling hosted embedding model "all-MiniLM-L6-v2" via HF Inference API..')
        embeddings = HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=os.getenv("HF_TOKEN"),
        )

        # Generate embeddgins and injest into the in-memory FAISS database
        # Normalized embeddings + cosine distance strategy => ranking by cosine similarity
        print(f"Indexing {len(document)} text chunks in FAISS")
        vector_store = FAISS.from_documents(
            document,
            embeddings,
            distance_strategy=DistanceStrategy.COSINE,
        )

        return vector_store
    except Exception as e:
        print(f"Error building RAG vector store: {e}")
        raise