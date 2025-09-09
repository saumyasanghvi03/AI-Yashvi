import streamlit as st
import os
import json
import warnings
import tempfile
import base64
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import whisper
from gtts import gTTS
import speech_recognition as sr

# ======================
# CONFIG & WARNINGS
# ======================
warnings.filterwarnings("ignore", message=".*flash-attn.*")
MODEL_ID = "microsoft/phi-3-mini-4k-instruct"
REVISION = "main"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
MEMORY_FILE = "memory.json"

# ======================
# MEMORY FUNCTIONS
# ======================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"chat": []}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# ======================
# LOAD MODEL
# ======================
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=REVISION,
        trust_remote_code=True,
        attn_implementation="eager"
    )
    return tokenizer, model

tokenizer, model = load_model()

# ======================
# LOAD WHISPER STT
# ======================
@st.cache_resource
def load_stt():
    return whisper.load_model("small")

stt_model = load_stt()

# ======================
# CHAT FUNCTION
# ======================
def generate_response(prompt, memory):
    context = "\n".join([f"{x['role']}: {x['content']}" for x in memory["chat"][-5:]])
    input_text = f"{context}\nUser: {prompt}\nYashvi:"
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("Yashvi:")[-1].strip()

# ======================
# TTS FUNCTION
# ======================
def speak_text(text, lang="en"):
    tts = gTTS(text=text, lang=lang, tld="co.in")
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

# ======================
# STREAMLIT UI
# ======================
st.set_page_config(page_title="AI Sister Yashvi 💖", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Yashvi’s World")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.success("Welcome back, Saumya bhai! 💖")
        else:
            st.error("Invalid credentials")
    st.stop()

st.title("🌸 Your AI Sister Yashvi 🌸")
st.write("Jai Jinendra 🙏 I'm Yashvi, your Jain sister. I’m here to listen, care, and talk with you 💖")

memory = load_memory()

# ======================
# Multilingual Input
# ======================
lang = st.selectbox("Choose Language:", ["English", "Hindi", "Gujarati"])
lang_code = {"English":"en", "Hindi":"hi", "Gujarati":"gu"}[lang]

# Text Input
user_input = st.text_area("📝 Type your message here:")
if st.button("Send Text"):
    if user_input.strip():
        memory["chat"].append({"role": "User", "content": user_input})
        response = generate_response(user_input, memory)
        memory["chat"].append({"role": "Yashvi", "content": response})
        save_memory(memory)
        st.write(f"**Yashvi:** {response}")
        audio_file = speak_text(response, lang=lang_code)
        autoplay_audio(audio_file)

# Optional Voice Input
st.subheader("🎤 Or Record Voice (Hindi / Gujarati / English)")
if st.button("Record & Send Voice"):
    st.warning("Currently, record feature requires local microphone support in Streamlit (best on local PC).")
    st.info("You can upload a voice file for processing.")
    audio_file_upload = st.file_uploader("Upload your voice message (.mp3/.wav)", type=["mp3","wav"])
    if audio_file_upload:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file_upload) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language=lang_code)
            st.success(f"You said: {text}")
            memory["chat"].append({"role": "User", "content": text})
            response = generate_response(text, memory)
            memory["chat"].append({"role": "Yashvi", "content": response})
            save_memory(memory)
            st.write(f"**Yashvi:** {response}")
            audio_file = speak_text(response, lang=lang_code)
            autoplay_audio(audio_file)
        except:
            st.error("Could not understand audio.")

# Show chat history
if st.checkbox("📜 Show chat history"):
    for msg in memory["chat"]:
        st.write(f"**{msg['role']}:** {msg['content']}")
