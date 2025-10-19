import streamlit as st
from pathlib import Path
from backend.audio_processing import transcribe_audio, answer_question_from_transcript


def back_to_home():
    if st.button("🏠 На главную", key="back_home_audio"):
        st.session_state.mode = "🏠 Home"
        st.rerun()


def Audio_QA_Session():


    back_to_home()
    st.header("🎧 Chat with Audio (Docling + Whisper + OpenAI)")


    if not st.session_state.get("openai_api_key"):
        st.warning("⚠️ Введите OpenAI API ключ в настройках.")
        return


    uploaded_audio = st.file_uploader(
        "📤 Загрузите аудиофайл",
        type=["mp3", "wav", "m4a", "flac"]
    )

    if uploaded_audio is not None:

        with st.spinner(f"🎙️ Обработка {uploaded_audio.name}..."):
            try:
                transcript_path = transcribe_audio(uploaded_audio.getvalue(), uploaded_audio.name)
                st.session_state["transcript_path"] = transcript_path  # сохраняем для повторного использования
                st.success(f"✅ Аудио успешно транскрибировано: {uploaded_audio.name}")


                with open(transcript_path, "r", encoding="utf-8") as f:
                    transcript_text = f.read()
                st.markdown("### 📝 Текстовая расшифровка")
                st.text_area("Transcript", transcript_text[:3000], height=300)

            except Exception as e:
                st.error(f"❌ Ошибка при транскрипции: {e}")
                return


        st.markdown("---")
        question = st.text_input("💬 Задай вопрос по содержанию аудио:")
        if question and st.button("Получить ответ"):
            if "transcript_path" not in st.session_state:
                st.error("⚠️ Сначала загрузите и обработайте аудио.")
            else:
                with st.spinner("🤔 Анализирую..."):
                    try:
                        answer = answer_question_from_transcript(
                            st.session_state["transcript_path"],
                            st.session_state.openai_api_key,
                            question
                        )
                        st.success("🧠 Ответ:")
                        st.write(answer)
                    except Exception as e:
                        st.error(f"❌ Ошибка при анализе: {e}")
