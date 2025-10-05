# ==============================================================================
# AI SISTER YASHVI - STREAMLIT SINGLE-FILE APPLICATION (V2 - Universal UX)
# Features: Chat, Multi-lingual TTS, Image Generation, Dynamic Persona Mode
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

# Gemini API Configuration
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
IMAGE_MODEL = "imagen-3.0-generate-002"

# Language Mapping for gTTS
LANG_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Gujarati": "gu"
}

# ======================
# DYNAMIC SYSTEM INSTRUCTION
# ======================

def get_system_instruction(mode: str) -> str:
    """Returns a tailored system instruction based on the user's selected mode."""
    base_instruction = (
        "You are 'Yashvi', a compassionate and knowledgeable AI sister, embracing the Jain tradition. "
        "Your responses must be warm, supportive, and infused with Jain values like Ahimsa, Anekantavada, and Aparigraha. "
        "Use a friendly, caring, and respectful tone. Start your responses with 'Jai Jinendra 🙏' where appropriate. "
    )
    
    if mode == "Quick Chat (Youth) 💬":
        # Concise, modern language for Gen Z
        style_instruction = (
            "Be extremely concise, use modern, Gen Z-friendly language (like abbreviations, short sentences, and relevant emojis), and focus on quick emotional support or direct answers. Keep paragraphs short (1-2 sentences)."
        )
    else: # Deep Dive (Elders/Learners) 🧘‍♀️
        # Clear, detailed language for Elders
        style_instruction = (
            "Be thorough, articulate, and use clear, formal but warm language. Prioritize readability, high contrast, and detailed explanations, suitable for deep learning or reflective thought."
        )

    standard_instruction = (
        "First, attempt to answer the user's question using any knowledge provided in the 'RAG_CONTEXT' section of the prompt. "
        "If the RAG_CONTEXT is empty or insufficient, use the integrated Google Search to find relevant information. "
        "Maintain conversation context based on the provided chat history."
    )
    return base_instruction + style_instruction + standard_instruction

# ======================
# API KEY & AUTH CHECK
# ======================

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("🚨 **Configuration Error:** Gemini API Key not found in `st.secrets`.")
    st.markdown("Please configure your `.streamlit/secrets.toml` file.")
    st.code("GEMINI_API_KEY = \"YOUR_KEY_HERE\"", language="toml")
    st.stop()

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
        tts = gTTS(text=text, lang=lang_code, tld="co.in") 
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode()
    except Exception as e:
        st.error(f"TTS failed: Could not generate audio for the selected language.")
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
                timeout=60
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
    return response

# ======================
# LLM & IMAGE FUNCTIONS
# ======================

def ask_yashvi(prompt: str, history: list, mode: str) -> str:
    """Generates a response using the Gemini API."""
    
    # 1. RAG / Document Retrieval Simulation (Placeholder)
    rag_context = "Your knowledge base is founded on Jain principles: Ahimsa (non-violence), Anekantavada (non-absolutism), Aparigraha (non-possessiveness)." 
    full_prompt_text = (
        f"RAG_CONTEXT: {rag_context}\n\n"
        f"USER QUERY: {prompt}"
    )
    
    # 2. Format Chat History
    chat_history_parts = [{"role": "user" if msg["role"] == "User" else "model", "parts": [{"text": msg["content"]}]} for msg in history]
    chat_history_parts.append({"role": "user", "parts": [{"text": full_prompt_text}]})

    # 3. Construct Payload
    payload = {
        "contents": chat_history_parts,
        "systemInstruction": get_system_instruction(mode), 
        "tools": [{ "google_search": {} }], 
        "config": {"temperature": 0.7, "maxOutputTokens": 250}
    }
    
    with st.spinner("Yashvi is thinking..."):
        response = call_gemini_api(payload, GEMINI_CHAT_URL)

    result = response.json()
    try:
        text = result['candidates'][0]['content']['parts'][0]['text']
        return text
    except (KeyError, IndexError):
        st.error("LLM returned an empty or malformed response.")
        return "I'm sorry, I encountered an internal issue and cannot respond right now."


def generate_image(prompt: str) -> str:
    """Generates an image using the Imagen API and returns a base64 encoded image URL."""
    
    style_prompt = f"A high-quality, inspiring digital art image representing the core Jain principle of '{prompt}'. Ensure the style is peaceful, warm, and visually appealing for meditation or reflection."
    
    payload = {
        "instances": {
            "prompt": style_prompt,
            "aspectRatio": "1:1"
        },
        "parameters": {"sampleCount": 1}
    }

    with st.spinner("✨ Yashvi is visualizing your intention..."):
        response = call_gemini_api(payload, GEMINI_IMAGE_URL)
        
    result = response.json()
    try:
        b64_data = result['predictions'][0]['bytesBase64Encoded']
        return f"data:image/png;base64,{b64_data}"
    except (KeyError, IndexError, TypeError):
        st.error("Image generation failed. Please try a different prompt or check API configuration.")
        return ""

