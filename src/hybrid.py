class HybridRetriever:

    def __init__(self, dense_retriever, bm25_retriever):
        self.dense_retriever = dense_retriever
        self.bm25_retriever = bm25_retriever

    def search(self, query, k=5, rrf_k=60):

        dense_results = self.dense_retriever.search(
            query,
            k=k
        )

        bm25_results = self.bm25_retriever.search(
            query,
            k=k
        )

        scores = {}
        chunks = {}

        # Dense retrieval
        for rank, result in enumerate(
            dense_results,
            start=1
        ):
            key = result["text"]

            scores[key] = scores.get(key, 0) + (
                1 / (rrf_k + rank)
            )

            chunks[key] = result

        # BM25 retrieval
        for rank, result in enumerate(
            bm25_results,
            start=1
        ):
            key = result["text"]

            scores[key] = scores.get(key, 0) + (
                1 / (rrf_k + rank)
            )

            chunks[key] = result

        ranked_chunks = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        results = []

        for text, score in ranked_chunks[:k]:

            result = chunks[text].copy()

            result["score"] = score

            results.append(result)

        return results