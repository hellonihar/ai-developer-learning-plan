from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
import uuid


MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "policy_chunks"


class EmbeddingStore:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.model = SentenceTransformer(MODEL_NAME)
        self.client = PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=MODEL_NAME
            ),
        )

    def add_chunks(self, chunks: list[str]) -> list[str]:
        ids = [str(uuid.uuid4()) for _ in chunks]
        self.collection.add(documents=chunks, ids=ids)
        return ids

    def search(self, query: str, k: int = 5) -> list[str]:
        results = self.collection.query(query_texts=[query], n_results=k)
        return results["documents"][0] if results["documents"] else []

    def count(self) -> int:
        return self.collection.count()

    def reset(self):
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=MODEL_NAME
            ),
        )
