import json

from src.bm25 import BM25Retriever
from src.hybrid import HybridRetriever
from src.retrieve import VectorStore

INDEX_PATH = "data/index/faiss.json"
CHUNKS_PATH = "data/index/chunks.json"
QUESTIONS_PATH = "evaluation/questions.json"


def recall_at_k(retriever, questions, k):
    hits = 0

    for item in questions:
        results = retriever.search(item["question"], k=k)

        retrieved_ids = {result["chunk_id"] for result in results}
        relevant_ids = set(item["relevant_chunks"])

        if relevant_ids.intersection(retrieved_ids):
            hits += 1

    return hits / len(questions)

def reciprocal_rank(retriever, questions, k=5):

    total = 0.0

    for item in questions:
        results = retriever.search(item["question"], k=k)
        relevant_ids = set(item["relevant_chunks"])

        for rank, result in enumerate(results, start=1):
            if result["chunk_id"] in relevant_ids:
                total += 1 / rank
                break

    return total / len(questions)


def print_retrieval_results(retrievers, questions, k=5):
    """
    Print the retrieved chunk IDs for every
    question and every retriever.
    """

    for question_number, item in enumerate(questions,start=1):
        print("\n" + "=" * 70)
        print(f"Question {question_number}: {item['question']}")
        print(f"Expected chunks: {item['relevant_chunks']}")

        for name, retriever in retrievers.items():
            results = retriever.search(item["question"], k=k)
            retrieved_ids = [result["chunk_id"] for result in results]
            print(f"{name:<12}: {retrieved_ids}")


def main():
    # Load evaluation questions
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    # Load vector store

    store = VectorStore()
    store.load(INDEX_PATH, CHUNKS_PATH)

    # Create retrievers

    bm25 = BM25Retriever(store.chunks)
    hybrid = HybridRetriever(store, bm25)

    retrievers = {
        "Dense": store,
        "BM25": bm25,
        "Hybrid RRF": hybrid
    }

    # Evaluation metrics

    print("\n" + "=" * 70)
    print("RECALL RESULTS")
    print("=" * 70)

    for name, retriever in retrievers.items():
        print(f"\n{name}")

        for k in [1, 3, 5]:
            score = recall_at_k(retriever, questions, k)
            print(f"Recall@{k}: {score:.3f}")

    # Detailed retrieval results

    print("\n\n" + "=" * 70)
    print("DETAILED RETRIEVAL RESULTS")
    print("=" * 70)

    print_retrieval_results(retrievers, questions, k = 5)

    print("\n" + "=" * 70)
    print("MRR RESULTS")
    print("=" * 70)

    for name, retriever in retrievers.items():
        score = reciprocal_rank(retriever, questions, k=5)
        print(f"{name} MRR@5: {score:.3f}")


if __name__ == "__main__":
    main()