import speech_recognition as sr
import streamlit as st


def record_voice(language="ru-RU"):

    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Скажи что-нибудь...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language=language)
        st.success("🗣️ Распознано:")
        st.write(f"➡️ {text}")
        return text
    except sr.UnknownValueError:
        st.error("Не удалось распознать речь.")
        return None
    except sr.RequestError as e:
        st.error(f"Ошибка сервиса распознавания: {e}")
        return None
