import json

from src.retrieve import VectorStore
from src.bm25 import BM25Retriever
from src.hybrid import HybridRetriever


INDEX_PATH = "data/index/faiss.json"
CHUNKS_PATH = "data/index/chunks.json"
QUESTIONS_PATH = "evaluation/questions.json"


def get_chunk_id(result, chunks):

    for i, chunk in enumerate(chunks):

        if chunk["text"] == result["text"]:
            return i

    return None


def recall_at_k(retriever, questions, chunks, k):

    hits = 0

    for item in questions:

        results = retriever.search(
            item["question"],
            k=k
        )

        retrieved_ids = {
            get_chunk_id(result, chunks)
            for result in results
        }

        relevant_ids = set(
            item["relevant_chunks"]
        )

        if relevant_ids.intersection(
            retrieved_ids
        ):
            hits += 1

    return hits / len(questions)


def main():

    with open(QUESTIONS_PATH, "r") as f:
        questions = json.load(f)

    store = VectorStore()

    store.load(
        INDEX_PATH,
        CHUNKS_PATH
    )

    bm25 = BM25Retriever(
        store.chunks
    )

    hybrid = HybridRetriever(
        store,
        bm25
    )

    retrievers = {
        "Dense": store,
        "BM25": bm25,
        "Hybrid RRF": hybrid
    }

    for name, retriever in retrievers.items():

        score = recall_at_k(
            retriever,
            questions,
            store.chunks,
            k=2
        )

        print(
            f"{name} Recall@2: "
            f"{score:.3f}"
        )


if __name__ == "__main__":
    main()