from pathlib import Path
from pypdf import PdfReader


def load_documents(directory="data/documents"):
    documents = []

    directory = Path(directory)

    for file_path in directory.rglob("*"):

        if file_path.suffix.lower() == ".pdf":
            reader = PdfReader(file_path)

            text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            documents.append({
                "text": text,
                "source": str(file_path)
            })

        elif file_path.suffix.lower() in [".txt", ".md"]:
            text = file_path.read_text(encoding="utf-8")
            
            documents.append({
                "text": text,
                "source": str(file_path)
            })

    return documents

def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks



def create_chunks(documents, chunk_size=500, overlap=100):
    chunks = []

    for document in documents:

        source = document["source"]
        source_path = Path(source)

        # Project is the directory immediately
        # below data/documents/
        project = source_path.parent.name

        document_type = source_path.suffix.lower().lstrip(".")

        text_chunks = chunk_text(
            document["text"],
            chunk_size,
            overlap
        )

        for chunk_number, chunk in enumerate(text_chunks):

            chunks.append({
                "chunk_id": len(chunks),
                "project": project,
                "document_type": document_type,
                "source": source,
                "chunk_number": chunk_number,
                "text": chunk
            })

    return chunks