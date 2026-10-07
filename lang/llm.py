import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


llm = ChatOpenAI(
    model="google/gemini-2.5-flash",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0,
    max_tokens = 1000
)