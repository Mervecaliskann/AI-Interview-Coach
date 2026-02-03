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
load_dotenv() 

# API Keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
index_name = "ai-coach"

# Pinecone Başlat
pc = Pinecone(api_key=PINECONE_API_KEY)

# Streamlit Sayfa Ayarları
st.set_page_config(page_title="AI Technical Recruiter", page_icon="👩‍💼", layout="wide")

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
        /* Reveal Hint kutusunu tamamen yok etmek için */
        .stExpander { display: none !important; } 
    </style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---

def get_response_from_llm(chat_history, resume_text):
    system_prompt = f"""
    You are a Professional Technical Interviewer. 
    
    YOUR GOAL: 
    Conduct a realistic technical interview based on the context.
    
    CONTENT STRATEGY (MIX THESE TOPICS):
    1. **Resume Projects:** Ask about architecture/decisions (Max 1 question per project).
    2. **General Engineering:** Ask standard questions like "What is the difference between List and Tuple?", "Explain Docker vs VM", "Explain CAP Theorem".
    3. **Scenario/Debugging:** Give a short scenario: "If your API returns 500 Error, how do you debug it?"
    
    OUTPUT RULES (STRICT):
    1. **English Check:**
       - If user made a grammar mistake: Start with "TIP: [Correction] |||".
       - If NO mistake or Start of interview: Start with "|||". (Just the separator).
    2. **Question:**
       - After "|||", ask your technical question directly.
    
    EXAMPLE (With Mistake):
    TIP: Say 'I went' not 'I goed'. ||| What is the difference between TCP and UDP?
    
    EXAMPLE (No Mistake):
    ||| Let's talk about Python. How does garbage collection work?
    
    INTERVIEW CONTEXT:
    {resume_text}
    """
    messages = [{"role": "system", "content": system_prompt}] + chat_history
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7, # Biraz çeşitlilik için artırdık
            max_tokens=250,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"||| Error: {e}"

def text_to_speech(text):
    try:
        # Sadece metin varsa ses oluştur
        if text and len(text) > 1:
            tts = gTTS(text=text, lang='en')
            filename = f"response_{len(st.session_state.chat_history)}.mp3" # Benzersiz isim
            tts.save(filename)
            return filename
    except:
        return None
    return None

def upload_to_pinecone(uploaded_file):
    file_name = uploaded_file.name
    namespace_name = "".join([c if c.isalnum() else "_" for c in file_name])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    loader = PyPDFLoader(tmp_path)
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(pages)

    embeddings = PineconeEmbeddings(
        model="multilingual-e5-large",
        pinecone_api_key=PINECONE_API_KEY
    )

    try:
        index = pc.Index(index_name)
        index.delete(delete_all=True, namespace=namespace_name)
    except:
        pass 

    PineconeVectorStore.from_documents(
        documents=chunks,
        index_name=index_name,
        embedding=embeddings,
        namespace=namespace_name
    )
    
    os.remove(tmp_path)
    return "".join([doc.page_content for doc in chunks])

# --- UI & LOGIC ---

# Session State
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "resume_text" not in st.session_state: st.session_state.resume_text = ""

# Sidebar
with st.sidebar:
    st.header("⚙️ Setup")
    uploaded_file = st.file_uploader("Upload CV (PDF)", type="pdf")
    if st.button("Reset Interview"):
        st.session_state.clear()
        st.rerun()

# Avatar Mantığı
avatar_placeholder = st.empty()
def render_avatar(state):
    img = AVATAR_TALKING if state == "talking" else AVATAR_IDLE
    avatar_placeholder.markdown(f'<div class="avatar-container"><img src="{img}" class="avatar-img"></div>', unsafe_allow_html=True)

render_avatar("idle")

# --- BAŞLANGIÇ MANTIĞI (CV Yüklenince) ---
if uploaded_file and not st.session_state.resume_text:
    with st.spinner("AI Technical Recruiter is reading your resume..."):
        st.session_state.resume_text = upload_to_pinecone(uploaded_file)
        
        # İlk Soru İçin LLM Çağrısı
        full_res = get_response_from_llm([], st.session_state.resume_text)
        
        # AYRIŞTIRMA (Önemli Kısım!)
        question_part = full_res
        if "|||" in full_res:
            parts = full_res.split("|||")
            question_part = parts[1].strip() # Sağ taraf sorudur
        
        # Geçmişe Ekle
        st.session_state.chat_history.append({"role": "assistant", "content": question_part})
        
        # Avatar Konuşsun
        render_avatar("talking")
        
        # Sesi Çal
        audio = text_to_speech(question_part)
        if audio: 
            st.audio(audio, format="audio/mp3", autoplay=True)

# Geçmiş Mesajları Ekrana Bas
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]): 
        st.write(msg["content"])

# Reveal Hint KUTUSU ARTIK YOK (Silindi) ❌

# --- SESLİ SOHBET DÖNGÜSÜ ---
if audio_val := st.audio_input("🎤 Record Your Answer"):
    # 1. Kullanıcı Mesajı
    st.session_state.chat_history.append({"role": "user", "content": "🎤 (Voice Input)"}) 
    
    with st.spinner("Listening..."):
        try:
            trans = client.audio.transcriptions.create(
                file=("in.wav", audio_val, "audio/wav"), 
                model="whisper-large-v3", 
                response_format="text", 
                language="en"
            )
        except:
            trans = "Error in transcription."
        
        # Transkripti güncelle
        st.session_state.chat_history[-1]["content"] = trans

    with st.spinner("Thinking..."):
        # 2. LLM Cevabı
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
        full_res = get_response_from_llm(history, st.session_state.resume_text)
        
        # --- AYRIŞTIRMA (SPLIT) ---
        feedback = None
        question = full_res

        if "|||" in full_res:
            parts = full_res.split("|||")
            # Sol Taraf (Düzeltme) -> Varsa Al
            if len(parts[0].strip()) > 0:
                feedback = parts[0].strip()
            # Sağ Taraf (Soru) -> Her zaman Al
            question = parts[1].strip()

        # --- EKRANA BASMA ---
        with st.chat_message("assistant"):
            render_avatar("talking")
            
            # Hata varsa Kırmızı Uyarı (Kutu yok, sadece uyarı)
            if feedback:
                st.error(f"🇬🇧 {feedback}")
            
            # Soruyu Direkt Yaz
            st.write(question)

        # Geçmişe Kaydet
        st.session_state.chat_history.append({"role": "assistant", "content": question})
        
        # --- SES OYNATMA ---
        if question:
            audio = text_to_speech(question)
            if audio: 
                # 'key' parametresini sildik!
                st.audio(audio, format="audio/mp3", autoplay=True)

    # İş bitince avatar sussun
    render_avatar("idle")