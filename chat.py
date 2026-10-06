from src.retrieve import VectorStore
from src.generate import generate_answer


INDEX_PATH = "data/index/faiss.json"
CHUNKS_PATH = "data/index/chunks.json"

def main():

    store = VectorStore()
    store.load(INDEX_PATH, CHUNKS_PATH)

    print("Ready to answer any question.")

    # -------------------------
    # 4. Chat loop
    # -------------------------

    while True:

        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        # Retrieve relevant chunks
        results = store.search(
            question,
            k=5
        )

        print("\nRetrieved sources:")

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