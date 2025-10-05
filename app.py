# ==============================================================================
# AI SISTER YASHVI - STREAMLIT SINGLE-FILE APPLICATION (V8 - Fixed API + Local Intelligence)
# Features: Chat (Hybrid), Multi-lingual TTS/STT, Dynamic Persona
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
import random
import re

# ======================
# CONFIGURATION
# ======================

# Model Configuration
GEMINI_MODEL = "gemini-2.5-pro-preview-05-20" 

# Language Mapping for gTTS and STT
LANG_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Gujarati": "gu"
}

# Local ML Responses Database
JAIN_KNOWLEDGE_BASE = {
    "ahims?a": [
        "Ahimsa means non-violence in thought, word, and action! 🌱 It's about being kind to all living beings.",
        "Practice Ahimsa by being mindful of your actions and words. Even small acts of kindness matter! 💫",
        "Ahimsa isn't just physical - watch your thoughts and words too. Spread peace everywhere! 🕊️"
    ],
    "anekantavada": [
        "Anekantavada means multiple viewpoints! 🔶 Truth has many sides - be open to different perspectives.",
        "Remember Anekantavada: everyone sees truth differently. Avoid absolute judgments! 🌈",
        "This principle teaches us tolerance and understanding. See the world through others' eyes! 👁️"
    ],
    "aparigraha": [
        "Aparigraha means non-possessiveness! 📦 Live simply and avoid unnecessary attachments.",
        "Practice Aparigraha by decluttering your life and mind. Freedom comes from letting go! 🕊️",
        "Minimalism is key! Focus on what truly matters rather than accumulating stuff. 🌟"
    ],
    "jain": [
        "Jainism emphasizes compassion, self-discipline, and spiritual growth! 🙏",
        "Our path focuses on non-violence, truth, and non-possessiveness for inner peace. 🌸",
        "Jain teachings guide us toward liberation through right knowledge and conduct. 📚"
    ],
    "meditat": [
        "Meditation helps calm the mind and connect with your inner self! 🧘‍♀️",
        "Try sitting quietly for 10 minutes daily. Focus on your breath and let thoughts pass. 💫",
        "Meditation builds mindfulness and inner peace - essential for spiritual growth! 🌟"
    ],
    "pray": [
        "Prayer connects us with higher consciousness and expresses gratitude! 🙏",
        "Morning prayers set positive intentions for the day. Evening prayers help reflection. 🌅",
        "Pray with sincerity - it's the quality, not quantity, that matters. 💖"
    ]
}

# ======================
# LOCAL ML RESPONSE GENERATOR
# ======================

def generate_local_response(user_input, mode):
    """Generate responses using local pattern matching and Jain knowledge base"""
    
    input_lower = user_input.lower()
    
    # Greeting patterns
    if any(word in input_lower for word in ["hello", "hi", "hey", "namaste", "jai jinendra"]):
        greetings = [
            "Jai Jinendra! 🙏 How can I help you today?",
            "Jai Jinendra! 🌸 What's on your mind?",
            "Hello! 🙏 How are you feeling today?"
        ]
        return random.choice(greetings)
    
    # Feeling/emotion detection
    if any(word in input_lower for word in ["sad", "upset", "depressed", "unhappy"]):
        return "I'm here for you! 💖 Remember, difficult times pass. Want to talk about what's bothering you?"
    
    if any(word in input_lower for word in ["happy", "good", "great", "excited"]):
        return "That's wonderful! 😊 Your positive energy brightens the space around you!"
    
    if any(word in input_lower for word in ["stress", "anxious", "worried", "nervous"]):
        return "Take a deep breath! 🌬️ Remember Anekantavada - there are always multiple perspectives to any situation."
    
    # Search knowledge base for matching topics
    for pattern, responses in JAIN_KNOWLEDGE_BASE.items():
        if re.search(pattern, input_lower):
            response = random.choice(responses)
            if mode == "Quick Chat (Youth) 💬":
                # Add emojis and make more casual for youth mode
                emojis = ["💫", "🌟", "✨", "🌱", "🕊️", "🌈", "🙏"]
                response += " " + random.choice(emojis)
            return response
    
    # Default responses based on mode
    if mode == "Quick Chat (Youth) 💬":
        defaults = [
            "Interesting! Could you tell me more? 💭",
            "I'd love to help! Could you elaborate? 🌟",
            "That's cool! What specifically are you wondering about? 🔍",
            "Great question! Let me think about that... 💫"
        ]
    else:
        defaults = [
            "That's a thoughtful question. Could you share more about what you're seeking?",
            "I appreciate your curiosity. Let me understand your question better.",
            "This sounds important. Would you like to explore this topic in more depth?",
            "Your inquiry shows deep reflection. Please tell me more about your interest in this matter."
        ]
    
    return random.choice(defaults)

