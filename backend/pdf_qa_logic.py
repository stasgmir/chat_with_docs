from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from backend.pdf_utils import extract_text_chunks


def process_pdf(file_bytes: bytes, api_key: str):

    try:

        chunks = extract_text_chunks(file_bytes)

        if not chunks:
            raise ValueError("Не удалось извлечь или разделить текст PDF.")

        embeddings = OpenAIEmbeddings(api_key=api_key)
        vector_store = FAISS.from_documents(chunks, embeddings)

        return vector_store, len(chunks)

    except Exception as e:
        raise RuntimeError(f"Ошибка при обработке PDF: {e}") from e


def ask_pdf_question(vector_store, question: str, api_key: str, model: str):

    try:

        retriever = vector_store.as_retriever()
        docs = retriever.get_relevant_documents(question)

        if not docs:
            return "Не удалось найти релевантную информацию в PDF.", []


        context = "\n\n".join([d.page_content for d in docs])

        prompt = f"""
        You are a helpful assistant that answers questions strictly based on the provided PDF content.
        If the answer cannot be found in the text, say you don't have enough information.

        Context:
        {context}

        Question: {question}
        Answer clearly and concisely:
        """


        llm = ChatOpenAI(api_key=api_key, model=model, temperature=0.3)
        response = llm.invoke(prompt)

        return response.content.strip(), docs

    except Exception as e:
        raise RuntimeError(f"Ошибка при запросе к LLM: {e}") from e
