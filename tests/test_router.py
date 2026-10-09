from src.router import route_query

questions = [
    "What does the compiler project do?",
    "How do I run the ML project?",
    "Compare my compiler and DBMS projects.",
    "What projects use FastAPI?",
    "What is the capital of Australia?",
    "Hello, how are you?"
]


for question in questions:
    route = route_query(question)

    print(f"\nQuestion: {question}")
    print(f"Route: {route}")