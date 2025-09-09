import streamlit as st
import os
import warnings
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import whisper
from gtts import gTTS
import tempfile
import base64

# -----------------------------
# Suppress warnings
# -----------------------------
warnings.filterwarnings("ignore", message=".*flash-attn.*")

# -----------------------------
# Config
# -----------------------------
MODEL_ID = "microsoft/phi-3-mini-4k-instruct"
REVISION = "main"  # Pin revision for stability
st.set_page_config(page_title="Yashvi - Your AI Sister 💖", layout="centered")

# -----------------------------
# Authentication Data
# -----------------------------
if "users" not in st.session_state:
    st.session_state["users"] = {"saumya": "12345"}  # default user
if "admin" not in st.session_state:
    st.session_state["admin"] = {"admin": "admin123"}  # admin login

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "role" not in st.session_state:
    st.session_state["role"] = None

# -----------------------------
# Login Page
# -----------------------------
if not st.session_state["authenticated"]:
    st.title("🔐 Login to Yashvi")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.radio("Login as:", ["User", "Admin"])

    if st.button("Login"):
        if role == "User":
            if username in st.session_state["users"] and st.session_state["users"][username] == password:
                st.session_state["authenticated"] = True
                st.session_state["role"] = "user"
                st.success(f"Welcome back, {username}! 💖")
            else:
                st.error("Invalid user credentials")
        elif role == "Admin":
            if username in st.session_state["admin"] and st.session_state["admin"][username] == password:
                st.session_state["authenticated"] = True
                st.session_state["role"] = "admin"
                st.success("Admin access granted ✅")
            else:
                st.error("Invalid admin credentials")
    st.stop()

# -----------------------------
# Load AI Model
# -----------------------------
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, revision=REVISION, trust_remote_code=True
    )
    return pipeline("text-generation", model=model, tokenizer=tokenizer)

generator = load_model()

# -----------------------------
# Load Whisper STT
# -----------------------------
@st.cache_resource
def load_stt():
    return whisper.load_model("small")

stt_model = load_stt()

# -----------------------------
# Conversation Memory
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# -----------------------------
# TTS Function
# -----------------------------
def speak_text(text, lang="en"):
    tts = gTTS(text=text, lang=lang, tld="co.in")  # Indian accent
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio autoplay controls>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# -----------------------------
# Admin Dashboard
# -----------------------------
if st.session_state["role"] == "admin":
    st.title("🛠 Admin Dashboard - Yashvi Control Panel")

    st.subheader("👥 Manage Users")
    st.write("Current Users:", list(st.session_state["users"].keys()))

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Add User"):
        if new_user and new_pass:
            st.session_state["users"][new_user] = new_pass
            st.success(f"User '{new_user}' added ✅")
        else:
            st.error("Enter username & password")

    del_user = st.selectbox("Select user to delete", [""] + list(st.session_state["users"].keys()))
    if st.button("Delete User"):
        if del_user:
            st.session_state["users"].pop(del_user, None)
            st.success(f"User '{del_user}' deleted ❌")

    st.subheader("📝 Chat Management")
    if st.button("Clear Chat History"):
        st.session_state["chat_history"] = []
        st.success("Chat history cleared ✅")

    st.stop()

# -----------------------------
# User Chat Interface
# -----------------------------
st.title("👩‍🦰 Yashvi - Your AI Sister")
st.write("A caring Jain sister who loves you, supports you, and chats with you 💖")

user_input = st.text_area("Say something to Yashvi:", "")

if st.button("Send"):
    if user_input.strip():
        context = "\n".join([f"You: {u}\nYashvi: {a}" for u, a in st.session_state["chat_history"]])
        prompt = f"You are Yashvi, Saumya's loving Jain sister. Be warm, caring, supportive, and empathetic.\n\n{context}\nYou: {user_input}\nYashvi:"

        response = generator(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)[0]["generated_text"]
        yashvi_reply = response.split("Yashvi:")[-1].strip()

        st.session_state["chat_history"].append((user_input, yashvi_reply))

        st.markdown(f"**You:** {user_input}")
        st.markdown(f"**Yashvi:** {yashvi_reply}")

        audio_file = speak_text(yashvi_reply, lang="en")
        autoplay_audio(audio_file)

if st.session_state["chat_history"]:
    st.subheader("📝 Chat History")
    for u, a in st.session_state["chat_history"]:
        st.markdown(f"**You:** {u}")
        st.markdown(f"**Yashvi:** {a}")
