import streamlit as st
from backend.url_processing import process_url_and_answer


def back_to_home():
    if st.button("🏠 На главную", key="back_home_url"):
        st.session_state.mode = "🏠 Home"
        st.rerun()


def URL_QA_Session():
    """Интерфейс для задания вопросов по ссылке."""
    back_to_home()
    st.header("🌐 Chat with a Web Page")

    if not st.session_state.get("openai_api_key"):
        st.warning("⚠️ Введите OpenAI API ключ в настройках.")
        return

    url = st.text_input("🔗 Вставьте ссылку на страницу или документ:")
    if not url:
        st.info("Введите ссылку, например: https://example.com/article")
        return

    question = st.text_input("💬 Вопрос к содержимому страницы:")
    if st.button("Получить ответ"):
        with st.spinner("⏳ Загружаю и анализирую страницу..."):
            try:
                answer, summary = process_url_and_answer(
                    url,
                    question,
                    st.session_state.openai_api_key
                )
                st.success("🧠 Ответ:")
                st.write(answer)

                with st.expander("📄 Краткое содержание страницы"):
                    st.write(summary)

            except Exception as e:
                st.error(f"❌ Ошибка при обработке ссылки: {e}")
