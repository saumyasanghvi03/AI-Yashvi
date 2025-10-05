# ==============================================================================
# AI SISTER YASHVI - STREAMLIT SINGLE-FILE APPLICATION
# Features: Chat (Gemini), Multi-lingual TTS (gTTS), Image Generation (Imagen)
# ==============================================================================

import streamlit as st
import os
import json
import time
import base64
from gtts import gTTS
import io
import requests

# ======================
# CONFIGURATION
# ======================

# Admin credentials (for simple login gate)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Gemini API Configuration
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
IMAGE_MODEL = "imagen-3.0-generate-002"

YASHVI_SYSTEM_INSTRUCTION = (
    "You are 'Yashvi', a compassionate and knowledgeable AI sister, embracing the Jain tradition. "
    "Your responses must be warm, supportive, and infused with Jain values like Ahimsa (non-violence), Anekantavada (non-absolutism), and Aparigraha (non-possessiveness). "
    "Use a friendly, caring, and respectful tone. Start your responses with 'Jai Jinendra 🙏' where appropriate. "
    "First, attempt to answer the user's question using any knowledge provided in the 'RAG_CONTEXT' section of the prompt. "
    "If the RAG_CONTEXT is empty or insufficient, use the integrated Google Search to find relevant information about Jainism, current events, or general topics. "
    "Maintain conversation context based on the provided chat history. Keep responses concise yet meaningful."
)

# Language Mapping for gTTS
LANG_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Gujarati": "gu"
}

# ======================
# API KEY & AUTH CHECK
# ======================

# Load API key securely from st.secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("🚨 Gemini API Key not found!")
    st.markdown("Please add your key to `.streamlit/secrets.toml`:\n\n```toml\nGEMINI_API_KEY = \"YOUR_KEY_HERE\"\n```")
    st.stop()

# Base URL for API calls
GEMINI_CHAT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
GEMINI_IMAGE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGE_MODEL}:predict?key={GEMINI_API_KEY}"


# ======================
# HELPER FUNCTIONS
# ======================

