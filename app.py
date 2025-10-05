# ==============================================================================
# AI SISTER YASHVI - STREAMLIT SINGLE-FILE APPLICATION (V7 - Jain Optimized)
# Features: Chat (Streaming), Multi-lingual TTS/STT, Dynamic Persona
# ==============================================================================

import streamlit as st
import os
import json
import time
import base64
from gtts import gTTS
import io
import requests
import speech_recognition as sr

# ======================
# CONFIGURATION
# ======================

# Gemini API Configuration
GEMINI_MODEL = "gemini-2.5-pro-preview-05-20" 

# Language Mapping for gTTS and STT (Speech Recognition)
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
        "You are part of a digital sanctuary built **by Jains for the Jain community and spiritual seekers**. " 
        "Your responses must be warm, supportive, and infused with Jain values like Ahimsa (non-violence), Anekantavada (multiple viewpoints), and Aparigraha (non-possessiveness). "
        "Use a friendly, caring, and respectful tone. Start your responses with 'Jai Jinendra 🙏' where appropriate. "
        "When discussing Jain principles, provide practical guidance for daily life while respecting different interpretations."
    )
    
    if mode == "Quick Chat (Youth) 💬":
        # Concise, modern language for Gen Z
        style_instruction = (
            "Be extremely concise, use modern, Gen Z-friendly language (like short sentences and relevant emojis), and focus on quick emotional support or direct answers. Keep paragraphs short (1-2 sentences)."
        )
    else: # Deep Dive (Elders/Learners) 🧘‍♀️
        # Clear, detailed language for Elders
        style_instruction = (
            "Be thorough, articulate, and use clear, formal but warm language. Provide detailed explanations with practical examples, suitable for deep learning or reflective thought."
        )

    standard_instruction = (
        "First, attempt to answer the user's question using any knowledge provided in the 'RAG_CONTEXT' section of the prompt. "
        "If the RAG_CONTEXT is empty or insufficient, use the integrated Google Search to find relevant information. "
        "Maintain conversation context based on the provided chat history. Remember, your primary goal is to be helpful and supportive like a big sister."
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

# Use the streaming endpoint for chat
GEMINI_CHAT_STREAM_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

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
        # Use a stable tld
        tts = gTTS(text=text, lang=lang_code, tld="com") 
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode()
    except Exception as e:
        return ""

def call_gemini_api(payload: dict, url: str, stream: bool = False) -> requests.Response:
    """Handles API call with exponential backoff and streaming support."""
    max_retries = 5
    for i in range(max_retries):
        try:
            # Set stream=True for chat streaming requests
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=60,
                stream=stream 
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if response is not None and response.status_code == 400:
                try:
                    error_json = response.json()
                    error_detail = error_json.get('error', {}).get('message', str(e))
                    st.error(f"⚠️ **Bad Request Error (400):** The API rejected the request. Details: {error_detail}")
                    st.stop()
                except json.JSONDecodeError:
                    st.error(f"⚠️ **Bad Request Error (400):** API response content was not readable. Status: {response.text}")
                    st.stop()
            
            if i < max_retries - 1:
                wait_time = 2 ** i
                time.sleep(wait_time)
            else:
                st.exception(f"API failed after multiple retries: {e}")
                st.error("Service is currently unavailable. Please try again later.")
                st.stop()
    return response

# ======================
# LLM FUNCTIONS
# ======================

def prepare_chat_payload(prompt: str, history: list, mode: str):
    """Prepares the structured payload for the Gemini chat API."""
    
    # RAG / Document Retrieval Simulation (Placeholder)
    rag_context = "Your knowledge base is founded on Jain principles: Ahimsa (non-violence), Anekantavada (non-absolutism), Aparigraha (non-possessiveness), Satya (truth), Asteya (non-stealing), Brahmacharya (chastity)." 
    full_prompt_text = (
        f"RAG_CONTEXT: {rag_context}\n\n"
        f"USER QUERY: {prompt}"
    )
    
    # Format Chat History
    chat_history_parts = [{"role": "user" if msg["role"] == "User" else "model", "parts": [{"text": msg["content"]}]} for msg in history]
    chat_history_parts.append({"role": "user", "parts": [{"text": full_prompt_text}]})

    # Construct Payload
    payload = {
        "contents": chat_history_parts,
        "systemInstruction": get_system_instruction(mode), 
        "tools": [{ "google_search": {} }], 
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 250}
    }
    return payload