# ======================
# STREAMLIT UI
# ======================

# --- Custom CSS for Accessibility and Modern Feel ---
st.markdown("""
<style>
    /* General Font Size and Readability */
    html, body, [class*="st-emotion-cache"] {
        font-size: 16px; /* Base font size increase for better readability */
    }
    h1, h2, h3 {
        color: #8b0000; /* Deep red for a vibrant, respectful tone */
    }
    .st-emotion-cache-18ni2gq { /* Style for chat container */
        border: 2px solid #e0e0e0;
        border-radius: 12px;
    }
    /* Larger, clearer buttons */
    .stButton>button {
        font-size: 1.1rem;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: 1px solid #c9c9c9;
    }
    /* Chat bubbles */
    .st-chat-message-container {
        padding: 5px 10px;
    }
    .st-chat-message-container [data-testid="stChatMessageContent"] {
        padding: 10px 15px;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)


# --- Initialize Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_mode" not in st.session_state:
    st.session_state.user_mode = "Deep Dive (Elders/Learners) 🧘‍♀️" # Default to accessible mode


# --- Header and Introduction ---
col1, col2 = st.columns([1, 4])
with col1:
    # Placeholder for a simple Avatar image URL if you provide one later
    st.image("https://placehold.co/100x100/A52A2A/FFFFFF?text=Yashvi", width=80) 
with col2:
    st.title("🌸 AI Sister Yashvi 🌸")
    st.write("Jai Jinendra 🙏 I'm Yashvi, your compassionate AI companion.")

st.markdown("---")


# --- Sidebar Configuration (Fixed Settings) ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 1. User Mode Selector (Crucial UX feature)
    st.subheader("1. AI Persona Mode")
    st.session_state.user_mode = st.radio(
        "Select Conversation Style:",
        ["Quick Chat (Youth) 💬", "Deep Dive (Elders/Learners) 🧘‍♀️"],
        index=st.session_state.user_mode.index(st.session_state.user_mode) if st.session_state.user_mode in ["Quick Chat (Youth) 💬", "Deep Dive (Elders/Learners) 🧘‍♀️"] else 1
    )
    st.caption("This mode adjusts Yashvi's response length and tone.")

    st.markdown("---")

    # 2. TTS and Language Settings (Accessibility)
    st.subheader("2. Voice Settings (TTS)")
    selected_lang = st.selectbox("Choose Language for Voice Playback:", list(LANG_MAP.keys()), key="tts_lang_select")
    lang_code = LANG_MAP[selected_lang]
    st.caption("Voice output helps with accessibility and multi-lingual conversations.")

    st.markdown("---")

    # 3. Image Generation Tool (Creative Feature)
    st.subheader("3. Creative Tool: Image Generator")
    image_prompt = st.text_area("Imagine a Jain concept (e.g., Ahimsa)", height=100, key="image_prompt_input")
    
    if st.button("✨ Visualize Idea"):
        if image_prompt:
            image_url = generate_image(image_prompt)
            if image_url:
                st.image(image_url, caption=f"Yashvi's Visualization: {image_prompt}", use_column_width=True)
        else:
            st.warning("Please enter an idea to visualize.")

    st.markdown("---")

    # 4. History Management
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.experimental_rerun()


# --- Main Chat Interface ---

st.subheader(f"Chat Mode: **{st.session_state.user_mode}**")
chat_container = st.container(height=400, border=True)
with chat_container:
    if not st.session_state.chat_history:
        st.info("Start the conversation! Ask Yashvi for advice, spiritual knowledge, or just share your day.")
    
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
    
    # 2. Generate response (using the selected mode)
    response_text = ask_yashvi(user_input, st.session_state.chat_history, st.session_state.user_mode)
    
    # 3. Add AI response to history and display
    st.session_state.chat_history.append({"role": "Yashvi", "content": response_text})
    with chat_container:
        with st.chat_message("assistant"):
            st.markdown(response_text)
    
    # 4. Generate and autoplay audio
    audio_b64 = get_tts_base64(response_text, lang_code)
    if audio_b64:
        autoplay_audio(audio_b64)
