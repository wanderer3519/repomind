import streamlit as st
import requests

from lang.graph import app as langgraph_app


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="RepoMind",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🤖 RepoMind")
st.caption(
    "Evidence-Grounded AI Engineering Assistant"
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Configuration")

implementation = st.sidebar.radio(
    "RAG implementation",
    [
        "From-scratch RAG",
        "LangGraph"
    ]
)


# --------------------------------------------------
# Question
# --------------------------------------------------

question = st.text_area(
    "Ask a question about your projects",
    placeholder=(
        "Example: Compare my ML project and compiler project."
    ),
    height=100
)


ask = st.button(
    "Ask RepoMind",
    type="primary"
)


# --------------------------------------------------
# Query
# --------------------------------------------------

if ask and question.strip():

    question = question.strip()

    # ==============================================
    # FROM-SCRATCH RAG
    # ==============================================

    if implementation == "From-scratch RAG":

        try:

            response = requests.post(
                "http://127.0.0.1:8000/api/query",
                json={
                    "question": question
                },
                timeout=120
            )

            response.raise_for_status()

            result = response.json()

            route = result.get(
                "route",
                "UNKNOWN"
            )

            answer = result.get(
                "answer",
                ""
            )

            sources = result.get(
                "sources",
                []
            )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Could not connect to FastAPI: {e}"
            )

            st.stop()


    # ==============================================
    # LANGGRAPH
    # ==============================================

    else:

        try:

            result = langgraph_app.invoke(
                {
                    "question": question
                }
            )

            route = result.get(
                "route",
                "UNKNOWN"
            )

            answer = result.get(
                "answer",
                ""
            )

            documents = result.get(
                "documents",
                []
            )

        except Exception as e:

            st.error(
                f"LangGraph error: {e}"
            )

            st.stop()


    # --------------------------------------------------
    # Route
    # --------------------------------------------------

    st.divider()

    route_labels = {
        "DIRECT": "💬 DIRECT",
        "RETRIEVE": "🔎 RETRIEVE",
        "COMPARE": "⚖️ COMPARE"
    }

    st.subheader(
        route_labels.get(
            route,
            route
        )
    )


    # --------------------------------------------------
    # Answer
    # --------------------------------------------------

    st.markdown("### Answer")

    st.markdown(answer)


    # --------------------------------------------------
    # Sources / Evidence
    # --------------------------------------------------

    if implementation == "LangGraph":

        documents = result.get(
            "documents",
            []
        )

        if documents:

            with st.expander(
                "📚 Retrieved evidence"
            ):

                for i, document in enumerate(
                    documents,
                    start=1
                ):

                    project = document.metadata.get(
                        "project",
                        "Unknown project"
                    )

                    source = document.metadata.get(
                        "source",
                        "Unknown source"
                    )

                    st.markdown(
                        f"**{i}. {project}**"
                    )

                    st.caption(source)

                    with st.container(
                        border=True
                    ):
                        st.markdown(
                            document.page_content
                        )


    # --------------------------------------------------
    # From-scratch sources
    # --------------------------------------------------

    else:

        if sources:

            with st.expander(
                "📚 Sources"
            ):

                for source in sources:

                    st.markdown(
                        f"- {source}"
                    )