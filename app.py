import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000/api/query"


st.set_page_config(
    page_title="RepoMind",
    page_icon="🧠",
    layout="wide"
)


st.title("🧠 RepoMind")
st.caption(
    "Evidence-grounded AI assistant for software projects"
)

question = st.text_area(
    "Ask a question about your projects",
    placeholder=(
        "e.g. Compare my ML and DBMS projects."
    ),
    height=100
)


if st.button("Ask RepoMind", type="primary"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner("Thinking..."):

            response = requests.post(
                API_URL,
                json={"question": question},
                timeout=120
            )

        if response.status_code == 200:

            data = response.json()

            st.subheader("Answer")

            st.write(data["answer"])

            st.divider()

            st.subheader("Details")

            st.write(
                f"**Route:** `{data['route']}`"
            )

            if data["sources"]:

                st.subheader("Sources")

                for source in data["sources"]:

                    st.write(
                        f"- **{source['project']}** — "
                        f"{source['source']} "
                        f"(chunk {source['chunk_id']})"
                    )

        else:

            st.error(
                f"API error: {response.status_code}"
            )