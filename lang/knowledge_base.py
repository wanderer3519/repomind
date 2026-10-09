from pathlib import Path

from langchain_community.vectorstores import FAISS

from lang.embeddings import embeddings
from lang.ingest import load_documents
from lang.splitter import split_documents
from lang.upload import (
    get_project_names,
    load_project_index,
)
from lang.vectorstore import build_vectorstore

BASE_INDEX_DIR = Path("data/lang_index")

class KnowledgeBase:
    def __init__(self):
        self.vectorstore = None
        self.chunks = []
        self.projects = set()

        self.load()

    def build_base_index(self):

        print("Building base LangChain index...")

        documents = load_documents("data/documents")
        self.chunks = split_documents(documents)
        self.vectorstore = build_vectorstore(self.chunks)

        BASE_INDEX_DIR.mkdir(parents = True, exist_ok = True)

        self.vectorstore.save_local(str(BASE_INDEX_DIR))

        self.projects = {
            doc.metadata.get("project")
            for doc in self.chunks
            if doc.metadata.get("project")
        }

        print(f"Built base index with {len(self.chunks)} chunks.")

    def load(self):
        if not BASE_INDEX_DIR.exists():
            self.build_base_index()

        else:
            print("Loading persistent base index...")

            self.vectorstore = FAISS.load_local(
                str(BASE_INDEX_DIR),
                embeddings,
                allow_dangerous_deserialization=True,
            )

            # We still need metadata/chunks for project-aware comparison.
            documents = load_documents("data/documents")
            self.chunks = split_documents(documents)

            self.projects = {
                doc.metadata.get("project")
                for doc in self.chunks
                if doc.metadata.get("project")
            }

        self.load_uploaded_projects()

    def load_uploaded_projects(self):
        uploaded_projects = get_project_names()

        for project in uploaded_projects:
            project_vectorstore = load_project_index(project)

            if project_vectorstore is None:
                continue

            self.vectorstore.merge_from(project_vectorstore)
            self.projects.add(project)

            print(f"Loaded uploaded project: {project}")

    def get_retriever(self, k=5):
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

    def get_projects(self):
        return sorted(self.projects)

    def add_project(self, project_name):
        project_vectorstore = load_project_index(project_name)
        if project_vectorstore is None:
            return

        self.vectorstore.merge_from(project_vectorstore)
        self.projects.add(project_name)

        print(f"Added project to knowledge base: {project_name}")