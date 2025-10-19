import os
from typing import Tuple, List
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
import tempfile

from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from transformers import AutoTokenizer



def process_document(file_bytes: bytes, filename: str, openai_api_key: str):

    tmp_path = None
    try:

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name


        converter = DocumentConverter()
        result = converter.convert(tmp_path)
        doc = result.document
        markdown = doc.export_to_markdown()


        os.makedirs("output", exist_ok=True)
        md_path = f"output/output_{Path(filename).stem}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f" Markdown сохранён: {md_path}")


        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        chunker = HybridChunker(tokenizer=tokenizer, max_tokens=512, merge_peers=True)
        chunks = list(chunker.chunk(dl_doc=doc))

        docs = []
        for i, chunk in enumerate(chunks):
            contextual_text = chunker.contextualize(chunk=chunk)
            docs.append(Document(page_content=contextual_text, metadata={"source": filename, "chunk": i}))


        try:
            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            vector_store = FAISS.from_documents(docs, embeddings)
            print(" Векторное хранилище создано.")
            return vector_store, len(docs)
        except Exception as e:
            print(f"Не удалось создать векторизацию: {e}")
            return None, len(docs)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def ask_document_question(
    vector_store: FAISS,
    question: str,
    openai_api_key: str,
    model_name: str = "gpt-4o-mini"
) -> Tuple[str, List[Document]]:


    try:
        llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=model_name,
            temperature=0.2
        )

        retriever = vector_store.as_retriever(search_kwargs={"k": 4})

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )

        result = qa_chain.invoke({"query": question})
        answer = result["result"]
        sources = result["source_documents"]

        return answer, sources

    except Exception as e:
        raise RuntimeError(f"Ошибка при запросе: {e}")
