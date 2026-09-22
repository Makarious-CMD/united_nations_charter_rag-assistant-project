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


## 🧠 Advanced Methodology & Anti-Hallucination Strategy
Given the sensitive nature of International Law and the United Nations Charter, minimizing hallucinations and ensuring absolute factual accuracy is critical. To achieve this, the project implements a highly optimized, resource-efficient architecture:

1. **Two-Stage Retrieval:(hybird search)** The system retrieves the Top-K documents and applies a **Reranker** based strictly on question similarity to isolate the single most relevant and accurate context chunk.
2. **Multi-Candidate Generation (Local):** It generates three distinct candidate answers using a lightweight local model (**Llama 3 8B**). A strict `temperature` of `0.1` is enforced to suppress creative text generation and ground the model entirely in the provided facts.
3. **LLM-as-a-Judge (API):** The three candidates are passed to a larger, more powerful model (**Llama 3 70B via Groq API**) acting as a judge. The judge evaluates the candidates against the retrieved context and selects the most accurate, grounded answer.

**🎯 The Impact:** 
This hybrid approach achieves the "impossible equation"—maximizing the reasoning capabilities of a low-resource local model while minimizing API credit consumption for the judge. The system achieved an exceptional **88% - 90% accuracy rate**, proving that highly reliable, production-grade results can be achieved locally with smart architectural design.

## 📊 Evaluation Results
*Evaluated against a test set to verify retrieval relevance and grounding, in compliance with project requirements.*

| Metric | Result | Notes |
|--------|--------|-------|
| **Overall Accuracy** | **88% - 90%** | Exceptionally high for a local 8B model, achieved via the LLM-as-a-Judge approach. |
| **Hallucination Rate** | less 5-7% | Mitigated by Temperature = 0.1 and strict prompt constraints. |
| **Retrieval Quality** | High | Enhanced by Top-K + Reranking strategy. |

*(Detailed question/answer breakdown is available in the `notebooks/rag_pipeline.ipynb` evaluation table).*
│   └── requirements.txt
│
└── frontend/
    ├── app.py                  # Chat UI
    ├── api_client.py           # Backend communication
    └── requirements.txt
