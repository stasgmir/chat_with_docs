import streamlit as st
import sys, os
from langchain.vectorstores import FAISS  # или Chroma, в зависимости от твоей реализации


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.document_processing import process_document, ask_document_question



def back_to_home():
    if st.button("🏠 На главную", key="back_home_button"):
        st.session_state.mode = "🏠 Home"
        st.rerun()


def Document_QA_Session():

    if "doc_vector_store" not in st.session_state:
        st.session_state.doc_vector_store = None
        st.session_state.doc_names = []

    st.markdown("""
        <style>
        div[data-testid="stFileUploader"] > div {
            border: 2px dashed #ccc;
            border-radius: 12px;
            padding: 1rem;
            background-color: #fafafa;
        }
        </style>
    """, unsafe_allow_html=True)

    back_to_home()
    st.header("📚 Chat with Multiple Documents (Docling + OpenAI)")

    if not st.session_state.get("openai_api_key"):
        st.warning("⚠️ Введите OpenAI API ключ в настройках.")
        return

    model = st.session_state.get("selected_llm_model", "gpt-4o-mini")


    uploaded_files = st.file_uploader(
        "📤 Загрузите один или несколько документов",
        type=["pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls", "html", "htm", "png", "jpg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        all_vectorstores = []
        with st.spinner("⏳ Обработка документов..."):
            for uploaded_file in uploaded_files:
                try:
                    vector_store, chunk_count = process_document(
                        uploaded_file.getvalue(),
                        uploaded_file.name,
                        st.session_state.openai_api_key
                    )
                    all_vectorstores.append(vector_store)
                    st.session_state.doc_names.append(uploaded_file.name)
                    st.success(f"✅ {uploaded_file.name} обработан ({chunk_count} фрагментов).")

                except Exception as e:
                    st.error(f"❌ Ошибка при обработке {uploaded_file.name}: {e}")


        if all_vectorstores:
            base_vs = all_vectorstores[0]
            for vs in all_vectorstores[1:]:
                base_vs.merge_from(vs)

            st.session_state.doc_vector_store = base_vs
            st.success(f"🧩 Объединено {len(all_vectorstores)} документов.")


    if st.session_state.get("doc_vector_store"):
        st.subheader(f"💬 Вопрос к документам: {', '.join(st.session_state.doc_names)}")

        question = st.text_input(
            "Введите вопрос:",
            key="multi_doc_question",
            placeholder="Например: Какие основные выводы во всех отчётах?",
        )

        if st.button("Получить ответ"):
            if not question.strip():
                st.warning("Введите вопрос перед отправкой.")
            else:
                with st.spinner("🤔 Думаю..."):
                    try:
                        answer, docs = ask_document_question(
                            st.session_state.doc_vector_store,
                            question,
                            st.session_state.openai_api_key,
                            model,
                        )

                        if not answer.strip():
                            st.warning("⚠️ Модель не смогла найти ответ.")
                        else:
                            st.success("🧠 Ответ:")
                            st.write(answer)

                        if docs:
                            with st.expander("📚 Источники (фрагменты текста)"):
                                for doc in docs:
                                    src_name = doc.metadata.get("source", "Неизвестный документ")
                                    page = doc.metadata.get("page", "")
                                    st.markdown(f"**📄 {src_name} {('(стр. ' + str(page) + ')') if page else ''}**")
                                    st.markdown(doc.page_content[:500] + "...")
                        else:
                            st.info("Источники не найдены.")

                    except Exception as e:
                        st.error(f"⚠️ Ошибка при запросе: {e}")

        st.markdown("---")
        if st.button("🧹 Очистить все документы"):
            st.session_state.doc_vector_store = None
            st.session_state.doc_names = []
            st.success("Документы очищены. Можно загрузить новые.")
            st.rerun()
