import os
import tempfile
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

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

def Create_RAG_Memory(FAISS_INDEX_PATH, RAG_DOCS_DIR):
    back_to_home()
    st.header("🧠 Create RAG Memory (Persistent Knowledge Base)")

    if "openai_api_key" not in st.session_state or not st.session_state.openai_api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar.")
        return

    st.markdown("Upload **PDF** or **TXT** files to build a persistent RAG memory (stored as FAISS index).")

    uploaded_files = st.file_uploader(
        "📂 Upload files for RAG memory",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if st.button("🚀 Build / Update RAG Memory"):
        if not uploaded_files:
            st.warning("Please upload at least one document.")
            return

        all_docs = []
        for uploaded in uploaded_files:
            file_ext = os.path.splitext(uploaded.name)[1].lower()

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                tmp_file.write(uploaded.getvalue())
                tmp_path = tmp_file.name

            loader = PyPDFLoader(tmp_path) if file_ext == ".pdf" else TextLoader(tmp_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = uploaded.name
            all_docs.extend(docs)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(all_docs)
        st.info(f"📄 Split into {len(texts)} text chunks.")

        embeddings = OpenAIEmbeddings(api_key=st.session_state.openai_api_key)
        vector_store = FAISS.from_documents(texts, embeddings)
        vector_store.save_local(FAISS_INDEX_PATH)

        st.session_state.rag_vector_store = vector_store
        st.success(f"✅ RAG memory saved to `{FAISS_INDEX_PATH}`")

    if os.path.exists(FAISS_INDEX_PATH):
        st.info(f"📦 FAISS index found at `{FAISS_INDEX_PATH}`")
        if st.button("🗑️ Delete Memory"):
            os.remove(FAISS_INDEX_PATH)
            st.session_state.rag_vector_store = None
            st.success("🧹 RAG memory deleted.")
            st.rerun()
