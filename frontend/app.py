
import os
import requests
import streamlit as st


# Backend URL
API_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

# Page configuration
st.set_page_config(
    page_title="AI PDF Chatbot",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "filename" not in st.session_state:
    st.session_state.filename = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# Application title
st.title("📚 AI PDF Chatbot")
st.caption("Upload a PDF and ask questions using AI.")


# Sidebar
with st.sidebar:
    st.header("Settings")

    provider = st.selectbox(
        "Select AI Model",
        ["ollama", "gemini"]
    )

    st.divider()

    st.subheader("Upload PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"]
    )

    if st.button(
        "Upload PDF",
        use_container_width=True,
        disabled=uploaded_file is None
    ):

        try:
            with st.spinner("Processing your PDF..."):

                response = requests.post(
                    f"{API_URL}/api/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    },
                    timeout=300
                )

            if response.ok:
                data = response.json()

                st.session_state.document_id = data["document_id"]
                st.session_state.filename = data["filename"]
                st.session_state.messages = []

                st.success("PDF uploaded successfully!")

                st.write("Pages:", data["total_pages"])
                st.write("Chunks:", data["total_chunks"])

            else:
                st.error(response.text)

        except requests.RequestException as error:
            st.error(f"Backend connection failed: {error}")

    st.divider()

    if st.session_state.document_id:

        st.success("Document ready")

        st.write(
            f"**File:** {st.session_state.filename}"
        )

        if st.button(
            "Delete Document",
            use_container_width=True
        ):

            try:
                response = requests.delete(
                    f"{API_URL}/api/documents/"
                    f"{st.session_state.document_id}",
                    timeout=60
                )

                if response.ok:
                    st.session_state.document_id = None
                    st.session_state.filename = None
                    st.session_state.messages = []

                    st.success("Document deleted.")
                    st.rerun()
                else:
                    st.error(response.text)

            except requests.RequestException as error:
                st.error(str(error))


# Main chat area
if not st.session_state.document_id:

    st.info("Upload a PDF from the sidebar to start chatting.")

else:

    st.subheader(
        f"Chatting with: {st.session_state.filename}"
    )

    # Display previous messages
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message.get("sources"):
                st.caption(
                    "Source pages: "
                    + ", ".join(map(str, message["sources"]))
                )

    # Chat input
    question = st.chat_input(
        "Ask a question about your PDF..."
    )

    if question:

        # Display user question
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        # Call FastAPI
        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:
                    response = requests.post(
                        f"{API_URL}/api/chat",
                        json={
                            "document_id": st.session_state.document_id,
                            "question": question,
                            "provider": provider
                        },
                        timeout=180
                    )

                    response.raise_for_status()

                    data = response.json()

                    answer = data["answer"]
                    sources = data.get("sources", [])

                    st.markdown(answer)

                    if sources:
                        st.caption(
                            "Source pages: "
                            + ", ".join(map(str, sources))
                        )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except requests.RequestException as error:

                    error_message = (
                        f"Could not generate an answer: {error}"
                    )

                    if getattr(error, "response", None) is not None:
                        error_message += (
                            f"\n\nAPI response: "
                            f"{error.response.text}"
                        )

                    st.error(error_message)

                except (KeyError, ValueError) as error:
                    st.error(f"Invalid API response: {error}")
