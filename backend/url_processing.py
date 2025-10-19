import os
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from langchain_openai import ChatOpenAI


def fetch_url_content(url: str) -> str:


    print(f"\n🌍 Загружаю страницу: {url}")

    headers = {"User-Agent": "Mozilla/5.0 (ChatWithDocsBot/1.0)"}
    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code != 200:
        raise Exception(f"Ошибка загрузки: {response.status_code}")

    content_type = response.headers.get("Content-Type", "").lower()

    if "application/pdf" in content_type or url.endswith(".pdf"):
        print("📄 Обнаружен PDF — сохраняем временно для анализа Docling...")
        tmp_pdf = Path("temp_url_doc.pdf")
        with open(tmp_pdf, "wb") as f:
            f.write(response.content)
        return f"[PDF файл сохранён: {tmp_pdf.resolve()}]"

    if "html" in content_type:
        print("🧩 Обнаружен HTML — извлекаем текст из тегов...")
        soup = BeautifulSoup(response.text, "html.parser")


        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        clean_text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
        print(f"✅ Извлечено {len(clean_text)} символов текста.")
        return clean_text[:50000]


    if "text" in content_type:
        print("🧾 Обнаружен текстовый ресурс.")
        return response.text[:50000]

    raise Exception("❌ Неизвестный формат ссылки или тип контента.")



def ask_question_about_url_text(text: str, question: str, openai_api_key: str):

    print(f"\n💭 Вопрос по содержанию: {question}")

    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key, temperature=0.4)

    prompt = (
        "Вот текст, извлечённый со страницы. "
        "Ответь кратко и по сути на вопрос пользователя.\n\n"
        f"=== Текст страницы ===\n{text[:15000]}\n\n"
        f"=== Вопрос ===\n{question}"
    )

    response = llm.invoke(prompt)
    return response.content



def process_url_and_answer(url: str, question: str, openai_api_key: str):


    text = fetch_url_content(url)

    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key, temperature=0.4)


    summary_prompt = (
        "Составь краткое (5 предложений) резюме следующего текста:\n\n"
        f"{text[:10000]}"
    )
    summary = llm.invoke(summary_prompt).content

    answer = ask_question_about_url_text(text, question, openai_api_key)

    return answer, summary



def main():
    print("=" * 60)
    print("🌐 URL Content Q&A (Requests + BeautifulSoup + OpenAI)")
    print("=" * 60)

    url = input("🔗 Введите ссылку: ").strip()
    if not url:
        print("❌ Не указана ссылка.")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Установите переменную окружения OPENAI_API_KEY.")
        return

    try:
        text = fetch_url_content(url)
        print(f"\n📜 Извлечено {len(text)} символов текста.")
        print(f"Превью:\n{text[:400]}...\n")

        question = input("💬 Введите вопрос к содержимому: ").strip()
        if not question:
            print("❌ Вопрос не задан.")
            return

        answer = ask_question_about_url_text(text, question, api_key)
        print("\n🧠 Ответ:\n" + answer)

    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