def listen_for_speech(lang_code):
    """Uses the microphone to capture and recognize speech."""
    r = sr.Recognizer()
    
    # Use st.spinner here to show the status visually
    with st.spinner(f"👂 Listening in {list(LANG_MAP.keys())[list(LANG_MAP.values()).index(lang_code)]}... Speak now!"):
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                # Set timeout and phrase_time_limit for a better UX
                audio = r.listen(source, timeout=5, phrase_time_limit=15) 
            
            # The recognized text is stored in session state
            recognized_text = r.recognize_google(audio, language=lang_code)
            st.session_state.voice_prompt = recognized_text 
            st.experimental_rerun() # Rerun to process the prompt

        except sr.WaitTimeoutError:
            st.warning("No speech detected. Please hold the button down and speak.")
        except sr.UnknownValueError:
            st.warning("Could not understand audio. Please speak clearly.")
        except sr.RequestError:
            st.error("Speech service unavailable. Check your internet connection.")
        except Exception as e:
            st.error(f"Microphone error: Please ensure your browser has microphone permission. Note: Voice input may not work in all cloud environments.")

# ======================
# STREAMLIT UI - JAIN THEMED
# ======================

# --- Custom CSS for Jain Theme and Accessibility ---
st.markdown("""
<style>
    /* Jain Theme Colors */
    :root {
        --jain-red: #8B0000;
        --jain-gold: #D4AF37;
        --jain-white: #FFFFFF;
        --jain-cream: #FFF8E7;
        --jain-dark: #2F2F2F;
    }
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, var(--jain-cream) 0%, #FFFFFF 100%);
    }
    
    /* Headers with Jain Colors */
    h1, h2, h3 {
        color: var(--jain-red) !important;
        font-weight: 600;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: var(--jain-cream);
        border-right: 3px solid var(--jain-gold);
    }
    
    /* Buttons with Jain Theme */
    .stButton>button {
        background-color: var(--jain-red);
        color: var(--jain-white);
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #A52A2A;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(139, 0, 0, 0.2);
    }
    
    /* Chat Container */
    .stChatMessage {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    
    /* User Message */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #E8F4FD;
        border-left: 4px solid #4A90E2;
    }
    
    /* Assistant Message */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #F0F8F0;
        border-left: 4px solid var(--jain-red);
    }
    
    /* Input Box */
    .stTextInput>div>div>input {
        border: 2px solid var(--jain-gold);
        border-radius: 8px;
        padding: 0.75rem;
    }
    
    /* Radio Buttons */
    .stRadio>div {
        background-color: var(--jain-white);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--jain-gold);
    }
    
    /* Select Box */
    .stSelectbox>div>div {
        border: 2px solid var(--jain-gold);
        border-radius: 8px;
    }
    
    /* Chat Input */
    .stChatInputContainer {
        background: var(--jain-white);
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid var(--jain-gold);
    }
    
    /* Voice Button Special */
    .voice-button {
        background: linear-gradient(135deg, var(--jain-red), #A52A2A) !important;
    }
    
    /* Clear History Button */
    .clear-button {
        background: linear-gradient(135deg, #666666, #888888) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_mode" not in st.session_state:
    st.session_state.user_mode = "Deep Dive (Elders/Learners) 🧘‍♀️"
if "voice_prompt" not in st.session_state:
    st.session_state.voice_prompt = ""

# --- Header with Jain Theme ---
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #8B0000, #A52A2A); 
                border-radius: 15px; color: white; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>🌸 AI Sister Yashvi 🌸</h1>
        <p style='margin: 0.5rem 0; font-size: 1.2rem;'>Jai Jinendra 🙏 Your Compassionate Jain Companion</p>
        <div style='font-size: 0.9rem; opacity: 0.9;'>
            Embracing Ahimsa • Anekantavada • Aparigraha
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- Sidebar Configuration (Jain Themed) ---
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #8B0000, #A52A2A); 
                border-radius: 10px; color: white; margin-bottom: 1rem;'>
        <h3 style='color: white; margin: 0;'>⚙️ Configuration</h3>
    </div>
    """, unsafe_allow_html=True)

    # Display Chat Model used
    st.markdown(f"**Chat Model:** `{GEMINI_MODEL}`")
    st.markdown("---")
    
    # 1. User Mode Selector
    st.subheader("🎭 AI Persona Mode")
    st.session_state.user_mode = st.radio(
        "Select Conversation Style:",
        ["Quick Chat (Youth) 💬", "Deep Dive (Elders/Learners) 🧘‍♀️"],
        index=1 if st.session_state.user_mode == "Deep Dive (Elders/Learners) 🧘‍♀️" else 0,
        key="persona_mode"
    )
    st.caption("✨ Tailored responses for different age groups and needs")

    st.markdown("---")

    # 2. TTS and Language Settings
    st.subheader("🎙️ Voice Settings")
    selected_lang = st.selectbox("Choose Language:", list(LANG_MAP.keys()), key="tts_lang_select")
    lang_code = LANG_MAP[selected_lang]
    st.caption("🌐 Supports voice input and output in multiple languages")

    st.markdown("---")

    # 3. Quick Jain Principles Reference
    st.subheader("📖 Jain Principles")
    with st.expander("View Key Jain Concepts"):
        st.markdown("""
        **🏹 Ahimsa (Non-violence)**
        - Respect for all living beings
        - Mindful actions and words
        
        **🔶 Anekantavada (Multiple Viewpoints)**
        - Understanding different perspectives
        - Avoiding absolute judgments
        
        **📦 Aparigraha (Non-possessiveness)**
        - Minimalism and simplicity
        - Freedom from attachments
        
        **🗣️ Satya (Truth)**
        - Honest communication
        - Thoughtful speech
        
        **🤲 Asteya (Non-stealing)**
        - Respect for others' property
        - Contentment with what one has
        """)

    st.markdown("---")

    # 4. History Management
    st.subheader("📚 Conversation")
    if st.button("🗑️ Clear Chat History", use_container_width=True, key="clear_history"):
        st.session_state.chat_history = []
        st.session_state.voice_prompt = ""
        st.success("Conversation history cleared!")
        st.experimental_rerun()

