import streamlit as st

from lang.graph import app as langgraph_app
from lang.graph import knowledge_base
from lang.upload import (
    build_project_index,
    save_uploaded_files,
)

# Page configuration

st.set_page_config(
    page_title="RepoMind",
    page_icon="🧠",
    layout="wide",
)


# Header
st.title("🧠 RepoMind")

st.markdown(
    """
**Evidence-Grounded AI Engineering Assistant**

Ask questions about your projects, compare projects,
or upload your own project documentation.
"""
)

# Project upload
st.sidebar.subheader("📁 Add Project")

project_name = st.sidebar.text_input(
    "Project name",
    placeholder="e.g. my_project",
)

uploaded_files = st.sidebar.file_uploader(
    "Upload project documents",
    type=["pdf", "md", "txt"],
    accept_multiple_files=True,
)

if st.sidebar.button(
    "Add Project",
    use_container_width=True,
):

    if not project_name.strip():

        st.sidebar.error(
            "Please enter a project name."
        )

    elif not uploaded_files:

        st.sidebar.error(
            "Please upload at least one document."
        )

    else:

        project_name = project_name.strip()

        try:
            # Save uploaded files

            save_uploaded_files(
                project_name,
                uploaded_files,
            )

            # Build + persist project FAISS index
            with st.spinner("Processing project documents..."):

                build_project_index(
                    project_name
                )

            # Add persisted index to running KnowledgeBase
            knowledge_base.add_project(
                project_name
            )

            st.sidebar.success(
                f"Added project: {project_name}"
            )

        except Exception as e:

            st.sidebar.error(
                f"Failed to add project: {e}"
            )



# Show available projects
st.sidebar.divider()

st.sidebar.subheader("📚 Available Projects")

projects = knowledge_base.get_projects()

if projects:

    for project in projects:

        st.sidebar.write(
            f"• {project}"
        )

else:

    st.sidebar.caption(
        "No projects available."
    )



# Main question area
st.subheader("Ask RepoMind")

question = st.text_area(
    "Question",
    placeholder=(
        "e.g. What algorithms did I use "
        "in my ML project?"
    ),
    height=100,
)

ask = st.button(
    "🔍 Ask",
    type="primary",
    use_container_width=True,
)


# Query execution
if ask:
    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:
        with st.spinner("RepoMind is thinking..."):
            result = langgraph_app.invoke({
                "question": question
            })

        route = result.get(
            "route",
            "UNKNOWN"
        )
        
        # Route indicator
        if route == "DIRECT":
            st.info(
                "💬 DIRECT — "
                "No project retrieval required."
            )

        elif route == "RETRIEVE":
            st.info(
                "🔎 RETRIEVE — "
                "Searching project knowledge."
            )

        elif route == "COMPARE":
            st.info(
                "⚖️ COMPARE — "
                "Retrieving evidence from projects."
            )

        
        # Answer
        st.subheader("Answer")
        st.markdown(
            result.get(
                "answer",
                "No answer generated."
            )
        )
        
        # Retrieved evidence
        
        documents = result.get("documents",[])
        
        if documents:
            with st.expander("📄 Retrieved Evidence"):
                for i, document in enumerate(documents, start = 1):
                    st.markdown(f"### Document {i}")
                    st.caption(
                        f"Project: "
                        f"{document.metadata.get('project', 'unknown')}"
                    )
                    st.caption(
                        f"Source: "
                        f"{document.metadata.get('source', 'unknown')}"
                    )
                    st.markdown(document.page_content)
                    if i < len(documents):
                        st.divider()