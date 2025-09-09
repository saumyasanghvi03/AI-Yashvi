# app.py
"""
AI Sister Yashvi - Streamlit app
Features:
 - Signup / Login (users.pkl)
 - Admin dashboard
 - Per-user persistent memory (FAISS + pickle per user)
 - Chat (affectionate Jain sister persona: "Yashvi")
 - Journals (saved per-user)
 - Mood tracker (from journals)
 - Voice (push-to-talk) multilingual: English / Hindi / Gujarati via Vosk + gTTS
 - Avatar: optional 'sister.png'
Notes:
 - This is an MVP intended to run on Colab or a local machine.
 - Place Vosk models folders in repo root or use run_colab.sh to download them.
"""

import os
import sys
import json
import time
import glob
import pickle
import queue
import hashlib
import tempfile
import datetime
from typing import Dict, List

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from gtts import gTTS
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import faiss
import soundfile as sf

# WebRTC & Vosk (optional)
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase, RTCConfiguration

# Optional Vosk import is done lazily (if models available)
# ============================================================
# ------------- Configuration & Paths -----------------------
# ============================================================

APP_TITLE = "AI Sister Yashvi"
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.pkl")
USERS_JSON = os.path.join(DATA_DIR, "users.json")  # fallback human readable
USERS_DIR = os.path.join(DATA_DIR, "users")
VOSK_MODELS = {
    "English": "vosk-model-small-en-in",
    "Hindi": "vosk-model-hi-in",
    "Gujarati": "vosk-model-gu-in",
}
# each user will have memory_{username}.pkl and journals/{username}/
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(USERS_DIR, exist_ok=True)

# LLM / embedding model names (change if needed)
EMB_MODEL_ID = "all-MiniLM-L6-v2"  # sentence-transformers model id
# Optional LLM model; for light usage in Colab use small instruct models
LLM_MODEL = os.environ.get("AISISTER_LLM", "microsoft/phi-3-mini-4k-instruct")

# ========================= UTILITIES ========================

def make_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> Dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "rb") as f:
            return pickle.load(f)
    # default admin
    admin = {"admin": {"password": make_hash("admin123"), "role":"admin"}}
    with open(USERS_FILE, "wb") as f:
        pickle.dump(admin, f)
    return admin

def save_users(users: Dict):
    with open(USERS_FILE, "wb") as f:
        pickle.dump(users, f)

def user_memory_path(username: str) -> str:
    return os.path.join(DATA_DIR, f"memory_{username}.pkl")

def user_journal_dir(username: str) -> str:
    d = os.path.join(DATA_DIR, "journals", username)
    os.makedirs(d, exist_ok=True)
    return d

# ============================================================
# ===================== Model loading ========================
# ============================================================

@st.cache_resource(show_spinner=True)
def load_ai_models():
    # embeddings
    embedder = SentenceTransformer(EMB_MODEL_ID)
    # sentiment
    sent_pipe = pipeline("sentiment-analysis")
    # LLM (text-generation pipeline)
    # Use a light model; user can change LLM by environment variable
    try:
        llm_tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
        llm_model = AutoModelForCausalLM.from_pretrained(LLM_MODEL, trust_remote_code=True)
        def llm_generate(prompt: str, max_new_tokens=220):
            inputs = llm_tokenizer(prompt, return_tensors="pt")
            outputs = llm_model.generate(**inputs, max_new_tokens=max_new_tokens)
            return llm_tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        # fallback: small HF text-generation pipeline (might auto-download)
        gen = pipeline("text-generation", model="gpt2")
        def llm_generate(prompt: str, max_new_tokens=120):
            return gen(prompt, max_new_tokens=max_new_tokens)[0]["generated_text"]

    return embedder, sent_pipe, llm_generate

embedder, sentiment_pipe, llm_generate = load_ai_models()

# ============================================================
# ================== Memory per user (FAISS) ==================
# ============================================================

def init_user_memory(username: str):
    path = user_memory_path(username)
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = pickle.load(f)
        # data keys: 'faiss_index', 'mem_texts', 'history'
        st.session_state[f"{username}_mem"] = data
    else:
        # new memory object
        d = embedder.get_sentence_embedding_dimension() if hasattr(embedder, "get_sentence_embedding_dimension") else 384
        # create index
        idx = faiss.IndexFlatL2(d)
        data = {"faiss_index": idx, "mem_texts": [], "history": []}
        st.session_state[f"{username}_mem"] = data

