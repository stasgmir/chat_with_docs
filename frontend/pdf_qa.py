# frontend/pdf_qa.py
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.pdf_qa_logic import process_pdf, ask_pdf_question


def back_to_home():
    if st.button("🏠 На главную", key="back_home_button"):
        st.session_state.mode = "🏠 Home"
        st.rerun()


def PDF_QA_Session():
    if "pdf_vector_store" not in st.session_state:
        st.session_state.pdf_vector_store = None

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
    st.header("📄 Chat with Your PDF (OpenAI)")


    if not st.session_state.get("openai_api_key"):
        st.warning("⚠️ Введите OpenAI API ключ в настройках.")
        return

    model = st.session_state.get("selected_llm_model", "gpt-4o-mini")


    uploaded_file = st.file_uploader("📤 Загрузите PDF-документ", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner("⏳ Обрабатываю PDF..."):
            try:
                vector_store = process_pdf(uploaded_file.getvalue(), st.session_state.openai_api_key)
                st.session_state.pdf_vector_store = vector_store
                st.success(f"✅ Файл **{uploaded_file.name}** обработан и готов к вопросам!")
            except Exception as e:
                st.error(f"❌ Ошибка при обработке PDF: {e}")
                st.info("Проверь, что файл не защищён паролем и не повреждён.")

    if st.session_state.get("pdf_vector_store"):
        st.subheader("💬 Задай вопрос о документе")

        question = st.text_input(
            "Вопрос:",
            key="pdf_question",
            placeholder="Например: Какие основные выводы в этом отчёте?",
        )

        if st.button("Получить ответ") and question.strip():
            with st.spinner("🤔 Думаю..."):
                try:
                    answer, docs = ask_pdf_question(
                        st.session_state.pdf_vector_store,
                        question,
                        st.session_state.openai_api_key,
                        model,
                    )

                    if not answer or not answer.strip():
                        st.warning("⚠️ Модель не смогла найти ответ в тексте PDF.")
                    else:
                        st.success("🧠 Ответ:")
                        st.write(answer)

                    if docs:
                        with st.expander("📚 Источники"):
                            for doc in docs:
                                st.markdown(f"**Страница {doc.metadata.get('page', 'N/A')}**")
                                st.markdown(doc.page_content[:500] + "...")
                    else:
                        st.info("Источники не найдены.")
                except Exception as e:
                    st.error(f"⚠️ Ошибка при запросе: {e}")

        elif st.button("Получить ответ") and not question.strip():
            st.warning("Введите вопрос перед отправкой.")

        st.markdown("---")
        if st.button("🧹 Очистить PDF"):
            st.session_state.pdf_vector_store = None
            st.success("PDF очищен. Можно загрузить новый.")
            st.rerun()