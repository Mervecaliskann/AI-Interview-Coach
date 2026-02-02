# 👩‍💼 AI Interview Coach: Zara

**Zara** is an AI-powered interactive interview simulator designed to conduct voice-based technical interviews. It analyzes your resume (PDF) using **RAG (Retrieval-Augmented Generation)** and asks tailored questions to test your skills.

Built with **Llama-3**, **Pinecone**, and **Docker**.

## 🚀 Features

* **📄 Resume Analysis:** Upload your CV (PDF), and Zara creates a custom knowledge base using vector embeddings.
* **🧠 RAG Architecture:** Uses **LangChain** and **Pinecone** to ground questions in your actual experience (no hallucinations).
* **🗣️ Voice Interaction:** Real-time Speech-to-Text (Whisper) and Text-to-Speech (gTTS) for a natural conversation flow.
* **🐳 Dockerized:** Fully containerized application for easy deployment and reproducibility.
* **⚡ Fast Inference:** Powered by **Groq API** running Llama-3-70b for sub-second latency.

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **LLM Engine:** Llama-3 (via Groq)
* **Vector DB:** Pinecone (Serverless)
* **Orchestration:** LangChain
* **DevOps:** Docker
* **Audio:** OpenAI Whisper & gTTS

## 📦 How to Run (Docker)

This project is fully dockerized. You can run it locally with a single command.

### Prerequisites
* Docker Desktop installed
* `.env` file with API keys (`GROQ_API_KEY`, `PINECONE_API_KEY`)

### Quick Start

1. **Build the Image:**
   ```bash
   docker build -t zara-ai .

2. **Run the Container:**
    ```bash
    docker run -p 8501:8501 --env-file .env zara-ai
3. **Open Browser: Go to http://localhost:8501 and start your interview!**

Developed by Merve Caliskan