# ======================
# GEMINI API FUNCTIONS (FALLBACK)
# ======================

def get_system_instruction(mode: str) -> dict:
    """Returns a tailored system instruction in correct API format"""
    base_instruction = (
        "You are 'Yashvi', a compassionate AI sister embracing Jain tradition. "
        "Your responses must be warm, supportive, and infused with Jain values. "
        "Use a friendly, caring, and respectful tone."
    )
    
    if mode == "Quick Chat (Youth) 💬":
        style_instruction = "Be concise, use modern language with emojis, and focus on quick emotional support."
    else:
        style_instruction = "Be thorough and use clear, formal but warm language with detailed explanations."

    full_instruction = base_instruction + " " + style_instruction
    return {"parts": [{"text": full_instruction}]}

def prepare_gemini_payload(prompt: str, history: list, mode: str):
    """Prepares the structured payload for Gemini API"""
    
    # Format conversation history
    contents = []
    for msg in history[-6:]:  # Keep last 6 messages for context
        role = "user" if msg["role"] == "User" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
    
    # Add current message
    contents.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })

    payload = {
        "contents": contents,
        "systemInstruction": get_system_instruction(mode),
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 250,
            "topP": 0.8
        }
    }
    return payload

def call_gemini_api(prompt: str, history: list, mode: str) -> str:
    """Call Gemini API with proper error handling"""
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        
        payload = prepare_gemini_payload(prompt, history, mode)
        
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            st.warning("🔗 Gemini connection issue - using local wisdom")
            return generate_local_response(prompt, mode)
            
    except Exception as e:
        st.warning("🌐 Network issue - using local knowledge base")
        return generate_local_response(prompt, mode)

# ======================
# HELPER FUNCTIONS
# ======================

