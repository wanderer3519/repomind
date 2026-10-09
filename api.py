from fastapi import FastAPI
from pydantic import BaseModel

from src.bm25 import BM25Retriever
from src.generate import generate_answer
from src.hybrid import HybridRetriever
from src.project_extractor import extract_projects
from src.retrieve import VectorStore
from src.router import route_query

INDEX_PATH = "data/index/faiss.json"
CHUNKS_PATH = "data/index/chunks.json"


app = FastAPI(
    title="RepoMind API",
    description="Evidence-grounded AI assistant for software projects",
    version="1.0"
)

# Load retrieval system once when the API starts
store = VectorStore()
store.load(INDEX_PATH, CHUNKS_PATH)

bm25 = BM25Retriever(store.chunks)
hybrid = HybridRetriever(store, bm25)

available_projects = sorted({chunk["project"] for chunk in store.chunks})

class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    route: str
    answer: str
    sources: list


@app.get("/api")
def root():
    return {
        "message": "RepoMind API is running"
    }


@app.post("/api/query", response_model=QueryResponse)
def query(request: QueryRequest):
    question = request.question
    route = route_query(question)
    results = []

    if route == "DIRECT":
        answer = generate_answer(question, results, use_context=False)

    elif route == "RETRIEVE":
        results = hybrid.search(question, k=5)
        answer = generate_answer(question, results)

    elif route == "COMPARE":
        projects = extract_projects(question, available_projects)

        for project in projects:
            project_results = hybrid.search_by_project(question, project, k=3)
            results.extend(project_results)

        answer = generate_answer(question, results)

    else:
        results = hybrid.search(question, k=5)
        answer = generate_answer(question, results)

    sources = []
    seen = set()

    for result in results:
        key = (result["source"], result["chunk_id"])

        if key not in seen:
            sources.append({
                "project": result["project"],
                "source": result["source"],
                "chunk_id": result["chunk_id"]
            })

            seen.add(key)

    return {
        "question": question,
        "route": route,
        "answer": answer,
        "sources": sources
    }