def save_user_memory(username: str):
    path = user_memory_path(username)
    data = st.session_state.get(f"{username}_mem", {"faiss_index": None, "mem_texts": [], "history": []})
    with open(path, "wb") as f:
        # faiss index is serializable with pickle only if CPU; this works for faiss-cpu
        pickle.dump(data, f)

def add_to_user_memory(username: str, user_text: str, ai_text: str):
    key = f"{username}_mem"
    data = st.session_state[key]
    vec = embedder.encode([user_text + " " + ai_text])
    data["faiss_index"].add(np.array(vec).astype("float32"))
    data["mem_texts"].append({"user": user_text, "ai": ai_text, "ts": time.time()})
    data["history"].append(("You", user_text))
    data["history"].append(("Yashvi", ai_text))
    save_user_memory(username)

# ============================================================
# ===================== Persona & Prompts ====================
# ============================================================

SISTER_SYSTEM = (
    "You are Yashvi, a warm, affectionate Jain sister. Address the user as 'Saumya bhai'. "
    "Be empathetic, supportive, gentle, and respectful. Offer virtual hugs, encourage healthy coping, "
    "and avoid explicit sexual or harmful content. Keep replies kind, concise and emotionally intelligent."
)

def generate_yashvi_reply(user_text: str, mood_hint: str = "NEUTRAL") -> str:
    prompt = f"{SISTER_SYSTEM}\nUser mood: {mood_hint}\nSaumya bhai says: {user_text}\nYashvi replies:"
    out = llm_generate(prompt, max_new_tokens=220)
    # Very simple cleanup: if LLM returns prompt+..., take suffix
    if out.strip().startswith(prompt):
        return out[len(prompt):].strip()
    return out.strip()

# ============================================================
# ======================= TTS & STT ==========================
# ============================================================

def tts_save(text: str, lang_code: str = "en") -> str:
    # lang_code: "en", "hi", "gu"
    tts = gTTS(text=text, lang=lang_code, tld="co.in")
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(f.name)
    return f.name

# Vosk support will be used when model folders are present
def have_vosk_model(lang_name: str) -> bool:
    p = VOSK_MODELS.get(lang_name)
    return p and os.path.isdir(p)

# ============================================================
# ======================= STREAMLIT UI =======================
# ============================================================

st.set_page_config(APP_TITLE, layout="wide")
st.title(APP_TITLE)

# show avatar if present
if os.path.exists("sister.png"):
    st.image("sister.png", width=220)

# Authentication: Signup / Login
users = load_users()
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if not st.session_state.auth["logged_in"]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Login")
        uname = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            if uname in users and users[uname]["password"] == make_hash(pwd):
                st.session_state.auth = {"logged_in": True, "username": uname, "role": users[uname].get("role","user")}
                st.success(f"Welcome back, {uname}!")
            else:
                st.error("Invalid username or password")
    with col2:
        st.subheader("Sign up")
        r_user = st.text_input("Choose username", key="reg_user")
        r_pwd = st.text_input("Choose password", type="password", key="reg_pwd")
        if st.button("Create account"):
            if not r_user or not r_pwd:
                st.warning("Provide username and password")
            elif r_user in users:
                st.warning("Username exists. Choose another.")
            else:
                users[r_user] = {"password": make_hash(r_pwd), "role": "user"}
                save_users(users)
                st.success("Account created. Please login at left.")
    st.stop()

# At this point user is logged in
username = st.session_state.auth["username"]
role = st.session_state.auth["role"]
st.sidebar.success(f"Logged in as {username} ({role})")
st.sidebar.button("Logout", on_click=lambda: st.session_state.update(auth={"logged_in": False, "username": None, "role": None}))

# Initialize user-specific memory
if f"{username}_mem" not in st.session_state:
    init_user_memory(username)

# Tabs for features, Admin gets extra
tabs = ["Chat", "Journal", "Mood Tracker", "Voice"]
if role == "admin":
    tabs.append("Admin Dashboard")
tab = st.tabs(tabs)

