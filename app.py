import os
import streamlit as st
import tempfile
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from groq import Groq
from gtts import gTTS
from langchain_community.document_loaders import PyPDFLoader

# --- CONFIGURATION & ENV ---
load_dotenv() # .env dosyasını oku

# API Keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
index_name = "ai-coach"

# Pinecone Başlat
pc = Pinecone(api_key=PINECONE_API_KEY)

# Streamlit Sayfa Ayarları
st.set_page_config(page_title="Zara: AI Interviewer", page_icon="👩‍💼", layout="wide")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY bulunamadı! .env dosyanı kontrol et.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# --- AVATAR & CSS ---
AVATAR_IDLE = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDd5Y3h6a2txY3Z4bnZtY3Z4bnZtY3Z4bnZtY3Z4bnZtY3Z4bnZtJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l3V0yA9zHe5m29sxW/giphy.gif"
AVATAR_TALKING = "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnZ5Y3h6a2txY3Z4bnZtY3Z4bnZtY3Z4bnZtY3Z4bnZtY3Z4bnZtJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKs69j4h9vK6qTm/giphy.gif"

st.markdown("""
    <style>
        .avatar-container { display: flex; justify-content: center; align-items: center; margin-bottom: 20px; }
        .avatar-img { width: 250px; height: 250px; border-radius: 50%; object-fit: cover; border: 4px solid #4F46E5; box-shadow: 0 0 20px rgba(79, 70, 229, 0.5); animation: pulse 2s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(79, 70, 229, 0); } 100% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); } }
    </style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---

def get_response_from_llm(chat_history, resume_text):
    system_prompt = f"""
    You are Zara, a professional AI Technical Recruiter.
    INTERVIEW STYLE: Professional, encouraging, but rigorous. Ask ONE question at a time.
    RESUME CONTEXT: {resume_text}
    """
    messages = [{"role": "system", "content": system_prompt}] + chat_history
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            max_tokens=250,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e} ||| No hint."

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        filename = "response.mp3"
        tts.save(filename)
        return filename
    except:
        return None

def upload_to_pinecone(uploaded_file):
    # Dosya isminden temiz bir Namespace (klasör adı) oluştur
    file_name = uploaded_file.name
    namespace_name = "".join([c if c.isalnum() else "_" for c in file_name])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    loader = PyPDFLoader(tmp_path)
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(pages)

    # Embedding modelini tanımla
    embeddings = PineconeEmbeddings(
        model="multilingual-e5-large",
        pinecone_api_key=PINECONE_API_KEY
    )

    # 🌟 AKILLI TEMİZLİK: Eski veriyi sil, yenisini yükle (Maliyet tasarrufu)
    try:
        index = pc.Index(index_name)
        index.delete(delete_all=True, namespace=namespace_name)
    except:
        pass 

    # Pinecone'a Yükle
    vectorstore = PineconeVectorStore.from_documents(
        documents=chunks,
        index_name=index_name,
        embedding=embeddings,
        namespace=namespace_name # Veriyi özel klasöre koy
    )
    
    os.remove(tmp_path)
    return "".join([doc.page_content for doc in chunks])

# --- UI & LOGIC ---

# Session State
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "resume_text" not in st.session_state: st.session_state.resume_text = ""
if "current_hint" not in st.session_state: st.session_state.current_hint = "Upload CV to start!"

# Sidebar
with st.sidebar:
    st.header("⚙️ Setup")
    uploaded_file = st.file_uploader("Upload CV (PDF)", type="pdf")
    if st.button("Reset Interview"):
        st.session_state.clear()
        st.rerun()

# Avatar
avatar_placeholder = st.empty()
def render_avatar(state):
    img = AVATAR_TALKING if state == "talking" else AVATAR_IDLE
    avatar_placeholder.markdown(f'<div class="avatar-container"><img src="{img}" class="avatar-img"></div>', unsafe_allow_html=True)

render_avatar("idle")

# Main Logic
if uploaded_file and not st.session_state.resume_text:
    with st.spinner("Zara is reading your resume and indexing to Pinecone..."):
        st.session_state.resume_text = upload_to_pinecone(uploaded_file)
        full_res = get_response_from_llm([], st.session_state.resume_text)
        q_part, h_part = full_res.split("|||") if "|||" in full_res else (full_res, "Intro")
        st.session_state.chat_history.append({"role": "assistant", "content": q_part.strip()})
        st.session_state.current_hint = h_part.strip()
        render_avatar("talking")
        audio = text_to_speech(q_part.strip())
        if audio: st.audio(audio, format="audio/mp3", autoplay=True)

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]): st.write(msg["content"])

with st.expander("💡 Reveal Hint"): st.info(st.session_state.current_hint)

if audio_val := st.audio_input("🎤 Record Your Answer"):
    render_avatar("idle")
    with st.spinner("Listening..."):
        trans = client.audio.transcriptions.create(file=("in.wav", audio_val, "audio/wav"), model="whisper-large-v3", response_format="text", language="en")
    st.session_state.chat_history.append({"role": "user", "content": trans})
    
    with st.spinner("Zara is thinking..."):
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
        full_res = get_response_from_llm(history, st.session_state.resume_text)
        q_part, h_part = full_res.split("|||") if "|||" in full_res else (full_res, "No hint")
        st.session_state.chat_history.append({"role": "assistant", "content": q_part.strip()})
        st.session_state.current_hint = h_part.strip()
        render_avatar("talking")
        audio = text_to_speech(q_part.strip())
        if audio: st.audio(audio, format="audio/mp3", autoplay=True)