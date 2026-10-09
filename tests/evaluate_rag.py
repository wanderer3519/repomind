import json

from src.bm25 import BM25Retriever
from src.generate import generate_answer
from src.hybrid import HybridRetriever
from src.project_extractor import extract_projects
from src.retrieve import VectorStore
from src.router import route_query

INDEX_PATH = "data/index/faiss.json"
CHUNKS_PATH = "data/index/chunks.json"


def main():
    with open("tests/questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    store = VectorStore()
    store.load(INDEX_PATH, CHUNKS_PATH)

    bm25 = BM25Retriever(store.chunks)
    hybrid = HybridRetriever(store, bm25)

    available_projects = sorted({chunk["project"] for chunk in store.chunks})
    total = len(questions)
    passed = 0

    for i, item in enumerate(questions, start=1):
        question = item["question"]

        print(f"\n{'=' * 60}")
        print(f"Question {i}: {question}")

        route = route_query(question)

        if route == "DIRECT":
            results = []
            answer = generate_answer(question, results, use_context=False)

        elif route == "COMPARE":
            results = []
            projects = extract_projects(question, available_projects)
            
            for project in projects:
                project_results = hybrid.search_by_project(question, project, k=3)
                results.extend(project_results)

            answer = generate_answer(question, results)

        else:
            results = hybrid.search(question, k=5)
            answer = generate_answer(question,results)

        expected_projects = item.get("expected_projects", [])
        expected_keywords = item.get("expected_keywords", [])

        answer_lower = answer.lower()

        keywords_found = all(
            keyword.lower() in answer_lower
            for keyword in expected_keywords
        )

        projects_found = all(
            any(
                project.lower() in
                result["project"].lower()
                for result in results
            )
            for project in expected_projects
        )

        passed_question = keywords_found and projects_found

        if passed_question:
            passed += 1
            print("RESULT: PASS")

        else:
            print("RESULT: FAIL")

        print("\nAnswer:")
        print(answer)

    print(f"\n{'=' * 60}")
    print(f"RAG Evaluation: {passed}/{total} ({passed / total:.2%})")


if __name__ == "__main__":
    main()