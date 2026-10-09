from lang.upload import build_project_index, load_project_index


def main():
    project_name = "test_project"

    # Build and save the index
    print("Building index...")

    _vectorstore, chunks = build_project_index(project_name)

    print("Number of chunks:", len(chunks))

    # Simulate a new application/query session:
    # load the index from disk instead of rebuilding it.
    print("\nLoading persisted index...")

    loaded_vectorstore = load_project_index(project_name)

    if loaded_vectorstore is None:
        print("Failed to load index.")
        return

    retriever = loaded_vectorstore.as_retriever(search_kwargs={"k": 3})
    results = retriever.invoke("What technologies are used in this project?")

    print("\nRetrieved documents:")

    for i, doc in enumerate(results, start=1):
        print(f"\n--- Document {i} ---")

        print("Project:", doc.metadata.get("project"))
        print("Source:", doc.metadata.get("source"))
        print(doc.page_content[:500])


if __name__ == "__main__":
    main()