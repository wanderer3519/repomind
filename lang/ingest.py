from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
)


def load_documents(directory = "data/documents"):
    documents = []
    directory = Path(directory)

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()
        project = file_path.parent.name

        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()

        elif suffix in [".txt", ".md"]:
            loader = TextLoader(str(file_path), encoding="utf-8")
            docs = loader.load()

        else:
            continue

        for doc in docs:
            doc.metadata.update({
                "project": project,
                "source": str(file_path),
                "document_type": suffix.lstrip(".")
            })

        documents.extend(docs)

    return documents