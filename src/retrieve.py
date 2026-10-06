import faiss
import numpy as np
import ollama
import json


class VectorStore:

    def __init__(self):
        self.index = None
        self.chunks = []

    def get_embeddings(self, texts):

        response = ollama.embed(
            model="nomic-embed-text",
            input=texts
        )

        return np.array(
            response["embeddings"],
            dtype="float32"
        )

    def build(self, chunks):

        self.chunks = chunks

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self.get_embeddings(texts)

        # Normalize vectors so inner product = cosine similarity
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        print(
            f"FAISS index built with "
            f"{len(chunks)} chunks."
        )

    def search(self, query, k=5):

        query_embedding = self.get_embeddings(
            [query]
        )

        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(
            query_embedding,
            k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            results.append({
                "text": self.chunks[index]["text"],
                "source": self.chunks[index]["source"],
                "score": float(score)
            })

        return results

    def save(self, index_path, chunks_path):
        faiss.write_index(
            self.index,
            index_path
        )

        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(
                self.chunks,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("Index saved.")

    def load(self, index_path, chunks_path):
        self.index = faiss.read_index(index_path)

        with open(chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        print(
            f"Index loaded with "
            f"{len(self.chunks)} chunks."
        )