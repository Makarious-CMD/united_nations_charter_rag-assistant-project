# 🌐 United Nations Charter - RAG Assistant

![GitHub repo size](https://img.shields.io/github/repo-size/Makarious-CMD/united_nations_charter_rag-assistant-project)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit)

## 📌 Overview
This is a Retrieval-Augmented Generation (RAG) web application designed to act as an expert assistant on the **United Nations Charter**. It retrieves relevant sections from the charter and generates grounded, accurate answers with citations using a local LLM.

## 🏛 Domain & Data Description
- **Domain:** International Law and International Relations.
- **Data Source:** Text data and PDFs of the United Nations Charter, treaties, and relevant diplomatic documents.
- The data was cleaned, chunked, and embedded into a local vector database for semantic retrieval.

## 🛠 Tech Stack
- **Backend:** FastAPI, Python
- **Frontend:** Streamlit (or Gradio)
- **Vector Database:** ChromaDB
- **LLM Engine:** Ollama (Local LLM)
- **Embeddings:** HuggingFace / Sentence-Transformers

## 📂 Project Structure
```text
  Graduation Project /
│
├── rag_assistant_project/
│   └── rag_pipeline.ipynb      # Data extraction, chunking, and evaluation
│
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── api/routes/query.py # API endpoints
│   │   └── services/           # Retrieval and LLM calling logic
│   ├── data/vector_store/      # Persisted ChromaDB 
│   └── requirements.txt
│
└── frontend/
    ├── app.py                  # Chat UI
    ├── api_client.py           # Backend communication
    └── requirements.txt
