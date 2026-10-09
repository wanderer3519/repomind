from lang.ingest import load_documents
from lang.rag import build_rag_chain
from lang.splitter import split_documents
from lang.vectorstore import build_vectorstore, get_retriever


def main():
    print("Loading documents...")

    documents = load_documents()

    print(f"Loaded {len(documents)} documents/pages.")
    print("Splitting documents...")

    chunks = split_documents(documents)

    print(f"Created {len(chunks)} chunks.")
    print("Building vector store...")

    vectorstore = build_vectorstore(chunks)

    print("Vector store ready.")

    retriever = get_retriever(vectorstore, k=5)

    chain = build_rag_chain(retriever)
    query = "What algorithms did I use in my ML project?"
    answer = chain.invoke(query)

    print("\nAnswer:\n")
    print(answer)


if __name__ == "__main__":
    main()