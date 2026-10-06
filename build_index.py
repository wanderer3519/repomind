from src.ingest import load_documents, create_chunks
from src.retrieve import VectorStore


INDEX_PATH = "data/index/faiss.json"
CHUNKS_PATH = "data/index/chunks.json"



def main():
    documents = load_documents()
    chunks = create_chunks(documents)

    print("Documents loaded:", len(documents))
    print("Chunks created:", len(chunks))

    store = VectorStore()

    store.build(chunks)
    store.save(INDEX_PATH, CHUNKS_PATH)


if __name__ == '__main__':
    main()