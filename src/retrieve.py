import os
import faiss
import numpy as np
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


class VectorStore:

    def __init__(self):
        self.index = None
        self.chunks = []

    def get_embeddings(self, texts):

        response = client.embeddings.create(
            model="nvidia/nemotron-3-embed-1b:free",
            input=texts
        )

        embeddings = [
            item.embedding
            for item in response.data
        ]

        return np.array(
            embeddings,
            dtype="float32"
        )

    def build(self, chunks):

        self.chunks = chunks

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self.get_embeddings(texts)

        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        print(
            f"FAISS index built with {len(chunks)} chunks."
        )

    def save(self, index_path, chunks_path):

        faiss.write_index(
            self.index,
            index_path
        )

        with open(
            chunks_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.chunks,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("Index saved.")

    def load(self, index_path, chunks_path):

        self.index = faiss.read_index(
            index_path
        )

        with open(
            chunks_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.chunks = json.load(f)

        print(
            f"Index loaded with {len(self.chunks)} chunks."
        )

    def search(self, query, k=5):

        query_embedding = self.get_embeddings(
            [query]
        )

        faiss.normalize_L2(
            query_embedding
        )

        scores, indices = self.index.search(
            query_embedding,
            min(k, len(self.chunks))
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            results.append({
                "chunk_id": self.chunks[index]["chunk_id"],
                "project": self.chunks[index]["project"],
                "document_type": self.chunks[index]["document_type"],
                "source": self.chunks[index]["source"],
                "chunk_number": self.chunks[index]["chunk_number"],
                "text": self.chunks[index]["text"],
                "score": float(score)
            })

        return results