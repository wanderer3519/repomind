from src.retrieve import VectorStore
from src.generate import generate_answer
from src.bm25 import BM25Retriever
from src.hybrid import HybridRetriever

INDEX_PATH = "data/index/faiss.json"
CHUNKS_PATH = "data/index/chunks.json"

def main():

    

    store = VectorStore()
    store.load(INDEX_PATH, CHUNKS_PATH)

    bm25 = BM25Retriever(store.chunks)
    hybrid = HybridRetriever(store, bm25)

    print("Ready to answer any question.")

    # -------------------------
    # 4. Chat loop
    # -------------------------

    while True:

        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        # Retrieve relevant chunks
        results = hybrid.search(
            question,
            k = 5
        )


        print("\nHybrid Retrieval:")

        for result in results:

            print(
                f"- {result['source']} "
                f"(score={result['score']:.3f})"
            )


        # Generate answer
        answer = generate_answer(
            question,
            results
        )

        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()