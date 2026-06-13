from langchain_chroma import Chroma
from app.embeddings import embedding_model

vector_store = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model
)


def get_vector_store():
    return vector_store


def save_documents(documents):
    vs = get_vector_store()
    vs.add_documents(documents)


def search_documents(
    query: str,
    k: int = 5,
    filter: dict | None = None
):
    vs = get_vector_store()

    return vs.similarity_search(
        query=query,
        k=k,
        filter=filter
    )
