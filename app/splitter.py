from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.cleaner import clean_text

def split_documents(documents):

    for doc in documents:
        doc.page_content = clean_text(doc.page_content)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    return chunks