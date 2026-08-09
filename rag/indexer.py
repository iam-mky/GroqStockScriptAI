from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


def initialize_vector_store(raw_chunks: list[dict]) -> FAISS :
    if not raw_chunks:
        raise ValueError("No text chunks provided")

    print("Initializing in-memory FAISS vector store..")
    # Convert dictionary into standard langchain document objects
    document = [Document(page_content=chunk["text"], metadata=chunk["metadata"])
                for chunk in raw_chunks
            ]
    # Load an open source embedding model
    print('Loading embedding model "all-MiniLM-L6-v2"..')
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        encode_kwargs={"normalize_embeddings": True},
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