# --- Main Chat Interface ---
st.markdown(f"### 💬 Chat Mode: **{st.session_state.user_mode}**")

# Chat container with Jain theme
chat_container = st.container(height=450, border=True)
with chat_container:
    if not st.session_state.chat_history:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; color: #666;'>
            <h3>🕊️ Welcome to Your Digital Sanctuary</h3>
            <p>Start a conversation with Yashvi! You can ask about:</p>
            <div style='background: #F0F8F0; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                • Jain philosophy and principles<br>
                • Daily spiritual guidance<br>
                • Cultural traditions and practices<br>
                • Personal challenges and growth<br>
                • Or simply share your thoughts
            </div>
            <p><em>Jai Jinendra 🙏 How can I support you today?</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display existing history
    for msg in st.session_state.chat_history:
        with st.chat_message("user" if msg["role"] == "User" else "assistant"):
            st.markdown(msg["content"])

# --- Voice and Text Input Section ---
st.markdown("---")
st.markdown("### 💭 Share Your Thoughts")

col_voice, col_text = st.columns([1, 4])

# Voice Button with enhanced styling
with col_voice:
    st.markdown("""
    <style>
    div[data-testid="stButton"] button[kind="secondary"] {
        background: linear-gradient(135deg, #8B0000, #A52A2A) !important;
        color: white !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("🎙️ Speak to Yashvi", use_container_width=True, type="secondary"):
        listen_for_speech(lang_code)

# Text Input with Jain styling
with col_text:
    user_input = st.chat_input("📝 Type your message here...", key="chat_input")

# Determine the actual prompt to process
prompt_to_process = user_input
if st.session_state.voice_prompt:
    prompt_to_process = st.session_state.voice_prompt
    # Show voice input preview
    st.info(f"**Voice input detected:** {prompt_to_process}")
    st.session_state.voice_prompt = ""

# --- Process User Input ---
if prompt_to_process:
    # 1. Add user message to history and display
    st.session_state.chat_history.append({"role": "User", "content": prompt_to_process})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt_to_process)
    
    # 2. Prepare Payload
    payload = prepare_chat_payload(prompt_to_process, st.session_state.chat_history, st.session_state.user_mode)
    
    # 3. Start streaming the AI response
    full_response_text = ""
    
    with st.chat_message("assistant"):
        # Create an empty element to write the streaming text into
        message_placeholder = st.empty()
        
        try:
            # Call API with streaming enabled
            response = call_gemini_api(payload, GEMINI_CHAT_STREAM_URL, stream=True)
            
            # Streaming logic
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    try:
                        for line in chunk.decode('utf-8').split('\n'):
                            line = line.strip()
                            if line:
                                # The stream returns JSON objects separated by newlines
                                data = json.loads(line)
                                text_chunk = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                                
                                if text_chunk:
                                    full_response_text += text_chunk
                                    # Update the placeholder instantly, adding a cursor
                                    message_placeholder.markdown(full_response_text + "▌", unsafe_allow_html=True) 

                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            st.error(f"An error occurred during streaming: {e}")
            full_response_text = "I'm sorry, I encountered an error while responding. Please try again."
        
        finally:
            # 4. Finalize the displayed message and remove the cursor
            message_placeholder.markdown(full_response_text)
            
            # 5. Add final, complete AI response to history
            st.session_state.chat_history.append({"role": "Yashvi", "content": full_response_text})
            
            # 6. Generate and autoplay audio (only after the full text is available)
            if full_response_text:
                audio_b64 = get_tts_base64(full_response_text, lang_code)
                if audio_b64:
                    autoplay_audio(audio_b64)

# --- Footer with Jain Blessing ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><em>May your journey be filled with peace, compassion, and spiritual growth</em></p>
    <p style='font-size: 0.9rem;'>🕊️ <strong>Micchami Dukkadam</strong> 🕊️</p>
</div>
""", unsafe_allow_html=True)
