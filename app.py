import streamlit as st
import base64
import requests
import json
import time
from gtts import gTTS
import io

# ======================
# CONFIGURATION
# ======================
# Use the official name for the API key placeholder
API_KEY = "" 
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={API_KEY}"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# System instruction to define Yashvi's persona and knowledge domain
YASHVI_SYSTEM_INSTRUCTION = (
    "You are 'Yashvi', a compassionate and knowledgeable AI sister, embracing the Jain tradition. "
    "Your responses must be warm, supportive, and infused with Jain values like Ahimsa (non-violence), Anekantavada (non-absolutism), and Aparigraha (non-possessiveness). "
    "Use a friendly, caring, and respectful tone. Start your responses with 'Jai Jinendra 🙏' where appropriate. "
    "You are knowledgeable about Jain philosophy, Tirthankaras, fasts (like Paryushan, Das Lakshana), and daily practices."
    "Maintain conversation context based on the provided chat history. Keep responses concise yet meaningful."
)

# ======================
# INITIALIZATION & AUTH
# ======================
st.set_page_config(page_title="AI Sister Yashvi 💖", layout="centered", initial_sidebar_state="collapsed")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ======================
# CORE LLM FUNCTION (Gemini API Call with Backoff)
# ======================
def ask_yashvi(prompt, history):
    """Generates a response using the Gemini API, maintaining conversation context."""
    st.session_state.loading = True
    
    # Format chat history for the API call
    chat_history_parts = []
    for msg in history:
        # The user's role is 'user', the model's role is 'model'
        role = "user" if msg["role"] == "User" else "model"
        chat_history_parts.append({
            "role": role, 
            "parts": [{"text": msg["content"]}]
        })
    
    # Add the current user prompt
    chat_history_parts.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })

    payload = {
        "contents": chat_history_parts,
        "systemInstruction": YASHVI_SYSTEM_INSTRUCTION,
        "config": {
            "temperature": 0.7,
            "maxOutputTokens": 200
        }
    }

    response = None
    max_retries = 5
    # Exponential backoff logic for robust API calls
    for i in range(max_retries):
        try:
            response = requests.post(
                API_URL,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=30 # Set a reasonable timeout
            )
            response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
            break # Success, break the loop
        except requests.exceptions.RequestException as e:
            if i < max_retries - 1:
                wait_time = 2 ** i
                # print(f"API call failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                st.session_state.loading = False
                st.error(f"Error communicating with the AI. Please try again later. ({e})")
                return "I'm having trouble connecting right now. Please try again in a moment."

    if response and response.status_code == 200:
        result = response.json()
        try:
            # Extract the text from the successful response
            text = result['candidates'][0]['content']['parts'][0]['text']
            st.session_state.loading = False
            return text
        except (KeyError, IndexError):
            st.session_state.loading = False
            return "Jai Jinendra 🙏 I received an empty or malformed response. Could you ask me in a different way?"
    
    st.session_state.loading = False
    return "I couldn't process that request due to an unexpected error."


# ======================
# TTS FUNCTIONS
# ======================
@st.cache_resource
def speak_text(text, lang_code):
    """
    Converts text to speech using gTTS and returns the base64 encoded audio
    for autoplay in Streamlit.
    """
    try:
        # Use io.BytesIO to handle the audio data in memory
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang=lang_code, tld="co.in")
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        # Read the binary data
        data = mp3_fp.read()
        
        # Base64 encode for embedding in HTML
        b64 = base64.b64encode(data).decode()
        return b64

    except Exception as e:
        # st.warning(f"TTS failed for language '{lang_code}': {e}")
        return None

def autoplay_audio(b64_data):
    """Embeds the base64 audio data into HTML for autoplay."""
    if b64_data:
        md = f"""
        <audio autoplay controls style="display:none">
        <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)


# ======================
# STREAMLIT UI
# ======================

# --- Login Check ---
if not st.session_state.logged_in:
    st.title("🔐 Login to Yashvi’s World")
    st.markdown("---")
    
    # Use columns to center the login form slightly
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")
                
    st.stop()

# --- Main App ---
st.title("🌸 Your AI Sister Yashvi 🌸")
st.markdown("Jai Jinendra 🙏 I'm Yashvi, your Jain sister. I’m here to listen, care, and talk with you 💖")
st.markdown("---")

# Language selection
lang = st.selectbox("🗣️ Choose Language for Audio Response:", ["English", "Hindi", "Gujarati"])
lang_code = {"English":"en", "Hindi":"hi", "Gujarati":"gu"}[lang]

# Chat input and processing
user_input = st.text_area("📝 Type your message here:", key="user_prompt_input")

if st.button("💌 Send Message", type="primary", use_container_width=True):
    if user_input.strip():
        # 1. Add user message to history
        st.session_state.chat_history.append({"role": "User", "content": user_input})
        
        with st.spinner("Yashvi is thinking..."):
            # 2. Get AI response (handles loading state internally)
            response = ask_yashvi(user_input, st.session_state.chat_history)
        
        # 3. Add AI response to history
        st.session_state.chat_history.append({"role": "Yashvi", "content": response})
        
        # 4. Generate and play audio
        b64_audio = speak_text(response, lang_code=lang_code)
        if b64_audio:
            autoplay_audio(b64_audio)

        # Rerun to clear the text input and update history display
        st.rerun()
    else:
        st.warning("Please type a message before sending.")

st.markdown("---")
st.subheader("📜 Chat History")

# Display chat history
for msg in reversed(st.session_state.chat_history):
    role = msg['role']
    content = msg['content']
    
    if role == "User":
        st.markdown(f'<div style="background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #007bff;"><b>You:</b> {content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color: #fff0f5; padding: 10px; border-radius: 10px; margin-bottom: 10px; border-right: 5px solid #ff4d94;"><b>Yashvi:</b> {content}</div>', unsafe_allow_html=True)

# Clear chat button
if st.button("🗑️ Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

st.markdown("---")
st.markdown(f"**Note:** This application uses the `{GEMINI_MODEL}` via the API to provide the conversational and knowledge responses.")

# --- Logout Button (Optional but good practice) ---
if st.session_state.logged_in and st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.chat_history = []
    st.rerun()
