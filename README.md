# Documentation Chatbot — “Chat with Your Docs”

Chat with your documents using AI.  
Upload PDFs, Markdown, or TXT files and ask natural language questions — the bot will return precise answers with context, citations, and code examples.

---

##  Features
- Upload and analyze one or multiple documentation files (PDF, MD, TXT)
- Ask questions in natural language
- Context-aware answers with source references
- Persistent chat history and memory (Redis / SQLite)

---

##  Tech Stack
- **Streamlit** — for building the interactive web application UI  
- **FastAPI** — backend framework for handling file uploads, user queries, and chat history  
- **LangChain** — framework for building LLM-powered workflows (retrieval, prompting, memory)  
- **OpenAI API** — for GPT-4 / GPT-5 access and embedding generation  
- **langchain.embeddings.OpenAIEmbeddings** — generating text embeddings using OpenAI models  
- **langchain.vectorstores.FAISS** — efficient similarity search and vector database management  
- **langchain.chains.RetrievalQA** / **LLMChain** — orchestrating document retrieval and LLM responses  
- **langchain_core.prompts.PromptTemplate** — defining structured prompts for OpenAI models  
- **PyMuPDF**, **Markdown parser**, and **Docling** — for extracting and parsing text from PDF, Markdown, and rich-formatted documents  
- **FAISS / Qdrant** — vector databases for storing and searching document embeddings  
- **Redis / SQLite** — for chat history, caching, and session persistence  

---

##  System Architecture (OpenAI-based)

### 1️ User Interface (Streamlit)
- Multiple file upload support  
- Chat window for interacting with AI  
- Display of answers, source citations, and metadata  

---

### 2️⃣ Backend API (FastAPI)
- `/upload` — handle single or multiple file uploads and preprocessing  
- `/query` — process user questions and return model answers  
- `/history` — manage chat history (Redis / SQLite)  
- Connects to vector database for context retrieval  

---

### 3️⃣ Document Preprocessing Pipeline
1. **Text extraction:** PyMuPDF, Markdown parser, **Docling**  
2. **Text cleaning:** whitespace normalization, merging hyphenated words, cleaning Markdown/HTML artifacts, removing headers, footers, and page numbers  
3. **Chunking:** LangChain TextSplitter (~1000 tokens per chunk)  
4. **Metadata enrichment:** file name, section, page reference  
5. **Embedding generation:** OpenAI Embeddings API  

---

### 4️⃣ Vector Database (FAISS / Qdrant)
- Stores text embeddings  
- Performs similarity search  
- Returns top relevant document chunks  

---

### 5️⃣ LLM Query Module (LangChain + OpenAI API)
- Builds a context from retrieved document fragments  
- Generates natural-language answers via GPT-4 / GPT-5  
- Includes sources and references in responses  
