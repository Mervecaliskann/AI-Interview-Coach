# 👩‍💼 AI Technical Interview Coach

**AI Interview Coach** is an interactive, voice-based interview simulator designed to prepare candidates for technical roles. Unlike standard chatbots, it acts as a **professional recruiter**, balancing resume-specific questions with general engineering concepts.

Built with **Llama-3**, **Pinecone**, and **Streamlit**.

## 🚀 Key Features

* **📄 Hybrid Interview Engine:**
    * **Resume Analysis (RAG):** Upload your PDF, and the AI asks specific questions about your past projects using Vector Search.
    * **General Knowledge:** Randomly tests you on core concepts (e.g., "Monolith vs Microservices", "Python Memory Management").
    * **Scenario & Debugging:** Poses real-world problem-solving scenarios.
* **🇬🇧 Real-time English Coaching:** Detects grammar mistakes in your speech and provides instant correction tips (e.g., *"Tip: Say 'I went' instead of 'I goed'"*) before asking the next question.
* **🗣️ Full Voice Interaction:**
    * **Speech-to-Text:** Speaks with you using OpenAI's Whisper model.
    * **Text-to-Speech:** Responds with a natural voice using gTTS.
* **⚡ High Performance:** Powered by **Groq API** (Llama-3.3-70b) for sub-second latency.

## 🛠️ Tech Stack

* **Frontend:** Streamlit (Custom CSS & Avatar Animations)
* **LLM Engine:** Llama-3.3-70b-versatile (via Groq)
* **Vector DB:** Pinecone (Serverless / Semantic Search)
* **Orchestration:** LangChain
* **Audio Processing:** OpenAI Whisper (STT) & gTTS (TTS)
* **Deployment:** Docker

## 📦 How to Run

### Option 1: Using Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/ai-interview-coach.git](https://github.com/YOUR_USERNAME/ai-interview-coach.git)
    cd ai-interview-coach
    ```

2.  **Create a `.env` file** with your API keys:
    ```env
    GROQ_API_KEY=your_groq_api_key
    PINECONE_API_KEY=your_pinecone_api_key
    ```

3.  **Build and Run:**
    ```bash
    docker build -t ai-coach .
    docker run -p 8501:8501 --env-file .env ai-coach
    ```

### Option 2: Local Python Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

## 📸 Usage

1.  Open `http://localhost:8501`.
2.  Upload your CV (PDF format).
3.  The AI will analyze your profile and start the interview verbally.
4.  Reply using the microphone button!

---
**Developed by Merve Caliskan**
