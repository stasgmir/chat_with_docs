import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import os

def back_to_home():
    st.markdown(
        """
        <style>
        .home-button {
            background-color: #f0f2f6;
            color: #333;
            border-radius: 10px;
            padding: 8px 16px;
            border: none;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .home-button:hover {
            background-color: #e0e3e8;
            transform: translateY(-2px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🏠 На главную", key="back_home_button"):
        st.session_state.mode = "🏠 Home"
        st.rerun()

def RAG_Chat(temperature, FAISS_INDEX_PATH):
    back_to_home()
    st.header("🔍 Chat with RAG Memory")

    if "openai_api_key" not in st.session_state or not st.session_state.openai_api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar.")
        return

    if not os.path.exists(FAISS_INDEX_PATH):
        st.info("No RAG memory found. Please create one first.")
        return

    if "rag_vector_store" not in st.session_state:
        embeddings = OpenAIEmbeddings(api_key=st.session_state.openai_api_key)
        st.session_state.rag_vector_store = FAISS.load_local(
            FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
        )
        st.success("✅ RAG memory loaded successfully!")

    question = st.chat_input("💬 Ask something based on your RAG memory...")

    if question:
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("🔎 Searching RAG memory..."):
                try:
                    retriever = st.session_state.rag_vector_store.as_retriever()
                    docs = retriever.get_relevant_documents(question)
                    context = "\n\n".join([d.page_content for d in docs])

                    prompt = f"Answer the question based on the following context:\n{context}\n\nQuestion: {question}\nAnswer:"

                    llm = ChatOpenAI(
                        api_key=st.session_state.openai_api_key,
                        temperature=temperature,
                        model=st.session_state.get("selected_llm_model", "gpt-4o-mini")
                    )

                    response = llm.invoke(prompt)
                    st.markdown(response.content)

                    with st.expander("📚 Source Documents"):
                        for i, doc in enumerate(docs):
                            st.markdown(f"**Document {i+1}: {doc.metadata.get('source', 'Unknown')}**")
                            st.markdown(doc.page_content[:400] + "...")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