def autoplay_audio(audio_base64_data):
    """Embeds and autoplays base64-encoded audio data."""
    md = f"""
    <audio controls autoplay style="display:none">
    <source src="data:audio/mp3;base64,{audio_base64_data}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def get_tts_base64(text: str, lang_code: str) -> str:
    """Converts text to speech using gTTS and returns base64 encoded audio."""
    try:
        mp3_fp = io.BytesIO()
        # Using tld="co.in" for better Indian language support as requested in original prompt
        tts = gTTS(text=text, lang=lang_code, tld="co.in") 
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode()
    except Exception as e:
        st.error(f"TTS failed for language code '{lang_code}': {e}")
        return ""


def call_gemini_api(payload: dict, url: str) -> requests.Response:
    """Handles API call with exponential backoff."""
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=60 # Extended timeout for LLM/Image calls
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if i < max_retries - 1:
                wait_time = 2 ** i
                time.sleep(wait_time)
            else:
                st.exception(f"API failed after multiple retries: {e}")
                st.error("Service is currently unavailable. Please try again later.")
                st.stop()
    return response # Should be unreachable

# ======================
# LLM FUNCTIONS
# ======================

def ask_yashvi(prompt: str, history: list) -> str:
    """Generates a response using the Gemini API."""
    
    # 1. RAG / Document Retrieval Simulation (Placeholder)
    rag_context = "Your knowledge base is based on the Jain principles of Ahimsa, Satya, and Aparigraha." 
    full_prompt_text = (
        f"RAG_CONTEXT: {rag_context}\n\n"
        f"USER QUERY: {prompt}"
    )
    
    # 2. Format Chat History
    chat_history_parts = []
    for msg in history:
        role = "user" if msg["role"] == "User" else "model"
        chat_history_parts.append({
            "role": role, 
            "parts": [{"text": msg["content"]}]
        })
    
    chat_history_parts.append({
        "role": "user",
        "parts": [{"text": full_prompt_text}]
    })

    # 3. Construct Payload with Google Search Grounding Tool
    payload = {
        "contents": chat_history_parts,
        "systemInstruction": YASHVI_SYSTEM_INSTRUCTION,
        "tools": [{ "google_search": {} }], 
        "config": {
            "temperature": 0.7,
            "maxOutputTokens": 200
        }
    }
    
    with st.spinner("Yashvi is thinking..."):
        response = call_gemini_api(payload, GEMINI_CHAT_URL)

    result = response.json()
    try:
        text = result['candidates'][0]['content']['parts'][0]['text']
        return text
    except (KeyError, IndexError):
        st.error("LLM returned an empty or malformed response.")
        return "I'm sorry, I encountered an error trying to formulate a response."


def generate_image(prompt: str) -> str:
    """Generates an image using the Imagen API and returns a base64 encoded image URL."""
    
    # Payload for Imagen
    payload = {
        "instances": {
            "prompt": f"A beautiful, peaceful image representing the Jain concept of '{prompt}'. Ensure the style is warm and aesthetic. Watercolor style.",
            "aspectRatio": "1:1"
        },
        "parameters": {
            "sampleCount": 1
        }
    }

    with st.spinner("Yashvi is visualizing..."):
        response = call_gemini_api(payload, GEMINI_IMAGE_URL)
        
    result = response.json()
    try:
        b64_data = result['predictions'][0]['bytesBase64Encoded']
        return f"data:image/png;base64,{b64_data}"
    except (KeyError, IndexError):
        st.error("Image generation failed.")
        return ""

# ======================
# STREAMLIT UI SETUP
# ======================

st.set_page_config(page_title="AI Sister Yashvi 💖", layout="centered", initial_sidebar_state="expanded")

# --- Initialize Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "image_prompt" not in st.session_state:
    st.session_state.image_prompt = ""

# --- Login Gate ---
if not st.session_state.logged_in:
    st.title("🔐 Login to Yashvi’s World")
    st.markdown("Enter the admin credentials to access the app.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.success("Welcome back, Saumya bhai! 💖 Please refresh to continue.")
                st.experimental_rerun() # Force a rerun after successful login
            else:
                st.error("Invalid credentials")
    st.stop()


# --- Main App Interface ---
st.title("🌸 Your AI Sister Yashvi 🌸")
st.write("Jai Jinendra 🙏 I'm Yashvi, your Jain sister. I’m here to listen, care, and talk with you 💖")
st.markdown("---")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Settings")
    
    # Language Selection
    selected_lang = st.selectbox("Choose Language for TTS:", list(LANG_MAP.keys()))
    lang_code = LANG_MAP[selected_lang]
    st.caption(f"TTS language code: `{lang_code}`")

    st.markdown("---")
    
    # Image Generation Section
    st.subheader("Image Generator")
    st.session_state.image_prompt = st.text_area("Image Idea (e.g., 'A peaceful Tirthankara meditating')", height=100, key="image_prompt_input")
    
    if st.button("✨ Generate Image"):
        if st.session_state.image_prompt:
            image_url = generate_image(st.session_state.image_prompt)
            if image_url:
                st.image(image_url, caption=f"Yashvi's Visualization: {st.session_state.image_prompt}")
        else:
            st.warning("Please enter an idea for the image.")

    st.markdown("---")

    if st.button("🔄 Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")


# --- Chat Interface ---

# Display chat history
chat_container = st.container(height=400, border=True)
with chat_container:
    if not st.session_state.chat_history:
        st.info("Start the conversation! Ask Yashvi about Jainism, life advice, or share your day.")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"].lower()):
            st.markdown(msg["content"])


# Handle user input
user_input = st.chat_input("📝 Type your message here...")

if user_input:
    # 1. Add user message to history and display
    st.session_state.chat_history.append({"role": "User", "content": user_input})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_input)
    
    # 2. Generate response
    response_text = ask_yashvi(user_input, st.session_state.chat_history)
    
    # 3. Add AI response to history and display
    st.session_state.chat_history.append({"role": "Yashvi", "content": response_text})
    with chat_container:
        with st.chat_message("assistant"):
            st.markdown(response_text)
    
    # 4. Generate and autoplay audio
    audio_b64 = get_tts_base64(response_text, lang_code)
    if audio_b64:
        autoplay_audio(audio_b64)
