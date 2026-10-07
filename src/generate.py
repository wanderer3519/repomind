import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


def generate_answer(question, results, use_context = True):
    
    if not use_context:
        prompt = f"""
Answer the following question normally.

Question:
{question}
"""

    else:

        context_parts = []

        for i, result in enumerate(results, start=1):

            context_parts.append(
                f"""
        [{i}]
        Project: {result['project']}
        Source: {result['source']}
        Chunk: {result['chunk_id']}

        {result['text']}
        """
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are a helpful technical assistant.

Answer the user's question using ONLY the
provided project evidence.

CITATION RULES:

1. Every factual claim based on the documents
   must have a citation.

2. Use the citation number corresponding to
   the evidence.

3. Format citations like [1], [2], [3].

4. You may use multiple citations when a claim
   is supported by multiple sources.

5. Do not invent citations.

6. If the evidence does not contain the answer,
   say:

"I don't know based on the provided documents."

For comparison questions, clearly distinguish
which project each claim refers to.

PROJECT EVIDENCE:

{context}

QUESTION:

{question}
"""

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content