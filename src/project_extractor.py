import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


def extract_projects(question, available_projects):
    project_list = ", ".join(available_projects)

    prompt = f"""
You are given a question about a collection of software projects.

Available projects:
{project_list}

Identify which projects are explicitly relevant to the question.

Rules:
- Return ONLY project names from the available project list.
- If the question mentions two projects, return both.
- If the question asks about projects generally, return all relevant projects.
- Do not invent project names.

Question:
{question}
"""

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=50
    )

    output = response.choices[0].message.content.strip()
    projects = []

    for project in available_projects:
        if project.lower() in output.lower():
            projects.append(project)

    return projects