def autoplay_audio(audio_base64_data):
    """Embeds and autoplays base64-encoded audio data"""
    md = f"""
    <audio controls autoplay style="display:none">
    <source src="data:audio/mp3;base64,{audio_base64_data}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_tts_base64(text: str, lang_code: str) -> str:
    """Converts text to speech using gTTS and returns base64 encoded audio"""
    try:
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang=lang_code, tld="com") 
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode()
    except Exception:
        return ""

def listen_for_speech(lang_code):
    """Uses the microphone to capture and recognize speech"""
    r = sr.Recognizer()
    
    with st.spinner(f"👂 Listening in {list(LANG_MAP.keys())[list(LANG_MAP.values()).index(lang_code)]}..."):
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=5, phrase_time_limit=15) 
            
            recognized_text = r.recognize_google(audio, language=lang_code)
            st.session_state.voice_prompt = recognized_text 
            st.rerun()

        except sr.WaitTimeoutError:
            st.warning("No speech detected. Please hold the button and speak.")
        except sr.UnknownValueError:
            st.warning("Could not understand audio. Please speak clearly.")
        except Exception as e:
            st.error("Microphone error. Please check permissions.")

# ======================
# HYBRID RESPONSE GENERATOR
# ======================

def generate_response(prompt: str, history: list, mode: str, use_local: bool = False) -> str:
    """Generate response using either local ML or Gemini API"""
    
    if use_local:
        return generate_local_response(prompt, mode)
    else:
        # Try Gemini first, fallback to local
        try:
            return call_gemini_api(prompt, history, mode)
        except:
            return generate_local_response(prompt, mode)

# ======================
# STREAMLIT UI - JAIN THEMED
# ======================

# Custom CSS for Jain Theme
st.markdown("""
<style>
    :root {
        --jain-red: #8B0000;
        --jain-gold: #D4AF37;
        --jain-cream: #FFF8E7;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--jain-cream) 0%, #FFFFFF 100%);
    }
    
    h1, h2, h3 {
        color: var(--jain-red) !important;
    }
    
    .stButton>button {
        background-color: var(--jain-red);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #A52A2A;
    }
    
    .local-mode {
        background: linear-gradient(135deg, #4CAF50, #45a049) !important;
    }
    
    .api-mode {
        background: linear-gradient(135deg, #2196F3, #1976D2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_mode" not in st.session_state:
    st.session_state.user_mode = "Quick Chat (Youth) 💬"
if "voice_prompt" not in st.session_state:
    st.session_state.voice_prompt = ""
if "use_local_model" not in st.session_state:
    st.session_state.use_local_model = True  # Default to local model

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #8B0000, #A52A2A); 
                border-radius: 15px; color: white; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>🌸 AI Sister Yashvi 🌸</h1>
        <p style='margin: 0.5rem 0; font-size: 1.2rem;'>Jai Jinendra 🙏 Your Compassionate Jain Companion</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #8B0000, #A52A2A); 
                border-radius: 10px; color: white; margin-bottom: 1rem;'>
        <h3 style='color: white; margin: 0;'>⚙️ Configuration</h3>
    </div>
    """, unsafe_allow_html=True)

    # AI Mode Selector
    st.subheader("🤖 AI Mode")
    ai_mode = st.radio(
        "Choose Response Engine:",
        ["Local ML (Fast 🚀)", "Gemini AI (Advanced 🧠)"],
        index=0 if st.session_state.use_local_model else 1,
        key="ai_mode"
    )
    st.session_state.use_local_model = (ai_mode == "Local ML (Fast 🚀)")
    
    if st.session_state.use_local_model:
        st.success("✅ Using Local ML Model")
        st.caption("Fast, reliable responses using Jain knowledge base")
    else:
        st.info("🔗 Using Gemini AI")
        st.caption("Advanced responses with internet search")

    st.markdown("---")
    
    # Persona Mode
    st.subheader("🎭 Conversation Style")
    st.session_state.user_mode = st.radio(
        "Select Style:",
        ["Quick Chat (Youth) 💬", "Deep Dive (Elders/Learners) 🧘‍♀️"],
        key="persona_mode"
    )

    st.markdown("---")

    # Language Settings
    st.subheader("🎙️ Voice Settings")
    selected_lang = st.selectbox("Choose Language:", list(LANG_MAP.keys()))
    lang_code = LANG_MAP[selected_lang]

    st.markdown("---")

    # Jain Principles
    st.subheader("📖 Jain Principles")
    with st.expander("View Key Concepts"):
        st.markdown("""
        **🏹 Ahimsa** - Non-violence  
        **🔶 Anekantavada** - Multiple viewpoints  
        **📦 Aparigraha** - Non-possessiveness  
        **🗣️ Satya** - Truth  
        **🤲 Asteya** - Non-stealing
        """)

    st.markdown("---")

    # Clear History
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.voice_prompt = ""
        st.success("Conversation cleared!")
        st.rerun()

# Main Chat Interface
st.markdown(f"### 💬 Chat Mode: **{st.session_state.user_mode}**")
st.markdown(f"### 🤖 AI Engine: **{'Local ML 🚀' if st.session_state.use_local_model else 'Gemini AI 🧠'}**")

chat_container = st.container(height=400, border=True)
with chat_container:
    if not st.session_state.chat_history:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; color: #666;'>
            <h3>🕊️ Welcome to Your Digital Sanctuary</h3>
            <p>Start a conversation with Yashvi! Ask about Jain principles, spiritual guidance, or daily life.</p>
            <div style='background: #F0F8F0; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                <strong>Try asking:</strong><br>
                • What is Ahimsa?<br>
                • How to practice meditation?<br>
                • Tell me about Jain philosophy<br>
                • I'm feeling stressed today
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history:
        with st.chat_message("user" if msg["role"] == "User" else "assistant"):
            st.markdown(msg["content"])

# Input Section
st.markdown("---")
col_voice, col_text = st.columns([1, 4])

with col_voice:
    if st.button("🎙️ Speak to Yashvi", use_container_width=True, type="secondary"):
        listen_for_speech(lang_code)

with col_text:
    user_input = st.chat_input("📝 Type your message here...")

# Process Input
prompt_to_process = user_input
if st.session_state.voice_prompt:
    prompt_to_process = st.session_state.voice_prompt
    st.info(f"**Voice input:** {prompt_to_process}")
    st.session_state.voice_prompt = ""

if prompt_to_process:
    # Add user message to history
    st.session_state.chat_history.append({"role": "User", "content": prompt_to_process})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt_to_process)
        
        with st.chat_message("assistant"):
            with st.spinner("Yashvi is thinking..."):
                # Generate response using selected mode
                response = generate_response(
                    prompt_to_process, 
                    st.session_state.chat_history, 
                    st.session_state.user_mode,
                    st.session_state.use_local_model
                )
                
                st.markdown(response)
                
                # Add to history
                st.session_state.chat_history.append({"role": "Yashvi", "content": response})
                
                # Generate audio
                audio_b64 = get_tts_base64(response, lang_code)
                if audio_b64:
                    autoplay_audio(audio_b64)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><em>May your journey be filled with peace and compassion</em></p>
    <p style='font-size: 0.9rem;'>🕊️ <strong>Micchami Dukkadam</strong> 🕊️</p>
</div>
""", unsafe_allow_html=True)
