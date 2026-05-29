import os
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DOCUMENTS = [
    "Python is a high-level programming language.",
    "FAISS enables fast similarity search.",
    "RAG combines retrieval with generation.",
    "Pinecone is a managed vector database.",
]

def embed(texts):
    resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([r.embedding for r in resp.data])

def search(query, k=2):
    query_vec = embed([query])
    doc_vecs = embed(DOCUMENTS)
    scores = query_vec @ doc_vecs.T
    top_idx = np.argsort(scores[0])[::-1][:k]
    return [(DOCUMENTS[i], scores[0][i]) for i in top_idx]

if __name__ == "__main__":
    results = search("vector search")
    for doc, score in results:
        print(f"{score:.4f}: {doc}")
