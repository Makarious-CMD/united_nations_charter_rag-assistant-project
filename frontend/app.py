
import streamlit as st
from api_client import get_answer_from_backend

# Page configuration
st.set_page_config(
    page_title="United Nations Charter Chatbot",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ United Nations Charter Chatbot")
st.markdown(
    "Ask questions about the United Nations Charter and international law. "
    "The chatbot provides answers based on reliable sources from the UN document."
)

# Keep conversation history so the chat remains visible and connected
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if "sources" in message and message["sources"]:
            with st.expander("📚 Cited Sources"):
                for idx, source in enumerate(message["sources"], 1):
                    st.markdown(f"**Source {idx}:** {source}")

# User input
if user_input := st.chat_input("Ask a question about the UN Charter..."):

    # Save and display user's question
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Show loading indicator while waiting for the backend
    with st.chat_message("assistant"):
        with st.spinner("Analyzing the UN document and preparing an answer..."):

            result = get_answer_from_backend(user_input)

            if result.get("error"):
                error_msg = f"⚠️ {result.get('message', 'Something went wrong.')}"
                st.error(error_msg)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })

            else:
                answer = result.get("answer", "")
                sources = result.get("sources", [])

                # Display answer
                st.markdown(answer)

                # Display cited sources
                if sources:
                    with st.expander("📚 Cited Sources"):
                        for idx, source in enumerate(sources, 1):
                            st.markdown(f"**Source {idx}:** {source}")

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

