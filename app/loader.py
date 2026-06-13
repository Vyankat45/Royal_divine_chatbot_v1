from langchain_community.document_loaders import WebBaseLoader
from app.metadata import generate_metadata
import os

os.environ["USER_AGENT"] = "RoyalDivineRAGBot/1.0"


def load_documents(urls):

    documents = []

    for url in urls:

        print(f"Loading: {url}")

        loader = WebBaseLoader(url)

        loaded_docs = loader.load()

        for doc in loaded_docs:

            doc.metadata.update(
                generate_metadata(url)
            )

            # Uncomment for debugging
            # print(doc.metadata)

        documents.extend(loaded_docs)

    return documents