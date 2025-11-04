# 🤖 Multimodal RAG Chatbot with Milvus and OpenAI

A full stack, multimodal Retrieval Augmented Generation (RAG) system that lets users chat with their custom knowledge base containing both text (PDFs) and images. The system uses:

- **Milvus** for vector storage and retrieval  
- **OpenAI** for embeddings, vision, and chat generation  
- **Flask + React** for UI and backend orchestration  

---

## ✨ Features

- **Multimodal ingestion**  
  Index text (PDFs) and image data into Milvus

- **Hybrid retrieval**
  - Text queries use `text-embedding-3-small`
  - Images are captioned using `gpt-4o` then embedded for retrieval

- **Full-stack implementation**
  - Flask backend handles RAG pipeline
  - Lightweight React chat interface

- **Real-time chat UI**
  View responses and latency metrics instantly

---

## ⚙️ Prerequisites

Make sure you have:

- **Python 3.x**
- **Milvus server** (local or cloud)
- **Node.js + npm** (for React UI)
- **OpenAI API key** (embeddings + GPT models)

---

## 📦 Install Dependencies

### Python packages
```bash
pip install flask pymilvus openai Pillow PyPDF2 python-dotenv
