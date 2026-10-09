from src.bm25 import BM25Retriever
from src.generate import generate_answer
from src.hybrid import HybridRetriever
from src.project_extractor import extract_projects
from src.retrieve import VectorStore
from src.router import route_query

INDEX_PATH = "data/index/faiss.json"
CHUNKS_PATH = "data/index/chunks.json"


def main():
    # Load persistent index

    store = VectorStore()
    store.load(INDEX_PATH, CHUNKS_PATH)
    available_projects = sorted({chunk["project"] for chunk in store.chunks})

    print("Available projects:", available_projects)
    
    # Create retrievers
    
    bm25 = BM25Retriever(store.chunks)
    hybrid = HybridRetriever(store, bm25)

    print("RepoMind is ready.")

    # Chat loop

    while True:
        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        # Route query

        route = route_query(question)
        print(f"\nRoute: {route}")

        # Direct question
        
        if route == "DIRECT":
            results = []
            answer = generate_answer(question, results, use_context=False)

        elif route == "RETRIEVE":
            results = hybrid.search(question, k=5)
            print("\nRetrieved chunks:")

            for result in results:
                print(
                    f"- [{result['project']}] "
                    f"{result['source']} "
                    f"(chunk={result['chunk_id']}, "
                    f"score={result['score']:.5f})"
                )

            answer = generate_answer(question, results)

        elif route == "COMPARE":
            projects = extract_projects(question, available_projects)
            print(f"\nProjects identified: {projects}")

            if not projects:
                print("No specific projects identified.")
                results = hybrid.search(question, k=5)
                answer = generate_answer(question, results)

            else:
                project_results = {}

                for project in projects:
                    results = hybrid.search_by_project(question, project, k=3)
                    project_results[project] = results

                    print(f"\nEvidence for [{project}]:")

                    for result in results:
                        print(f"- {result['source']} (chunk={result['chunk_id']}, score={result['score']:.5f})")

                # Combine evidence for the LLM
                results = []
                for project, project_chunks in project_results.items():
                    
                    for result in project_chunks:
                        result = result.copy()
                        result["retrieval_project"] = project

                        results.append(result)

                answer = generate_answer(question, results)
        
        else:
            print("Unknown route. Treating as retrieval.")
            results = hybrid.search(question, k=5)
            answer = generate_answer(question, results)

        print("\nAnswer:")
        print(answer)

        if results:
            print("\nSources:")
            seen = set()

            for i, result in enumerate(results, start=1):
                source = (result["source"], result["chunk_id"])
                
                if source not in seen:
                    print(f"[{i}] {result['source']} (chunk {result['chunk_id']})")
                    seen.add(source)


if __name__ == "__main__":
    main()