from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from lang.llm import llm


prompt = ChatPromptTemplate.from_template(
    """
You are a helpful technical assistant.

Answer the question using ONLY the provided context.

If the answer cannot be found in the context,
say:

"I don't know based on the provided documents."

Always mention the source supporting your answer.

Context:

{context}

Question:

{question}
"""
)


def format_documents(documents):

    return "\n\n".join(
        [
            f"""
Project: {doc.metadata.get('project')}
Source: {doc.metadata.get('source')}

{doc.page_content}
"""
            for doc in documents
        ]
    )


def build_rag_chain(retriever):

    chain = (
        {
            "context": retriever | format_documents,
            "question": lambda x: x
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain