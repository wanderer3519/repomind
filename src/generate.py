import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


def generate_answer(question, results):

    context = "\n\n".join(
        [
            f"Source: {result['source']}\n"
            f"{result['text']}"
            for result in results
        ]
    )

    prompt = f"""
You are a helpful technical assistant.

Answer the user's question using ONLY the
provided context.

If the answer cannot be found in the context,
say:

"I don't know based on the provided documents."

Do not use outside knowledge.

Always mention the source(s) supporting your answer.

CONTEXT:

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