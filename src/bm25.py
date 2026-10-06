from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(self, chunks):
        self.chunks = chunks

        tokenized_chunks = [
            chunk["text"].lower().split()
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_chunks)

    def search(self, query, k=5):

        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = scores.argsort()[::-1]

        results = []

        for index in ranked_indices[:k]:

            results.append({
                "text": self.chunks[index]["text"],
                "source": self.chunks[index]["source"],
                "score": float(scores[index])
            })

        return results