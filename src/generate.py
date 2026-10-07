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

        context = "\n\n".join(
            [
                f"Project: {result['project']}\n"
                f"Source: {result['source']}\n"
                f"Chunk: {result['chunk_id']}\n"
                f"{result['text']}"
                for result in results
            ]
        )

        prompt = f"""
You are a helpful technical assistant.

Answer the user's question using ONLY
the provided project evidence.

When comparing projects, keep the evidence
from each project separate and explicitly
compare them.

If the answer cannot be found in the context,
say:

"I don't know based on the provided documents."

Always mention the source(s) supporting
your answer.

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