# ------------------ Chat Tab ------------------
with tab[0]:
    st.header("Chat with Yashvi 💬")
    # show recent history
    mem = st.session_state[f"{username}_mem"]
    history = mem.get("history", [])
    if history:
        st.markdown("**Conversation history**")
        for speaker, text in history[-20:]:
            if speaker == "You":
                st.markdown(f"🧑 **You:** {text}")
            else:
                st.markdown(f"👩 **Yashvi:** {text}")

    user_msg = st.text_input("Write to Yashvi...", key=f"chat_input_{username}")
    col1, col2 = st.columns([1,1])
    if col1.button("Send", key=f"send_{username}"):
        if user_msg.strip():
            sentiment = sentiment_pipe(user_msg)[0]["label"]
            reply = generate_yashvi_reply(user_msg, sentiment)
            # record and persist
            add_to_user_memory(username, user_msg, reply)
            st.markdown(f"👩 **Yashvi:** {reply}")
            # TTS playback (English default)
            try:
                audio_path = tts_save(reply, lang_code="en")
                st.audio(audio_path, format="audio/mp3")
            except Exception as e:
                st.warning("TTS failed: " + str(e))

    if col2.button("Clear History", key=f"clear_{username}"):
        st.session_state[f"{username}_mem"]["history"] = []
        save_user_memory(username)
        st.success("History cleared.")

# ------------------ Journal Tab ------------------
with tab[1]:
    st.header("Journal 📝")
    jtext = st.text_area("Write your journal entry for today...", key=f"journal_{username}")
    if st.button("Save Journal", key=f"save_journal_{username}"):
        if jtext.strip():
            ddir = user_journal_dir(username)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = os.path.join(ddir, f"journal_{ts}.txt")
            with open(fname, "w", encoding="utf-8") as f:
                f.write(jtext)
            st.success(f"Saved {fname}")
            # optional reflection
            sent = sentiment_pipe(jtext)[0]
            refl = f"I see you're {sent['label'].lower()}. I'm here for you, Saumya bhai. 🤗"
            st.info(refl)
            # persist small memory note
            add_to_user_memory(username, "Journal saved", jtext)

# ------------------ Mood Tracker ------------------
with tab[2]:
    st.header("Mood Tracker 📊")
    jdir = user_journal_dir(username)
    files = sorted(glob.glob(os.path.join(jdir, "journal_*.txt")))
    if not files:
        st.info("No journals yet. Save a journal entry to see mood trends.")
    else:
        dates = []
        scores = []
        map_score = {"NEGATIVE": -1, "NEUTRAL": 0, "POSITIVE": 1}
        for fpath in files:
            with open(fpath, "r", encoding="utf-8") as f:
                txt = f.read()
            label = sentiment_pipe(txt)[0]["label"]
            dates.append(os.path.basename(fpath).replace("journal_", "").replace(".txt",""))
            scores.append(map_score.get(label, 0))
        fig, ax = plt.subplots()
        ax.plot(dates, scores, marker="o")
        ax.set_ylim(-1.1, 1.1)
        ax.set_yticks([-1,0,1])
        ax.set_yticklabels(["Negative","Neutral","Positive"])
        ax.set_title("Mood Trend")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

