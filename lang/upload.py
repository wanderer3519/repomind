from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from lang.vectorstore import build_vectorstore
from langchain_community.vectorstores import FAISS
from lang.embeddings import embeddings


UPLOAD_DIR = Path("data/user_projects")


def save_uploaded_files(project_name, uploaded_files):
    project_dir = UPLOAD_DIR / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    for uploaded_file in uploaded_files:

        file_path = project_dir / uploaded_file.name

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        saved_files.append(file_path)

    return project_dir, saved_files


def load_uploaded_documents(project_name):

    project_dir = UPLOAD_DIR / project_name

    documents = []

    for file_path in project_dir.iterdir():

        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()

        elif suffix in [".md", ".txt"]:
            loader = TextLoader(
                str(file_path),
                encoding="utf-8"
            )
            docs = loader.load()

        else:
            continue

        for doc in docs:
            doc.metadata.update(
                {
                    "project": project_name,
                    "source": str(file_path),
                }
            )

        documents.extend(docs)

    return documents


def build_project_index(project_name):
    documents = load_uploaded_documents(project_name)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400,
    )

    chunks = splitter.split_documents(documents)

    vectorstore = build_vectorstore(chunks)

    # Persistent index location
    index_dir = UPLOAD_DIR / project_name / "index"
    index_dir.mkdir(parents=True, exist_ok=True)

    vectorstore.save_local(str(index_dir))

    return vectorstore, chunks

def get_project_names():
    if not UPLOAD_DIR.exists():
        return []

    return sorted(
        [
            directory.name
            for directory in UPLOAD_DIR.iterdir()
            if directory.is_dir()
        ]
    )

def load_project_index(project_name):
    index_dir = UPLOAD_DIR / project_name / "index"

    if not index_dir.exists():
        return None

    vectorstore = FAISS.load_local(
        str(index_dir),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vectorstore