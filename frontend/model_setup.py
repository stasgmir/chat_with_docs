import streamlit as st


def model_setup_page():

    st.title("⚙️ Настройка модели")
    st.markdown("Выберите источник языковой модели, с которой вы хотите работать:")

    model_type = st.radio(
        "Тип модели:",
        ["☁️ OpenAI (облачная)", "🧠 Ollama (локальная)"],
        key="selected_model_type",
        horizontal=True,
    )

    st.markdown("---")

    if model_type == "☁️ OpenAI (облачная)":
        st.subheader("🔑 Подключение к OpenAI API")

        api_key = st.text_input(
            "Введите ваш OpenAI API Key:",
            type="password",
            placeholder="sk-...",
            help="Ключ можно получить в [OpenAI Dashboard](https://platform.openai.com/account/api-keys).",
        )

        model_name = st.selectbox(
            "Выберите модель:",
            ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0,
        )

        if st.button("💾 Сохранить настройки"):
            if not api_key:
                st.error("Введите API ключ, чтобы продолжить.")
            else:
                st.session_state["model_type"] = "openai"
                st.session_state["openai_api_key"] = api_key
                st.session_state["selected_llm_model"] = model_name
                st.session_state["setup_complete"] = True
                st.success(" Настройки сохранены!")
                st.rerun()

    else:
        st.subheader("Подключение к локальной модели Ollama")

        ollama_url = st.text_input(
            "Базовый URL Ollama:",
            value=st.session_state.get("ollama_base_url", "http://localhost:11434"),
        )

        local_model = st.selectbox(
            "Выберите модель Ollama:",
            ["llama3", "mistral", "gemma2", "phi3"],
            index=0,
        )

        if st.button("💾 Сохранить настройки"):
            st.session_state["model_type"] = "ollama"
            st.session_state["ollama_base_url"] = ollama_url
            st.session_state["selected_llm_model"] = local_model
            st.session_state["setup_complete"] = True
            st.success("✅ Настройки сохранены!")
            st.rerun()