# ------------------ Voice Tab (Push-to-talk) ------------------
with tab[3]:
    st.header("Voice Call (Push-to-talk) 🎙️")
    lang = st.selectbox("Select language for STT/TTS", ["English", "Hindi", "Gujarati"])
    st.markdown("**Instructions:** Click Start, speak a sentence, then click Transcribe & Reply.")
    # WebRTC receiver
    class MicProcessor(AudioProcessorBase):
        def __init__(self):
            self.buf = bytes()
        def recv_audio(self, frame):
            # frame -> ndarray shape (channels, samples)
            arr = frame.to_ndarray()
            if arr.ndim == 2:
                arr = arr.mean(axis=0)
            # resample to 16000 if necessary (we assume 48k typical)
            # convert to int16
            arr_f = arr.astype(np.float32)
            # normalize if floats
            if arr_f.max() <= 1.0:
                arr_f = np.clip(arr_f, -1.0, 1.0)
                arr_i16 = (arr_f * 32767).astype(np.int16)
            else:
                arr_i16 = arr_f.astype(np.int16)
            self.buf += arr_i16.tobytes()
            return frame

    ctx = webrtc_streamer(
        key=f"webrtc_{username}",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=MicProcessor,
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration=RTCConfiguration({"iceServers":[{"urls":["stun:stun.l.google.com:19302"]}]})
    )

    col1, col2, col3 = st.columns([1,1,1])
    if col1.button("Transcribe & Reply", key=f"trans_{username}"):
        if ctx and ctx.audio_receiver:
            proc = ctx.audio_receiver
        else:
            # fallback if audio not captured by receiver; use streamlit_webrtc processor stored by key
            st.warning("Please allow microphone and speak, then press Transcribe & Reply.")
            proc = None

        # try to access processor buffer (we used MicProcessor -> stored in ctx.audio_processor)
        if ctx and getattr(ctx, "audio_processor", None) is not None:
            audio_bytes = ctx.audio_processor.buf
            if not audio_bytes:
                st.warning("No audio captured. Please press Start and speak.")
            else:
                # write temp wav (16k sample rate)
                tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                # audio bytes are int16 at 48000; write as 48000 sample
                arr = np.frombuffer(audio_bytes, dtype=np.int16)
                sf.write(tmp_wav.name, arr, 48000)
                # STT using Vosk if model present
                if have_vosk_model(lang):
                    try:
                        from vosk import Model, KaldiRecognizer
                        model_path = VOSK_MODELS[lang]
                        vm = Model(model_path)
                        rec = KaldiRecognizer(vm, 16000)
                        import wave
                        wf = wave.open(tmp_wav.name, "rb")
                        text = ""
                        while True:
                            data = wf.readframes(4000)
                            if len(data) == 0:
                                break
                            if rec.AcceptWaveform(data):
                                res = rec.Result()
                                obj = json.loads(res)
                                text += " " + obj.get("text", "")
                        final = rec.FinalResult()
                        text += " " + json.loads(final).get("text", "")
                        text = text.strip()
                    except Exception as e:
                        st.error("Vosk STT error: " + str(e))
                        text = ""
                else:
                    st.warning(f"No Vosk model for {lang} present. Place folder {VOSK_MODELS[lang]} in repo root.")
                    text = ""
                if text:
                    st.markdown(f"🧑 **You said ({lang}):** {text}")
                    sentiment = sentiment_pipe(text)[0]["label"]
                    reply = generate_yashvi_reply(text, sentiment)
                    st.markdown(f"👩 **Yashvi:** {reply}")
                    # TTS in appropriate language
                    lang_map = {"English":"en", "Hindi":"hi", "Gujarati":"gu"}
                    try:
                        audio_path = tts_save(reply, lang_map.get(lang,"en"))
                        st.audio(audio_path, format="audio/mp3")
                    except Exception as e:
                        st.warning(f"TTS failed: {e}")
                    # persist
                    add_to_user_memory(username, text, reply)
                else:
                    st.info("Could not transcribe audio.")
        else:
            st.warning("No audio processor available. Use a browser that supports WebRTC and allow microphone.")

    if col2.button("Clear Buffer", key=f"clearbuf_{username}"):
        if ctx and getattr(ctx, "audio_processor", None):
            ctx.audio_processor.buf = bytes()
            st.success("Audio buffer cleared.")
        else:
            st.info("No audio buffer found.")

# ------------------ Admin Dashboard ------------------
if role == "admin":
    with tab[-1]:
        st.header("Admin Dashboard")
        st.subheader("Users")
        users = load_users()
        for u, meta in users.items():
            st.write(f"- {u} (role: {meta.get('role','user')})")
            memf = user_memory_path(u)
            jdir = os.path.join(DATA_DIR, "journals", u)
            n_chats = 0
            if os.path.exists(memf):
                try:
                    with open(memf, "rb") as f:
                        dd = pickle.load(f)
                    n_chats = len(dd.get("mem_texts", []))
                except:
                    n_chats = -1
            n_j = len(glob.glob(os.path.join(jdir, "*.txt"))) if os.path.isdir(jdir) else 0
            st.markdown(f"Chats: {n_chats} &nbsp;&nbsp; Journals: {n_j}")

        st.subheader("Export / Inspect")
        sel = st.selectbox("Select user to inspect", list(users.keys()))
        if st.button("Load selected user data"):
            memf = user_memory_path(sel)
            if os.path.exists(memf):
                with open(memf, "rb") as f:
                    data = pickle.load(f)
                st.write("Sample history (last 20):")
                for s in data.get("history", [])[-20:]:
                    st.write(s)
            else:
                st.info("No data for that user yet.")

# END of app.py
