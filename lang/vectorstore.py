from langchain_community.vectorstores import FAISS

from lang.embeddings import embeddings


def build_vectorstore(documents):

    vectorstore = FAISS.from_documents(
        documents,
        embeddings
    )

    return vectorstore


def get_retriever(vectorstore, k=5):

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k
        }
    )