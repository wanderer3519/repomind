import os
import numpy as np

from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.embeddings import Embeddings


load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


class OpenRouterEmbeddings(Embeddings):

    def __init__(
        self,
        model="nvidia/nemotron-3-embed-1b:free"
    ):
        self.model = model

    def embed_documents(self, texts):

        response = client.embeddings.create(
            model=self.model,
            input=texts
        )

        return [
            item.embedding
            for item in response.data
        ]

    def embed_query(self, text):

        response = client.embeddings.create(
            model=self.model,
            input=[text]
        )

        return response.data[0].embedding


embeddings = OpenRouterEmbeddings()