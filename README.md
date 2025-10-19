# Chat with Your Docs — Documentation Chatbot

Chat with your documentation using AI.
Upload PDF, Markdown, or TXT files and ask natural language questions — the bot returns precise answers with citations.

## Features
- Upload and analyze one or multiple docs (PDF, MD, TXT)
- Ask questions in natural language
- Context-aware answers with source references
- Chat history and memory (Redis / SQLite)

## Quickstart
```
pip install -r requirements.txt
uvicorn backend.main:app --reload
streamlit run frontend/app.py
```