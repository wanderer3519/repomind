from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400
    )

    return splitter.split_documents(documents)