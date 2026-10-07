class HybridRetriever:
    def __init__(self, dense_retriever, bm25_retriever):
        self.dense_retriever = dense_retriever
        self.bm25_retriever = bm25_retriever

    def search(self, query, k=5, rrf_k=60, projects=None):
        # Retrieve more candidates before filtering
        dense_results = self.dense_retriever.search(query, k=len(self.dense_retriever.chunks))
        bm25_results = self.bm25_retriever.search(query, k=len(self.bm25_retriever.chunks))

        # Filter by project if requested
        if projects:
            projects = {p.lower() for p in projects}

            dense_results = [
                result
                for result in dense_results
                if result["project"].lower() in projects
            ]

            bm25_results = [
                result
                for result in bm25_results
                if result["project"].lower() in projects
            ]

        scores = {}
        chunks = {}

        for rank, result in enumerate(dense_results, start=1):
            key = result["chunk_id"]

            scores[key] = scores.get(key, 0) + 1 / (rrf_k + rank)
            chunks[key] = result

        for rank, result in enumerate(bm25_results, start=1):
            key = result["chunk_id"]

            scores[key] = scores.get(key, 0) + 1 / (rrf_k + rank)
            chunks[key] = result

        ranked_chunks = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        results = []

        for chunk_id, score in ranked_chunks[:k]:
            result = chunks[chunk_id].copy()
            result["score"] = score
            results.append(result)

        return results

    def search_by_project(self, query, project, k=5, rrf_k=60):
        return self.search(
            query,
            k=k,
            rrf_k=rrf_k,
            projects=[project]
        )