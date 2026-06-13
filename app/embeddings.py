from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2


class LightweightEmbeddings:
    """LangChain-compatible embedding wrapper using ChromaDB's ONNX model (no PyTorch)."""

    def __init__(self):
        self._model = ONNXMiniLM_L6_V2()

    def embed_documents(self, texts):
        return self._model(texts)

    def embed_query(self, text):
        return self._model([text])[0]


embedding_model = LightweightEmbeddings()
