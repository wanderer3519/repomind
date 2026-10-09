from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph

from lang.ingest import load_documents
from lang.knowledge_base import KnowledgeBase
from lang.llm import llm
from lang.splitter import split_documents
from lang.upload import (
    get_project_names,
    load_project_index,
    load_uploaded_documents,
)
from lang.vectorstore import build_vectorstore, get_retriever
from src.project_extractor import extract_projects


# 0. Graph state
class State(TypedDict):
    question: str
    route: str
    projects: list
    documents: list
    context: str
    answer: str


# 1. Load documents and build retriever
knowledge_base = KnowledgeBase()

def load_all_documents():
    # Built-in projects
    documents = load_documents("data/documents")

    # User-uploaded projects
    uploaded_projects = get_project_names()

    for project in uploaded_projects:
        uploaded_docs = load_uploaded_documents(project)
        documents.extend(uploaded_docs)

    return documents

def build_current_retriever():
    # Built-in documents
    documents = load_documents("data/documents")
    chunks = split_documents(documents)
    base_vectorstore = build_vectorstore(chunks)

    # Load persisted uploaded project indexes
    uploaded_projects = get_project_names()

    for project in uploaded_projects:

        project_vectorstore = load_project_index(project)
        if project_vectorstore is None:
            continue

        base_vectorstore.merge_from(project_vectorstore)

    retriever = get_retriever(base_vectorstore, k = 5)

    projects = sorted(
        {
            doc.metadata.get("project")
            for doc in chunks
            if doc.metadata.get("project")
        }
        |
        set(uploaded_projects)
    )

    return retriever, chunks, projects





# 3. Prompts

router_prompt = ChatPromptTemplate.from_template(
    """
Classify the user's question into exactly ONE category.

RETRIEVE:
The question requires information from one project or the
project documents.

COMPARE:
The question asks to compare, contrast, or relate multiple
projects.

DIRECT:
The question can be answered without using the project documents.

Return ONLY one word:
RETRIEVE
COMPARE
or
DIRECT

Question:
{question}
"""
)


answer_prompt = ChatPromptTemplate.from_template(
    """
You are RepoMind, an evidence-grounded AI assistant.

Answer the user's question using ONLY the retrieved documents.

Rules:

1. Treat the retrieved documents as the source of truth.
2. Do not use outside knowledge.
3. Answer the question directly and completely.
4. Do not invent information.
5. If the documents do not contain enough information, say:
   "I don't know based on the provided documents."

Retrieved documents:

{context}

Question:

{question}

Answer:
"""
)

compare_prompt = ChatPromptTemplate.from_template(
    """
You are RepoMind, an evidence-grounded AI assistant.

The user wants a comparison between projects.

Use ONLY the retrieved project documents.

Rules:

1. Keep evidence from different projects separate.
2. Do not invent information.
3. Compare the projects only using information present
   in the retrieved documents.
4. Clearly identify which project each fact belongs to.
5. If information needed for the comparison is missing,
   say so explicitly.

Retrieved project evidence:

{context}

Question:

{question}

Provide a clear comparison.
"""
)

# 4. Router
def route_question(state: State):

    response = llm.invoke(
        router_prompt.format_messages(question=state["question"])
    )

    route = response.content.strip().upper()

    if route not in ["DIRECT", "RETRIEVE", "COMPARE"]:
        route = "RETRIEVE"

    return {
        "route": route
    }


# --------------------------------------------------
# 5. DIRECT
# --------------------------------------------------

def direct_answer(state: State):

    response = llm.invoke(
        f"""
Answer the following question directly.

Question:
{state["question"]}
"""
    )

    return {
        "answer": response.content,
        "documents": [],
        "context": "",
        "projects": []
    }


# --------------------------------------------------
# 6. RETRIEVE
# --------------------------------------------------

def retrieve_documents(state: State):

    retriever = knowledge_base.get_retriever(
        k=5
    )

    documents = retriever.invoke(
        state["question"]
    )

    context_parts = []

    for i, document in enumerate(documents, start = 1):
        project = document.metadata.get("project", "unknown")
        source = document.metadata.get("source", "unknown")

        context_parts.append(
            f"""
[Document {i}]
Project: {project}
Source: {source}

{document.page_content}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    return {
        "documents": documents,
        "context": context
    }


def retrieve_answer(state: State):

    response = llm.invoke(
        answer_prompt.format_messages(
            context=state["context"],
            question=state["question"]
        )
    )

    return {
        "answer": response.content
    }

# 7. COMPARE - identify projects

def extract_compare_projects(state: State):
    available_projects = knowledge_base.get_projects()
    projects = extract_projects(state["question"], available_projects)

    return {
        "projects": projects
    }

# 8. COMPARE - retrieve separately for each project

def retrieve_compare_documents(state: State):
    all_documents = []
    context_parts = []

    uploaded_projects = set(get_project_names())

    for project in state["projects"]:
        # Uploaded project

        if project in uploaded_projects:
            project_vectorstore = load_project_index(project)

            if project_vectorstore is None:
                continue

            project_retriever = project_vectorstore.as_retriever(search_kwargs={"k": 3})
            retrieved = project_retriever.invoke(state["question"])

        
        # Built-in project
        else:

            project_documents = [
                doc
                for doc in knowledge_base.chunks
                if doc.metadata.get("project")
                == project
            ]

            if not project_documents:
                continue

            # IMPORTANT:
            # We don't want to embed these again.
            #
            # For now, use the already loaded base
            # vectorstore and filter by project using
            # similarity results.

            base_retriever = knowledge_base.get_retriever(k=10)
            candidates = base_retriever.invoke(state["question"])

            retrieved = [
                doc
                for doc in candidates
                if doc.metadata.get("project")
                == project
            ][:3]

        all_documents.extend(retrieved)
        project_context = "\n\n".join(doc.page_content for doc in retrieved)

        context_parts.append(
            f"""
==============================
PROJECT: {project}
==============================

{project_context}
"""
        )

    context = "\n\n".join(context_parts)

    return {
        "documents": all_documents,
        "context": context
    }


# 9. COMPARE - generate comparison

def compare_answer(state: State):

    response = llm.invoke(
        compare_prompt.format_messages(
            context=state["context"],
            question=state["question"]
        )
    )

    return {
        "answer": response.content
    }


# 10. Decide route

def decide_route(state: State):
    if state["route"] == "DIRECT":
        return "direct"

    if state["route"] == "COMPARE":
        return "compare"

    return "retrieve"

# 11. Build graph

graph = StateGraph(State)

graph.add_node("router", route_question)
graph.add_node("direct", direct_answer)
graph.add_node("retrieve_documents", retrieve_documents)
graph.add_node("retrieve_answer", retrieve_answer)
graph.add_node("extract_compare_projects", extract_compare_projects)
graph.add_node("retrieve_compare_documents", retrieve_compare_documents)
graph.add_node("compare_answer", compare_answer)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    decide_route,
    {
        "direct": "direct",
        "retrieve": "retrieve_documents",
        "compare": "extract_compare_projects"
    }
)

# RETRIEVE
graph.add_edge("retrieve_documents", "retrieve_answer")
graph.add_edge("retrieve_answer", END)

# COMPARE
graph.add_edge("extract_compare_projects", "retrieve_compare_documents")
graph.add_edge("retrieve_compare_documents", "compare_answer")
graph.add_edge("compare_answer", END)

# DIRECT
graph.add_edge("direct", END)

app = graph.compile()