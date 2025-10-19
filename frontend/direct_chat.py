import streamlit as st
from openai import OpenAI
from langchain_community.llms import Ollama
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.voice_recognition import record_voice



st.markdown("""
    <style>
    div[data-testid="stTextInput"] > div > div {
        border-radius: 20px;
        border: 1px solid #ccc;
        padding: 0.2rem 0.8rem;
    }


    button[kind="secondary"] {
        border-radius: 50%;
        height: 2.5em;
        width: 2.5em;
        padding: 0 !important;
        font-size: 1.2em !important;
    }

    div[data-testid="column"]:has(button[title="Отправить сообщение"]) button {
        background-color: #000000 !important;
        color: white !important;
        border-radius: 50% !important;
        height: 2.5em !important;
        width: 2.5em !important;
        font-size: 1.2em !important;
        border: none !important;
    }

    div[data-testid="column"]:has(button[title="Отправить сообщение"]) button:hover {
        background-color: #333333 !important;
    }
    </style>
""", unsafe_allow_html=True)


def back_to_home():
    if st.button("🏠 На главную", key="back_home_button"):
        st.session_state.mode = "🏠 Home"
        st.rerun()


def Direct_LLM_Chat(temperature: float):
    back_to_home()
    st.header("💬 Direct Chat")

    model_type = st.session_state.get("model_type")
    if not model_type:
        st.error("⚠️ Модель не выбрана. Вернитесь на экран настройки.")
        if st.button("🔄 Настроить модель"):
            st.session_state.setup_complete = False
            st.rerun()
        return


    if model_type == "openai":
        st.subheader("OpenAI Chat Mode")
        if not st.session_state.get("openai_api_key"):
            st.warning(" Введите свой OpenAI API ключ в настройках.")
            return
        client = OpenAI(api_key=st.session_state.openai_api_key)
        model_name = st.session_state.get("selected_llm_model", "gpt-4o-mini")

    elif model_type == "ollama":
        st.subheader("Ollama Chat Mode")
        base_url = st.session_state.get("ollama_base_url", "http://localhost:11434")
        model_name = st.session_state.get("selected_llm_model", "llama3")
        try:
            llm = Ollama(model=model_name, base_url=base_url)
        except Exception as e:
            st.error(f"Ошибка подключения к Ollama: {e}")
            return

    if "direct_chat_history" not in st.session_state:
        st.session_state.direct_chat_history = []
    if "user_text" not in st.session_state:
        st.session_state.user_text = ""

    if st.session_state.get("clear_input"):
        st.session_state.user_text = ""
        del st.session_state["clear_input"]

    if "voice_buffer" in st.session_state:
        st.session_state.user_text = st.session_state.voice_buffer
        del st.session_state.voice_buffer

    for msg in st.session_state.direct_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("---")
    st.markdown("### 💬 Напиши сообщение или используй микрофон")


    input_col, mic_col, send_col = st.columns([12, 1, 1])

    with input_col:
        st.text_input(
            "Введите сообщение:",
            key="user_text",
            placeholder="Напиши сообщение...",
            label_visibility="collapsed",
        )

    with mic_col:
        mic_pressed = st.button("🎙️", help="Сказать сообщение", use_container_width=True)
        if mic_pressed:
            text = record_voice()
            if text:
                st.session_state.voice_buffer = text
            st.rerun()

    with send_col:
        send_pressed = st.button("➤", help="Отправить сообщение", use_container_width=True)


    if send_pressed:
        prompt = (st.session_state.get("user_text") or "").strip()
        if prompt:
            st.session_state.direct_chat_history.append({"role": "user", "content": prompt})
            st.session_state["clear_input"] = True
            st.rerun()


    if st.session_state.direct_chat_history and st.session_state.direct_chat_history[-1]["role"] == "user":
        prompt = st.session_state.direct_chat_history[-1]["content"]
        with st.chat_message("assistant"):
            with st.spinner("Думаю..."):
                try:
                    if model_type == "openai":
                        stream = client.chat.completions.create(
                            model=model_name,
                            messages=st.session_state.direct_chat_history,
                            temperature=temperature,
                            stream=True,
                        )
                        placeholder = st.empty()
                        acc = ""
                        for ch in stream:
                            delta = ch.choices[0].delta
                            if "content" in delta:
                                acc += delta.content
                                placeholder.markdown(acc + "▌")
                        placeholder.markdown(acc)
                        st.session_state.direct_chat_history.append({"role": "assistant", "content": acc})

                    else:  # ollama
                        resp = llm.invoke(prompt)
                        st.markdown(resp)
                        st.session_state.direct_chat_history.append({"role": "assistant", "content": resp})

                except Exception as e:
                    st.error(f"⚠️ Ошибка при работе с моделью: {e}")

    st.markdown("---")
    if st.button("🧹 Очистить чат"):
        st.session_state.direct_chat_history = []
        st.session_state["clear_input"] = True
        st.rerun()
