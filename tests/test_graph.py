from lang.graph import app


def run_question(question):
    print("\n" + "=" * 70)
    print(f"QUESTION: {question}")
    print("=" * 70)

    result = app.invoke({"question": question})

    print("\nROUTE:")
    print(result.get("route"))

    print("\nPROJECTS:")
    print(result.get("projects", []))

    print("\nRETRIEVED DOCUMENTS:")

    documents = result.get("documents", [])

    if not documents:
        print("No documents retrieved.")

    else:
        for i, document in enumerate(documents, start=1):
            print(f"\n--- Document {i} ---")
            
            print("Project:", document.metadata.get("project"))
            print("Source:", document.metadata.get("source"))

            print("\nContent:")
            print(document.page_content[:500])


    print("\n" + "-" * 70)

    print("ANSWER:")
    print(result.get("answer"))

    print("=" * 70)


def main():
    questions = [
        # # RETRIEVE
        "What algorithms did I use in my ML project?",

        # # DIRECT
        "What is the capital of Australia?",

        # COMPARE
        "Compare my test_project and compiler project.",

        # UPLOAD and RETRIEVE
        "What technologies are used in test_project?"
    ]

    for question in questions:
        run_question(question)


if __name__ == "__main__":
    main()