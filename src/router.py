import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def route_query(question):
    prompt = f"""
Classify the user's question into exactly ONE
of these categories:

RETRIEVE
- The user is asking about information
  contained in the project documents.

COMPARE
- The user wants to compare or relate
  multiple projects or documents.

DIRECT
- The question does not require the
  project documents.

Return ONLY the category name.

Question:
{question}
"""

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=10
    )

    route = response.choices[0].message.content.strip()
    return route